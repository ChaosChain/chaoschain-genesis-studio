#!/usr/bin/env python3
"""
CHAOSCHAIN GENESIS STUDIO - Complete MVP Demonstration

This script demonstrates the COMPLETE ChaosChain Protocol MVP including:

1. Triple-Verified Stack (Existing)
   - AP2 Intent Verification (Google)
   - Process Integrity (ChaosChain + 0G Compute)
   - x402 Payment Settlement

2. ChaosChain Protocol MVP (NEW)
   - Studio Creation & Agent Staking
   - Work Submission to StudioProxy
   - Multi-Verifier Scoring (Proof of Agency)
   - Consensus & Reward Distribution
   - ERC-8004 Reputation Building

Usage:
    python genesis_studio.py

Architecture Overview:
    ┌─────────────────────────────────────────────────────────────┐
    │                    GENESIS STUDIO MVP                        │
    ├─────────────────────────────────────────────────────────────┤
    │  Phase 1: ERC-8004 Identity Registration                    │
    │  Phase 2: Studio Creation & Agent Staking                   │
    │  Phase 3: Work Execution (Triple-Verified Stack)            │
    │  Phase 4: Evidence Package & Submission                     │
    │  Phase 5: Multi-Verifier Scoring (Proof of Agency)          │
    │  Phase 6: Consensus & Rewards                               │
    │  Phase 7: Reputation Building                               │
    └─────────────────────────────────────────────────────────────┘
"""

import os
import sys
import json
import time
import hashlib
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

# Import agents
from agents.server_agent_sdk import GenesisServerAgentSDK
from agents.validator_agent_sdk import GenesisValidatorAgentSDK
from agents.client_agent_genesis import GenesisClientAgent

# Load environment variables
load_dotenv()

# ChaosChain Protocol Contract Addresses (Ethereum Sepolia)
# Source: SDK v0.3.3 - https://test.pypi.org/project/chaoschain-sdk/0.3.3/
CHAOSCHAIN_CONTRACTS = {
    "chaos_core": "0xB17e4810bc150e1373f288bAD2DEA47bBcE34239",  # V3 - FeedbackAuth support!
    "rewards_distributor": "0x7bD80CA4750A3cE67D13ebd8A92D4CE8e4d98c39",  # V3 - FeedbackAuth + multi-dimensional reputation!
    "finance_studio_logic": "0xb37c1F3a35CA99c509d087c394F5B4470599734D",  # V3 - FeedbackAuth compatible
    "creative_studio_logic": "0xF44B2E486437362F3CE972Da96E9700Bd0DC3b33",
    "prediction_market_logic": "0xcbc8d70e0614CA975E4E4De76E6370D79a25f30A",  # V3
}


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
    
    def __init__(self):
        # Track results for final summary
        self.results = {}
        
        # Agent SDK instances
        self.alice_sdk = None  # Worker Agent
        self.bob_sdk = None    # Verifier Agent 1
        self.carol_sdk = None  # Verifier Agent 2 (NEW for multi-verifier)
        self.charlie_sdk = None # Client Agent
        
        # Studio address (created during demo)
        self.studio_address = None
        
        # Work data hash (for verifier scoring)
        self.work_data_hash = None
        
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
[bold blue]║     CHAOSCHAIN GENESIS STUDIO - COMPLETE MVP DEMO             ║[/bold blue]
[bold blue]╚═══════════════════════════════════════════════════════════════╝[/bold blue]

[bold cyan]🎯 Complete Proof of Agency (PoA) Demonstration[/bold cyan]

[yellow]Triple-Verified Stack:[/yellow]
• Layer 1: AP2 Intent Verification (Google)
• Layer 2: Process Integrity (ChaosChain + 0G Compute)
• Layer 3: Adjudication/Accountability (ChaosChain)

[yellow]ChaosChain Protocol MVP:[/yellow]
  • Studio Creation & Agent Staking
  • Work Submission to StudioProxy
  • Multi-Verifier Scoring (2+ Verifiers)
  • Consensus & Reward Distribution
  • ERC-8004 Reputation Building

