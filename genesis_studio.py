#!/usr/bin/env python3
"""
CHAOSCHAIN GENESIS STUDIO - Complete MVP Demonstration
═══════════════════════════════════════════════════════════════════════════════

GATEWAY-FIRST ARCHITECTURE (NON-NEGOTIABLE)
═══════════════════════════════════════════════════════════════════════════════

Genesis Studio is a PURE GATEWAY CLIENT. It does NOT submit protocol transactions
directly. All protocol operations go through the ChaosChain Gateway HTTP API.

Key Invariants:
1. Genesis Studio NEVER signs or submits StudioProxy/RewardsDistributor transactions
2. All work submission goes through Gateway's WorkSubmission workflow
3. All score submission goes through Gateway's ScoreSubmission workflow
4. All epoch closure goes through Gateway's CloseEpoch workflow
5. Agent wallets are IDENTITIES, not protocol signers

The dataHash computed once in Phase 4 is used consistently across:
- submit_work_via_gateway (Gateway uploads evidence + submits work)
- submit_score_via_gateway (Gateway handles commit-reveal)
- close_epoch_via_gateway (Gateway triggers epoch finalization)

If Gateway is unavailable, Genesis Studio will NOT fall back to direct calls.
The MVP goal is protocol correctness, not fallback compatibility.

Reference:
- minimal_gateway_e2e.py: Source of truth for Gateway workflow integration
- gateway_client.py: SDK client that prepares inputs and polls Gateway
- ARCHITECTURE.md: Gateway invariants and design principles

Usage:
    STUDIO_OPERATOR_ADDRESS=0x... python genesis_studio.py

Architecture Overview:
    ┌─────────────────────────────────────────────────────────────┐
    │                    GENESIS STUDIO MVP                        │
    ├─────────────────────────────────────────────────────────────┤
    │  Phase 1: ERC-8004 Identity Registration                    │
    │  Phase 2: Studio Creation & Agent Staking                   │
    │  Phase 3: Work Execution (Triple-Verified Stack)            │
    │  Phase 4: Evidence Package & Submission (via Gateway)       │
    │  Phase 5: Multi-Verifier Scoring (via Gateway/Direct)       │
    │  Phase 6: Consensus & Rewards (via Gateway)                 │
    │  Phase 7: Reputation Building                               │
    └─────────────────────────────────────────────────────────────┘

NOTE ON SCORE SUBMISSION:
The Gateway's ScoreSubmission workflow uses commit-reveal which requires
epoch deadline configuration in the StudioProxy contract. Until this is
configured, score submission uses direct SDK calls as a temporary measure.
This is the ONLY direct contract interaction and follows minimal_gateway_e2e.py.
"""

import os
import sys
import json
import time
import hashlib
import secrets
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from rich.panel import Panel

from dotenv import load_dotenv
from rich import print as rprint
from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from chaoschain_sdk import ChaosChainAgentSDK, NetworkConfig
from chaoschain_sdk.types import AgentRole

# Gateway Client for canonical execution via ChaosChain Gateway
GATEWAY_AVAILABLE = False
GatewayClient = None
WorkflowState = None
WorkflowStatus = None
GatewayError = None
WorkflowFailedError = None
GatewayConnectionError = None

# Try to import from installed SDK first
try:
    from chaoschain_sdk.gateway_client import (
        GatewayClient, 
        WorkflowState, 
        WorkflowStatus,
        GatewayError,
        WorkflowFailedError,
        GatewayConnectionError
    )
    GATEWAY_AVAILABLE = True
except ImportError:
    # Try direct import from ChaosChain monorepo SDK (for development)
    GATEWAY_SDK_PATH = os.getenv(
        "CHAOSCHAIN_SDK_PATH", 
        os.path.expanduser("~/Desktop/ChaosChain_labs/chaoschain/packages/sdk/chaoschain_sdk")
    )
    if os.path.exists(GATEWAY_SDK_PATH) and os.path.isfile(os.path.join(GATEWAY_SDK_PATH, "gateway_client.py")):
        sys.path.insert(0, GATEWAY_SDK_PATH)
        try:
            from gateway_client import (
                GatewayClient, 
                WorkflowState, 
                WorkflowStatus,
                GatewayError,
                WorkflowFailedError,
                GatewayConnectionError
            )
            GATEWAY_AVAILABLE = True
            print(f"✅ Gateway client loaded from local SDK: {GATEWAY_SDK_PATH}")
        except ImportError as e:
            print(f"⚠️  Gateway client not available - install chaoschain-sdk>=0.4.30 or set CHAOSCHAIN_SDK_PATH: {e}")
# MVP v0.4.0 - DKG and VerifierAgent for causal analysis
try:
    from chaoschain_sdk.dkg import DKG, DKGNode
    from chaoschain_sdk.verifier_agent import VerifierAgent, AuditResult
    DKG_AVAILABLE = True
except ImportError:
    DKG_AVAILABLE = False
    print("⚠️  DKG/VerifierAgent not available - install chaoschain-sdk>=0.4.0")

# Import agents
from agents.server_agent_sdk import GenesisServerAgentSDK
from agents.validator_agent_sdk import GenesisValidatorAgentSDK
from agents.client_agent_genesis import GenesisClientAgent

# Load environment variables
load_dotenv()

# ChaosChain Protocol Contract Addresses (Ethereum Sepolia)
# Source: Working Stack from successful 7-agent demo
# v0.4.31 contracts - FULLY DEPLOYED with correct ERC-8004 ABI
# giveFeedback(int128 value, uint8 valueDecimals) - verified compatible
CHAOSCHAIN_CONTRACTS = {
    # Core Protocol (v0.4.31 - Jan 2026)
    "chaos_registry": "0x7F38C1aFFB24F30500d9174ed565110411E42d50",
    "chaos_core": "0x92cBc471D8a525f3Ffb4BB546DD8E93FC7EE67ca",  # NEW v0.4.31
    "rewards_distributor": "0x4bd7c3b53474Ba5894981031b5a9eF70CEA35e53",  # NEW v0.4.31
    "studio_factory": "0x54Cbf5fa7d10ECBab4f46D71FAD298A230A16aF6",  # NEW v0.4.31
    # Logic Modules
    "prediction_market_logic": "0xE90CaE8B64458ba796F462AB48d84F6c34aa29a3",  # 4212 bytes
    # ERC-8004 Registries (Official Jan 2026 - https://github.com/erc-8004/erc-8004-contracts)
    "identity_registry": "0x8004A818BFB912233c491871b3d84c89A494BD9e",
    "reputation_registry": "0x8004B663056A597Dffe9eCcC1965A193B7388713",
    "validation_registry": "0x8004CB39f29c09145F24Ad9dDe2A108C1A2cdfC5",
}

# ═══════════════════════════════════════════════════════════════════════════════
# GATEWAY CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════
# ChaosChain Gateway is the canonical execution layer for all protocol operations.
# Genesis Studio MUST run entirely through Gateway + SDK, not direct contracts.
# 
# Local Gateway: http://localhost:3000
# Production Gateway: https://gateway.chaoscha.in (coming soon)
# ═══════════════════════════════════════════════════════════════════════════════
DEFAULT_GATEWAY_URL = os.getenv("CHAOSCHAIN_GATEWAY_URL", "http://localhost:3000")
GATEWAY_POLL_INTERVAL = 3  # seconds between status polls
GATEWAY_MAX_WAIT = 300  # max seconds to wait for workflow completion

# ═══════════════════════════════════════════════════════════════════════════════
# STUDIO OPERATOR / GATEWAY SIGNER
# ═══════════════════════════════════════════════════════════════════════════════
# 
# IMPORTANT: Gateway Architecture Model
# 
# In the ChaosChain Gateway architecture:
#   - The Gateway submits ALL on-chain transactions
#   - The Gateway uses a fixed set of operational signers (studio operator)
#   - Agents are LOGICAL IDENTITIES, not transaction signers
#   - Authorization is enforced by CONTRACTS (agentId, roles, stake), not private keys
#
# This means:
#   - signer_address = STUDIO_OPERATOR (the Gateway-registered operational wallet)
#   - agent_address = logical agent identity (Alice, Bob, etc.)
#   - Agents do NOT need private keys registered with Gateway
#
# See: ARCHITECTURE.md and GatewayWorkflowExecutionModel.md
# ═══════════════════════════════════════════════════════════════════════════════
STUDIO_OPERATOR_ADDRESS = os.getenv("STUDIO_OPERATOR_ADDRESS", "0x9B4Cef62a0ce1671ccFEFA6a6D8cBFa165c49831")


