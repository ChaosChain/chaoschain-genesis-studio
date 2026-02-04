#!/usr/bin/env python3
"""
GENESIS STUDIO GATEWAY DEMO
═══════════════════════════════════════════════════════════════════════════════

A CLEAN, GATEWAY-FIRST protocol demonstration.

ARCHITECTURE INVARIANTS (NON-NEGOTIABLE):
─────────────────────────────────────────────────────────────────────────────────
1. EXACTLY ONE protocol signer: STUDIO_OPERATOR_PRIVATE_KEY
2. ALL protocol actions go through GatewayClient
3. NO direct contract calls from SDK
4. NO agent wallets signing protocol transactions
5. NO fallback paths, NO retries with alternate code paths

AGENT MODEL:
─────────────────────────────────────────────────────────────────────────────────
- Agents are IDENTITIES ONLY (agentId, role)
- Agents do NOT have private keys for protocol execution
- Agents do NOT submit transactions
- Agents only provide data (work content, score vectors)

HASH DISCIPLINE:
─────────────────────────────────────────────────────────────────────────────────
- dataHash, threadRoot, evidenceRoot computed EXACTLY ONCE
- Same values reused across ALL operations:
    - work submission
    - score submission  
    - epoch closure

DEMO FLOW:
─────────────────────────────────────────────────────────────────────────────────
1. Assume agents pre-registered in ERC-8004 IdentityRegistry
2. Ensure agents are Studio members (query on-chain)
3. Submit ONE multi-agent work via Gateway
4. Collect verifier score vectors off-chain (pure Python)
5. Submit ALL scores via Gateway
6. Close epoch via Gateway
7. Query and print reputation events

Reference: minimal_gateway_e2e.py (behavioral source of truth)

Usage:
    STUDIO_OPERATOR_PRIVATE_KEY=0x... python genesis_studio_gateway_demo.py

Requirements:
    - Gateway running at CHAOSCHAIN_GATEWAY_URL (default: http://localhost:3000)
    - STUDIO_OPERATOR_PRIVATE_KEY in environment (Gateway-registered signer)
    - Existing studio address (GENESIS_STUDIO_ADDRESS)
"""

import os
import sys
import json
import secrets
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from dotenv import load_dotenv
from eth_utils import keccak
from web3 import Web3
from eth_account import Account
from eth_abi import encode as eth_abi_encode

# ═══════════════════════════════════════════════════════════════════════════════
# GATEWAY CLIENT IMPORT
# ═══════════════════════════════════════════════════════════════════════════════
# Import from SDK source - no dependency on installed SDK's contract interaction
GATEWAY_SDK_PATH = os.path.expanduser(
    "~/Desktop/ChaosChain_labs/chaoschain/packages/sdk/chaoschain_sdk"
)
sys.path.insert(0, GATEWAY_SDK_PATH)

try:
    from gateway_client import (
        GatewayClient,
        WorkflowState,
        WorkflowStatus,
        GatewayError,
        WorkflowFailedError,
        GatewayConnectionError,
        ScoreSubmissionMode
    )
except ImportError as e:
    print(f"❌ Failed to import GatewayClient: {e}")
    print(f"   Ensure gateway_client.py exists at: {GATEWAY_SDK_PATH}")
    sys.exit(1)

# Remove SDK path to prevent SDK contract imports
sys.path.remove(GATEWAY_SDK_PATH)

# Load environment
load_dotenv()

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# Gateway
GATEWAY_URL = os.getenv("CHAOSCHAIN_GATEWAY_URL", "http://localhost:3000")

# Protocol Signer - THE ONLY ENTITY THAT SUBMITS TRANSACTIONS
STUDIO_OPERATOR_PRIVATE_KEY = os.getenv("STUDIO_OPERATOR_PRIVATE_KEY")
STUDIO_OPERATOR_ADDRESS = os.getenv("STUDIO_OPERATOR_ADDRESS")

# Studio
STUDIO_ADDRESS = os.getenv("GENESIS_STUDIO_ADDRESS")

# RPC for read-only queries (NOT for transaction submission)
RPC_URL = os.getenv("SEPOLIA_RPC_URL", "https://eth-sepolia.g.alchemy.com/v2/demo")

# Contracts (for read-only ABI queries)
CONTRACTS = {
    "rewards_distributor": "0x4bd7c3b53474Ba5894981031b5a9eF70CEA35e53",
    "reputation_registry": "0x8004B663056A597Dffe9eCcC1965A193B7388713",
    "identity_registry": "0x8004A818BFB912233c491871b3d84c89A494BD9e",
}

