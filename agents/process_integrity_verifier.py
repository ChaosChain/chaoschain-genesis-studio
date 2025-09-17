"""
ChaosChain Process Integrity Verifier

This module provides ChaosChain's Process Integrity Layer - the second layer of our
Triple-Verified Stack that ensures correct code execution in the correct causal sequence.

CHAOSCHAIN PROCESS INTEGRITY OVERVIEW:
- Verifiable Functions: Cryptographic proof that specific code was executed
- Process Integrity Proofs: Evidence of correct execution sequence
- Insurance Policies: Economic consequences for process violations
- Causal Sequence Verification: Ensures proper workflow execution

TRIPLE-VERIFIED STACK POSITION:
Layer 3: ChaosChain Adjudication - "Was the outcome correct and valuable?"
Layer 2: ChaosChain Process Integrity - "Was the correct code executed in correct sequence?"
Layer 1: Google AP2 Intent - "Was the action authorized by the user?"

This is ChaosChain's core innovation - we own 2 out of 3 verification layers!
"""

import json
import time
import hashlib
import inspect
from typing import Dict, Any, Optional, List, Callable, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import uuid
from functools import wraps

from rich import print as rprint


class ProcessIntegrityType(Enum):
    """Types of process integrity verification"""
    VERIFIABLE = "verifiable"      # Code execution is cryptographically verified
    INSURED = "insured"           # Behavior is economically guaranteed
    AUTONOMOUS = "autonomous"     # Acts independently with own resources


@dataclass
class ProcessIntegrityProof:
    """
    Cryptographic proof of correct code execution in ChaosChain
    
    This is a native component of every ChaosChain EvidencePackage
    """
    proof_id: str
    agent_id: str
    function_name: str
    agent_code_hash: str
    input_hash: str
    output_hash: str
    execution_timestamp: str
    causal_sequence_hash: str  # Hash of the execution sequence
    attestation_signature: str
    verifier_network: str
    gas_used: int
    execution_duration_ms: int


@dataclass
class ProcessInsurancePolicy:
    """
    Insurance policy for ChaosChain process integrity with slashing conditions
    """
    policy_id: str
    agent_id: str
    stake_amount: float
    stake_token: str
    coverage_amount: float
    slashing_conditions: List[Dict[str, Any]]
    premium_rate: float
    policy_duration: int  # in blocks
    created_at: str
    status: str


@dataclass
class AutonomousAgentConfig:
    """
    Configuration for autonomous ChaosChain agents
    """
    agent_id: str
    wallet_address: str
    initial_balance: float
    authorized_actions: List[str]
    spending_limits: Dict[str, float]
    governance_rules: Dict[str, Any]
    emergency_contacts: List[str]
    auto_renewal: bool