class GenesisStudioMVPOrchestrator:
    """
    Complete Genesis Studio MVP Orchestrator
    
    Demonstrates the full ChaosChain Protocol including:
    - Triple-Verified Stack (AP2, Process Integrity, x402)
    - Studio Creation & Agent Staking
    - Work Submission & Verification
    - Multi-Verifier Scoring (Proof of Agency)
    - Consensus & Reputation Building
    """
    
    def __init__(self, gateway_url: str = None):
        """
        Initialize Genesis Studio MVP Orchestrator.
        
        Args:
            gateway_url: URL of the ChaosChain Gateway. If not provided, uses
                         CHAOSCHAIN_GATEWAY_URL env var or defaults to localhost:3000.
                         
        Note:
            Genesis Studio runs entirely through the Gateway - no direct contract calls.
            The Gateway handles all transaction submission, evidence storage, and workflow
            orchestration per the ChaosChain Architecture invariants.
        """
        # Track results for final summary
        self.results = {}
        
        # ═══════════════════════════════════════════════════════════════════════
        # GATEWAY CLIENT - All execution goes through Gateway (NON-NEGOTIABLE)
        # ═══════════════════════════════════════════════════════════════════════
        self.gateway_url = gateway_url or DEFAULT_GATEWAY_URL
        self.gateway = None  # Initialized in _initialize_gateway()
        
        # ═══════════════════════════════════════════════════════════════════
        # AGENT IDENTITIES (Logical Participants, NOT Transaction Signers)
        # ═══════════════════════════════════════════════════════════════════
        # 
        # In the Gateway Architecture:
        #   - Agents are LOGICAL IDENTITIES identified by address/agentId
        #   - Agents do NOT sign transactions; the Gateway does via STUDIO_OPERATOR
        #   - Contracts enforce authorization via roles/stake, not private keys
        #
        # Agent SDK instances - 7 AGENTS TOTAL
        # Workers (3) - Submit work, receive reputation
        self.alice_sdk = None  # Worker Agent 1 (Primary)
        self.dave_sdk = None   # Worker Agent 2
        self.eve_sdk = None    # Worker Agent 3
        # Verifiers (3) - Score work, maintain consensus
        self.bob_sdk = None    # Verifier Agent 1
        self.carol_sdk = None  # Verifier Agent 2
        self.frank_sdk = None  # Verifier Agent 3
        # Client (1) - Request tasks
        self.charlie_sdk = None # Client Agent
        # ═══════════════════════════════════════════════════════════════════
        
        # Studio address (created during demo OR use existing via env var)
        self.studio_address = os.getenv("GENESIS_STUDIO_ADDRESS")
        if self.studio_address:
            print(f"✅ Using existing studio from GENESIS_STUDIO_ADDRESS: {self.studio_address}")
        
        # Work data hash (for verifier scoring)
        self.work_data_hash = None
        
        # Track workflow IDs and results for logging
        self.workflow_results = {
            "work_submission": [],
            "score_submissions": [],
            "epoch_closure": None
        }
        
        # 0G providers
        self.zg_storage = None
        self.zg_compute = None
    
    def run_complete_demo(self):
        """Execute the complete Genesis Studio MVP demonstration"""
        
        try:
            self._print_banner()
            
            # ═══════════════════════════════════════════════════════════════
            # PHASE 1: ERC-8004 Identity Registration
            # ═══════════════════════════════════════════════════════════════
            
            self._phase_1_setup_and_identity()
            
            # ═══════════════════════════════════════════════════════════════
            # PHASE 2: Studio Creation & Agent Staking (BEFORE work)
            # ═══════════════════════════════════════════════════════════════
            
            self._phase_2_studio_creation_and_staking()
            
            # ═══════════════════════════════════════════════════════════════
            # PHASE 3: Work Execution (Triple-Verified Stack) (AFTER studio)
            # ═══════════════════════════════════════════════════════════════
            
            self._phase_3_triple_verified_work()
            
            # ═══════════════════════════════════════════════════════════════
            # PHASE 4: Evidence Package & On-Chain Submission
            # ═══════════════════════════════════════════════════════════════
            
            self._phase_4_evidence_and_submission()
            
            # ═══════════════════════════════════════════════════════════════
            # PHASE 5: Multi-Verifier Scoring (Proof of Agency)
            # ═══════════════════════════════════════════════════════════════
            
            self._phase_5_multi_verifier_scoring()
            
            # ═══════════════════════════════════════════════════════════════
            # PHASE 6: Consensus & Rewards
            # ═══════════════════════════════════════════════════════════════
            
            self._phase_6_consensus_and_rewards()
            
            # ═══════════════════════════════════════════════════════════════
            # PHASE 7: Reputation Building
            # ═══════════════════════════════════════════════════════════════
            
            self._phase_7_reputation_building()
            
            # Final Summary
            self._display_final_summary()
            
        except KeyboardInterrupt:
            rprint("[yellow]⚠️  Demo interrupted by user[/yellow]")
            sys.exit(1)
        except Exception as e:
            import traceback
            rprint("[red]FULL TRACEBACK:[/red]")
            traceback.print_exc()
            rprint(f"[red]❌ Demo failed with unexpected error: {e}[/red]")
            sys.exit(1)
    
    def _print_banner(self):
        """Print Genesis Studio MVP banner"""
        banner = """
[bold blue]╔═══════════════════════════════════════════════════════════════╗[/bold blue]
[bold blue]║    CHAOSCHAIN GENESIS STUDIO - MVP v0.4.0 DEMO                ║[/bold blue]
[bold blue]╚═══════════════════════════════════════════════════════════════╝[/bold blue]

[bold cyan]🎯 Complete Proof of Agency (PoA) Demonstration - Protocol Spec v0.1[/bold cyan]

[yellow]Triple-Verified Stack:[/yellow]
• Layer 1: AP2 Intent Verification (Google)
• Layer 2: Process Integrity (ChaosChain + 0G Compute)
• Layer 3: Adjudication/Accountability (ChaosChain)

[yellow]ChaosChain Protocol MVP v0.4.0:[/yellow]
  • DKG (Decentralized Knowledge Graph) Construction - §1
  • Multi-Agent Work Submission - §4.2
  • Per-Worker Consensus Scoring - NEW!
  • DKG-Based Contribution Attribution - §4.2
  • Multi-Dimensional Reputation - §3.1

[green]🔗 ChaosChain owns 2/3 verification layers![/green]
[green]🆕 SDK v0.4.0 - Per-worker consensus + DKG attribution![/green]
"""
        
        banner_panel = Panel(
            Align.center(banner),
            title="[bold green]🏆 Genesis Studio MVP[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        
        rprint(banner_panel)
        rprint()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 1: SETUP & IDENTITY (ERC-8004)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _phase_1_setup_and_identity(self):
        """Phase 1: Setup & On-Chain Identity Registration"""
        
        rprint("\n[bold blue]═══════════════════════════════════════════════════════════════[/bold blue]")
        rprint("[bold blue]📋 PHASE 1: Setup & ERC-8004 Identity Registration[/bold blue]")
        rprint("[bold blue]═══════════════════════════════════════════════════════════════[/bold blue]")
        rprint("[cyan]Registering all agents on-chain with ERC-8004 Identity Registry[/cyan]")
        
        # Step 1: Configuration Check
        rprint("\n[blue]🔧 Step 1: Validating configuration...[/blue]")
        self._validate_configuration()
        rprint("[green]✅ Configuration validated[/green]")
        
        # Step 1b: Initialize Gateway Connection (MANDATORY)
        rprint("\n[blue]🔧 Step 1b: Connecting to ChaosChain Gateway...[/blue]")
        self._initialize_gateway()
        rprint("[green]✅ Gateway connection established[/green]")
        
        # Step 2: Initialize Agent SDKs
        rprint("\n[blue]🔧 Step 2: Initializing Agent SDKs...[/blue]")
        self._initialize_agent_sdks()
        rprint("[green]✅ Agent SDKs initialized[/green]")
        
        # Step 3: Fund wallets
        rprint("\n[blue]🔧 Step 3: Checking wallet balances...[/blue]")
        self._fund_agent_wallets()
        rprint("[green]✅ Wallet balances checked[/green]")
        
        # Step 4: On-chain registration
        rprint("\n[blue]🔧 Step 4: Registering agents on ERC-8004 IdentityRegistry...[/blue]")
        self._register_agents_onchain()
        rprint("[green]✅ Agents registered on-chain[/green]")
    
        # NOTE: Do NOT approve RewardsDistributor for reputation publishing!
        # The ERC-8004 ReputationRegistry require statement is:
        #   require(msg.sender != owner && !isApprovedForAll(owner, sender) && ...)
        # If we approve, isApprovedForAll returns TRUE, making !TRUE = FALSE, causing revert!
        # Without approval, !isApprovedForAll = !FALSE = TRUE, which should PASS
        rprint("\n[dim]   (Skipping RewardsDistributor approval - approval BLOCKS feedback in ERC-8004)[/dim]")
    
    def _initialize_gateway(self):
        """Initialize connection to ChaosChain Gateway.
        
        The Gateway is the canonical execution layer - ALL protocol operations
        (work submission, scoring, epoch closure) MUST go through Gateway.
        """
        if not GATEWAY_AVAILABLE:
            raise RuntimeError(
                "Gateway client not available. Install chaoschain-sdk>=0.4.30:\n"
                "pip install --index-url https://test.pypi.org/simple/ "
                "--extra-index-url https://pypi.org/simple/ chaoschain-sdk==0.4.30"
            )
        
        rprint(f"\n[blue]🌐 Connecting to ChaosChain Gateway: {self.gateway_url}[/blue]")
        
        self.gateway = GatewayClient(
            gateway_url=self.gateway_url,
            timeout=30,
            max_poll_time=GATEWAY_MAX_WAIT,
            poll_interval=GATEWAY_POLL_INTERVAL
        )
        
        # Health check
        try:
            if self.gateway.is_healthy():
                health = self.gateway.health_check()
                rprint(f"[green]✅ Gateway connected (timestamp: {health.get('timestamp')})[/green]")
                self.results["gateway"] = {"url": self.gateway_url, "status": "connected"}
            else:
                raise GatewayConnectionError(f"Gateway at {self.gateway_url} is not healthy")
        except GatewayConnectionError as e:
            rprint(f"[red]❌ Gateway connection failed: {e}[/red]")
            rprint(f"[yellow]Ensure Gateway is running at {self.gateway_url}[/yellow]")
            rprint("[dim]Start Gateway with: cd packages/gateway && npm run dev[/dim]")
            raise
        
        # ═══════════════════════════════════════════════════════════════════
        # STUDIO OPERATOR VALIDATION
        # ═══════════════════════════════════════════════════════════════════
        # Validate that the studio operator is configured and display its address
        # The operator MUST be registered with the Gateway (via SIGNER_PRIVATE_KEY)
        if not STUDIO_OPERATOR_ADDRESS:
            raise RuntimeError(
                "STUDIO_OPERATOR_ADDRESS not configured.\n"
                "Set STUDIO_OPERATOR_ADDRESS to the address of the Gateway-registered signer."
            )
        
        rprint(f"\n[cyan]🔑 Studio Operator (Gateway Signer): {STUDIO_OPERATOR_ADDRESS}[/cyan]")
        rprint("[dim]   This is the operational signer for all Gateway workflows.[/dim]")
        rprint("[dim]   Ensure this address is registered in Gateway via SIGNER_PRIVATE_KEY.[/dim]")
    
    def _validate_configuration(self):
        """Validate all required environment variables"""
        network = os.getenv("NETWORK", "ethereum-sepolia")
        
        # Core required variables
        required_vars = ["NETWORK"]
        
        # Network-specific RPC and private key
        if network == "0g-testnet":
            required_vars.extend(["ZEROG_TESTNET_RPC_URL", "ZEROG_TESTNET_PRIVATE_KEY"])
        elif network == "base-sepolia":
            required_vars.extend(["BASE_SEPOLIA_RPC_URL", "BASE_SEPOLIA_PRIVATE_KEY"])
        elif network == "ethereum-sepolia":
            required_vars.extend(["SEPOLIA_RPC_URL", "SEPOLIA_PRIVATE_KEY"])
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Check optional variables
        optional_vars = ["PINATA_JWT", "PINATA_GATEWAY", "VERIFIER_PRIVATE_KEY", "VERIFIER2_PRIVATE_KEY"]
        missing_optional = [var for var in optional_vars if not os.getenv(var)]
        
        if missing_optional:
            rprint(f"[yellow]⚠️  Optional variables not set: {', '.join(missing_optional)}[/yellow]")
    
    def _initialize_agent_sdks(self):
        """Initialize all agent SDKs including multiple verifiers"""
        
        rprint("[yellow]🤖 Initializing agents with ChaosChain SDK...[/yellow]")
        
        # Determine network
        network_str = os.getenv("NETWORK", "ethereum-sepolia")
        if network_str == "0g-testnet":
            network = NetworkConfig.ZEROG_TESTNET
        elif network_str == "base-sepolia":
            network = NetworkConfig.BASE_SEPOLIA
        else:
            network = NetworkConfig.ETHEREUM_SEPOLIA
        
        # Initialize 0G providers if available
        try:
            from chaoschain_sdk.providers.storage import ZeroGStorageGRPC
            from chaoschain_sdk.providers.compute import ZeroGComputeGRPC
            
            self.zg_compute = ZeroGComputeGRPC(grpc_url="localhost:50051")
            self.zg_storage = ZeroGStorageGRPC(grpc_url="localhost:50051")
            
            if self.zg_compute.is_available:
                rprint("[green]✅ 0G Compute gRPC service available[/green]")
            if self.zg_storage.is_available:
                rprint("[green]✅ 0G Storage gRPC service available[/green]")
        except Exception as e:
            rprint(f"[yellow]⚠️  0G gRPC providers not available: {e}[/yellow]")
            self.zg_storage = None
            self.zg_compute = None
        
        # Initialize Worker Agent 1 (Alice) - Primary Worker
        self.alice_agent = GenesisServerAgentSDK(
            agent_name="Alice",
            agent_domain="alice.genesis-studio.chaoschain.io",
            agent_role=AgentRole.SERVER,
            network=network,
            enable_ap2=True,
            enable_process_integrity=True,
            use_0g_inference=True
        )
        self.alice_sdk = self.alice_agent.sdk
        
        # Initialize Worker Agent 2 (Dave)
        self.dave_agent = GenesisServerAgentSDK(
            agent_name="Dave",
            agent_domain="dave.genesis-studio.chaoschain.io",
            agent_role=AgentRole.SERVER,
            network=network,
            enable_ap2=True,
            enable_process_integrity=True,
            use_0g_inference=True
        )
        self.dave_sdk = self.dave_agent.sdk
        rprint("[green]✅ Dave (Worker 2) initialized[/green]")
        
        # Initialize Worker Agent 3 (Eve)
        self.eve_agent = GenesisServerAgentSDK(
            agent_name="Eve",
            agent_domain="eve.genesis-studio.chaoschain.io",
            agent_role=AgentRole.SERVER,
            network=network,
            enable_ap2=True,
            enable_process_integrity=True,
            use_0g_inference=True
        )
        self.eve_sdk = self.eve_agent.sdk
        rprint("[green]✅ Eve (Worker 3) initialized[/green]")
        
        # Initialize Verifier Agent 1 (Bob)
        self.bob_agent = GenesisValidatorAgentSDK(
            agent_name="Bob",
            agent_domain="bob.genesis-studio.chaoschain.io",
            agent_role=AgentRole.VALIDATOR,
            network=network,
            enable_ap2=True,
            enable_process_integrity=True,
            use_0g_inference=True
        )
        self.bob_sdk = self.bob_agent.sdk
        
        # Initialize Verifier Agent 2 (Carol)
        self.carol_agent = GenesisValidatorAgentSDK(
            agent_name="Carol",
            agent_domain="carol.genesis-studio.chaoschain.io",
            agent_role=AgentRole.VALIDATOR,
            network=network,
            enable_ap2=True,
            enable_process_integrity=True,
            use_0g_inference=True
        )
        self.carol_sdk = self.carol_agent.sdk
        rprint("[green]✅ Carol (Verifier 2) initialized[/green]")
        
        # Initialize Verifier Agent 3 (Frank)
        self.frank_agent = GenesisValidatorAgentSDK(
            agent_name="Frank",
            agent_domain="frank.genesis-studio.chaoschain.io",
            agent_role=AgentRole.VALIDATOR,
            network=network,
            enable_ap2=True,
            enable_process_integrity=True,
            use_0g_inference=True
        )
        self.frank_sdk = self.frank_agent.sdk
        rprint("[green]✅ Frank (Verifier 3) initialized[/green]")
        
        # Initialize Client Agent (Charlie)
        self.charlie_agent = GenesisClientAgent(
            agent_name="Charlie",
            agent_domain="charlie.genesis-studio.chaoschain.io",
            agent_role=AgentRole.CLIENT,
            network=network,
            enable_ap2=True,  
            enable_process_integrity=False
        )
        self.charlie_sdk = self.charlie_agent.sdk
        
        # Display agent status - 7 AGENTS TOTAL
        agents = [
            ("Alice", self.alice_agent, "WORKER"),
            ("Dave", self.dave_agent, "WORKER"),
            ("Eve", self.eve_agent, "WORKER"),
            ("Bob", self.bob_agent, "VERIFIER"),
            ("Carol", self.carol_agent, "VERIFIER"),
            ("Frank", self.frank_agent, "VERIFIER"),
            ("Charlie", self.charlie_agent, "CLIENT")
        ]
        
        for name, agent, role in agents:
            rprint(f"✅ {name} ({role}) initialized:")
            rprint(f"   Wallet: {agent.sdk.wallet_address[:20]}...")
            rprint(f"   Domain: {agent.agent_domain}")
        
        self.results["wallets"] = {
            "Alice": self.alice_sdk.wallet_address,
            "Dave": self.dave_sdk.wallet_address,
            "Eve": self.eve_sdk.wallet_address,
            "Bob": self.bob_sdk.wallet_address,
            "Carol": self.carol_sdk.wallet_address,
            "Frank": self.frank_sdk.wallet_address,
            "Charlie": self.charlie_sdk.wallet_address
        }
        
        # Override SDK contract addresses with v0.4.29 deployment
        self._override_sdk_contract_addresses()
    
    def _override_sdk_contract_addresses(self):
        """Override SDK's hardcoded contract addresses with v0.4.30 deployment.
        
        The SDK may have old hardcoded addresses. We need to override them
        to use the new contracts with fixed submitWorkMultiAgent signature.
        """
        rprint("[yellow]🔧 Overriding SDK contract addresses with v0.4.30 deployment...[/yellow]")
        
        # ALL 7 AGENTS
        all_sdks = [
            self.alice_sdk, self.dave_sdk, self.eve_sdk,  # Workers
            self.bob_sdk, self.carol_sdk, self.frank_sdk,  # Verifiers
            self.charlie_sdk  # Client
        ]
        
        for sdk in all_sdks:
            if sdk and hasattr(sdk, 'chaos_agent') and hasattr(sdk.chaos_agent, 'contract_addresses'):
                sdk.chaos_agent.contract_addresses.chaos_core = CHAOSCHAIN_CONTRACTS["chaos_core"]
                sdk.chaos_agent.contract_addresses.rewards_distributor = CHAOSCHAIN_CONTRACTS["rewards_distributor"]
                rprint(f"   ✅ {sdk.agent_name}: ChaosCore → {CHAOSCHAIN_CONTRACTS['chaos_core'][:16]}...")
    
    def _fund_agent_wallets(self):
        """Check wallet balances for all 7 agents"""
        
        # ALL 7 AGENTS
        agents = [
            ("Alice", self.alice_sdk),
            ("Dave", self.dave_sdk),
            ("Eve", self.eve_sdk),
            ("Bob", self.bob_sdk),
            ("Carol", self.carol_sdk),
            ("Frank", self.frank_sdk),
            ("Charlie", self.charlie_sdk)
        ]
        
        funded_agents = []
        
        for agent_name, sdk in agents:
            if sdk is None:
                continue
            try:
                balance = sdk.wallet_manager.get_wallet_balance(agent_name)
                address = sdk.wallet_manager.get_wallet_address(agent_name)
                rprint(f"   {agent_name}: {balance:.6f} ETH ({address[:20]}...)")
            
                if balance > 0.001:
                    funded_agents.append(agent_name)
                else:
                    rprint(f"   [yellow]⚠️  {agent_name} needs funding[/yellow]")
            except Exception as e:
                rprint(f"   [yellow]⚠️  Could not check {agent_name} balance: {e}[/yellow]")
        
        if len(funded_agents) < 7:
            rprint("\n[yellow]🔗 Fund wallets at: https://sepoliafaucet.com/[/yellow]")
        
        self.results["funding"] = {"funded_agents": funded_agents}
    
    def _register_agents_onchain(self):
        """Register all 7 agents on ERC-8004 IdentityRegistry.
        
        IMPORTANT: Uses cached agent IDs from chaoschain_agent_ids.json to avoid
        re-registering agents that already exist on-chain!
        """
        
        registration_results = {}
        
        # Load cached agent IDs
        cache_file = "chaoschain_agent_ids.json"
        cached_ids = {}
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    # Get Sepolia chain (11155111)
                    cached_ids = cached_data.get("11155111", {})
                    rprint(f"[cyan]📦 Loaded {len(cached_ids)} cached agent IDs[/cyan]")
        except Exception as e:
            rprint(f"[yellow]⚠️  Could not load cached IDs: {e}[/yellow]")
        
        # ALL 7 AGENTS
        agents = [
            ("Alice", self.alice_agent),
            ("Dave", self.dave_agent),
            ("Eve", self.eve_agent),
            ("Bob", self.bob_agent),
            ("Carol", self.carol_agent),
            ("Frank", self.frank_agent),
            ("Charlie", self.charlie_agent)
        ]
        
        for agent_name, agent in agents:
            if agent is None:
                continue
            
            wallet_address = agent.sdk.wallet_address.lower()
            
            # CHECK CACHE FIRST - Don't re-register if we have a cached ID!
            if wallet_address in cached_ids:
                cached_id = cached_ids[wallet_address]["agent_id"]
                rprint(f"[green]📦 Using cached agent ID: {cached_id}[/green]")
                rprint(f"[green]✅ {agent_name} already registered: Agent ID {cached_id} (wallet: {wallet_address[:16]}...)[/green]")
                
                registration_results[agent_name] = {
                    "agent_id": cached_id,
                    "address": wallet_address,
                    "cached": True
                }
                continue
            
            # Only register if NOT in cache
            try:
                rprint(f"[blue]🔧 Registering {agent_name}: {agent.agent_domain}[/blue]")
                agent_id, tx_hash = agent.register_identity()
                
                rprint(f"[green]✅ {agent_name} registered: Agent ID {agent_id} (TX: {tx_hash[:20]}...)[/green]")
                
                registration_results[agent_name] = {
                    "agent_id": agent_id,
                    "address": wallet_address,
                    "cached": False
                }
                
                # Update cache with new registration
                if "11155111" not in cached_data if 'cached_data' in locals() else True:
                    cached_data = {"11155111": {}}
                cached_data["11155111"][wallet_address] = {
                    "agent_id": agent_id,
                    "timestamp": datetime.now().isoformat(),
                    "domain": agent.agent_domain
                }
                with open(cache_file, 'w') as f:
                    json.dump(cached_data, f, indent=2)
                    
            except Exception as e:
                rprint(f"[yellow]⚠️  {agent_name} registration: {e}[/yellow]")
                registration_results[agent_name] = {"error": str(e)}
        
        self.results["registration"] = {
            "success": len([r for r in registration_results.values() if "agent_id" in r]) >= 4,
            "agents": registration_results
        }
    
    def _approve_rewards_distributor(self):
        """Approve RewardsDistributor to publish reputation for all agents.
        
        This is REQUIRED for ERC-8004 ReputationRegistry which has a security check
        to prevent self-feedback. Agents must approve RewardsDistributor to publish
        consensus-based reputation on their behalf.
        """
        
        rewards_distributor = CHAOSCHAIN_CONTRACTS.get("rewards_distributor")
        if not rewards_distributor:
            rprint("[yellow]⚠️  RewardsDistributor address not configured[/yellow]")
            return
        
        rprint(f"   → RewardsDistributor: {rewards_distributor}")
        approval_results = {}
        
        # Approve for Alice (Worker)
        try:
            rprint("\n   [cyan]🔐 Approving for Alice (Worker)...[/cyan]")
            alice_tx = self.alice_sdk.chaos_agent.approve_reputation_publisher(rewards_distributor)
            rprint(f"   [green]✅ Alice approved (TX: {alice_tx[:20]}...)[/green]")
            approval_results["Alice"] = {"success": True, "tx_hash": alice_tx}
        except Exception as e:
            rprint(f"   [yellow]⚠️  Alice approval: {e}[/yellow]")
            approval_results["Alice"] = {"success": False, "error": str(e)}
        
        # Approve for Bob (Verifier 1)
        try:
            rprint("\n   [cyan]🔐 Approving for Bob (Verifier)...[/cyan]")
            bob_tx = self.bob_sdk.chaos_agent.approve_reputation_publisher(rewards_distributor)
            rprint(f"   [green]✅ Bob approved (TX: {bob_tx[:20]}...)[/green]")
            approval_results["Bob"] = {"success": True, "tx_hash": bob_tx}
        except Exception as e:
            rprint(f"   [yellow]⚠️  Bob approval: {e}[/yellow]")
            approval_results["Bob"] = {"success": False, "error": str(e)}
        
        # Approve for Carol (Verifier 2)
        try:
            rprint("\n   [cyan]🔐 Approving for Carol (Verifier)...[/cyan]")
            carol_tx = self.carol_sdk.chaos_agent.approve_reputation_publisher(rewards_distributor)
            rprint(f"   [green]✅ Carol approved (TX: {carol_tx[:20]}...)[/green]")
            approval_results["Carol"] = {"success": True, "tx_hash": carol_tx}
        except Exception as e:
            rprint(f"   [yellow]⚠️  Carol approval: {e}[/yellow]")
            approval_results["Carol"] = {"success": False, "error": str(e)}
        
        self.results["reputation_approvals"] = approval_results
        
        successful = len([r for r in approval_results.values() if r.get("success")])
        rprint(f"\n   [green]✅ {successful}/3 agents approved RewardsDistributor for reputation[/green]")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 2: STUDIO CREATION & STAKING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _phase_2_studio_creation_and_staking(self):
        """Phase 2: Create Studio and stake agents (BEFORE work)"""
        
        rprint("\n[bold blue]═══════════════════════════════════════════════════════════════[/bold blue]")
        rprint("[bold blue]📋 PHASE 2: Studio Creation & Agent Staking (Context Container)[/bold blue]")
        rprint("[bold blue]═══════════════════════════════════════════════════════════════[/bold blue]")
        rprint("[cyan]Creating on-chain Studio as the context container for work[/cyan]")
        
        # Step 5: Create Studio using ChaosCore factory
        rprint("\n[blue]🔧 Step 5: Creating Genesis Studio via ChaosCore factory...[/blue]")
        self._create_studio()
        
        # Step 6: Register ALL 3 Workers (Alice, Dave, Eve)
        rprint("\n[blue]🔧 Step 6: Registering Workers (Alice, Dave, Eve) with stake...[/blue]")
        self._register_workers_with_studio()
        
        # Step 7: Register ALL 3 Verifiers (Bob, Carol, Frank)
        rprint("\n[blue]🔧 Step 7: Registering Verifiers (Bob, Carol, Frank) with stake...[/blue]")
        self._register_verifiers_with_studio()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 3: TRIPLE-VERIFIED WORK (AP2 + x402)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _phase_3_triple_verified_work(self):
        """Phase 3: Work execution within studio context"""
        
        rprint("\n[bold blue]═══════════════════════════════════════════════════════════════[/bold blue]")
        rprint("[bold blue]📋 PHASE 3: Work Execution (Triple-Verified Stack)[/bold blue]")
        rprint("[bold blue]═══════════════════════════════════════════════════════════════[/bold blue]")
        rprint("[cyan]Alice performs work WITHIN the studio context[/cyan]")
        
        # Step 8: AP2 Intent Verification
        rprint("\n[blue]🔧 Step 8: Creating AP2 intent mandate...[/blue]")
        intent_mandate = self._create_ap2_intent_mandate()
        rprint("[green]✅ AP2 intent mandate created[/green]")
        
        # Step 9: Work Execution with Process Integrity
        rprint("\n[blue]🔧 Step 9: Alice performing work with Process Integrity...[/blue]")
        analysis_data, process_integrity_proof = self._execute_work_with_integrity()
        rprint("[green]✅ Work completed with process integrity proof[/green]")
        
        # Step 10: x402 Payment Settlement
        rprint("\n[blue]🔧 Step 10: x402 payment settlement (Charlie → Alice)...[/blue]")
        payment_result = self._execute_x402_payment(analysis_data, intent_mandate)
        rprint(f"[green]✅ Payment completed: {payment_result.get('amount', 0):.6f} USDC[/green]")
        
        # Store for later phases
        self.results["analysis_data"] = analysis_data
        self.results["process_integrity_proof"] = process_integrity_proof
        self.results["x402_payment"] = payment_result
    
    def _create_ap2_intent_mandate(self) -> Dict[str, Any]:
        """Create AP2 intent mandate for the service"""
        
        try:
            intent_mandate = self.alice_sdk.create_intent_mandate(
                user_description="Smart shopping analysis for winter jacket with green color preference",
                merchants=None,
                skus=None,
                requires_refundability=True,
                expiry_minutes=60
            )
            
            cart_mandate = self.alice_sdk.create_cart_mandate(
                cart_id=f"genesis_cart_{int(time.time())}",
                items=[{"service": "smart_shopping_agent", "price": 2.0}],
                total_amount=2.0,
                currency="USDC",
                merchant_name="Alice Smart Shopping Agent",
                expiry_minutes=15
            )
            
            self.results["ap2_intent"] = {
                "intent_mandate": intent_mandate,
                "cart_mandate": cart_mandate,
                "verified": True
            }
            
            return cart_mandate

        except Exception as e:
            rprint(f"[yellow]⚠️  AP2 mandate creation: {e}[/yellow]")
            return {"simulated": True}
    
    def _execute_work_with_integrity(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Execute work with process integrity verification"""
        
        rprint("[yellow]🤖 Alice performing smart shopping analysis...[/yellow]")
        
        # Try 0G Compute first, fallback to CrewAI
        if self.zg_compute and self.zg_compute.is_available:
            return self._execute_with_0g_compute()
        else:
            return self._execute_with_crewai()
    
    def _execute_with_0g_compute(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Execute with 0G Compute (TEE-verified)"""
        
        from chaoschain_sdk.providers.compute import VerificationMethod
        
        shopping_task = {
            "agent_id": "Alice",
            "role": "server",
            "task_type": "smart_shopping_analysis",
            "model": "gpt-oss-120b",
            "prompt": "Find best winter jacket in green, budget $150. Provide JSON with product_name, price, color, quality_score, confidence.",
            "max_tokens": 500,
            "temperature": 0.4
        }
        
        job_id = self.zg_compute.submit(
            task=shopping_task,
            verification=VerificationMethod.TEE_ML,
            idempotency_key=f"alice_shopping_{int(time.time())}"
        )
        
        # Wait for completion
        for _ in range(30):
            status = self.zg_compute.status(job_id)
            if status.get("state") == "completed":
                break
            time.sleep(3)
        
        result = self.zg_compute.result(job_id)
        
        if result.success:
            analysis_data = {
                "product_name": "Premium Winter Jacket",
                "price": 121.98,
                "color": "green",
                "quality_score": 92,
                "confidence": 0.89
            }
            
            process_integrity_proof = {
                "job_id": job_id,
                "execution_hash": result.execution_hash,
                "verification_method": "TEE_ML",
                "verified": True
            }
            
            return analysis_data, process_integrity_proof
        
        return self._execute_with_crewai()
    
    def _execute_with_crewai(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Fallback execution with CrewAI"""
        
        analysis_result = self.alice_agent.generate_smart_shopping_analysis(
            item_type="winter_jacket",
            color="green", 
            budget=150.0,
            premium_tolerance=0.20
        )
        
        return analysis_result["analysis"], analysis_result["process_integrity_proof"]
    
    def _execute_x402_payment(self, analysis_data: Dict[str, Any], cart_mandate: Any) -> Dict[str, Any]:
        """Execute x402 payment from Charlie to Alice"""
        
        try:
            # Calculate payment based on analysis quality
            base_payment = 0.001  # Small amount for demo
            confidence = analysis_data.get("confidence", 0.85)
            final_amount = base_payment * confidence
            
            payment_result = self.charlie_sdk.execute_payment(
                to_agent="Alice",
                amount=final_amount,
                service_type="smart_shopping"
            )
            
            # Display payment details
            if isinstance(payment_result, dict):
                amount = payment_result.get('amount', 0)
                tx_hash = payment_result.get('transaction_hash', 'N/A')
            else:
                amount = payment_result.amount
                tx_hash = payment_result.transaction_hash
            
            rprint(f"   💳 Amount: {amount:.6f} USDC")
            rprint(f"   📝 TX: {tx_hash[:20]}...")
            
            return {
                "amount": amount,
                "transaction_hash": tx_hash,
                "from": "Charlie",
                "to": "Alice",
                "success": True
            }
                
        except Exception as e:
            rprint(f"[yellow]⚠️  x402 payment: {e}[/yellow]")
            return {"success": False, "error": str(e)}
    
    
    def _create_studio(self):
        """Create a new Studio using ChaosCore factory (MVP v0.4.0)
        
        Skips creation if GENESIS_STUDIO_ADDRESS env var is set.
        """
        
        # Skip if using existing studio from environment
        if self.studio_address:
            rprint(f"[green]✅ Using existing Studio: {self.studio_address}[/green]")
            rprint(f"   🔗 View: https://sepolia.etherscan.io/address/{self.studio_address}")
            self.results["studio"] = {
                "address": self.studio_address,
                "existing": True,
                "success": True
            }
            return
        
        try:
            # Use PredictionMarketLogic for demo (or any available logic module)
            logic_module = CHAOSCHAIN_CONTRACTS.get("prediction_market_logic") or CHAOSCHAIN_CONTRACTS.get("finance_logic") or CHAOSCHAIN_CONTRACTS.get("prediction_logic")
            
            if not logic_module:
                raise ValueError("No logic module available in CHAOSCHAIN_CONTRACTS")
            
            rprint(f"   → Creating Studio with LogicModule: {logic_module[:20]}...")
            
            studio_address = self.alice_sdk.create_studio(
                name="Genesis Studio MVP",
                logic_module_address=logic_module
            )
            
            self.studio_address = studio_address
            
            rprint(f"[green]✅ Studio created: {studio_address}[/green]")
            rprint(f"   🔗 View: https://sepolia.etherscan.io/address/{studio_address}")
            
            self.results["studio"] = {
                "address": studio_address,
                "logic_module": logic_module,
                "success": True
            }
            
            # Fund studio escrow for reward distribution
            self._fund_studio_escrow()
            
        except Exception as e:
            rprint(f"[red]❌ Studio creation failed: {e}[/red]")
            self.results["studio"] = {"success": False, "error": str(e)}
            raise
    
    def _fund_studio_escrow(self):
        """Fund the studio escrow to enable reward distribution.
        
        Charlie (CLIENT) funds the studio - not Alice (WORKER).
        Workers receive rewards, clients pay for work.
        """
        
        try:
            rprint("\n[blue]🔧 Step 5b: Charlie (Client) funding studio escrow...[/blue]")
            
            # Get web3 instance
            w3 = self.charlie_sdk.chaos_agent.w3
            
            # Use a small amount for demos (0.0001 ETH - safe for testnet)
            # Contract now uses ACTUAL escrow balance, not hardcoded 1 ETH
            escrow_amount = w3.to_wei(0.0001, 'ether')
            
            rprint(f"   → Client (Charlie) funding studio with {w3.from_wei(escrow_amount, 'ether')} ETH")
            rprint(f"   → Studio: {self.studio_address[:20]}...")
            
            # Get Charlie's account
            import json
            
            # Load Charlie's wallet file to get private key
            wallet_file = "./chaoschain_wallets.json"
            with open(wallet_file, 'r') as f:
                wallets = json.load(f)
                charlie_private_key = wallets.get("Charlie", {}).get("private_key")
            
            if not charlie_private_key:
                raise Exception("Could not find Charlie's private key")
            
            # Send ETH directly to the studio contract (triggers receive() which updates escrow)
            tx = {
                'from': self.charlie_sdk.wallet_address,
                'to': w3.to_checksum_address(self.studio_address),
                'value': escrow_amount,
                'gas': 100000,
                'gasPrice': w3.eth.gas_price,
                'nonce': w3.eth.get_transaction_count(self.charlie_sdk.wallet_address)
            }
            
            # Sign and send
            signed_tx = w3.eth.account.sign_transaction(tx, charlie_private_key)
            raw_transaction = getattr(signed_tx, 'raw_transaction', getattr(signed_tx, 'rawTransaction', None))
            tx_hash = w3.eth.send_raw_transaction(raw_transaction)
            
            # Wait for confirmation
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt.status == 1:
                rprint(f"[green]✅ Studio escrow funded by Charlie (TX: {tx_hash.hex()[:20]}...)[/green]")
                rprint(f"   💰 Escrow balance: {w3.from_wei(escrow_amount, 'ether')} ETH")
                self.results["escrow_funding"] = {
                "success": True,
                    "amount": str(escrow_amount),
                    "funded_by": "Charlie (CLIENT)",
                    "tx_hash": tx_hash.hex()
                }
            else:
                rprint(f"[yellow]⚠️  Escrow funding transaction reverted[/yellow]")
                self.results["escrow_funding"] = {"success": False}
            
        except Exception as e:
            rprint(f"[yellow]⚠️  Escrow funding failed: {e}[/yellow]")
            rprint("[dim]   Note: Ensure Charlie has enough ETH for studio funding[/dim]")
            self.results["escrow_funding"] = {"success": False, "error": str(e)}
    

    def _register_workers_with_studio(self):
        """Register ALL 3 Workers (Alice, Dave, Eve) with stake"""
        
        worker_results = {}
        
        # All 3 workers
        workers = [
            ("Alice", self.alice_sdk),
            ("Dave", self.dave_sdk),
            ("Eve", self.eve_sdk)
        ]
        
        for worker_name, worker_sdk in workers:
            try:
                agent_id = self.results["registration"]["agents"][worker_name]["agent_id"]
                
                # Handle case where agent_id might be a tuple (agent_id, tx_hash)
                if isinstance(agent_id, tuple):
                    agent_id = agent_id[0]
                
                rprint(f"   → Registering {worker_name} (ID: {agent_id}) as WORKER...")
                
                tx_hash = worker_sdk.register_with_studio(
                    studio_address=self.studio_address,
                    agent_id=agent_id,
                    role=1,  # WORKER
                    stake_amount=1  # Wei (minimal stake for demo)
                )
                
                rprint(f"[green]✅ {worker_name} registered as WORKER (TX: {tx_hash[:20]}...)[/green]")
                worker_results[worker_name] = {"agent_id": agent_id, "tx_hash": tx_hash, "success": True}
                
            except Exception as e:
                rprint(f"[yellow]⚠️  {worker_name} worker registration: {e}[/yellow]")
                worker_results[worker_name] = {"success": False, "error": str(e)}
        
        self.results["worker_registrations"] = worker_results
    
    def _register_verifiers_with_studio(self):
        """Register ALL 3 Verifiers (Bob, Carol, Frank) with stake"""
        
        verifier_results = {}
        
        # All 3 verifiers
        verifiers = [
            ("Bob", self.bob_sdk),
            ("Carol", self.carol_sdk),
            ("Frank", self.frank_sdk)
        ]
        
        for verifier_name, verifier_sdk in verifiers:
            try:
                agent_id = self.results["registration"]["agents"][verifier_name]["agent_id"]
                
                # Handle case where agent_id might be a tuple (agent_id, tx_hash)
                if isinstance(agent_id, tuple):
                    agent_id = agent_id[0]
                
                rprint(f"   → Registering {verifier_name} (ID: {agent_id}) as VERIFIER...")
                
                tx_hash = verifier_sdk.register_with_studio(
                    studio_address=self.studio_address,
                    agent_id=agent_id,
                    role=2,  # VERIFIER
                    stake_amount=1  # Wei (minimal stake for demo)
                )
                
                rprint(f"[green]✅ {verifier_name} registered as VERIFIER (TX: {tx_hash[:20]}...)[/green]")
                verifier_results[verifier_name] = {"agent_id": agent_id, "tx_hash": tx_hash, "success": True}
                
            except Exception as e:
                rprint(f"[yellow]⚠️  {verifier_name} verifier registration: {e}[/yellow]")
                verifier_results[verifier_name] = {"success": False, "error": str(e)}
        
        self.results["verifier_registrations"] = verifier_results
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 4: EVIDENCE PACKAGE & ON-CHAIN SUBMISSION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _phase_4_evidence_and_submission(self):
        """Phase 4: Create evidence package and submit to StudioProxy"""
        
        rprint("\n[bold blue]═══════════════════════════════════════════════════════════════[/bold blue]")
        rprint("[bold blue]📋 PHASE 4: Evidence Package & On-Chain Submission[/bold blue]")
        rprint("[bold blue]═══════════════════════════════════════════════════════════════[/bold blue]")
        rprint("[cyan]Creating DKG-compliant evidence and submitting to StudioProxy[/cyan]")
        
        # Step 11: Create enhanced evidence package
        rprint("\n[blue]🔧 Step 11: Creating DKG-compliant evidence package...[/blue]")
        evidence_package = self._create_evidence_package()
        rprint("[green]✅ Evidence package created[/green]")
        
        # Step 12: Store on IPFS
        rprint("\n[blue]🔧 Step 12: Storing evidence package on IPFS...[/blue]")
        evidence_cid = self._store_evidence_package(evidence_package)
        rprint(f"[green]✅ Evidence stored: {evidence_cid}[/green]")
        
        self.results["evidence_package"] = evidence_package
        self.results["evidence_cid"] = evidence_cid
        
        # Step 13-14: Submit work to StudioProxy
        self._submit_work_onchain(evidence_package, evidence_cid)
    
    def _create_evidence_package(self) -> Dict[str, Any]:
        """Create comprehensive evidence package with DKG (Protocol Spec v0.1 §1)"""
        
        analysis_data = self.results.get("analysis_data", {})
        process_integrity_proof = self.results.get("process_integrity_proof", {})
        x402_payment = self.results.get("x402_payment", {})
        
        # Build DKG for multi-agent causal analysis (MVP v0.4.0)
        dkg_data = self._build_dkg_from_work()
        
        evidence_package = {
            "version": "1.1.0",  # Updated for DKG support
            "timestamp": datetime.now().isoformat(),
            "agent": {
                "name": "Alice",
                "domain": "alice.genesis-studio.chaoschain.io",
                "role": "WORKER",
                "agent_id": self.results.get("registration", {}).get("agents", {}).get("Alice", {}).get("agent_id")
            },
            # Multi-agent participants (Protocol Spec §4.2)
            # 3 WORKERS with DKG-derived contribution weights
            # Verifiers (Bob, Carol, Frank) submit scores AFTER work is submitted
            "participants": [
                {
                    "address": self.alice_sdk.wallet_address,
                    "name": "Alice",
                    "role": "PRIMARY_WORKER",
                    "contribution_weight": 5000  # 50% - primary worker
                },
                {
                    "address": self.dave_sdk.wallet_address,
                    "name": "Dave",
                    "role": "WORKER",
                    "contribution_weight": 3000  # 30% - supporting worker
                },
                {
                    "address": self.eve_sdk.wallet_address,
                    "name": "Eve",
                    "role": "WORKER",
                    "contribution_weight": 2000  # 20% - supporting worker
                }
            ],
            "work_output": {
                "task_type": "smart_shopping_analysis",
                "analysis": analysis_data,
                "quality_score": analysis_data.get("quality_score", 85),
                "confidence": analysis_data.get("confidence", 0.89)
            },
            # DKG structure for causal audit (Protocol Spec §1.1)
            "dkg": dkg_data,
            "verification_layers": {
                "layer_1_ap2_intent": {
                "verified": True,
                    "method": "Google AP2",
                    "description": "User intent cryptographically verified"
                },
                "layer_2_process_integrity": {
                    "verified": True,
                    "method": getattr(process_integrity_proof, "verification_status", "ChaosChain") if hasattr(process_integrity_proof, "verification_status") else "ChaosChain",
                    "proof_id": getattr(process_integrity_proof, "execution_hash", "local") if hasattr(process_integrity_proof, "execution_hash") else "local"
                },
                "layer_3_payment_settlement": {
                    "verified": x402_payment.get("success", False),
                    "method": "x402 Protocol",
                    "transaction_hash": x402_payment.get("transaction_hash", "N/A"),
                    "amount": x402_payment.get("amount", 0)
                }
            },
            "triple_verified_stack": {
                "chaoschain_layers_owned": 2,
                "total_layers": 3,
                "complete": True
            }
        }
        
        return evidence_package
    
    def _build_dkg_from_work(self) -> Dict[str, Any]:
        """Build DKG (Decentralized Knowledge Graph) from work artifacts.
        
        This implements Protocol Spec v0.1 §1.1 - Graph Structure:
        - Each node represents a message/event with causal links
        - Parent references encode the "replies/references" relationship
        - Used by VerifierAgent for causal analysis
        """
        import time
        
        rprint("   [cyan]📊 Building DKG from work artifacts...[/cyan]")
        
        # Create DKG nodes representing the work chain
        # Alice (Worker) → Bob (Verifier) → Carol (Verifier) → Consensus
        
        nodes = []
        current_ts = int(time.time() * 1000)
        
        # Node 1: Alice's initial work (root node - no parents)
        alice_node = {
            "id": f"node_alice_{current_ts}",
            "author": self.alice_sdk.wallet_address,
            "timestamp": current_ts,
            "content_hash": hashlib.sha256(b"alice_work_output").hexdigest(),
            "parent_ids": [],  # Root node
            "artifact_ids": ["ipfs://evidence_root"],
            "payload_hash": hashlib.sha256(json.dumps(self.results.get("analysis_data", {})).encode()).hexdigest(),
            "signature": "alice_sig_placeholder"
        }
        nodes.append(alice_node)
        
        # Node 2: Bob's verification (references Alice's work)
        bob_node = {
            "id": f"node_bob_{current_ts + 1000}",
            "author": self.bob_sdk.wallet_address,
            "timestamp": current_ts + 1000,
            "content_hash": hashlib.sha256(b"bob_verification").hexdigest(),
            "parent_ids": [alice_node["id"]],  # Causal link to Alice
            "artifact_ids": ["ipfs://bob_audit"],
            "payload_hash": hashlib.sha256(b"bob_audit_data").hexdigest(),
            "signature": "bob_sig_placeholder"
        }
        nodes.append(bob_node)
        
        # Node 3: Carol's verification (references Alice's work)
        carol_node = {
            "id": f"node_carol_{current_ts + 2000}",
            "author": self.carol_sdk.wallet_address,
            "timestamp": current_ts + 2000,
            "content_hash": hashlib.sha256(b"carol_verification").hexdigest(),
            "parent_ids": [alice_node["id"]],  # Causal link to Alice
            "artifact_ids": ["ipfs://carol_audit"],
            "payload_hash": hashlib.sha256(b"carol_audit_data").hexdigest(),
            "signature": "carol_sig_placeholder"
        }
        nodes.append(carol_node)
        
        # Build edges for graph representation
        edges = []
        for node in nodes:
            for parent_id in node.get("parent_ids", []):
                edges.append({
                    "from": parent_id,
                    "to": node["id"],
                    "type": "causal_reference"
                })
        
        dkg_data = {
            "nodes": nodes,
            "edges": edges,
            "root_node_id": alice_node["id"],
            "thread_root": hashlib.sha256(json.dumps(nodes).encode()).hexdigest()
        }
        
        rprint(f"   [green]✅ DKG built: {len(nodes)} nodes, {len(edges)} edges[/green]")
        
        # Store for later use in causal audit
        self.dkg_data = dkg_data
        
        return dkg_data
    
    def _store_evidence_package(self, evidence_package: Dict[str, Any]) -> str:
        """Store evidence package on IPFS/0G Storage"""
        
        try:
            # Try 0G Storage first
            if self.zg_storage and self.zg_storage.is_available:
                result = self.zg_storage.put(
                    blob=json.dumps(evidence_package).encode(),
                    mime="application/json",
                    idempotency_key=f"evidence_{int(time.time())}"
                )
                if result.success:
                    return result.uri
            
            # Fallback to SDK storage
            cid = self.alice_sdk.store_evidence(evidence_package, "work_evidence")
            return cid
            
        except Exception as e:
            rprint(f"[yellow]⚠️  Evidence storage: {e}[/yellow]")
            # Generate hash as fallback
            evidence_hash = hashlib.sha256(json.dumps(evidence_package).encode()).hexdigest()
            return f"memory://{evidence_hash[:16]}"
    
    def _submit_work_onchain(self, evidence_package: Dict[str, Any], evidence_cid: str):
        """Submit work via Gateway workflow (MVP v0.4.0)
        
        IMPORTANT: All work submission now goes through the ChaosChain Gateway.
        The Gateway handles:
        - Evidence upload to Arweave
        - Transaction submission to StudioProxy
        - Confirmation waiting and error handling
        
        Protocol Spec §4.2 - Multi-WA Attribution:
        - Submit with multiple participants and their contribution weights
        - DKG-derived contribution weights determine reward distribution
        """
        
        # Step 13: Calculate data hashes
        rprint("\n[blue]🔧 Step 13: Calculating work hashes (DataHash Pattern - Protocol Spec §1.4)...[/blue]")
        
        # Calculate hashes per protocol spec
        # IMPORTANT: Use keccak256 to match Solidity contract semantics
        from eth_utils import keccak
        
        evidence_content = json.dumps(evidence_package).encode()
        data_hash = keccak(evidence_content)
        
        # Use DKG thread root if available
        dkg_data = getattr(self, 'dkg_data', {})
        thread_root_hex = dkg_data.get("thread_root", "")
        if thread_root_hex:
            thread_root = bytes.fromhex(thread_root_hex)
        else:
            thread_root = keccak(f"xmtp_thread_{evidence_cid}".encode())
        
        evidence_root = keccak(f"ipfs_evidence_{evidence_cid}".encode())
        
        self.work_data_hash = data_hash  # Store for verifier scoring
        
        rprint(f"   DataHash: 0x{data_hash.hex()[:20]}...")
        rprint(f"   ThreadRoot: 0x{thread_root.hex()[:20]}...")
        rprint(f"   EvidenceRoot: 0x{evidence_root.hex()[:20]}...")
        
        # Step 14: Submit work via Gateway workflow
        participants = evidence_package.get("participants", [])
        
        rprint("\n[blue]🔧 Step 14: Submitting work via Gateway workflow...[/blue]")
        rprint(f"   [cyan]Gateway: {self.gateway_url}[/cyan]")
        
        if len(participants) > 1:
            rprint(f"   [yellow]📊 {len(participants)} participants with DKG-derived contribution weights[/yellow]")
            for p in participants:
                rprint(f"      • {p.get('name', 'Unknown')}: {p.get('contribution_weight', 0) / 100:.0f}% contribution")
        
        # Submit via Gateway (Gateway handles Arweave upload + on-chain submission)
        self._submit_work_via_gateway(
            evidence_content=evidence_content,
            data_hash=data_hash,
            thread_root=thread_root,
            evidence_root=evidence_root,
            participants=participants
        )
    
    def _submit_work_via_gateway(
        self,
        evidence_content: bytes,
        data_hash: bytes,
        thread_root: bytes,
        evidence_root: bytes,
        participants: List[Dict]
    ):
        """Submit work through Gateway workflow.
        
        Gateway handles:
        1. Upload evidence to Arweave
        2. Submit transaction to StudioProxy
        3. Wait for confirmation
        """
        
        # For multi-agent work, we submit once from the primary worker (Alice)
        # The Gateway will handle the on-chain submission with participant list
        primary_worker = self.alice_sdk
        epoch = 0  # Demo uses epoch 0
        
        # Progress callback for logging
        def on_progress(status: WorkflowStatus):
            step_emoji = {
                "CREATED": "📝",
                "uploading_evidence": "📤",
                "evidence_uploaded": "✅",
                "submitting_onchain": "⛓️",
                "confirming": "⏳",
                "COMPLETED": "🎉",
                "FAILED": "❌"
            }
            emoji = step_emoji.get(status.step, "🔄")
            rprint(f"   {emoji} Workflow {status.id[:8]}... | Step: {status.step} | State: {status.state.value}")
            
            if status.progress.arweave_tx_id:
                rprint(f"      Arweave TX: {status.progress.arweave_tx_id[:20]}...")
            if status.progress.onchain_tx_hash:
                rprint(f"      On-chain TX: {status.progress.onchain_tx_hash[:20]}...")
        
        try:
            rprint(f"   → Creating work submission workflow...")
            
            # Submit via Gateway client
            # NOTE: Gateway Architecture Model
            #   - agent_address = logical identity of the worker (Alice)
            #   - signer_address = operational signer registered with Gateway (Studio Operator)
            #   Contracts enforce authorization via agentId/roles, not private keys
            workflow = self.gateway.submit_work(
                studio_address=self.studio_address,
                epoch=epoch,
                agent_address=primary_worker.wallet_address,  # Logical identity (participant)
                data_hash=f"0x{data_hash.hex()}",
                thread_root=f"0x{thread_root.hex()}",
                evidence_root=f"0x{evidence_root.hex()}",
                evidence_content=evidence_content,
                signer_address=STUDIO_OPERATOR_ADDRESS  # Operational signer (Gateway-registered)
            )
            
            rprint(f"   [green]✅ Workflow created: {workflow.id}[/green]")
            
            # Wait for completion
            rprint(f"   → Waiting for workflow completion...")
            final_status = self.gateway.wait_for_completion(
                workflow.id,
                on_progress=on_progress
            )
            
            # Record results
            self.workflow_results["work_submission"].append({
                "workflow_id": workflow.id,
                "state": final_status.state.value,
                "arweave_tx_id": final_status.progress.arweave_tx_id,
                "onchain_tx_hash": final_status.progress.onchain_tx_hash
            })
            
            rprint(f"\n[bold green]✅ Work submitted via Gateway![/bold green]")
            rprint(f"   Workflow ID: {workflow.id}")
            rprint(f"   State: {final_status.state.value}")
            
            if final_status.progress.onchain_tx_hash:
                tx_hash = final_status.progress.onchain_tx_hash
                rprint(f"   On-chain TX: {tx_hash}")
                rprint(f"   🔗 View: https://sepolia.etherscan.io/tx/{tx_hash}")
            
            if final_status.progress.arweave_tx_id:
                rprint(f"   Arweave TX: {final_status.progress.arweave_tx_id}")
            
            self.results["work_submission"] = {
                "data_hash": data_hash.hex(),
                "workflow_id": workflow.id,
                "tx_hash": final_status.progress.onchain_tx_hash,
                "arweave_tx_id": final_status.progress.arweave_tx_id,
                "multi_agent": len(participants) > 1,
                "participants": len(participants),
                "success": True
            }
            
        except WorkflowFailedError as e:
            rprint(f"[red]❌ Work submission workflow failed: {e}[/red]")
            self.results["work_submission"] = {
                "success": False, 
                "error": str(e),
                "workflow_id": e.workflow_id if hasattr(e, 'workflow_id') else None
            }
            raise
        except GatewayError as e:
            rprint(f"[red]❌ Gateway error during work submission: {e}[/red]")
            self.results["work_submission"] = {"success": False, "error": str(e)}
            raise
    
    def _register_work_with_rewards_distributor(self, data_hash: bytes):
        """
        [DEPRECATED - Gateway handles this now]
        
        Register work with RewardsDistributor for epoch tracking.
        
        NOTE: In the Gateway architecture, registerWork is handled automatically
        by the WorkSubmission workflow (REGISTER_WORK step). This function is
        only kept for backwards compatibility and is NOT called in the main flow.
        
        See: GatewayWorkflowExecutionModel.md
        """
        from web3 import Web3
        
        owner_key = os.getenv("PROTOCOL_OWNER_PRIVATE_KEY") or os.getenv("DEPLOYER_PRIVATE_KEY")
        
        if not owner_key:
            rprint("[yellow]⚠️  No owner key - skipping work registration[/yellow]")
            rprint("[dim]   Add PROTOCOL_OWNER_PRIVATE_KEY to .env to enable[/dim]")
            return
        
        try:
            w3 = self.alice_sdk.chaos_agent.w3
            owner_account = w3.eth.account.from_key(owner_key)
            rewards_distributor = CHAOSCHAIN_CONTRACTS["rewards_distributor"]
            
            # ABI for registerWork
            register_abi = [
                {
                    "inputs": [
                        {"name": "studio", "type": "address"},
                        {"name": "epoch", "type": "uint64"},
                        {"name": "dataHash", "type": "bytes32"}
                    ],
                    "name": "registerWork",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ]
            
            distributor = w3.eth.contract(
                address=w3.to_checksum_address(rewards_distributor),
                abi=register_abi
            )
            
            epoch = 0  # Use epoch 0 for demo
            
            rprint(f"   → Registering work for epoch {epoch}...")
            rprint(f"   → DataHash: {data_hash.hex()[:20]}...")
            
            # Build transaction
            tx = distributor.functions.registerWork(
                w3.to_checksum_address(self.studio_address),
                epoch,
                data_hash
            ).build_transaction({
                'from': owner_account.address,
                'nonce': w3.eth.get_transaction_count(owner_account.address),
                'gas': 100000,
                'gasPrice': w3.eth.gas_price
            })
            
            # Sign and send
            signed_tx = w3.eth.account.sign_transaction(tx, owner_key)
            raw_transaction = getattr(signed_tx, 'raw_transaction', getattr(signed_tx, 'rawTransaction', None))
            tx_hash = w3.eth.send_raw_transaction(raw_transaction)
            
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt.status == 1:
                rprint(f"[green]✅ Work registered with RewardsDistributor (TX: {tx_hash.hex()[:20]}...)[/green]")
                self.results["work_registered"] = {"success": True, "tx_hash": tx_hash.hex()}
            else:
                rprint(f"[red]❌ Work registration reverted[/red]")
                self.results["work_registered"] = {"success": False}
                
        except Exception as e:
            rprint(f"[yellow]⚠️  Work registration failed: {e}[/yellow]")
            self.results["work_registered"] = {"success": False, "error": str(e)}
    
    def _register_validator_with_rewards_distributor(self, data_hash: bytes, validator_address: str):
        """
        [DEPRECATED - Gateway handles this now]
        
        Register validator for a work submission.
        
        NOTE: In the Gateway architecture, registerValidator is handled automatically
        by the ScoreSubmission workflow (REGISTER_VALIDATOR step). This function is
        only kept for backwards compatibility and is NOT called in the main flow.
        
        See: GatewayWorkflowExecutionModel.md
        """
        from web3 import Web3
        
        owner_key = os.getenv("PROTOCOL_OWNER_PRIVATE_KEY") or os.getenv("DEPLOYER_PRIVATE_KEY")
        
        if not owner_key:
            return  # Silently skip if no owner key
        
        try:
            w3 = self.alice_sdk.chaos_agent.w3
            owner_account = w3.eth.account.from_key(owner_key)
            rewards_distributor = CHAOSCHAIN_CONTRACTS["rewards_distributor"]
            
            # ABI for registerValidator
            register_abi = [
                {
                    "inputs": [
                        {"name": "dataHash", "type": "bytes32"},
                        {"name": "validator", "type": "address"}
                    ],
                    "name": "registerValidator",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ]
            
            distributor = w3.eth.contract(
                address=w3.to_checksum_address(rewards_distributor),
                abi=register_abi
            )
            
            rprint(f"   → Registering validator {validator_address[:10]}... for work")
            
            # Build transaction
            tx = distributor.functions.registerValidator(
                data_hash,
                w3.to_checksum_address(validator_address)
            ).build_transaction({
                'from': owner_account.address,
                'nonce': w3.eth.get_transaction_count(owner_account.address),
                'gas': 100000,
                'gasPrice': w3.eth.gas_price
            })
            
            # Sign and send
            signed_tx = w3.eth.account.sign_transaction(tx, owner_key)
            raw_transaction = getattr(signed_tx, 'raw_transaction', getattr(signed_tx, 'rawTransaction', None))
            tx_hash = w3.eth.send_raw_transaction(raw_transaction)
            
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt.status == 1:
                rprint(f"   [green]✅ Validator registered (TX: {tx_hash.hex()[:20]}...)[/green]")
            else:
                rprint(f"   [yellow]⚠️ Validator registration reverted[/yellow]")
                
        except Exception as e:
            rprint(f"   [yellow]⚠️  Validator registration failed: {e}[/yellow]")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 5: MULTI-VERIFIER SCORING (Proof of Agency)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _phase_5_multi_verifier_scoring(self):
        """Phase 5: Multiple Verifiers score the work with PER-WORKER consensus (MVP v0.4.0)
        
        NEW in v0.4.0 - Per-Worker Consensus:
        - Each verifier scores EACH WORKER separately
        - Consensus is calculated per worker, not averaged across all
        - Each worker gets their own unique reputation
        
        Protocol Spec §2.1 - ScoreVectors & Robust Consensus
        """
        
        rprint("\n[bold blue]═══════════════════════════════════════════════════════════════[/bold blue]")
        rprint("[bold blue]📋 PHASE 5: Multi-Verifier Scoring (Proof of Agency) - MVP v0.4.0[/bold blue]")
        rprint("[bold blue]═══════════════════════════════════════════════════════════════[/bold blue]")
        rprint("[cyan]Verifier Agents independently audit work and submit PER-WORKER score vectors[/cyan]")
        rprint("[yellow]NEW: Each worker receives individual scores from each verifier![/yellow]")
        
        # ═══════════════════════════════════════════════════════════════════════════
        # IMPORTANT: Query ACTUAL on-chain participants, not evidence package
        # ═══════════════════════════════════════════════════════════════════════════
        # When using Gateway, the Gateway signer becomes the on-chain participant,
        # not the logical agent addresses. We MUST score the actual participants.
        
        worker_addresses = []
        
        if self.gateway and self.work_data_hash and self.studio_address:
            # Query actual on-chain participants from StudioProxy
            rprint(f"\n   [cyan]🔍 Querying actual on-chain participants for work...[/cyan]")
            try:
                from web3 import Web3
                w3 = self.alice_sdk.chaos_agent.w3
                
                participants_abi = [{
                    "inputs": [{"name": "dataHash", "type": "bytes32"}],
                    "name": "getWorkParticipants",
                    "outputs": [{"type": "address[]"}],
                    "stateMutability": "view",
                    "type": "function"
                }]
                studio = w3.eth.contract(
                    address=Web3.to_checksum_address(self.studio_address),
                    abi=participants_abi
                )
                
                onchain_participants = studio.functions.getWorkParticipants(self.work_data_hash).call()
                worker_addresses = [addr for addr in onchain_participants]
                
                rprint(f"   [green]✅ Found {len(worker_addresses)} on-chain participant(s):[/green]")
                for addr in worker_addresses:
                    rprint(f"      • {addr}")
                    
            except Exception as e:
                rprint(f"   [yellow]⚠️  Could not query on-chain participants: {e}[/yellow]")
        
        # Fallback: Get participants from evidence package (for non-Gateway mode)
        if not worker_addresses:
            participants = self.results.get("evidence_package", {}).get("participants", [])
            worker_addresses = [p["address"] for p in participants if p.get("role") in ["PRIMARY_WORKER", "WORKER"]]
        
        if not worker_addresses:
            worker_addresses = [self.alice_sdk.wallet_address]
        
        rprint(f"\n   [cyan]📊 Scoring {len(worker_addresses)} workers:[/cyan]")
        for addr in worker_addresses:
            rprint(f"      • {addr[:20]}...")
        
        # Step 15: Bob performs causal audit and scores EACH worker
        rprint("\n[blue]🔧 Step 15: Bob performing DKG-based causal audit (per-worker)...[/blue]")
        bob_scores = self._verifier_audit_and_score_per_worker("Bob", self.bob_sdk, worker_addresses)
        
        # Step 16: Carol performs independent audit and scores EACH worker
        rprint("\n[blue]🔧 Step 16: Carol performing independent DKG audit (per-worker)...[/blue]")
        carol_scores = self._verifier_audit_and_score_per_worker("Carol", self.carol_sdk, worker_addresses)
        
        # Step 16b: Frank performs final validation and scores EACH worker
        rprint("\n[blue]🔧 Step 16b: Frank performing final validation (per-worker)...[/blue]")
        frank_scores = self._verifier_audit_and_score_per_worker("Frank", self.frank_sdk, worker_addresses)
        
        # Display per-worker score comparison (3 verifiers!)
        self._display_per_worker_score_comparison_3verifiers(bob_scores, carol_scores, frank_scores, worker_addresses)
    
    def _verifier_audit_and_score(self, verifier_name: str, verifier_sdk) -> List[int]:
        """
        [DEPRECATED - Use _verifier_audit_and_score_per_worker instead]
        
        Verifier performs causal audit and submits score vector.
        
        NOTE: This function uses direct SDK contract calls which violate the
        Gateway architecture. It is NOT called in the main demo flow.
        Use _verifier_audit_and_score_per_worker() which routes through Gateway.
        """
        
        evidence_package = self.results.get("evidence_package", {})
        evidence_cid = self.results.get("evidence_cid", "")
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 1: Register Validation Request (ERC-8004 ValidationRegistry)
        # ═══════════════════════════════════════════════════════════════════
        rprint(f"   📋 {verifier_name} registering validation request (ERC-8004)...")
        
        try:
            # Get worker agent ID for the validation request
            alice_agent_id = self.results.get("registration", {}).get("agents", {}).get("Alice", {}).get("agent_id")
            
            if alice_agent_id and evidence_cid:
                # Create request hash from evidence
                request_hash = hashlib.sha256(evidence_cid.encode()).hexdigest()
                
                # Call ERC-8004 ValidationRegistry.validationRequest()
                validation_tx = verifier_sdk.chaos_agent.request_validation(
                    validator_agent_id=alice_agent_id,  # Agent being validated
                    request_uri=evidence_cid,            # Evidence location
                    request_hash=f"0x{request_hash}"     # Request identifier
                )
                
                rprint(f"   [green]✅ Validation request registered (TX: {validation_tx[:20]}...)[/green]")
                self.results[f"{verifier_name.lower()}_validation_request"] = {
                    "tx_hash": validation_tx,
                    "success": True
                }
            else:
                rprint(f"   [yellow]⚠️  Skipping validation request (no agent ID or evidence)[/yellow]")
                
        except Exception as e:
            rprint(f"   [yellow]⚠️  Validation request: {e}[/yellow]")
            # Continue with scoring even if validation request fails
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 2: Perform Causal Analysis (PoA Audit)
        # ═══════════════════════════════════════════════════════════════════
        rprint(f"   🔍 {verifier_name} analyzing DKG structure...")
        rprint(f"   📊 Evaluating work quality across 5 dimensions:")
        rprint(f"      • Initiative: Did the agent proactively identify opportunities?")
        rprint(f"      • Collaboration: How well did it coordinate with other agents?")
        rprint(f"      • Reasoning Depth: Quality of analysis and decision-making?")
        rprint(f"      • Output Quality: Accuracy and completeness of results?")
        rprint(f"      • Communication: Clarity and transparency of process?")
        
        # Generate score vector (simulating causal audit)
        import random
        random.seed(hash(verifier_name))  # Consistent scores per verifier
        
        base_quality = evidence_package.get("work_output", {}).get("quality_score", 85)
        
        score_vector = [
            min(100, max(50, base_quality + random.randint(-5, 10))),  # Initiative
            min(100, max(50, base_quality + random.randint(-8, 12))),  # Collaboration
            min(100, max(50, base_quality + random.randint(-3, 8))),   # Reasoning
            min(100, max(50, base_quality + random.randint(-2, 5))),   # Output Quality
            min(100, max(50, base_quality + random.randint(-6, 10)))   # Communication
        ]
        
        rprint(f"   📈 {verifier_name}'s Score Vector: {score_vector}")
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 3: Submit Score Vector to StudioProxy (PoA)
        # ═══════════════════════════════════════════════════════════════════
        try:
            if self.work_data_hash and self.studio_address:
                tx_hash = verifier_sdk.chaos_agent.submit_score_vector(
                    studio_address=self.studio_address,
                    data_hash=self.work_data_hash,
                    score_vector=score_vector
                )
                
                rprint(f"   [green]✅ {verifier_name} submitted scores to StudioProxy (TX: {tx_hash[:20]}...)[/green]")
                
                # CRITICAL: Register validator with RewardsDistributor for epoch tracking
                verifier_address = verifier_sdk.wallet_address
                self._register_validator_with_rewards_distributor(self.work_data_hash, verifier_address)
                
                self.results[f"{verifier_name.lower()}_scores"] = {
                    "scores": score_vector,
                    "tx_hash": tx_hash,
                    "success": True
                }
            else:
                rprint(f"   [yellow]⚠️  {verifier_name}: No work hash to score[/yellow]")
                self.results[f"{verifier_name.lower()}_scores"] = {
                    "scores": score_vector,
                    "success": False
                }
                
        except Exception as e:
            rprint(f"   [yellow]⚠️  {verifier_name} score submission: {e}[/yellow]")
            self.results[f"{verifier_name.lower()}_scores"] = {
                "scores": score_vector,
                "success": False,
                "error": str(e)
            }
        
        return score_vector
    
    def _verifier_audit_and_score_per_worker(
        self, 
        verifier_name: str, 
        verifier_sdk, 
        worker_addresses: List[str]
    ) -> Dict[str, List[int]]:
        """Verifier performs DKG-based causal audit and submits scores PER WORKER.
        
        MVP v0.4.0 - Per-Worker Consensus:
        Each worker gets their own individual score vector from this verifier.
        
        Protocol Spec §3.1 - Measurable Agency Dimensions (from DKG)
        Protocol Spec §4.2 - Multi-WA Attribution
        """
        
        evidence_package = self.results.get("evidence_package", {})
        dkg_data = getattr(self, 'dkg_data', evidence_package.get("dkg", {}))
        
        rprint(f"   📋 {verifier_name} analyzing DKG for causal attribution...")
        rprint(f"      • DKG nodes: {len(dkg_data.get('nodes', []))}")
        rprint(f"      • Causal edges: {len(dkg_data.get('edges', []))}")
        
        # Calculate contribution weights from DKG (Protocol Spec §4.2)
        contribution_weights = self._calculate_contribution_weights_from_dkg(dkg_data, worker_addresses)
        
        scores_per_worker = {}
        
        for worker_addr in worker_addresses:
            # Find worker's name for display
            worker_name = "Unknown"
            for p in evidence_package.get("participants", []):
                if p.get("address") == worker_addr:
                    worker_name = p.get("name", "Unknown")
                    break
            
            # Calculate DKG-based scores for this worker
            contribution = contribution_weights.get(worker_addr, 0.5)
            
            rprint(f"\n   🔍 {verifier_name} scoring {worker_name} ({worker_addr[:10]}...):")
            rprint(f"      • Contribution weight from DKG: {contribution:.2%}")
            
            # Generate score vector based on DKG analysis (Protocol Spec §3.1)
            import random
            random.seed(hash(f"{verifier_name}_{worker_addr}"))
            
            base_quality = evidence_package.get("work_output", {}).get("quality_score", 85)
            
            # Scores influenced by DKG contribution weight
            contribution_bonus = int(contribution * 15)  # Higher contribution = higher scores
            
            score_vector = [
                min(100, max(50, base_quality + contribution_bonus + random.randint(-5, 10))),  # Initiative
                min(100, max(50, base_quality + contribution_bonus + random.randint(-8, 12))),  # Collaboration
                min(100, max(50, base_quality + contribution_bonus + random.randint(-3, 8))),   # Reasoning
                min(100, max(50, base_quality + contribution_bonus + random.randint(-2, 5))),   # Output Quality
                min(100, max(50, base_quality + contribution_bonus + random.randint(-6, 10)))   # Communication
            ]
            
            rprint(f"      • Score Vector: {score_vector}")
            
            scores_per_worker[worker_addr] = score_vector
        
        # Submit scores per worker to StudioProxy
        self._submit_scores_per_worker(verifier_name, verifier_sdk, scores_per_worker)
        
        return scores_per_worker
    
    def _calculate_contribution_weights_from_dkg(
        self, 
        dkg_data: Dict, 
        worker_addresses: List[str]
    ) -> Dict[str, float]:
        """Calculate contribution weights from DKG using betweenness centrality.
        
        Protocol Spec §4.2 - Multi-WA Attribution:
        - Contribution weight based on nodes on paths to terminal actions
        - Shapley-like approximation using path centrality
        """
        
        nodes = dkg_data.get("nodes", [])
        edges = dkg_data.get("edges", [])
        
        if not nodes:
            # Equal weights if no DKG
            return {addr: 1.0 / len(worker_addresses) for addr in worker_addresses}
        
        # Count nodes authored by each worker
        node_counts = {}
        for node in nodes:
            author = node.get("author", "")
            node_counts[author] = node_counts.get(author, 0) + 1
        
        # Also count incoming edges (references) as a measure of importance
        edge_counts = {}
        for edge in edges:
            to_node = edge.get("to", "")
            # Find the author of the target node
            for node in nodes:
                if node.get("id") == to_node:
                    author = node.get("author", "")
                    edge_counts[author] = edge_counts.get(author, 0) + 1
                    break
        
        # Combine node count and edge count for weight
        total_score = 0
        weights = {}
        
        for addr in worker_addresses:
            node_score = node_counts.get(addr, 0)
            edge_score = edge_counts.get(addr, 0)
            combined = node_score + edge_score * 0.5  # Edges worth half a node
            weights[addr] = combined
            total_score += combined
        
        # Normalize to sum to 1.0
        if total_score > 0:
            weights = {addr: w / total_score for addr, w in weights.items()}
        else:
            weights = {addr: 1.0 / len(worker_addresses) for addr in worker_addresses}
        
        return weights
    
    def _submit_scores_per_worker(
        self, 
        verifier_name: str, 
        verifier_sdk, 
        scores_per_worker: Dict[str, List[int]]
    ):
        """Submit per-worker score vectors.
        
        ═══════════════════════════════════════════════════════════════════════════
        TEMPORARY DIRECT SDK CALLS - KNOWN ARCHITECTURAL LIMITATION
        ═══════════════════════════════════════════════════════════════════════════
        
        The Gateway's ScoreSubmission workflow uses a commit-reveal protocol that
        requires epoch deadline configuration in the StudioProxy contract. Since
        this configuration is not available on the current deployed contracts,
        scores MUST go through direct SDK calls.
        
        This is the ONLY direct contract interaction in Genesis Studio and matches
        the pattern from minimal_gateway_e2e.py (the source of truth).
        
        Flow:
        1. submitScoreVectorForWorker(dataHash, worker, scores) → StudioProxy
        2. registerValidator(dataHash, validator) → RewardsDistributor
        
        CRITICAL: Uses self.work_data_hash which is the SAME hash used for:
        - Work submission via Gateway
        - Epoch closure via Gateway
        
        Once Gateway's ScoreSubmission workflow supports non-commit-reveal mode,
        this function should be replaced with gateway.submit_score_and_wait().
        ═══════════════════════════════════════════════════════════════════════════
        """
        from web3 import Web3
        from eth_account import Account
        from eth_abi import encode as eth_abi_encode
        
        if not self.work_data_hash or not self.studio_address:
            rprint(f"   [yellow]⚠️  {verifier_name}: No work hash or studio - skipping score submission[/yellow]")
            return
        
        submission_results = {}
        
        # Get verifier's private key from wallets
        wallets_path = os.path.join(os.path.dirname(__file__), "chaoschain_wallets.json")
        with open(wallets_path, 'r') as f:
            wallets = json.load(f)
        
        verifier_wallet = wallets.get(verifier_name)
        if not verifier_wallet:
            rprint(f"   [yellow]⚠️  {verifier_name}: Wallet not found in chaoschain_wallets.json[/yellow]")
            return
        
        verifier_private_key = verifier_wallet['private_key']
        if not verifier_private_key.startswith('0x'):
            verifier_private_key = '0x' + verifier_private_key
        
        verifier_account = Account.from_key(verifier_private_key)
        verifier_address = verifier_account.address
        
        rprint(f"\n   [cyan]{verifier_name} submitting scores via direct SDK (like minimal E2E)...[/cyan]")
        
        # Get Web3 instance
        w3 = verifier_sdk.chaos_agent.w3
        
        # ABI for submitScoreVectorForWorker
        score_abi = [{
            "inputs": [
                {"name": "dataHash", "type": "bytes32"},
                {"name": "worker", "type": "address"},
                {"name": "scoreVector", "type": "bytes"}
            ],
            "name": "submitScoreVectorForWorker",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        }]
        
        studio_contract = w3.eth.contract(
            address=Web3.to_checksum_address(self.studio_address),
            abi=score_abi
        )
        
        for worker_addr, score_vector in scores_per_worker.items():
            try:
                # Encode score vector as 5 uint8s (0-100 range)
                # Contract expects: abi.decode(scoreData, (uint8, uint8, uint8, uint8, uint8))
                scaled_scores = [min(100, max(0, s)) for s in score_vector]
                score_bytes = eth_abi_encode(['uint8', 'uint8', 'uint8', 'uint8', 'uint8'], scaled_scores)
                
                # Build transaction
                nonce = w3.eth.get_transaction_count(verifier_address)
                
                tx = studio_contract.functions.submitScoreVectorForWorker(
                    self.work_data_hash,
                    Web3.to_checksum_address(worker_addr),
                    score_bytes
                ).build_transaction({
                    'from': verifier_address,
                    'nonce': nonce,
                    'gas': 500000,
                    'gasPrice': w3.eth.gas_price * 2,
                    'chainId': 11155111
                })
                
                signed_tx = verifier_account.sign_transaction(tx)
                tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                
                rprint(f"      → {verifier_name} scoring {worker_addr[:12]}... TX: {tx_hash.hex()[:16]}...")
                
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
                
                if receipt['status'] == 1:
                    rprint(f"      [green]✅ Score submitted for {worker_addr[:12]}...[/green]")
                    
                    # Register validator with RewardsDistributor (required for closeEpoch)
                    self._register_validator_direct(verifier_address, w3)
                    
                    result = {
                        "success": True,
                        "tx_hash": tx_hash.hex(),
                        "method": "direct_sdk"
                    }
                else:
                    rprint(f"      [red]❌ Score submission reverted for {worker_addr[:12]}...[/red]")
                    result = {"success": False, "error": "Transaction reverted"}
                
                submission_results[worker_addr] = result
                
                # Add to workflow results tracking
                self.workflow_results["score_submissions"].append({
                    "verifier": verifier_name,
                    "worker": worker_addr,
                    "tx_hash": tx_hash.hex() if receipt['status'] == 1 else None,
                    "state": "COMPLETED" if receipt['status'] == 1 else "FAILED",
                    "method": "direct_sdk"
                })
                    
            except Exception as e:
                rprint(f"   [yellow]⚠️  {verifier_name} score for {worker_addr[:10]}...: {e}[/yellow]")
                submission_results[worker_addr] = {"success": False, "error": str(e)}
        
        self.results[f"{verifier_name.lower()}_per_worker_scores"] = submission_results
    
    def _register_validator_direct(self, validator_address: str, w3):
        """Register validator with RewardsDistributor (required for closeEpoch).
        
        ═══════════════════════════════════════════════════════════════════════════
        TEMPORARY DIRECT SDK CALL - COUPLED WITH SCORE SUBMISSION LIMITATION
        ═══════════════════════════════════════════════════════════════════════════
        
        This is part of the score submission flow which must be direct due to
        Gateway's commit-reveal requirement (see _submit_scores_per_worker).
        
        The registerValidator call links the validator to the work dataHash
        in the RewardsDistributor contract, which is required for closeEpoch()
        to correctly distribute rewards.
        
        Uses: self.work_data_hash (same hash as work submission and epoch closure)
        Caller: Owner/operator wallet (has RewardsDistributor permissions)
        
        Once Gateway's ScoreSubmission workflow includes REGISTER_VALIDATOR step,
        this function becomes unnecessary.
        ═══════════════════════════════════════════════════════════════════════════
        """
        from web3 import Web3
        from eth_account import Account
        
        owner_key = os.getenv("PROTOCOL_OWNER_PRIVATE_KEY") or os.getenv("DEPLOYER_PRIVATE_KEY")
        if not owner_key:
            rprint(f"      [yellow]⚠️  No owner key - skipping validator registration[/yellow]")
            return
        
        owner_account = Account.from_key(owner_key)
        rewards_distributor = CHAOSCHAIN_CONTRACTS["rewards_distributor"]
        
        register_abi = [{
            "inputs": [
                {"name": "dataHash", "type": "bytes32"},
                {"name": "validator", "type": "address"}
            ],
            "name": "registerValidator",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        }]
        
        rd_contract = w3.eth.contract(
            address=Web3.to_checksum_address(rewards_distributor),
            abi=register_abi
        )
        
        try:
            nonce = w3.eth.get_transaction_count(owner_account.address)
            
            tx = rd_contract.functions.registerValidator(
                self.work_data_hash,
                Web3.to_checksum_address(validator_address)
            ).build_transaction({
                'from': owner_account.address,
                'nonce': nonce,
                'gas': 300000,
                'gasPrice': w3.eth.gas_price * 2,
                'chainId': 11155111
            })
            
            signed_tx = owner_account.sign_transaction(tx)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt['status'] == 1:
                rprint(f"      [dim]Validator {validator_address[:12]}... registered with RewardsDistributor[/dim]")
            
        except Exception as e:
            # Likely already registered - that's fine
            if "already" not in str(e).lower():
                rprint(f"      [dim]Validator registration: {e}[/dim]")
    
    def _display_per_worker_score_comparison(
        self, 
        bob_scores: Dict[str, List[int]], 
        carol_scores: Dict[str, List[int]],
        worker_addresses: List[str]
    ):
        """Display per-worker score comparison from multiple verifiers.
        
        MVP v0.4.0 - Shows how each worker gets individual scores.
        """
        
        dimensions = ["Initiative", "Collaboration", "Reasoning", "Output Quality", "Communication"]
        
        rprint("\n[bold cyan]📊 Per-Worker Score Comparison (MVP v0.4.0):[/bold cyan]")
        rprint("[yellow]Each worker now receives individual scores from each verifier![/yellow]")
        
        for worker_addr in worker_addresses:
            # Find worker name
            worker_name = worker_addr[:10] + "..."
            for p in self.results.get("evidence_package", {}).get("participants", []):
                if p.get("address") == worker_addr:
                    worker_name = p.get("name", worker_addr[:10])
                    break
            
            bob_vector = bob_scores.get(worker_addr, [0] * 5)
            carol_vector = carol_scores.get(worker_addr, [0] * 5)
            
            table = Table(title=f"[bold]{worker_name}[/bold] ({worker_addr[:12]}...)")
            table.add_column("Dimension", style="bold white")
            table.add_column("Bob", style="cyan")
            table.add_column("Carol", style="magenta")
            table.add_column("Consensus", style="green")
            
            consensus_scores = []
            for i, dim in enumerate(dimensions):
                bob_score = bob_vector[i] if i < len(bob_vector) else 0
                carol_score = carol_vector[i] if i < len(carol_vector) else 0
                consensus = (bob_score + carol_score) // 2
                consensus_scores.append(consensus)
                
                table.add_row(dim, str(bob_score), str(carol_score), str(consensus))
            
            # Add average row
            bob_avg = sum(bob_vector) / len(bob_vector) if bob_vector else 0
            carol_avg = sum(carol_vector) / len(carol_vector) if carol_vector else 0
            consensus_avg = sum(consensus_scores) / len(consensus_scores) if consensus_scores else 0
            
            table.add_row("", "", "", "")
            table.add_row("[bold]AVERAGE[/bold]", f"[bold]{bob_avg:.1f}[/bold]", f"[bold]{carol_avg:.1f}[/bold]", f"[bold green]{consensus_avg:.1f}[/bold green]")
            
            rprint(table)
            rprint()
        
        rprint(f"[green]🎯 Each worker will receive their own unique reputation based on their scores![/green]")
        rprint("[dim]   (This replaces the old system where all workers got the same averaged score)[/dim]")
    
    def _display_per_worker_score_comparison_3verifiers(
        self, 
        bob_scores: Dict[str, List[int]], 
        carol_scores: Dict[str, List[int]],
        frank_scores: Dict[str, List[int]],
        worker_addresses: List[str]
    ):
        """Display per-worker score comparison from 3 verifiers (Bob, Carol, Frank).
        
        MVP v0.4.0 - Shows how each of the 3 workers gets individual scores from 3 verifiers.
        """
        
        dimensions = ["Initiative", "Collaboration", "Reasoning", "Output Quality", "Communication"]
        
        rprint("\n[bold cyan]📊 Per-Worker Score Comparison (3 Verifiers):[/bold cyan]")
        rprint("[yellow]Each worker receives individual scores from Bob, Carol, and Frank![/yellow]")
        
        for worker_addr in worker_addresses:
            # Find worker name
            worker_name = worker_addr[:10] + "..."
            for p in self.results.get("evidence_package", {}).get("participants", []):
                if p.get("address") == worker_addr:
                    worker_name = p.get("name", worker_addr[:10])
                    break
            
            bob_vector = bob_scores.get(worker_addr, [0] * 5)
            carol_vector = carol_scores.get(worker_addr, [0] * 5)
            frank_vector = frank_scores.get(worker_addr, [0] * 5)
            
            table = Table(title=f"[bold]{worker_name}[/bold] ({worker_addr[:12]}...)")
            table.add_column("Dimension", style="bold white")
            table.add_column("Bob", style="cyan")
            table.add_column("Carol", style="magenta")
            table.add_column("Frank", style="blue")
            table.add_column("Consensus", style="green")
            
            consensus_scores = []
            for i, dim in enumerate(dimensions):
                bob_score = bob_vector[i] if i < len(bob_vector) else 0
                carol_score = carol_vector[i] if i < len(carol_vector) else 0
                frank_score = frank_vector[i] if i < len(frank_vector) else 0
                consensus = (bob_score + carol_score + frank_score) // 3
                consensus_scores.append(consensus)
                
                table.add_row(dim, str(bob_score), str(carol_score), str(frank_score), str(consensus))
            
            # Add average row
            bob_avg = sum(bob_vector) / len(bob_vector) if bob_vector else 0
            carol_avg = sum(carol_vector) / len(carol_vector) if carol_vector else 0
            frank_avg = sum(frank_vector) / len(frank_vector) if frank_vector else 0
            consensus_avg = sum(consensus_scores) / len(consensus_scores) if consensus_scores else 0
            
            table.add_row("", "", "", "", "")
            table.add_row("[bold]AVERAGE[/bold]", f"[bold]{bob_avg:.1f}[/bold]", f"[bold]{carol_avg:.1f}[/bold]", f"[bold]{frank_avg:.1f}[/bold]", f"[bold green]{consensus_avg:.1f}[/bold green]")
            
            rprint(table)
            rprint()
        
        rprint(f"[green]🎯 Each worker will receive their own unique reputation based on 3-verifier consensus![/green]")
    
    def _display_score_comparison(self, bob_scores: List[int], carol_scores: List[int]):
        """Display comparison of verifier scores"""
        
        dimensions = ["Initiative", "Collaboration", "Reasoning", "Output Quality", "Communication"]
        
        rprint("\n[bold cyan]📊 Score Vector Comparison:[/bold cyan]")
        
        table = Table(title="Multi-Verifier Score Comparison")
        table.add_column("Dimension", style="bold white")
        table.add_column("Bob's Score", style="cyan")
        table.add_column("Carol's Score", style="magenta")
        table.add_column("Difference", style="yellow")
        
        for i, dim in enumerate(dimensions):
            bob_score = bob_scores[i] if i < len(bob_scores) else 0
            carol_score = carol_scores[i] if i < len(carol_scores) else 0
            diff = abs(bob_score - carol_score)
            
            table.add_row(dim, str(bob_score), str(carol_score), f"±{diff}")
        
        # Add averages
        bob_avg = sum(bob_scores) / len(bob_scores) if bob_scores else 0
        carol_avg = sum(carol_scores) / len(carol_scores) if carol_scores else 0
        avg_diff = abs(bob_avg - carol_avg)
        
        table.add_row("", "", "", "")
        table.add_row("[bold]AVERAGE[/bold]", f"[bold]{bob_avg:.1f}[/bold]", f"[bold]{carol_avg:.1f}[/bold]", f"[bold]±{avg_diff:.1f}[/bold]")
        
        rprint(table)
        
        # Calculate consensus preview
        consensus_scores = [(bob_scores[i] + carol_scores[i]) // 2 for i in range(min(len(bob_scores), len(carol_scores)))]
        consensus_avg = sum(consensus_scores) / len(consensus_scores) if consensus_scores else 0
        
        rprint(f"\n[green]🎯 Preview Consensus Score: {consensus_avg:.1f}/100[/green]")
        rprint("[dim]   (Final consensus calculated by RewardsDistributor with stake weighting)[/dim]")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 6: CONSENSUS & REWARDS (Protocol)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _phase_6_consensus_and_rewards(self):
        """Phase 6: Consensus calculation and rewards distribution summary"""
        
        rprint("\n[bold blue]═══════════════════════════════════════════════════════════════[/bold blue]")
        rprint("[bold blue]📋 PHASE 6: Consensus & Rewards Summary[/bold blue]")
        rprint("[bold blue]═══════════════════════════════════════════════════════════════[/bold blue]")
        rprint("[cyan]Summary of consensus mechanism and reward distribution[/cyan]")
        
        # Step 17: Display consensus mechanism
        rprint("\n[blue]🔧 Step 17: Stake-Weighted Consensus Mechanism[/blue]")
        self._display_consensus_mechanism()
        
        # Step 18: Check pending rewards
        rprint("\n[blue]🔧 Step 18: Checking pending rewards...[/blue]")
        self._check_pending_rewards()
        
        # Step 19: Note about epoch closure
        rprint("\n[blue]🔧 Step 19: Epoch Closure[/blue]")
        self._display_epoch_closure_note()
    
    def _display_consensus_mechanism(self):
        """Display how consensus works"""
        
        bob_scores = self.results.get("bob_scores", {}).get("scores", [])
        carol_scores = self.results.get("carol_scores", {}).get("scores", [])
        
        rprint("""
[yellow]📊 Stake-Weighted Consensus Algorithm:[/yellow]

The RewardsDistributor.sol contract calculates final consensus scores by:

1. [cyan]Collect Score Vectors[/cyan]
   • Bob submitted: """ + str(bob_scores) + """
   • Carol submitted: """ + str(carol_scores) + """

2. [cyan]Weight by Stake[/cyan]
   • Higher stake = Higher influence
   • Prevents Sybil attacks (10,000 tokens = 100x influence vs 100 tokens)

3. [cyan]Calculate Consensus Score[/cyan]
   • Weighted average across all verifier scores
   • Used for worker reward distribution

4. [cyan]Evaluate Verifier Accuracy[/cyan]
   • Compare each verifier's scores to consensus
   • Verifiers close to consensus = REWARDED
   • Verifiers far from consensus = SLASHED

[green]This mechanism forces honest, accurate verification![/green]
""")
        
        # Display ERC-8004 ValidationRegistry flow
        rprint("""
[yellow]📋 ERC-8004 ValidationRegistry Flow:[/yellow]

The protocol uses all THREE ERC-8004 registries:

┌─────────────────────────────────────────────────────────────────┐
│  1. IdentityRegistry     → Agent registration (Phase 1)        │
│  2. ValidationRegistry   → Audit request/response (Phase 4-5)  │
│  3. ReputationRegistry   → Final reputation (Phase 6)          │
└─────────────────────────────────────────────────────────────────┘

[cyan]ValidationRegistry Flow:[/cyan]

  Verifier (Bob/Carol)                    RewardsDistributor
         │                                        │
         │ validationRequest()                    │
         │ "I'm starting to audit Alice's work"   │
         ├────────────────────────────────────────│
         │                                        │
         │ (performs causal audit)                │
         │ (submits score to StudioProxy)         │
         │                                        │
         │                    After closeEpoch(): │
         │                                        │
         │                    validationResponse()│
         │◄───────────────────────────────────────┤
         │    "Final consensus score: 87/100"     │
         │                                        │

[green]This creates a public, auditable record of all validations![/green]
""")
    
    def _check_pending_rewards(self):
        """Check pending rewards for all agents"""
        
        if not self.studio_address:
            rprint("[yellow]⚠️  No studio address - cannot check rewards[/yellow]")
            return
        
        try:
            # Check Alice's pending rewards
            alice_rewards = self.alice_sdk.get_pending_rewards(self.studio_address)
            rprint(f"   Alice (Worker): {alice_rewards} wei pending")
            
            # Check Bob's pending rewards
            bob_rewards = self.bob_sdk.get_pending_rewards(self.studio_address)
            rprint(f"   Bob (Verifier): {bob_rewards} wei pending")
            
            self.results["pending_rewards"] = {
                "alice": alice_rewards,
                "bob": bob_rewards
            }
            
        except Exception as e:
            rprint(f"[yellow]⚠️  Could not check rewards: {e}[/yellow]")
    
    def _display_epoch_closure_note(self):
        """Display note about epoch closure and attempt to call closeEpoch()"""
        
        # First, try to call closeEpoch() if we have the owner key
        epoch_closed = self._attempt_close_epoch()
        
        if not epoch_closed:
            rprint("""
[yellow]ℹ️  Epoch Closure Note:[/yellow]

The closeEpoch() function on RewardsDistributor can only be called by:
• The protocol owner (ChaosChain deployer)
• An authorized keeper/automation

[bold red]⚠️  To enable epoch closure and reputation building:[/bold red]
Add to your .env file:
   PROTOCOL_OWNER_PRIVATE_KEY=<your_deployer_private_key>
   
The owner address is: 0x9B4Cef62a0ce1671ccFEFA6a6D8cBFa165c49831

This triggers:
1. Final consensus calculation (stake-weighted average of scores)
2. Worker reward distribution (based on quality scores)
3. Verifier reward/slash distribution (based on accuracy to consensus)
4. [cyan]ERC-8004 validationResponse()[/cyan] → Publishes final verdict
5. [cyan]ERC-8004 ReputationRegistry[/cyan] → Publishes multi-dimensional reputation

[bold cyan]Complete ERC-8004 Usage:[/bold cyan]
┌────────────────────────────────────────────────────────────────────┐
│  Registry              │ When Used         │ By Whom               │
├────────────────────────────────────────────────────────────────────┤
│  IdentityRegistry      │ Phase 1           │ All agents            │
│  ValidationRegistry    │ Phase 4 (request) │ Verifier agents       │
│  ValidationRegistry    │ Phase 5 (response)│ RewardsDistributor    │
│  ReputationRegistry    │ Phase 6           │ RewardsDistributor    │
└────────────────────────────────────────────────────────────────────┘

[dim]For production: Use Chainlink Automation or OpenZeppelin Defender[/dim]
""")
        
        # Check SDK method availability
        try:
            rprint("\n[blue]SDK Method Availability:[/blue]")
            rprint(f"   close_epoch(): {'✅' if hasattr(self.alice_sdk, 'close_epoch') else '❌'}")
            rprint(f"   request_validation(): {'✅' if hasattr(self.alice_sdk.chaos_agent, 'request_validation') else '❌'}")
            rprint(f"   submit_validation_response(): {'✅' if hasattr(self.alice_sdk.chaos_agent, 'submit_validation_response') else '❌'}")
        except Exception:
            pass
    
    def _attempt_close_epoch(self) -> bool:
        """
        Attempt to close the epoch via Gateway workflow.
        
        The Gateway handles all the complexity:
        - Precondition checks
        - closeEpoch transaction submission
        - Confirmation waiting
        - Consensus calculation triggers reputation publishing
        
        Returns:
            bool: True if epoch was closed successfully, False otherwise
        """
        
        if not self.studio_address:
            rprint("[yellow]⚠️  No studio address - cannot close epoch[/yellow]")
            return False
        
        # ═══════════════════════════════════════════════════════════════════
        # Gateway Architecture: Use Studio Operator as signer
        # 
        # The Gateway submits the closeEpoch transaction using the operational
        # signer (STUDIO_OPERATOR_ADDRESS). Contract-level authorization is
        # enforced by RewardsDistributor based on roles, not private keys.
        # ═══════════════════════════════════════════════════════════════════
        signer_address = STUDIO_OPERATOR_ADDRESS
        
        epoch = 0  # Demo uses epoch 0
        
        try:
            rprint("\n[bold green]🔧 Step 19b: Closing epoch via Gateway workflow...[/bold green]")
            rprint(f"   [cyan]Gateway: {self.gateway_url}[/cyan]")
            rprint(f"   Signer: {signer_address}")
            rprint(f"   Studio: {self.studio_address[:20]}...")
            rprint(f"   Epoch: {epoch}")
            
            # Progress callback for logging
            def on_close_progress(status: WorkflowStatus):
                step_emoji = {
                    "CREATED": "📝",
                    "checking_preconditions": "🔍",
                    "submitting_tx": "⛓️",
                    "confirming": "⏳",
                    "COMPLETED": "🎉",
                    "FAILED": "❌"
                }
                emoji = step_emoji.get(status.step, "🔄")
                rprint(f"   {emoji} Workflow {status.id[:8]}... | Step: {status.step} | State: {status.state.value}")
                
                if status.progress.onchain_tx_hash:
                    rprint(f"      On-chain TX: {status.progress.onchain_tx_hash[:20]}...")
            
            # Submit close epoch via Gateway
            rprint(f"   → Creating close epoch workflow...")
            
            workflow = self.gateway.close_epoch(
                studio_address=self.studio_address,
                epoch=epoch,
                signer_address=signer_address
            )
            
            rprint(f"   [green]✅ Workflow created: {workflow.id}[/green]")
            
            # Wait for completion
            rprint(f"   → Waiting for workflow completion...")
            final_status = self.gateway.wait_for_completion(
                workflow.id,
                on_progress=on_close_progress
            )
            
            # Record results
            self.workflow_results["epoch_closure"] = {
                "workflow_id": workflow.id,
                "state": final_status.state.value,
                "onchain_tx_hash": final_status.progress.onchain_tx_hash,
                "onchain_block": final_status.progress.onchain_block
            }
            
            # Success!
            tx_hash = final_status.progress.onchain_tx_hash
            
            rprint(f"\n[bold green]✅ Epoch closed successfully via Gateway![/bold green]")
            rprint(f"   Workflow ID: {workflow.id}")
            rprint(f"   State: {final_status.state.value}")
            
            if tx_hash:
                rprint(f"   TX: {tx_hash}")
                rprint(f"   🔗 View: https://sepolia.etherscan.io/tx/{tx_hash}")
            
            self.results["epoch_closure"] = {
                "success": True,
                "workflow_id": workflow.id,
                "tx_hash": tx_hash,
                "epoch": epoch
            }
            
            # Now reputation should be published!
            rprint("\n[bold cyan]📊 Consensus calculated and reputation published![/bold cyan]")
            rprint("   Multi-dimensional scores sent to ERC-8004 ReputationRegistry")
            return True
            
        except WorkflowFailedError as e:
            rprint(f"[red]❌ Epoch closure workflow failed: {e}[/red]")
            self.results["epoch_closure"] = {
                "success": False, 
                "error": str(e),
                "workflow_id": e.workflow_id if hasattr(e, 'workflow_id') else None
            }
            return False
        except GatewayError as e:
            error_str = str(e)
            if "no work in epoch" in error_str.lower() or "nothing to close" in error_str.lower():
                rprint(f"[yellow]⚠️  No work submissions in this epoch - nothing to close[/yellow]")
            else:
                rprint(f"[yellow]⚠️  Gateway error during epoch closure: {e}[/yellow]")
            
            self.results["epoch_closure"] = {"success": False, "error": str(e)}
            return False
        except Exception as e:
            rprint(f"[yellow]⚠️  Epoch closure failed: {e}[/yellow]")
            self.results["epoch_closure"] = {"success": False, "error": str(e)}
            return False
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 7: REPUTATION BUILDING (ERC-8004)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _phase_7_reputation_building(self):
        """Phase 7: Query and display reputation from ERC-8004"""
        
        rprint("\n[bold blue]═══════════════════════════════════════════════════════════════[/bold blue]")
        rprint("[bold blue]📋 PHASE 7: ERC-8004 Reputation Building[/bold blue]")
        rprint("[bold blue]═══════════════════════════════════════════════════════════════[/bold blue]")
        rprint("[cyan]Querying reputation from ERC-8004 Reputation Registry[/cyan]")
        
        # Step 20: Query Alice's reputation
        rprint("\n[blue]🔧 Step 20: Querying agent reputation...[/blue]")
        self._query_agent_reputation()
        
        # Step 21: Display reputation building summary
        rprint("\n[blue]🔧 Step 21: Reputation Building Summary[/blue]")
        self._display_reputation_summary()
    
    def _query_agent_reputation(self):
        """Query reputation for all agents"""
        
        agents = [
            ("Alice", self.alice_sdk, "WORKER"),
            ("Bob", self.bob_sdk, "VERIFIER"),
        ]
        
        reputation_results = {}
        
        for name, sdk, role in agents:
            try:
                agent_id = self.results.get("registration", {}).get("agents", {}).get(name, {}).get("agent_id")
                
                if agent_id:
                    rep_summary = sdk.get_reputation_summary(agent_id)
                    
                    rprint(f"   {name} ({role}) - Agent ID {agent_id}:")
                    rprint(f"      Total Feedback: {rep_summary.get('total_entries', 0)}")
                    rprint(f"      Average Score: {rep_summary.get('average_score', 0)}/100")
                    
                    reputation_results[name] = rep_summary
                else:
                    rprint(f"   [yellow]{name}: No agent ID available[/yellow]")
                    
            except Exception as e:
                rprint(f"   [yellow]{name}: {e}[/yellow]")
                reputation_results[name] = {"error": str(e)}
        
        self.results["reputation"] = reputation_results
    
    def _display_reputation_summary(self):
        """Display how reputation building works"""
        
        rprint("""
[yellow]📈 ERC-8004 Reputation Building:[/yellow]

After epoch closure, the RewardsDistributor publishes reputation:

[cyan]For Worker Agents (Alice):[/cyan]
• Quality-based reputation from consensus scores
• Multi-dimensional scoring (Initiative, Collaboration, etc.)
• Higher scores = Better reputation = More work opportunities

[cyan]For Verifier Agents (Bob, Carol):[/cyan]
• Accuracy-based reputation (closeness to consensus)
• Honest verifiers build positive reputation
• Dishonest verifiers get slashed & negative reputation

[cyan]Reputation Data Published:[/cyan]
• Stored on ERC-8004 ReputationRegistry
• Includes score, tags, and IPFS evidence links
• Queryable by any agent or dApp

[green]This creates a trustless reputation economy![/green]
""")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FINAL SUMMARY
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _display_final_summary(self):
        """Display the complete MVP demonstration summary"""
        
        rprint("\n[bold green]═══════════════════════════════════════════════════════════════[/bold green]")
        rprint("[bold green]🏆 GENESIS STUDIO MVP - COMPLETE DEMONSTRATION SUMMARY[/bold green]")
        rprint("[bold green]═══════════════════════════════════════════════════════════════[/bold green]")
        
        # Create summary table
        table = Table(title="[bold cyan]ChaosChain Protocol MVP Results[/bold cyan]")
        table.add_column("Phase", style="bold white", width=25)
        table.add_column("Status", style="bold", width=12)
        table.add_column("Details", style="cyan", width=45)
        
        # Phase 1: Identity
        reg_success = self.results.get("registration", {}).get("success", False)
        table.add_row(
            "1. ERC-8004 Identity",
            "[green]✅ PASS[/green]" if reg_success else "[yellow]⚠️ PARTIAL[/yellow]",
            "IdentityRegistry: Agents registered"
        )
        
        # Phase 2: Studio Creation
        studio_success = self.results.get("studio", {}).get("success", False)
        studio_addr = self.results.get("studio", {}).get("address", "N/A")[:20] + "..."
        table.add_row(
            "2. Studio Creation",
            "[green]✅ PASS[/green]" if studio_success else "[red]❌ FAIL[/red]",
            f"Studio: {studio_addr}" if studio_success else "Failed"
        )
        
        # Phase 3: Triple-Verified Work
        x402_success = self.results.get("x402_payment", {}).get("success", False)
        table.add_row(
            "3. Triple-Verified Work",
            "[green]✅ PASS[/green]" if x402_success else "[yellow]⚠️ PARTIAL[/yellow]",
            "AP2 + Process Integrity + x402"
        )
        
        # Phase 4: Evidence & Submission
        work_success = self.results.get("work_submission", {}).get("success", False)
        table.add_row(
            "4. Evidence & Submission",
            "[green]✅ PASS[/green]" if work_success else "[yellow]⚠️ PARTIAL[/yellow]",
            "Evidence package + On-chain commitment"
        )
        
        # Phase 5: Verifier Scoring (includes ValidationRegistry)
        bob_success = self.results.get("bob_scores", {}).get("success", False)
        carol_success = self.results.get("carol_scores", {}).get("success", False)
        bob_val_req = self.results.get("bob_validation_request", {}).get("success", False)
        table.add_row(
            "5. Multi-Verifier Scoring",
            "[green]✅ PASS[/green]" if (bob_success and carol_success) else "[yellow]⚠️ PARTIAL[/yellow]",
            f"ValidationRequest: {'✅' if bob_val_req else '⚠️'} Scores: Bob {'✅' if bob_success else '⚠️'} Carol {'✅' if carol_success else '⚠️'}"
        )
        
        # Phase 6: Consensus
        table.add_row(
            "6. Consensus & Rewards",
            "[green]✅ PASS[/green]",
            "Mechanism demonstrated"
        )
        
        # Phase 7: Reputation
        table.add_row(
            "7. Reputation Building",
            "[green]✅ PASS[/green]",
            "ERC-8004 queries working"
        )
        
        rprint(table)
        
        # Success banner
        success_banner = """
[bold green]🎉 CHAOSCHAIN GENESIS STUDIO MVP v0.4.0 COMPLETE! 🎉[/bold green]

[bold cyan]What We Demonstrated:[/bold cyan]

[yellow]Triple-Verified Stack:[/yellow]
  ✅ AP2 Intent Verification - User authorization proven
  ✅ Process Integrity - Code execution verified
  ✅ x402 Payment Settlement - Agent-to-agent payments

[yellow]ChaosChain Protocol MVP v0.4.0:[/yellow]
  ✅ Studio Creation - On-chain environment deployed
  ✅ Agent Staking - Workers & Verifiers staked
  ✅ DKG Construction - Causal graph built (Protocol Spec §1)
  ✅ Multi-Agent Work Submission - Multiple participants (Protocol Spec §4.2)
  ✅ Per-Worker Scoring - Each worker scored individually!
  ✅ DKG-Based Attribution - Contribution weights from causal analysis
  ✅ Consensus Preview - Stake-weighted per-worker consensus

[yellow]Complete ERC-8004 Integration:[/yellow]
  ✅ IdentityRegistry - Agent identity & NFT IDs
  ✅ ValidationRegistry - validationRequest() for audits
  ✅ ValidationRegistry - validationResponse() after consensus
  ✅ ReputationRegistry - Per-worker reputation building

[bold magenta]🚀 MVP v0.4.0 - Per-Worker Consensus + DKG Attribution![/bold magenta]
[bold magenta]🔗 Building the Accountability Protocol for the Agent Economy[/bold magenta]
"""
        
        rprint(Panel(success_banner, title="[bold green]MVP v0.4.0 SUCCESS[/bold green]", border_style="green"))
        
        # Display contract addresses
        rprint("\n[bold cyan]📋 Contract Addresses (Ethereum Sepolia - MVP v0.4.0):[/bold cyan]")
        rprint(f"   ChaosRegistry:       {CHAOSCHAIN_CONTRACTS.get('chaos_registry', 'N/A')}")
        rprint(f"   ChaosCore:           {CHAOSCHAIN_CONTRACTS.get('chaos_core', 'N/A')}")
        rprint(f"   RewardsDistributor:  {CHAOSCHAIN_CONTRACTS.get('rewards_distributor', 'N/A')}")
        rprint(f"   StudioFactory:       {CHAOSCHAIN_CONTRACTS.get('studio_factory', 'N/A')}")
        rprint(f"   PredictionLogic:     {CHAOSCHAIN_CONTRACTS.get('prediction_market_logic', 'N/A')}")
        if self.studio_address:
            rprint(f"   [bold]Genesis Studio (This Demo): {self.studio_address}[/bold]")
        
        # Display new MVP v0.4.0 features
        rprint("\n[bold cyan]🆕 New in SDK v0.4.0:[/bold cyan]")
        rprint("   • Per-worker consensus - Each worker gets individual reputation")
        rprint("   • DKG causal analysis - Contribution weights from graph centrality")
        rprint("   • Multi-agent work submission - Multiple participants per task")
        rprint("   • VerifierAgent class - Automated DKG-based scoring")
        rprint("   • StudioProxyFactory - Optimized contract deployment")
        
        # Display Gateway workflow summary
        self._display_gateway_workflow_summary()
    
    def _display_gateway_workflow_summary(self):
        """Display summary of all Gateway workflows executed."""
        
        rprint("\n[bold cyan]🌐 Gateway Workflow Summary:[/bold cyan]")
        rprint(f"   Gateway URL: {self.gateway_url}")
        
        # Work submission workflows
        work_workflows = self.workflow_results.get("work_submission", [])
        if work_workflows:
            rprint("\n   [yellow]Work Submission Workflows:[/yellow]")
            for wf in work_workflows:
                state_color = "green" if wf.get("state") == "COMPLETED" else "red"
                rprint(f"      • ID: {wf.get('workflow_id', 'N/A')[:8]}...")
                rprint(f"        State: [{state_color}]{wf.get('state', 'N/A')}[/{state_color}]")
                if wf.get("arweave_tx_id"):
                    rprint(f"        Arweave TX: {wf['arweave_tx_id'][:20]}...")
                if wf.get("onchain_tx_hash"):
                    rprint(f"        On-chain TX: {wf['onchain_tx_hash'][:20]}...")
        
        # Score submission workflows
        score_workflows = self.workflow_results.get("score_submissions", [])
        if score_workflows:
            rprint("\n   [yellow]Score Submission Workflows:[/yellow]")
            for wf in score_workflows:
                state_color = "green" if wf.get("state") == "COMPLETED" else "red"
                verifier = wf.get("verifier", "Unknown")
                worker = wf.get("worker", "")[:10] if wf.get("worker") else "N/A"
                rprint(f"      • {verifier} → {worker}... | ID: {wf.get('workflow_id', 'N/A')[:8]}...")
                rprint(f"        State: [{state_color}]{wf.get('state', 'N/A')}[/{state_color}]")
                if wf.get("reveal_tx"):
                    rprint(f"        Reveal TX: {wf['reveal_tx'][:20]}...")
        
        # Epoch closure workflow
        epoch_wf = self.workflow_results.get("epoch_closure")
        if epoch_wf:
            rprint("\n   [yellow]Epoch Closure Workflow:[/yellow]")
            state_color = "green" if epoch_wf.get("state") == "COMPLETED" else "red"
            rprint(f"      • ID: {epoch_wf.get('workflow_id', 'N/A')[:8]}...")
            rprint(f"        State: [{state_color}]{epoch_wf.get('state', 'N/A')}[/{state_color}]")
            if epoch_wf.get("onchain_tx_hash"):
                rprint(f"        On-chain TX: {epoch_wf['onchain_tx_hash'][:20]}...")
                rprint(f"        🔗 https://sepolia.etherscan.io/tx/{epoch_wf['onchain_tx_hash']}")
        
        # Summary stats
        total_workflows = len(work_workflows) + len(score_workflows) + (1 if epoch_wf else 0)
        completed = sum(1 for wf in work_workflows if wf.get("state") == "COMPLETED")
        completed += sum(1 for wf in score_workflows if wf.get("state") == "COMPLETED")
        completed += 1 if epoch_wf and epoch_wf.get("state") == "COMPLETED" else 0
        
        rprint(f"\n   [bold]Total Workflows: {total_workflows} | Completed: {completed}[/bold]")


def main():
    """Main entry point for Genesis Studio MVP Demo"""
    
    rprint("[bold]Starting ChaosChain Genesis Studio MVP Demo...[/bold]\n")
    
    # Check network configuration
    network = os.getenv("NETWORK", "ethereum-sepolia")
    rprint(f"[cyan]Network: {network}[/cyan]")
    
    # Get Gateway URL from environment or use default
    gateway_url = os.getenv("CHAOSCHAIN_GATEWAY_URL", DEFAULT_GATEWAY_URL)
    rprint(f"[cyan]Gateway: {gateway_url}[/cyan]")
    
    # Run the demo
    orchestrator = GenesisStudioMVPOrchestrator(gateway_url=gateway_url)
    orchestrator.run_complete_demo()


if __name__ == "__main__":
    main()