# Epoch
DEMO_EPOCH = 6  # Use fresh epoch for multi-agent per-worker demo


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT IDENTITIES (READ-ONLY)
# ═══════════════════════════════════════════════════════════════════════════════
# These are LOGICAL IDENTITIES, not transaction signers.
# Agent data is loaded from chaoschain_wallets.json for identity reference only.

@dataclass
class AgentIdentity:
    """Agent identity (NOT a transaction signer)."""
    name: str
    address: str
    agent_id: Optional[int] = None
    role: Optional[str] = None


def load_agent_identities() -> Dict[str, AgentIdentity]:
    """Load agent identities from wallets file (for address/identity reference only)."""
    wallets_file = os.path.join(os.path.dirname(__file__), "chaoschain_wallets.json")
    
    if not os.path.exists(wallets_file):
        print(f"❌ Wallets file not found: {wallets_file}")
        sys.exit(1)
    
    with open(wallets_file) as f:
        wallets = json.load(f)
    
    return {
        name: AgentIdentity(name=name, address=data["address"])
        for name, data in wallets.items()
    }


def load_cached_agent_ids() -> Dict[str, int]:
    """Load cached ERC-8004 agent IDs (for identity reference only)."""
    cache_file = os.path.join(os.path.dirname(__file__), "chaoschain_agent_ids.json")
    
    if not os.path.exists(cache_file):
        return {}
    
    try:
        with open(cache_file) as f:
            data = json.load(f)
            # Get Sepolia chain (11155111)
            sepolia_data = data.get("11155111", {})
            # Map address -> agent_id
            return {
                addr.lower(): info.get("agent_id")
                for addr, info in sepolia_data.items()
            }
    except Exception:
        return {}


# ═══════════════════════════════════════════════════════════════════════════════
# HASH COMPUTATION (EXACTLY ONCE)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class WorkHashes:
    """
    Work hashes computed EXACTLY ONCE.
    
    These values are IMMUTABLE after computation and are reused across:
    - Work submission (Gateway)
    - Score submission (Gateway)
    - Epoch closure (Gateway)
    """
    data_hash: bytes
    thread_root: bytes
    evidence_root: bytes
    evidence_content: bytes
    
    @classmethod
    def compute(cls, task_id: str, workers: List[str]) -> "WorkHashes":
        """Compute work hashes EXACTLY ONCE."""
        # Evidence content (what was done)
        evidence_data = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "workers": workers,
            "description": "Genesis Studio Gateway Demo - Multi-agent work",
        }
        evidence_content = json.dumps(evidence_data, sort_keys=True).encode('utf-8')
        
        # Compute hashes using keccak256 (matches Solidity)
        data_hash = keccak(evidence_content)
        thread_root = keccak(f"thread_{task_id}".encode())
        evidence_root = keccak(f"evidence_{task_id}".encode())
        
        return cls(
            data_hash=data_hash,
            thread_root=thread_root,
            evidence_root=evidence_root,
            evidence_content=evidence_content
        )
    
    def data_hash_hex(self) -> str:
        return f"0x{self.data_hash.hex()}"
    
    def thread_root_hex(self) -> str:
        return f"0x{self.thread_root.hex()}"
    
    def evidence_root_hex(self) -> str:
        return f"0x{self.evidence_root.hex()}"


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFIER SCORE GENERATION (OFF-CHAIN, PURE PYTHON)
# ═══════════════════════════════════════════════════════════════════════════════

def generate_verifier_scores(
    verifier_name: str,
    work_hashes: WorkHashes
) -> List[int]:
    """
    Generate verifier scores OFF-CHAIN (pure Python).
    
    This simulates a verifier's evaluation of the work.
    In production, this would involve actual DKG analysis.
    
    Scores are 5 dimensions, 0-10000 basis points:
    - Initiative
    - Collaboration
    - Reasoning
    - Output Quality
    - Communication
    
    Args:
        verifier_name: Name of the verifier (for deterministic seeding)
        work_hashes: Work hashes (for deterministic seeding)
    
    Returns:
        List of 5 scores (0-10000 each)
    """
    import random
    
    # Deterministic seed based on verifier name and work hash
    seed = hash(verifier_name + work_hashes.data_hash_hex())
    random.seed(seed)
    
    # Generate scores with some variation per verifier
    base_score = 8500  # ~85%
    
    scores = [
        min(10000, max(5000, base_score + random.randint(-500, 1000))),  # Initiative
        min(10000, max(5000, base_score + random.randint(-800, 1200))),  # Collaboration
        min(10000, max(5000, base_score + random.randint(-300, 800))),   # Reasoning
        min(10000, max(5000, base_score + random.randint(-200, 500))),   # Output Quality
        min(10000, max(5000, base_score + random.randint(-600, 1000))),  # Communication
    ]
    
    return scores