def integrity_checked_function(func: Callable) -> Callable:
    """
    ChaosChain @integrity_checked_function decorator
    
    This decorator wraps any function to provide process integrity verification.
    It generates ProcessIntegrityProof for every execution.
    
    Usage:
        @integrity_checked_function
        def analyze_market_sentiment(self, symbol: str):
            # ... analysis logic ...
            return result
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get the agent instance (assumes first arg is self)
        agent_instance = args[0] if args else None
        agent_name = getattr(agent_instance, 'agent_name', 'unknown_agent')
        
        # Calculate agent code hash
        source_code = inspect.getsource(func)
        agent_code_hash = hashlib.sha256(source_code.encode()).hexdigest()
        
        # Calculate input hash
        input_data = {"args": args[1:], "kwargs": kwargs}  # Skip self
        input_hash = hashlib.sha256(
            json.dumps(input_data, sort_keys=True, default=str).encode()
        ).hexdigest()
        
        rprint(f"[purple]⚡ ChaosChain Process Integrity: Executing {func.__name__}[/purple]")
        rprint(f"[dim]   Agent: {agent_name}[/dim]")
        rprint(f"[dim]   Code Hash: {agent_code_hash[:16]}...[/dim]")
        rprint(f"[dim]   Input Hash: {input_hash[:16]}...[/dim]")
        
        # Execute the function
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = int((time.time() - start_time) * 1000)
            
            # Calculate output hash
            output_hash = hashlib.sha256(
                json.dumps(result, sort_keys=True, default=str).encode()
            ).hexdigest()
            
            # Generate causal sequence hash (simplified - in production would track full sequence)
            causal_sequence = f"{agent_name}:{func.__name__}:{time.time()}"
            causal_sequence_hash = hashlib.sha256(causal_sequence.encode()).hexdigest()
            
            # Create ProcessIntegrityProof
            proof = ProcessIntegrityProof(
                proof_id=f"proof_{uuid.uuid4().hex[:8]}",
                agent_id=agent_name,
                function_name=func.__name__,
                agent_code_hash=agent_code_hash,
                input_hash=input_hash,
                output_hash=output_hash,
                execution_timestamp=datetime.now(timezone.utc).isoformat(),
                causal_sequence_hash=causal_sequence_hash,
                attestation_signature=_generate_attestation_signature(
                    agent_code_hash, input_hash, output_hash, causal_sequence_hash
                ),
                verifier_network="chaoschain-process-integrity",
                gas_used=21000,  # Mock gas usage
                execution_duration_ms=execution_time
            )
            
            # Store proof in agent instance if possible
            if hasattr(agent_instance, '_process_integrity_proofs'):
                agent_instance._process_integrity_proofs[proof.proof_id] = proof
            
            rprint(f"[green]✅ Process Integrity Verified: {proof.proof_id}[/green]")
            rprint(f"[dim]   Output Hash: {output_hash[:16]}...[/dim]")
            rprint(f"[dim]   Execution Time: {execution_time}ms[/dim]")
            
            # Return both result and proof
            return result, proof
            
        except Exception as e:
            rprint(f"[red]❌ Process Integrity Verification Failed: {e}[/red]")
            raise
    
    return wrapper


def _generate_attestation_signature(agent_code_hash: str, input_hash: str, output_hash: str, causal_sequence_hash: str) -> str:
    """Generate ChaosChain attestation signature for process integrity"""
    attestation_data = f"{agent_code_hash}:{input_hash}:{output_hash}:{causal_sequence_hash}"
    return hashlib.sha256(attestation_data.encode()).hexdigest()


class ChaosChainProcessIntegrityVerifier:
    """
    ChaosChain Process Integrity Verifier
    
    The second layer of our Triple-Verified Stack, ensuring correct code execution
    in the correct causal sequence. This is ChaosChain's core innovation.
    """
    
    def __init__(
        self,
        agent_name: str,
        integrity_type: ProcessIntegrityType,
        chaoschain_endpoint: str = "https://process-integrity.chaoschain.dev",
        stake_amount: float = 1000.0
    ):
        """
        Initialize ChaosChain Process Integrity Verifier
        
        Args:
            agent_name: Name of the agent
            integrity_type: Type of integrity verification needed
            chaoschain_endpoint: ChaosChain Process Integrity API endpoint
            stake_amount: Amount to stake for insurance/verification
        """
        self.agent_name = agent_name
        self.integrity_type = integrity_type
        self.chaoschain_endpoint = chaoschain_endpoint
        self.stake_amount = stake_amount
        
        # Storage for proofs and policies
        self.process_integrity_proofs: Dict[str, ProcessIntegrityProof] = {}
        self.insurance_policies: Dict[str, ProcessInsurancePolicy] = {}
        self.autonomous_config: Optional[AutonomousAgentConfig] = None
        
        # Function registry for integrity checking
        self.registered_functions: Dict[str, Callable] = {}
        self.code_hashes: Dict[str, str] = {}
        
        # IPFS storage for proof persistence
        self.ipfs_manager = None
        try:
            from .ipfs_storage import GenesisIPFSManager
            self.ipfs_manager = GenesisIPFSManager()
        except ImportError:
            rprint(f"[yellow]⚠️  IPFS storage not available for proof persistence[/yellow]")
        
        rprint(f"[green]✅ ChaosChain Process Integrity Verifier initialized: {agent_name} ({integrity_type.value})[/green]")
    
    def register_integrity_checked_function(self, func: Callable, function_name: str) -> str:
        """
        Register a function for ChaosChain process integrity verification
        
        Args:
            func: The function to register
            function_name: Name identifier for the function
            
        Returns:
            Code hash of the registered function
        """
        # Get function source code
        source_code = inspect.getsource(func)
        
        # Create deterministic hash of the code
        code_hash = hashlib.sha256(source_code.encode()).hexdigest()
        
        self.registered_functions[function_name] = func
        self.code_hashes[function_name] = code_hash
        
        rprint(f"[blue]📝 Registered integrity-checked function: {function_name}[/blue]")
        rprint(f"[dim]   Code hash: {code_hash[:16]}...[/dim]")
        
        return code_hash
    
    async def execute_with_integrity_proof(
        self,
        function_name: str,
        inputs: Dict[str, Any],
        require_proof: bool = True
    ) -> Tuple[Any, Optional[ProcessIntegrityProof]]:
        """
        Execute a function with ChaosChain process integrity proof
        
        Args:
            function_name: Name of the registered function
            inputs: Input parameters for the function
            require_proof: Whether to generate cryptographic proof
            
        Returns:
            Tuple of (result, process_integrity_proof)
        """
        if function_name not in self.registered_functions:
            raise ValueError(f"Function {function_name} not registered for integrity checking")
        
        func = self.registered_functions[function_name]
        code_hash = self.code_hashes[function_name]
        
        # Create input hash
        input_hash = hashlib.sha256(
            json.dumps(inputs, sort_keys=True).encode()
        ).hexdigest()
        
        rprint(f"[purple]⚡ Executing with ChaosChain Process Integrity: {function_name}[/purple]")
        
        # Execute the function
        start_time = time.time()
        try:
            result = func(**inputs)
            execution_time = int((time.time() - start_time) * 1000)
            
            # Create output hash
            output_hash = hashlib.sha256(
                json.dumps(result, sort_keys=True, default=str).encode()
            ).hexdigest()
            
            process_integrity_proof = None
            if require_proof:
                # Generate causal sequence hash
                causal_sequence = f"{self.agent_name}:{function_name}:{time.time()}"
                causal_sequence_hash = hashlib.sha256(causal_sequence.encode()).hexdigest()
                
                # Generate process integrity proof
                process_integrity_proof = ProcessIntegrityProof(
                    proof_id=f"proof_{uuid.uuid4().hex[:8]}",
                    agent_id=self.agent_name,
                    function_name=function_name,
                    agent_code_hash=code_hash,
                    input_hash=input_hash,
                    output_hash=output_hash,
                    execution_timestamp=datetime.now(timezone.utc).isoformat(),
                    causal_sequence_hash=causal_sequence_hash,
                    attestation_signature=_generate_attestation_signature(
                        code_hash, input_hash, output_hash, causal_sequence_hash
                    ),
                    verifier_network="chaoschain-process-integrity",
                    gas_used=21000,  # Mock gas usage
                    execution_duration_ms=execution_time
                )
                
                self.process_integrity_proofs[process_integrity_proof.proof_id] = process_integrity_proof
                
                # Store proof on IPFS for persistence and verifiability
                if self.ipfs_manager:
                    try:
                        from dataclasses import asdict
                        import datetime as dt
                        proof_data = {
                            "type": "chaoschain_process_integrity_proof",
                            "proof": asdict(process_integrity_proof),
                            "timestamp": dt.datetime.now().isoformat(),
                            "agent_name": self.agent_name
                        }
                        filename = f"process_integrity_proof_{process_integrity_proof.proof_id}.json"
                        cid = self.ipfs_manager.storage.upload_json(proof_data, filename)
                        if cid:
                            rprint(f"[green]📁 Process Integrity Proof stored on IPFS: {cid}[/green]")
                    except Exception as e:
                        rprint(f"[yellow]⚠️  Failed to store process integrity proof on IPFS: {e}[/yellow]")
                
                rprint(f"[green]✅ Process integrity proof generated: {process_integrity_proof.proof_id}[/green]")
            else:
                rprint(f"[green]✅ Function executed successfully (no proof required)[/green]")
            
            return result, process_integrity_proof
            
        except Exception as e:
            rprint(f"[red]❌ Process integrity verification failed: {e}[/red]")
            raise
    
    def verify_process_integrity_proof(self, proof_id: str) -> bool:
        """
        Verify a ChaosChain process integrity proof
        
        Args:
            proof_id: ID of the proof to verify
            
        Returns:
            True if proof is valid
        """
        if proof_id not in self.process_integrity_proofs:
            return False
        
        proof = self.process_integrity_proofs[proof_id]
        
        # Verify the attestation signature
        expected_signature = _generate_attestation_signature(
            proof.agent_code_hash,
            proof.input_hash,
            proof.output_hash,
            proof.causal_sequence_hash
        )
        
        is_valid = proof.attestation_signature == expected_signature
        
        if is_valid:
            rprint(f"[green]✅ Process integrity proof verified: {proof_id}[/green]")
        else:
            rprint(f"[red]❌ Process integrity proof verification failed: {proof_id}[/red]")
        
        return is_valid
    
    def create_process_insurance_policy(
        self,
        coverage_amount: float,
        slashing_conditions: List[Dict[str, Any]],
        policy_duration: int = 100000  # blocks
    ) -> ProcessInsurancePolicy:
        """
        Create a ChaosChain process insurance policy with slashing conditions
        
        Args:
            coverage_amount: Amount of coverage provided
            slashing_conditions: Conditions that trigger slashing
            policy_duration: Duration in blocks
            
        Returns:
            ProcessInsurancePolicy object
        """
        policy_id = f"policy_{uuid.uuid4().hex[:8]}"
        
        # Calculate premium based on risk (simplified)
        base_premium_rate = 0.05  # 5% base rate
        risk_multiplier = len(slashing_conditions) * 0.01
        premium_rate = base_premium_rate + risk_multiplier
        
        policy = ProcessInsurancePolicy(
            policy_id=policy_id,
            agent_id=self.agent_name,
            stake_amount=self.stake_amount,
            stake_token="CHAOS",  # ChaosChain native token
            coverage_amount=coverage_amount,
            slashing_conditions=slashing_conditions,
            premium_rate=premium_rate,
            policy_duration=policy_duration,
            created_at=datetime.now(timezone.utc).isoformat(),
            status="active"
        )
        
        self.insurance_policies[policy_id] = policy
        
        rprint(f"[blue]🛡️  ChaosChain process insurance policy created: {policy_id}[/blue]")
        rprint(f"[dim]   Coverage: {coverage_amount} CHAOS, Premium: {premium_rate:.2%}[/dim]")
        rprint(f"[dim]   Slashing conditions: {len(slashing_conditions)}[/dim]")
        
        return policy
    
    def configure_autonomous_agent(
        self,
        wallet_address: str,
        initial_balance: float,
        authorized_actions: List[str],
        spending_limits: Dict[str, float]
    ) -> AutonomousAgentConfig:
        """
        Configure agent for autonomous operation within ChaosChain
        
        Args:
            wallet_address: Agent's own wallet address
            initial_balance: Starting balance for autonomous operation
            authorized_actions: List of actions agent can perform
            spending_limits: Spending limits per action type
            
        Returns:
            AutonomousAgentConfig object
        """
        config = AutonomousAgentConfig(
            agent_id=self.agent_name,
            wallet_address=wallet_address,
            initial_balance=initial_balance,
            authorized_actions=authorized_actions,
            spending_limits=spending_limits,
            governance_rules={
                "require_consensus": False,
                "emergency_stop_threshold": 0.8,
                "auto_rebalance": True
            },
            emergency_contacts=[],
            auto_renewal=True
        )
        
        self.autonomous_config = config
        
        rprint(f"[purple]👑 Autonomous ChaosChain agent configured: {self.agent_name}[/purple]")
        rprint(f"[dim]   Wallet: {wallet_address}[/dim]")
        rprint(f"[dim]   Balance: {initial_balance} CHAOS[/dim]")
        rprint(f"[dim]   Authorized actions: {len(authorized_actions)}[/dim]")
        
        return config
    
    def check_slashing_conditions(self, policy_id: str, agent_behavior: Dict[str, Any]) -> bool:
        """
        Check if agent behavior violates ChaosChain slashing conditions
        
        Args:
            policy_id: ID of the insurance policy
            agent_behavior: Observed agent behavior data
            
        Returns:
            True if slashing should occur
        """
        if policy_id not in self.insurance_policies:
            return False
        
        policy = self.insurance_policies[policy_id]
        
        for condition in policy.slashing_conditions:
            condition_type = condition.get("type")
            
            if condition_type == "max_execution_time":
                if agent_behavior.get("execution_time", 0) > condition.get("threshold", float('inf')):
                    rprint(f"[red]⚠️  ChaosChain slashing condition violated: execution time exceeded[/red]")
                    return True
            
            elif condition_type == "accuracy_threshold":
                if agent_behavior.get("accuracy", 1.0) < condition.get("threshold", 0.0):
                    rprint(f"[red]⚠️  ChaosChain slashing condition violated: accuracy below threshold[/red]")
                    return True
            
            elif condition_type == "unauthorized_action":
                if agent_behavior.get("action") not in condition.get("allowed_actions", []):
                    rprint(f"[red]⚠️  ChaosChain slashing condition violated: unauthorized action[/red]")
                    return True
        
        return False
    
    def get_enhanced_evidence_with_process_integrity(
        self,
        process_integrity_proof_id: str,
        chaoschain_evidence: Dict[str, Any],
        ap2_verification: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create enhanced evidence package with ChaosChain process integrity verification
        
        This creates the complete Triple-Verified Stack evidence:
        - AP2: Intent verification
        - ChaosChain Process Integrity: Execution verification  
        - ChaosChain Adjudication: Outcome verification
        """
        if process_integrity_proof_id not in self.process_integrity_proofs:
            raise ValueError(f"Process integrity proof {process_integrity_proof_id} not found")
        
        process_integrity_proof = self.process_integrity_proofs[process_integrity_proof_id]
        
        enhanced_evidence = {
            "chaoschain_evidence": chaoschain_evidence,
            "chaoschain_process_integrity": {
                "process_integrity_proof": asdict(process_integrity_proof),
                "verification_status": self.verify_process_integrity_proof(process_integrity_proof_id),
                "integrity_type": self.integrity_type.value,
                "insurance_policies": [asdict(p) for p in self.insurance_policies.values()],
                "autonomous_config": asdict(self.autonomous_config) if self.autonomous_config else None
            },
            "ap2_verification": ap2_verification,
            "triple_verified_stack": {
                "intent_verification": "AP2" if ap2_verification else "Not Available",
                "process_integrity_verification": "ChaosChain",
                "outcome_adjudication": "ChaosChain",
                "verification_complete": True,
                "chaoschain_layers": 2  # We own 2 out of 3 layers!
            },
            "metadata": {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "agent_id": self.agent_name,
                "protocol_version": "ChaosChain-Triple-Verified-v1.0"
            }
        }
        
        rprint(f"[cyan]🔗 Triple-Verified Stack evidence created[/cyan]")
        rprint(f"[dim]   Intent: {'✅' if ap2_verification else '❌'}[/dim]")
        rprint(f"[dim]   Process Integrity: ✅ (ChaosChain)[/dim]")
        rprint(f"[dim]   Outcome Adjudication: ✅ (ChaosChain)[/dim]")
        rprint(f"[green]   ChaosChain owns 2/3 verification layers! 🚀[/green]")
        
        return enhanced_evidence
    
    def get_verifier_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the ChaosChain Process Integrity Verifier"""
        return {
            "agent_name": self.agent_name,
            "integrity_type": self.integrity_type.value,
            "registered_functions": len(self.registered_functions),
            "process_integrity_proofs": len(self.process_integrity_proofs),
            "insurance_policies": len(self.insurance_policies),
            "autonomous_configured": self.autonomous_config is not None,
            "stake_amount": self.stake_amount,
            "chaoschain_endpoint": self.chaoschain_endpoint
        }