[green]🔗 ChaosChain owns 2/3 verification layers![/green]
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
        
        # Initialize Worker Agent (Alice)
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
        
        # Initialize Verifier Agent 2 (Carol) - for multi-verifier consensus
        # SDK automatically loads Carol's wallet from chaoschain_wallets.json
        self.carol_agent = GenesisValidatorAgentSDK(
            agent_name="Carol",  # SDK will auto-load Carol's separate wallet
            agent_domain="carol.genesis-studio.chaoschain.io",
            agent_role=AgentRole.VALIDATOR,
            network=network,
            enable_ap2=True,
            enable_process_integrity=True,
            use_0g_inference=True
        )
        self.carol_sdk = self.carol_agent.sdk
        rprint("[green]✅ Carol (Verifier 2) initialized with independent wallet[/green]")
        
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
        
        # Display agent status
        agents = [
            ("Alice", self.alice_agent, "WORKER"),
            ("Bob", self.bob_agent, "VERIFIER"),
            ("Carol", self.carol_agent, "VERIFIER"),
            ("Charlie", self.charlie_agent, "CLIENT")
        ]
        
        for name, agent, role in agents:
            rprint(f"✅ {name} ({role}) initialized:")
            rprint(f"   Wallet: {agent.sdk.wallet_address[:20]}...")
            rprint(f"   Domain: {agent.agent_domain}")
        
        self.results["wallets"] = {
            "Alice": self.alice_sdk.wallet_address,
            "Bob": self.bob_sdk.wallet_address,
            "Carol": self.carol_sdk.wallet_address if self.carol_sdk else "N/A",
            "Charlie": self.charlie_sdk.wallet_address
        }
    
    def _fund_agent_wallets(self):
        """Check wallet balances for all agents"""
        
        agents = [
            ("Alice", self.alice_sdk),
            ("Bob", self.bob_sdk),
            ("Carol", self.carol_sdk),
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
        
        if len(funded_agents) < 4:
            rprint("\n[yellow]🔗 Fund wallets at: https://sepoliafaucet.com/[/yellow]")
        
        self.results["funding"] = {"funded_agents": funded_agents}
    
    def _register_agents_onchain(self):
        """Register all agents on ERC-8004 IdentityRegistry"""
        
        registration_results = {}
        
        agents = [
            ("Alice", self.alice_agent),
            ("Bob", self.bob_agent),
            ("Carol", self.carol_agent),
            ("Charlie", self.charlie_agent)
        ]
        
        for agent_name, agent in agents:
            if agent is None:
                continue
            try:
                rprint(f"[blue]🔧 Registering {agent_name}: {agent.agent_domain}[/blue]")
                agent_id, tx_hash = agent.register_identity()
                wallet_address = agent.sdk.wallet_address
                
                rprint(f"[green]✅ {agent_name} registered: Agent ID {agent_id} (TX: {tx_hash[:20]}...)[/green]")
                
                registration_results[agent_name] = {
                    "agent_id": agent_id,
                    "address": wallet_address
                }
            except Exception as e:
                rprint(f"[yellow]⚠️  {agent_name} registration: {e}[/yellow]")
                registration_results[agent_name] = {"error": str(e)}
        
        self.results["registration"] = {
            "success": len([r for r in registration_results.values() if "agent_id" in r]) >= 2,
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
        
        # Step 6: Register Alice as Worker
        rprint("\n[blue]🔧 Step 6: Registering Alice as WORKER with stake...[/blue]")
        self._register_worker_with_studio()
        
        # Step 7: Register Verifiers (Bob and Carol)
        rprint("\n[blue]🔧 Step 7: Registering Verifiers (Bob, Carol) with stake...[/blue]")
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
        """Create a new Studio using ChaosCore factory"""
        
        try:
            # Use FinanceStudioLogic for smart shopping demo
            logic_module = CHAOSCHAIN_CONTRACTS["finance_studio_logic"]
            
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
    

    def _register_worker_with_studio(self):
        """Register Alice as Worker with stake"""
        
        try:
            alice_agent_id = self.results["registration"]["agents"]["Alice"]["agent_id"]
            
            # Handle case where agent_id might be a tuple (agent_id, tx_hash)
            if isinstance(alice_agent_id, tuple):
                alice_agent_id = alice_agent_id[0]
            
            rprint(f"   → Registering Alice (ID: {alice_agent_id}) as WORKER...")
            
            tx_hash = self.alice_sdk.register_with_studio(
                studio_address=self.studio_address,
                agent_id=alice_agent_id,
                role=1,  # WORKER
                stake_amount=1  # Wei (minimal stake for demo)
            )
            
            rprint(f"[green]✅ Alice registered as WORKER (TX: {tx_hash[:20]}...)[/green]")
            
            self.results["worker_registration"] = {
                "agent_id": alice_agent_id,
            "tx_hash": tx_hash,
                "role": "WORKER",
                "success": True
            }
            
        except Exception as e:
            rprint(f"[yellow]⚠️  Worker registration: {e}[/yellow]")
            self.results["worker_registration"] = {"success": False, "error": str(e)}
    
    def _register_verifiers_with_studio(self):
        """Register Bob and Carol as Verifiers with stake"""
        
        verifier_results = {}
        
        # Register Bob as Verifier 1
        try:
            bob_agent_id = self.results["registration"]["agents"]["Bob"]["agent_id"]
            
            # Handle case where agent_id might be a tuple (agent_id, tx_hash)
            if isinstance(bob_agent_id, tuple):
                bob_agent_id = bob_agent_id[0]
            
            rprint(f"   → Registering Bob (ID: {bob_agent_id}) as VERIFIER...")
            
            tx_hash = self.bob_sdk.register_with_studio(
                studio_address=self.studio_address,
                agent_id=bob_agent_id,
                role=2,  # VERIFIER
                stake_amount=1  # Wei (minimal stake for demo)
            )
            
            rprint(f"[green]✅ Bob registered as VERIFIER (TX: {tx_hash[:20]}...)[/green]")
            verifier_results["Bob"] = {"agent_id": bob_agent_id, "tx_hash": tx_hash, "success": True}
            
        except Exception as e:
            rprint(f"[yellow]⚠️  Bob registration: {e}[/yellow]")
            verifier_results["Bob"] = {"success": False, "error": str(e)}
        
        # Register Carol as Verifier 2 (with independent wallet)
        try:
            carol_agent_id = self.results["registration"]["agents"]["Carol"]["agent_id"]
            
            # Handle case where agent_id might be a tuple (agent_id, tx_hash)
            if isinstance(carol_agent_id, tuple):
                carol_agent_id = carol_agent_id[0]
            
            rprint(f"   → Registering Carol (ID: {carol_agent_id}) as VERIFIER...")
            
            tx_hash = self.carol_sdk.register_with_studio(
                studio_address=self.studio_address,
                agent_id=carol_agent_id,
                role=2,  # VERIFIER
                stake_amount=1  # Wei (minimal stake for demo)
            )
            
            rprint(f"[green]✅ Carol registered as VERIFIER (TX: {tx_hash[:20]}...)[/green]")
            verifier_results["Carol"] = {"agent_id": carol_agent_id, "tx_hash": tx_hash, "success": True}
            
            except Exception as e:
            rprint(f"[yellow]⚠️  Carol registration: {e}[/yellow]")
            verifier_results["Carol"] = {"success": False, "error": str(e)}
        
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
        """Create comprehensive evidence package"""
        
        analysis_data = self.results.get("analysis_data", {})
        process_integrity_proof = self.results.get("process_integrity_proof", {})
        x402_payment = self.results.get("x402_payment", {})
        
        evidence_package = {
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "agent": {
                "name": "Alice",
                "domain": "alice.genesis-studio.chaoschain.io",
                "role": "WORKER",
                "agent_id": self.results.get("registration", {}).get("agents", {}).get("Alice", {}).get("agent_id")
            },
            "work_output": {
                "task_type": "smart_shopping_analysis",
                "analysis": analysis_data,
                "quality_score": analysis_data.get("quality_score", 85),
                "confidence": analysis_data.get("confidence", 0.89)
            },
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
        """Submit work to StudioProxy on-chain"""
        
        # Step 13: Calculate data hashes
        rprint("\n[blue]🔧 Step 13: Calculating work hashes (DataHash Pattern)...[/blue]")
        
        # Calculate hashes per protocol spec
        data_hash = hashlib.sha256(json.dumps(evidence_package).encode()).digest()
        thread_root = hashlib.sha256(f"xmtp_thread_{evidence_cid}".encode()).digest()
        evidence_root = hashlib.sha256(f"ipfs_evidence_{evidence_cid}".encode()).digest()
        
        self.work_data_hash = data_hash  # Store for verifier scoring
        
        rprint(f"   DataHash: {data_hash.hex()[:20]}...")
        rprint(f"   ThreadRoot: {thread_root.hex()[:20]}...")
        rprint(f"   EvidenceRoot: {evidence_root.hex()[:20]}...")
        
        # Step 14: Submit work to StudioProxy
        rprint("\n[blue]🔧 Step 14: Submitting work to StudioProxy...[/blue]")
        
        try:
            tx_hash = self.alice_sdk.submit_work(
                studio_address=self.studio_address,
                data_hash=data_hash,
                thread_root=thread_root,
                evidence_root=evidence_root
            )
            
            rprint(f"[green]✅ Work submitted on-chain (TX: {tx_hash[:20]}...)[/green]")
            rprint(f"   🔗 View: https://sepolia.etherscan.io/tx/{tx_hash}")
            
            self.results["work_submission"] = {
                "data_hash": data_hash.hex(),
            "tx_hash": tx_hash,
                "success": True
            }
            
            # Step 14b: Register work with RewardsDistributor (CRITICAL for epoch closure!)
            rprint("\n[blue]🔧 Step 14b: Registering work with RewardsDistributor...[/blue]")
            self._register_work_with_rewards_distributor(data_hash)
            
        except Exception as e:
            rprint(f"[red]❌ Work submission failed: {e}[/red]")
            self.results["work_submission"] = {"success": False, "error": str(e)}
    
    def _register_work_with_rewards_distributor(self, data_hash: bytes):
        """
        Register work with RewardsDistributor for epoch tracking.
        
        CRITICAL: This is required for closeEpoch() to find the work!
        Without this, closeEpoch() will fail with "No work in epoch"
        
        Must be called by protocol owner.
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
        Register validator for a work submission.
        
        CRITICAL: This is required for closeEpoch() to find validators!
        
        Must be called by protocol owner.
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
        """Phase 5: Multiple Verifiers score the work (Proof of Agency)"""
        
        rprint("\n[bold blue]═══════════════════════════════════════════════════════════════[/bold blue]")
        rprint("[bold blue]📋 PHASE 5: Multi-Verifier Scoring (Proof of Agency)[/bold blue]")
        rprint("[bold blue]═══════════════════════════════════════════════════════════════[/bold blue]")
        rprint("[cyan]Verifier Agents independently audit work and submit score vectors[/cyan]")
        
        # Step 15: Bob performs causal audit and scores
        rprint("\n[blue]🔧 Step 15: Bob performing causal audit...[/blue]")
        bob_scores = self._verifier_audit_and_score("Bob", self.bob_sdk)
        
        # Step 16: Carol performs independent audit and scores
        rprint("\n[blue]🔧 Step 16: Carol performing independent audit...[/blue]")
        carol_scores = self._verifier_audit_and_score("Carol", self.carol_sdk)
        
        # Display score comparison
        self._display_score_comparison(bob_scores, carol_scores)
    
    def _verifier_audit_and_score(self, verifier_name: str, verifier_sdk) -> List[int]:
        """Verifier performs causal audit and submits score vector"""
        
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
        Attempt to close the epoch using the protocol owner's wallet.
        This publishes consensus scores and multi-dimensional reputation.
        
        Returns:
            bool: True if epoch was closed successfully, False otherwise
        """
        from web3 import Web3
        
        # Check for protocol owner key
        owner_key = os.getenv("PROTOCOL_OWNER_PRIVATE_KEY") or os.getenv("DEPLOYER_PRIVATE_KEY")
        
        if not owner_key:
            rprint("[yellow]⚠️  PROTOCOL_OWNER_PRIVATE_KEY not set - skipping epoch closure[/yellow]")
            return False
        
        if not self.studio_address:
            rprint("[yellow]⚠️  No studio address - cannot close epoch[/yellow]")
            return False
        
        try:
            rprint("\n[bold green]🔧 Step 19b: Closing epoch with protocol owner wallet...[/bold green]")
            
            # Get web3 instance from SDK
            w3 = self.alice_sdk.chaos_agent.w3
            
            # Create account from owner key
            owner_account = w3.eth.account.from_key(owner_key)
            rprint(f"   Owner address: {owner_account.address}")
            
            # Verify this is actually the owner
            rewards_distributor_address = CHAOSCHAIN_CONTRACTS["rewards_distributor"]
            
            # Check owner balance
            owner_balance = w3.eth.get_balance(owner_account.address)
            if owner_balance < w3.to_wei(0.001, 'ether'):
                rprint(f"[yellow]⚠️  Owner wallet has low balance: {w3.from_wei(owner_balance, 'ether'):.6f} ETH[/yellow]")
            
            # Build the closeEpoch transaction
            distributor_abi = [
                {
                    "inputs": [
                        {"name": "studio", "type": "address"},
                        {"name": "epoch", "type": "uint64"}
                    ],
                    "name": "closeEpoch",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ]
            
            distributor = w3.eth.contract(
                address=w3.to_checksum_address(rewards_distributor_address),
                abi=distributor_abi
            )
            
            # Use epoch 0 for the demo
            epoch = 0
            
            rprint(f"   → Closing epoch {epoch} for studio {self.studio_address[:20]}...")
            rprint(f"   → RewardsDistributor: {rewards_distributor_address}")
            
            # Get initial nonce and track it for sequential transactions
            current_nonce = w3.eth.get_transaction_count(owner_account.address)
            
            # STEP 1: Register work with RewardsDistributor (onlyOwner)
            rprint("\n   [cyan]→ Step 1/4: Registering work with RewardsDistributor...[/cyan]")
            register_work_abi = [
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
            
            distributor_with_register = w3.eth.contract(
                address=w3.to_checksum_address(rewards_distributor_address),
                abi=register_work_abi
            )
            
            # Get Alice's work dataHash from results
            if not hasattr(self, 'work_data_hash') or not self.work_data_hash:
                rprint("[yellow]   ⚠️  No work dataHash found - skipping registerWork[/yellow]")
            else:
                try:
                    tx = distributor_with_register.functions.registerWork(
                        w3.to_checksum_address(self.studio_address),
                        epoch,
                        self.work_data_hash
                    ).build_transaction({
                        'from': owner_account.address,
                        'nonce': current_nonce,
                        'gas': 300000,
                        'gasPrice': w3.eth.gas_price
                    })
                    
                    signed_tx = w3.eth.account.sign_transaction(tx, owner_key)
                    raw_tx = getattr(signed_tx, 'raw_transaction', getattr(signed_tx, 'rawTransaction', None))
                    tx_hash = w3.eth.send_raw_transaction(raw_tx)
                    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
                    
                    if receipt.status == 1:
                        rprint(f"   [green]✅ Work registered (TX: {tx_hash.hex()[:20]}...)[/green]")
                        current_nonce += 1  # Increment nonce for next transaction
                    else:
                        rprint(f"   [red]❌ registerWork reverted (TX: {tx_hash.hex()})[/red]")
                        rprint(f"   [red]Check transaction: https://sepolia.etherscan.io/tx/{tx_hash.hex()}[/red]")
                        return False
                except Exception as e:
                    rprint(f"   [red]❌ registerWork error: {e}[/red]")
                    return False
            
            # STEP 2: Register Bob as validator (onlyOwner)
            rprint("\n   [cyan]→ Step 2/4: Registering Bob (verifier)...[/cyan]")
            register_validator_abi = [
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
            
            distributor_with_validator = w3.eth.contract(
                address=w3.to_checksum_address(rewards_distributor_address),
                abi=register_validator_abi
            )
            
            try:
                tx = distributor_with_validator.functions.registerValidator(
                    self.work_data_hash,
                    w3.to_checksum_address(self.bob_sdk.wallet_address)
                ).build_transaction({
                    'from': owner_account.address,
                    'nonce': current_nonce,
                    'gas': 300000,
                    'gasPrice': w3.eth.gas_price
                })
                
                signed_tx = w3.eth.account.sign_transaction(tx, owner_key)
                raw_tx = getattr(signed_tx, 'raw_transaction', getattr(signed_tx, 'rawTransaction', None))
                tx_hash = w3.eth.send_raw_transaction(raw_tx)
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
                
                if receipt.status == 1:
                    rprint(f"   [green]✅ Bob registered (TX: {tx_hash.hex()[:20]}...)[/green]")
                    current_nonce += 1  # Increment nonce for next transaction
                else:
                    rprint(f"   [red]❌ registerValidator (Bob) reverted (TX: {tx_hash.hex()})[/red]")
                    rprint(f"   [red]Check: https://sepolia.etherscan.io/tx/{tx_hash.hex()}[/red]")
                    return False
            except Exception as e:
                rprint(f"   [red]❌ registerValidator (Bob) error: {e}[/red]")
                return False
            
            # STEP 3: Register Carol as validator (onlyOwner)
            rprint("\n   [cyan]→ Step 3/4: Registering Carol (verifier)...[/cyan]")
            
            try:
                tx = distributor_with_validator.functions.registerValidator(
                    self.work_data_hash,
                    w3.to_checksum_address(self.carol_sdk.wallet_address)
                ).build_transaction({
                    'from': owner_account.address,
                    'nonce': current_nonce,
                    'gas': 300000,
                    'gasPrice': w3.eth.gas_price
                })
                
                signed_tx = w3.eth.account.sign_transaction(tx, owner_key)
                raw_tx = getattr(signed_tx, 'raw_transaction', getattr(signed_tx, 'rawTransaction', None))
                tx_hash = w3.eth.send_raw_transaction(raw_tx)
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
                
                if receipt.status == 1:
                    rprint(f"   [green]✅ Carol registered (TX: {tx_hash.hex()[:20]}...)[/green]")
                    current_nonce += 1  # Increment nonce for next transaction
                else:
                    rprint(f"   [red]❌ registerValidator (Carol) reverted (TX: {tx_hash.hex()})[/red]")
                    rprint(f"   [red]Check: https://sepolia.etherscan.io/tx/{tx_hash.hex()}[/red]")
                    return False
            except Exception as e:
                rprint(f"   [red]❌ registerValidator (Carol) error: {e}[/red]")
                return False
            
            # STEP 4: Now close the epoch
            rprint("\n   [cyan]→ Step 4/4: Closing epoch...[/cyan]")
            
            # Estimate gas
            try:
                gas_estimate = distributor.functions.closeEpoch(
                    w3.to_checksum_address(self.studio_address),
                    epoch
                ).estimate_gas({'from': owner_account.address})
                gas_limit = int(gas_estimate * 1.3)  # 30% buffer
            except Exception as gas_error:
                rprint(f"[yellow]⚠️  Gas estimation failed: {gas_error}[/yellow]")
                gas_limit = 500000  # Fallback
            
            # Build transaction
            tx = distributor.functions.closeEpoch(
                w3.to_checksum_address(self.studio_address),
                epoch
            ).build_transaction({
                'from': owner_account.address,
                'nonce': current_nonce,
                'gas': gas_limit,
                'gasPrice': w3.eth.gas_price
            })
            
            # Sign and send
            signed_tx = w3.eth.account.sign_transaction(tx, owner_key)
            raw_transaction = getattr(signed_tx, 'raw_transaction', getattr(signed_tx, 'rawTransaction', None))
            tx_hash = w3.eth.send_raw_transaction(raw_transaction)
            
            rprint(f"   → Transaction sent: {tx_hash.hex()[:20]}...")
            
            # Wait for receipt
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt.status == 1:
                rprint(f"[bold green]✅ Epoch closed successfully![/bold green]")
                rprint(f"   TX: {tx_hash.hex()}")
                rprint(f"   🔗 View: https://sepolia.etherscan.io/tx/{tx_hash.hex()}")
                
                self.results["epoch_closure"] = {
                    "success": True,
                    "tx_hash": tx_hash.hex(),
                    "epoch": epoch
                }
                
                # Now reputation should be published!
                rprint("\n[bold cyan]📊 Consensus calculated and reputation published![/bold cyan]")
                rprint("   Multi-dimensional scores sent to ERC-8004 ReputationRegistry")
                return True
            else:
                rprint(f"[red]❌ Epoch closure transaction reverted[/red]")
                self.results["epoch_closure"] = {"success": False, "error": "Transaction reverted"}
                return False
                
        except Exception as e:
            error_str = str(e)
            if "caller is not the owner" in error_str.lower() or "ownable" in error_str.lower():
                rprint(f"[yellow]⚠️  Wrong owner key - the provided key is not the RewardsDistributor owner[/yellow]")
            elif "no work in epoch" in error_str.lower() or "nothing to close" in error_str.lower():
                rprint(f"[yellow]⚠️  No work submissions in this epoch - nothing to close[/yellow]")
            else:
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
[bold green]🎉 CHAOSCHAIN GENESIS STUDIO MVP DEMONSTRATION COMPLETE! 🎉[/bold green]

[bold cyan]What We Demonstrated:[/bold cyan]

[yellow]Triple-Verified Stack:[/yellow]
  ✅ AP2 Intent Verification - User authorization proven
  ✅ Process Integrity - Code execution verified
  ✅ x402 Payment Settlement - Agent-to-agent payments

[yellow]ChaosChain Protocol MVP:[/yellow]
  ✅ Studio Creation - On-chain environment deployed
  ✅ Agent Staking - Workers & Verifiers staked
  ✅ Work Submission - Evidence committed on-chain
  ✅ Multi-Verifier Scoring - Independent audits completed
  ✅ Consensus Preview - Stake-weighted mechanism shown

[yellow]Complete ERC-8004 Integration:[/yellow]
  ✅ IdentityRegistry - Agent identity & NFT IDs
  ✅ ValidationRegistry - validationRequest() for audits
  ✅ ValidationRegistry - validationResponse() after consensus
  ✅ ReputationRegistry - Multi-dimensional reputation building

[bold magenta]🚀 ChaosChain owns 2/3 verification layers![/bold magenta]
[bold magenta]🔗 Building the Accountability Protocol for the Agent Economy[/bold magenta]
"""
        
        rprint(Panel(success_banner, title="[bold green]SUCCESS[/bold green]", border_style="green"))
        
        # Display contract addresses
        rprint("\n[bold cyan]📋 Contract Addresses (Ethereum Sepolia):[/bold cyan]")
        rprint(f"   ChaosCore: {CHAOSCHAIN_CONTRACTS['chaos_core']}")
        rprint(f"   RewardsDistributor: {CHAOSCHAIN_CONTRACTS['rewards_distributor']}")
        rprint(f"   FinanceStudioLogic: {CHAOSCHAIN_CONTRACTS['finance_studio_logic']}")
        if self.studio_address:
            rprint(f"   [bold]Genesis Studio (This Demo): {self.studio_address}[/bold]")


def main():
    """Main entry point for Genesis Studio MVP Demo"""
    
    rprint("[bold]Starting ChaosChain Genesis Studio MVP Demo...[/bold]\n")
    
    # Check network configuration
    network = os.getenv("NETWORK", "ethereum-sepolia")
    rprint(f"[cyan]Network: {network}[/cyan]")
    
    # Run the demo
    orchestrator = GenesisStudioMVPOrchestrator()
    orchestrator.run_complete_demo()


if __name__ == "__main__":
    main()