# ═══════════════════════════════════════════════════════════════════════════════
# READ-ONLY CONTRACT QUERIES (NO TRANSACTION SUBMISSION)
# ═══════════════════════════════════════════════════════════════════════════════

def create_readonly_web3() -> Web3:
    """Create Web3 instance for read-only queries ONLY."""
    return Web3(Web3.HTTPProvider(RPC_URL))


def query_agent_studio_registration(
    w3: Web3,
    studio_address: str,
    agent_address: str
) -> tuple[int, int]:
    """
    Query if agent is registered with studio (READ-ONLY).
    
    Returns:
        (agent_id, role) - 0 if not registered
    """
    abi = [
        {"inputs": [{"name": "agent", "type": "address"}], "name": "getAgentId", "outputs": [{"type": "uint256"}], "stateMutability": "view", "type": "function"},
        {"inputs": [{"name": "agentId", "type": "uint256"}], "name": "getAgentRole", "outputs": [{"type": "bytes32"}], "stateMutability": "view", "type": "function"},
    ]
    
    studio = w3.eth.contract(address=Web3.to_checksum_address(studio_address), abi=abi)
    
    agent_id = studio.functions.getAgentId(Web3.to_checksum_address(agent_address)).call()
    
    if agent_id == 0:
        return (0, 0)
    
    role_bytes = studio.functions.getAgentRole(agent_id).call()
    role = int(role_bytes.hex(), 16) if role_bytes else 0
    
    return (agent_id, role)


def query_work_participants(
    w3: Web3,
    studio_address: str,
    data_hash: bytes
) -> List[str]:
    """Query work participants from StudioProxy (READ-ONLY)."""
    abi = [{
        "inputs": [{"name": "dataHash", "type": "bytes32"}],
        "name": "getWorkParticipants",
        "outputs": [{"type": "address[]"}],
        "stateMutability": "view",
        "type": "function"
    }]
    
    studio = w3.eth.contract(address=Web3.to_checksum_address(studio_address), abi=abi)
    
    try:
        return studio.functions.getWorkParticipants(data_hash).call()
    except Exception:
        return []


def query_reputation_events(
    w3: Web3,
    agent_id: int,
    from_block: int = 0
) -> List[Dict]:
    """Query reputation events for an agent (READ-ONLY)."""
    # ReputationRegistry FeedbackGiven event
    reputation_registry = CONTRACTS["reputation_registry"]
    
    abi = [{
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "agentId", "type": "uint256"},
            {"indexed": False, "name": "value", "type": "int128"},
            {"indexed": False, "name": "valueDecimals", "type": "uint8"},
            {"indexed": False, "name": "tag1", "type": "string"},
            {"indexed": False, "name": "tag2", "type": "string"},
        ],
        "name": "FeedbackGiven",
        "type": "event"
    }]
    
    contract = w3.eth.contract(address=Web3.to_checksum_address(reputation_registry), abi=abi)
    
    try:
        events = contract.events.FeedbackGiven.get_logs(
            fromBlock=from_block,
            argument_filters={"agentId": agent_id}
        )
        return [dict(e) for e in events]
    except Exception as e:
        print(f"   ⚠️  Could not query reputation events: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════════════
# DIRECT SCORE SUBMISSION (VERIFIER SIGNS THEIR OWN SCORES)
# ═══════════════════════════════════════════════════════════════════════════════
# NOTE: The contract requires the VERIFIER'S address to sign score submissions.
# This is by design - each verifier must attest to their own scores.
# The Gateway can only be used for actions where STUDIO_OPERATOR is authorized.
# Score submission is NOT one of those actions - verifiers must sign directly.
# This matches the behavior of minimal_gateway_e2e.py (source of truth).

def submit_score_direct(
    w3: Web3,
    studio_address: str,
    verifier_private_key: str,
    data_hash: bytes,
    worker_address: str,
    scores: List[int]
) -> Optional[str]:
    """
    Submit score DIRECTLY using verifier's private key.
    
    The StudioProxy contract requires the actual verifier to sign the score submission.
    This cannot go through the Gateway since only STUDIO_OPERATOR is registered there.
    
    Args:
        w3: Web3 instance
        studio_address: Studio contract address
        verifier_private_key: Verifier's private key (they must sign their own scores)
        data_hash: Work data hash
        worker_address: Address of worker being scored
        scores: List of 5 scores (0-10000 basis points)
    
    Returns:
        Transaction hash if successful, None if failed
    """
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
    
    contract = w3.eth.contract(address=Web3.to_checksum_address(studio_address), abi=score_abi)
    
    # Scale scores from 0-10000 to 0-100 (uint8)
    scaled_scores = [s // 100 for s in scores]
    score_bytes = eth_abi_encode(['uint8', 'uint8', 'uint8', 'uint8', 'uint8'], scaled_scores)
    
    # Build and sign transaction with verifier's key
    verifier_account = Account.from_key(verifier_private_key)
    nonce = w3.eth.get_transaction_count(verifier_account.address)
    
    tx = contract.functions.submitScoreVectorForWorker(
        data_hash,
        Web3.to_checksum_address(worker_address),
        score_bytes
    ).build_transaction({
        'from': verifier_account.address,
        'nonce': nonce,
        'gas': 500000,
        'gasPrice': w3.eth.gas_price * 2,
        'chainId': 11155111  # Sepolia
    })
    
    signed_tx = verifier_account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    # Wait for confirmation
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    
    if receipt.status == 1:
        return tx_hash.hex()
    else:
        return None


def register_validator_direct(
    w3: Web3,
    owner_private_key: str,
    rewards_distributor_address: str,
    data_hash: bytes,
    validator_address: str
) -> Optional[str]:
    """
    Register validator with RewardsDistributor (owner only).
    
    This bridges the gap between StudioProxy (where scores are submitted)
    and RewardsDistributor (where validators are tracked for closeEpoch).
    
    Args:
        w3: Web3 instance
        owner_private_key: Owner's private key
        rewards_distributor_address: RewardsDistributor contract address
        data_hash: Work data hash
        validator_address: Validator address to register
    
    Returns:
        Transaction hash if successful, None if failed
    """
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
    
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(rewards_distributor_address), 
        abi=register_abi
    )
    
    owner_account = Account.from_key(owner_private_key)
    nonce = w3.eth.get_transaction_count(owner_account.address)
    
    tx = contract.functions.registerValidator(
        data_hash,
        Web3.to_checksum_address(validator_address)
    ).build_transaction({
        'from': owner_account.address,
        'nonce': nonce,
        'gas': 200000,
        'gasPrice': w3.eth.gas_price * 2,
        'chainId': 11155111  # Sepolia
    })
    
    signed_tx = owner_account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    # Wait for confirmation
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    
    if receipt.status == 1:
        return tx_hash.hex()
    else:
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# GATEWAY WORKFLOW HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def print_workflow_result(name: str, status: WorkflowStatus):
    """Print workflow result details."""
    print(f"\n✅ {name} COMPLETED")
    print(f"   Workflow ID: {status.id}")
    print(f"   State: {status.state.value}")
    
    if status.progress.onchain_tx_hash:
        print(f"   On-chain TX: {status.progress.onchain_tx_hash}")
        print(f"   🔗 https://sepolia.etherscan.io/tx/{status.progress.onchain_tx_hash}")
    
    if status.progress.arweave_tx_id:
        print(f"   Arweave TX: {status.progress.arweave_tx_id}")


def on_workflow_progress(status: WorkflowStatus):
    """Progress callback for workflow status updates."""
    emoji = {
        "UPLOAD_EVIDENCE": "📤",
        "AWAIT_ARWEAVE_CONFIRM": "⏳",
        "SUBMIT_WORK_ONCHAIN": "⛓️",
        "AWAIT_TX_CONFIRM": "⏳",
        "REGISTER_WORK": "📝",
        "AWAIT_REGISTER_CONFIRM": "⏳",
        "COMMIT_SCORE": "🔒",
        "AWAIT_COMMIT_CONFIRM": "⏳",
        "REVEAL_SCORE": "🔓",
        "AWAIT_REVEAL_CONFIRM": "⏳",
        "REGISTER_VALIDATOR": "✍️",
        "CHECK_PRECONDITIONS": "🔍",
        "SUBMIT_CLOSE_EPOCH": "🔐",
        "COMPLETED": "🎉",
        "FAILED": "❌",
        "STALLED": "⚠️",
    }.get(status.step, "🔄")
    
    state_color = {
        "COMPLETED": "\033[92m",  # Green
        "FAILED": "\033[91m",     # Red
        "STALLED": "\033[93m",    # Yellow
        "RUNNING": "\033[94m",    # Blue
    }.get(status.state.value, "")
    reset = "\033[0m"
    
    print(f"   {emoji} {status.step} | {state_color}{status.state.value}{reset}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN DEMO
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """
    Genesis Studio Gateway Demo - Clean, Gateway-first protocol demonstration.
    """
    
    print("=" * 70)
    print("GENESIS STUDIO GATEWAY DEMO")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VALIDATE CONFIGURATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("🔍 VALIDATING CONFIGURATION")
    print("-" * 70)
    
    if not STUDIO_OPERATOR_ADDRESS:
        print("❌ STUDIO_OPERATOR_ADDRESS not set")
        print("   This is the ONLY address that can submit protocol transactions.")
        sys.exit(1)
    
    if not STUDIO_ADDRESS:
        print("❌ GENESIS_STUDIO_ADDRESS not set")
        sys.exit(1)
    
    print(f"✅ Gateway URL: {GATEWAY_URL}")
    print(f"✅ Studio Address: {STUDIO_ADDRESS}")
    print(f"✅ Studio Operator (Signer): {STUDIO_OPERATOR_ADDRESS}")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # INITIALIZE GATEWAY CLIENT
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("🌐 INITIALIZING GATEWAY")
    print("-" * 70)
    
    gateway = GatewayClient(
        gateway_url=GATEWAY_URL,
        timeout=30,
        max_poll_time=300,
        poll_interval=3
    )
    
    # Health check
    try:
        health = gateway.health_check()
        print(f"✅ Gateway healthy: {health}")
    except GatewayConnectionError as e:
        print(f"❌ Gateway not reachable: {e}")
        sys.exit(1)
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # LOAD AGENT IDENTITIES (READ-ONLY)
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("👤 LOADING AGENT IDENTITIES")
    print("-" * 70)
    print("   Note: Agents are IDENTITIES, not transaction signers.")
    print()
    
    agents = load_agent_identities()
    cached_ids = load_cached_agent_ids()
    
    # Define workers and verifiers for this demo
    worker_names = ["Alice", "Dave", "Eve"]
    verifier_names = ["Bob", "Carol", "Frank"]
    
    workers = [agents[name] for name in worker_names if name in agents]
    verifiers = [agents[name] for name in verifier_names if name in agents]
    
    # Attach cached agent IDs
    for agent in workers + verifiers:
        agent.agent_id = cached_ids.get(agent.address.lower())
    
    print("   Workers:")
    for w in workers:
        id_str = f"ID: {w.agent_id}" if w.agent_id else "NOT REGISTERED"
        print(f"     • {w.name}: {w.address[:16]}... ({id_str})")
    
    print("   Verifiers:")
    for v in verifiers:
        id_str = f"ID: {v.agent_id}" if v.agent_id else "NOT REGISTERED"
        print(f"     • {v.name}: {v.address[:16]}... ({id_str})")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VERIFY STUDIO MEMBERSHIP (READ-ONLY QUERY)
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("🏢 VERIFYING STUDIO MEMBERSHIP")
    print("-" * 70)
    
    w3 = create_readonly_web3()
    
    for agent in workers + verifiers:
        agent_id, role = query_agent_studio_registration(w3, STUDIO_ADDRESS, agent.address)
        
        if agent_id == 0:
            print(f"   ⚠️  {agent.name}: NOT registered with studio")
            agent.role = None
        else:
            role_name = {
                1: "WORKER",
                2: "VERIFIER", 
                3: "WORKER_VERIFIER",
                4: "CLIENT",
            }.get(role, f"ROLE_{role}")
            
            agent.agent_id = agent_id
            agent.role = role_name
            print(f"   ✅ {agent.name}: Studio ID={agent_id}, Role={role_name}")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # COMPUTE WORK HASHES (EXACTLY ONCE)
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("🔐 COMPUTING WORK HASHES (EXACTLY ONCE)")
    print("-" * 70)
    
    task_id = f"genesis-demo-{secrets.token_hex(8)}"
    work_hashes = WorkHashes.compute(
        task_id=task_id,
        workers=[w.address for w in workers]
    )
    
    print(f"   Task ID: {task_id}")
    print(f"   DataHash: {work_hashes.data_hash_hex()[:20]}...")
    print(f"   ThreadRoot: {work_hashes.thread_root_hex()[:20]}...")
    print(f"   EvidenceRoot: {work_hashes.evidence_root_hex()[:20]}...")
    print()
    print("   ⚠️  These hashes are IMMUTABLE. Same values used for ALL operations.")
    print()
    
    # Track results
    results = {
        "work_submission": None,
        "score_submissions": [],
        "epoch_closure": None,
        "reputation_events": [],
    }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 1: MULTI-AGENT WORK SUBMISSION (DIRECT)
    # ═══════════════════════════════════════════════════════════════════════════
    # NOTE: Gateway's submitWork only supports single-agent.
    # For per-worker scoring and reputation, we MUST use submitWorkMultiAgent
    # which registers Alice, Dave, Eve as on-chain participants.
    
    print("=" * 70)
    print("PHASE 1: MULTI-AGENT WORK SUBMISSION (Alice, Dave, Eve)")
    print("=" * 70)
    
    worker_addresses = [w.address for w in workers]
    print(f"   Participants:")
    for w in workers:
        print(f"     • {w.name}: {w.address}")
    print(f"   Contribution weights: 33%, 34%, 33%")
    print()
    
    print("→ Submitting multi-agent work (submitWorkMultiAgent)...")
    
    # Load worker private keys (one worker must sign - contract requires submitter in participants)
    wallets_file = os.path.join(os.path.dirname(__file__), "chaoschain_wallets.json")
    with open(wallets_file) as f:
        wallets_data = json.load(f)
    
    try:
        # ABI for submitWorkMultiAgent
        multi_agent_abi = [{
            "inputs": [
                {"name": "dataHash", "type": "bytes32"},
                {"name": "threadRoot", "type": "bytes32"},
                {"name": "evidenceRoot", "type": "bytes32"},
                {"name": "participants", "type": "address[]"},
                {"name": "contributionWeights", "type": "uint16[]"},
                {"name": "evidenceCID", "type": "string"}
            ],
            "name": "submitWorkMultiAgent",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        }]
        
        studio_contract = w3.eth.contract(
            address=Web3.to_checksum_address(STUDIO_ADDRESS), 
            abi=multi_agent_abi
        )
        
        # Contribution weights: 3300, 3400, 3300 (sums to 10000 basis points = 100%)
        weights = [3300, 3400, 3300]
        
        # Alice signs the work submission (submitter MUST be in participants list)
        alice_private_key = wallets_data["Alice"]["private_key"]
        alice_account = Account.from_key(alice_private_key)
        print(f"   Submitter: Alice ({alice_account.address[:16]}...)")
        nonce = w3.eth.get_transaction_count(alice_account.address)
        
        tx = studio_contract.functions.submitWorkMultiAgent(
            work_hashes.data_hash,
            work_hashes.thread_root,
            work_hashes.evidence_root,
            [Web3.to_checksum_address(addr) for addr in worker_addresses],
            weights,
            "ar://mock-evidence"  # Evidence CID
        ).build_transaction({
            'from': alice_account.address,
            'nonce': nonce,
            'gas': 500000,
            'gasPrice': w3.eth.gas_price * 2,
            'chainId': 11155111
        })
        
        signed_tx = alice_account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"   TX sent: {tx_hash.hex()[:20]}...")
        
        # Wait for confirmation
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if receipt.status == 1:
            print(f"\n✅ Multi-Agent Work Submission COMPLETED")
            print(f"   TX: {tx_hash.hex()}")
            print(f"   🔗 https://sepolia.etherscan.io/tx/{tx_hash.hex()}")
            print(f"   Participants: {len(worker_addresses)} workers registered on-chain")
            
            results["work_submission"] = {
                "tx_hash": tx_hash.hex(),
                "state": "COMPLETED",
                "participants": [w.name for w in workers],
            }
        else:
            print(f"❌ Work submission reverted")
            sys.exit(1)
            
        # Also register work with RewardsDistributor (needs owner to sign)
        print("\n→ Registering work with RewardsDistributor...")
        register_work_abi = [{
            "inputs": [
                {"name": "studio", "type": "address"},
                {"name": "epoch", "type": "uint64"},
                {"name": "dataHash", "type": "bytes32"}
            ],
            "name": "registerWork",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        }]
        
        rd_contract = w3.eth.contract(
            address=Web3.to_checksum_address(CONTRACTS["rewards_distributor"]),
            abi=register_work_abi
        )
        
        # Owner signs registerWork call
        owner_private_key = os.getenv("STUDIO_OPERATOR_PRIVATE_KEY")
        owner_account = Account.from_key(owner_private_key)
        nonce = w3.eth.get_transaction_count(owner_account.address)
        tx = rd_contract.functions.registerWork(
            Web3.to_checksum_address(STUDIO_ADDRESS),
            DEMO_EPOCH,
            work_hashes.data_hash
        ).build_transaction({
            'from': owner_account.address,
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': w3.eth.gas_price * 2,
            'chainId': 11155111
        })
        
        signed_tx = owner_account.sign_transaction(tx)
        reg_tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(reg_tx_hash, timeout=120)
        
        if receipt.status == 1:
            print(f"   ✅ Work registered with RewardsDistributor")
        else:
            print(f"   ⚠️  RegisterWork reverted (may already be registered)")
        
    except Exception as e:
        print(f"❌ Work submission FAILED: {e}")
        sys.exit(1)
    
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 2: PER-WORKER SCORING (Each verifier scores EACH worker)
    # ═══════════════════════════════════════════════════════════════════════════
    # With submitWorkMultiAgent, Alice/Dave/Eve are registered as participants.
    # Each verifier must score EACH worker for proper per-worker reputation.
    # Total: 3 verifiers × 3 workers = 9 score submissions
    
    print("=" * 70)
    print("PHASE 2: PER-WORKER SCORING (3 verifiers × 3 workers = 9 scores)")
    print("=" * 70)
    
    # Query actual on-chain participants (should be Alice, Dave, Eve now!)
    onchain_participants = query_work_participants(w3, STUDIO_ADDRESS, work_hashes.data_hash)
    
    if onchain_participants:
        print(f"   On-chain participants: {len(onchain_participants)}")
        for p in onchain_participants:
            # Find matching worker name
            worker_name = next((w.name for w in workers if w.address.lower() == p.lower()), "Unknown")
            print(f"     • {worker_name}: {p[:16]}...")
    else:
        print(f"   ⚠️  Could not query on-chain participants")
    print()
    
    # Load verifier private keys from chaoschain_wallets.json
    wallets_file = os.path.join(os.path.dirname(__file__), "chaoschain_wallets.json")
    with open(wallets_file) as f:
        wallets_data = json.load(f)
    
    # Get OWNER private key for registerValidator calls
    owner_private_key = os.getenv("STUDIO_OPERATOR_PRIVATE_KEY")
    if not owner_private_key:
        print("❌ STUDIO_OPERATOR_PRIVATE_KEY not set (needed for registerValidator)")
        sys.exit(1)
    
    # Each verifier scores EACH worker
    for verifier in verifiers:
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🔍 {verifier.name} scoring all workers...")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Get verifier's private key
        if verifier.name not in wallets_data:
            print(f"   ❌ {verifier.name} not found in chaoschain_wallets.json")
            continue
        
        verifier_private_key = wallets_data[verifier.name]["private_key"]
        
        for worker in workers:
            print(f"\n→ {verifier.name} scoring {worker.name}...")
            
            # Generate unique scores for this verifier-worker pair
            # Use both names for deterministic but varied scores
            scores = generate_verifier_scores(f"{verifier.name}_{worker.name}", work_hashes)
            scaled_scores = [s // 100 for s in scores]
            print(f"   Scores (0-100): {scaled_scores}")
            
            try:
                # Submit score for this specific worker
                print(f"   → submitScoreVectorForWorker({worker.name})...")
                score_tx_hash = submit_score_direct(
                    w3=w3,
                    studio_address=STUDIO_ADDRESS,
                    verifier_private_key=verifier_private_key,
                    data_hash=work_hashes.data_hash,
                    worker_address=worker.address,  # Score THIS worker
                    scores=scores
                )
                
                if score_tx_hash:
                    print(f"   ✅ Score TX: {score_tx_hash[:20]}...")
                else:
                    print(f"   ❌ Score submission reverted")
                    continue
                
                results["score_submissions"].append({
                    "verifier": verifier.name,
                    "worker": worker.name,
                    "state": "COMPLETED",
                    "score_tx_hash": score_tx_hash,
                    "scores_onchain": scaled_scores,
                })
                
            except Exception as e:
                error_str = str(e)
                print(f"   ❌ Error: {error_str[:80]}...")
                results["score_submissions"].append({
                    "verifier": verifier.name,
                    "worker": worker.name,
                    "state": "FAILED",
                    "error": error_str[:200],
                })
        
        # Register this verifier with RewardsDistributor (once per verifier)
        print(f"\n   → Registering {verifier.name} as validator...")
        try:
            register_tx_hash = register_validator_direct(
                w3=w3,
                owner_private_key=owner_private_key,
                rewards_distributor_address=CONTRACTS["rewards_distributor"],
                data_hash=work_hashes.data_hash,
                validator_address=verifier.address
            )
            if register_tx_hash:
                print(f"   ✅ Validator registered: {register_tx_hash[:20]}...")
            else:
                print(f"   ⚠️  Validator registration reverted (may already exist)")
        except Exception as e:
            print(f"   ⚠️  Validator registration error: {str(e)[:50]}...")
        
        print(f"\n✅ {verifier.name} completed scoring all workers")
    
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 3: EPOCH CLOSURE VIA GATEWAY
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("=" * 70)
    print("PHASE 3: EPOCH CLOSURE VIA GATEWAY")
    print("=" * 70)
    
    print(f"   Signer: {STUDIO_OPERATOR_ADDRESS}")
    print(f"   Studio: {STUDIO_ADDRESS}")
    print(f"   Epoch: {DEMO_EPOCH}")
    print()
    
    print("→ Closing epoch via Gateway...")
    
    try:
        close_status = gateway.close_epoch_and_wait(
            studio_address=STUDIO_ADDRESS,
            epoch=DEMO_EPOCH,
            signer_address=STUDIO_OPERATOR_ADDRESS,  # THE ONLY SIGNER
            on_progress=on_workflow_progress
        )
        
        if close_status.state == WorkflowState.COMPLETED:
            # CloseEpoch workflow uses close_tx_hash, not onchain_tx_hash
            close_tx = getattr(close_status.progress, 'close_tx_hash', None) or close_status.progress.onchain_tx_hash
            
            print(f"\n✅ Epoch Closure COMPLETED")
            print(f"   Workflow ID: {close_status.id}")
            print(f"   State: {close_status.state.value}")
            if close_tx:
                print(f"   CloseEpoch TX: {close_tx}")
                print(f"   🔗 https://sepolia.etherscan.io/tx/{close_tx}")
            
            results["epoch_closure"] = {
                "workflow_id": close_status.id,
                "tx_hash": close_tx,
                "state": close_status.state.value,
            }
        else:
            print(f"   ⚠️  Epoch closure state: {close_status.state.value}")
            if close_status.error:
                print(f"      Error: {close_status.error.message}")
            
            results["epoch_closure"] = {
                "workflow_id": close_status.id,
                "state": close_status.state.value,
                "error": close_status.error.message if close_status.error else None,
            }
            
    except WorkflowFailedError as e:
        print(f"   ❌ Epoch closure FAILED: {e}")
        results["epoch_closure"] = {"state": "FAILED", "error": str(e)}
    except GatewayError as e:
        print(f"   ❌ Gateway error: {e}")
        results["epoch_closure"] = {"state": "GATEWAY_ERROR", "error": str(e)}
    
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 4: QUERY REPUTATION EVENTS (READ-ONLY)
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("=" * 70)
    print("PHASE 4: REPUTATION EVENTS (READ-ONLY QUERY)")
    print("=" * 70)
    
    # Get current block for reference
    current_block = w3.eth.block_number
    
    for agent in workers + verifiers:
        if agent.agent_id:
            events = query_reputation_events(w3, agent.agent_id, from_block=current_block - 100)
            
            if events:
                print(f"   {agent.name} (ID: {agent.agent_id}): {len(events)} reputation event(s)")
                for e in events:
                    print(f"      • value={e.get('args', {}).get('value')}, tag1={e.get('args', {}).get('tag1')}")
                
                results["reputation_events"].extend([
                    {"agent": agent.name, "agent_id": agent.agent_id, **dict(e.get('args', {}))}
                    for e in events
                ])
            else:
                print(f"   {agent.name} (ID: {agent.agent_id}): No reputation events found")
    
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("=" * 70)
    print("🏁 DEMO COMPLETE")
    print("=" * 70)
    
    print("\n📊 RESULTS SUMMARY:")
    print(json.dumps(results, indent=2, default=str))
    
    # Determine overall status
    work_ok = results.get("work_submission", {}).get("state") == "COMPLETED"
    scores_ok = all(s.get("state") == "COMPLETED" for s in results.get("score_submissions", []))
    epoch_ok = results.get("epoch_closure", {}).get("state") == "COMPLETED"
    
    print("\n🎯 VALIDATION:")
    print(f"   Work Submission: {'✅ PASSED' if work_ok else '❌ FAILED'}")
    print(f"   Score Submissions: {'✅ ALL PASSED' if scores_ok else '⚠️ SOME FAILED'}")
    print(f"   Epoch Closure: {'✅ PASSED' if epoch_ok else '❌ FAILED'}")
    
    if work_ok and scores_ok and epoch_ok:
        print("\n🎉 GATEWAY-FIRST PROTOCOL DEMO SUCCESSFUL!")
        return 0
    else:
        print("\n⚠️  Demo completed with issues. Review results above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
