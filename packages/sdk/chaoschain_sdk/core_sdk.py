"""
ChaosChain Agent SDK - Main SDK Class

This is the primary interface for developers building agents on the ChaosChain protocol.
It provides a unified API for all protocol interactions including identity management,
payments, process integrity, and evidence storage.
"""

import asyncio
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone
from rich import print as rprint

from .types import (
    AgentRole, 
    NetworkConfig, 
    PaymentMethod, 
    IntegrityProof,
    ValidationResult,
    PaymentProof,
    AgentIdentity,
    EvidencePackage,
    AgentID,
    TransactionHash
)
from .exceptions import (
    ChaosChainSDKError,
    AgentRegistrationError,
    PaymentError,
    IntegrityVerificationError
)
from .wallet_manager import WalletManager
from .storage_manager import StorageManager
from .payment_manager import PaymentManager
from .process_integrity import ProcessIntegrityVerifier
from .chaos_agent import ChaosAgent
from .google_ap2_integration import GoogleAP2Integration, GoogleAP2IntegrationResult
from .a2a_x402_extension import A2AX402Extension


class ChaosChainAgentSDK:
    """
    Production-ready SDK for building agents on the ChaosChain protocol.
    
    This is the main entry point for developers. It provides a unified interface
    for all ChaosChain protocol operations including:
    
    - ERC-8004 identity, reputation, and validation registries
    - Process integrity verification with cryptographic proofs
    - Multi-payment method support (W3C compliant + A2A-x402)
    - IPFS storage for verifiable evidence
    - Production-ready wallet management
    
    Example:
        ```python
        from chaoschain_sdk import ChaosChainAgentSDK, NetworkConfig, AgentRole
        
        # Initialize your agent
        sdk = ChaosChainAgentSDK(
            agent_name="MyAgent",
            agent_domain="myagent.example.com",
            agent_role=AgentRole.SERVER,
            network=NetworkConfig.BASE_SEPOLIA
        )
        
        # Register on ERC-8004
        agent_id, tx_hash = sdk.register_identity()
        
        # Execute work with process integrity
        result, proof = await sdk.execute_with_integrity_proof(
            "my_function", 
            {"param": "value"}
        )
        
        # Process payments
        payment_proof = sdk.execute_payment(
            to_agent="RecipientAgent",
            amount=1.5,
            service_type="analysis"
        )
        ```
    
    Attributes:
        agent_name: Name of the agent
        agent_domain: Domain where agent identity is hosted
        agent_role: Role of the agent (server, validator, client)
        network: Target blockchain network
        wallet_manager: Wallet management instance
        storage_manager: IPFS storage management instance
        payment_manager: Payment processing instance
        process_integrity: Process integrity verification instance
        chaos_agent: Core agent for ERC-8004 interactions
    """
    
    def __init__(
        self,
        agent_name: str,
        agent_domain: str,
        agent_role: AgentRole | str,
        network: NetworkConfig | str = NetworkConfig.BASE_SEPOLIA,
        enable_process_integrity: bool = True,
        enable_payments: bool = True,
        enable_storage: bool = True,
        enable_ap2: bool = True,
        wallet_file: str = None,
        storage_jwt: str = None,
        storage_gateway: str = None
    ):
        """
        Initialize the ChaosChain Agent SDK.
        
        Args:
            agent_name: Name of the agent
            agent_domain: Domain where agent identity is hosted  
            agent_role: Role of the agent (server, validator, client)
            network: Target blockchain network
            enable_process_integrity: Enable process integrity verification
            enable_payments: Enable payment processing
            enable_storage: Enable IPFS storage
            enable_ap2: Enable Google AP2 integration
            wallet_file: Custom wallet storage file path
            storage_jwt: Custom Pinata JWT token
            storage_gateway: Custom IPFS gateway URL
        """
        # Convert string parameters to enums if needed
        if isinstance(agent_role, str):
            try:
                agent_role = AgentRole(agent_role)
            except ValueError:
                raise ValueError(f"Invalid agent_role: {agent_role}. Must be one of: {[r.value for r in AgentRole]}")
        
        if isinstance(network, str):
            try:
                network = NetworkConfig(network)
            except ValueError:
                raise ValueError(f"Invalid network: {network}. Must be one of: {[n.value for n in NetworkConfig]}")
        
        self.agent_name = agent_name
        self.agent_domain = agent_domain
        self.agent_role = agent_role
        self.network = network
        
        # Initialize core components
        self._initialize_wallet_manager(wallet_file)
        self._initialize_storage_manager(enable_storage, storage_jwt, storage_gateway)
        self._initialize_payment_manager(enable_payments)
        self._initialize_process_integrity(enable_process_integrity)
        self._initialize_ap2_integration(enable_ap2)
        self._initialize_chaos_agent()
        
        rprint(f"[green]🚀 ChaosChain Agent SDK initialized for {agent_name} ({agent_role.value})[/green]")
        rprint(f"   Domain: {agent_domain}")
        rprint(f"   Network: {network.value}")
        rprint(f"   🔗 Triple-Verified Stack: ChaosChain owns 2/3 layers! 🚀")
    
    def get_sdk_status(self) -> Dict[str, Any]:
        """Get comprehensive SDK status and configuration."""
        return {
            "agent_name": self.agent_name,
            "agent_domain": self.agent_domain,
            "agent_role": self.agent_role.value,
            "network": self.network.value,
            "wallet_address": self.wallet_address if hasattr(self, 'wallet_manager') else None,
            "agent_id": getattr(self.chaos_agent, 'agent_id', None) if hasattr(self, 'chaos_agent') else None,
            "features": {
                "process_integrity": hasattr(self, 'process_integrity') and self.process_integrity is not None,
                "payments": hasattr(self, 'payment_manager') and self.payment_manager is not None,
                "storage": hasattr(self, 'storage_manager') and self.storage_manager is not None,
                "ap2_integration": hasattr(self, 'google_ap2') and self.google_ap2 is not None,
                "x402_extension": hasattr(self, 'a2a_x402') and self.a2a_x402 is not None,
            },
            "payment_methods": self.get_supported_payment_methods() if hasattr(self, 'payment_manager') and self.payment_manager else [],
            "chain_id": getattr(self.chaos_agent, 'chain_id', None) if hasattr(self, 'chaos_agent') else None,
        }
    
    def _initialize_wallet_manager(self, wallet_file: str = None):
        """Initialize wallet management."""
        try:
            self.wallet_manager = WalletManager(
                network=self.network,
                wallet_file=wallet_file
            )
            # Ensure wallet exists for this agent
            self.wallet_manager.create_or_load_wallet(self.agent_name)
        except Exception as e:
            raise ChaosChainSDKError(f"Failed to initialize wallet manager: {str(e)}")
    
    def _initialize_storage_manager(self, enabled: bool, jwt: str = None, gateway: str = None):
        """Initialize IPFS storage management."""
        if enabled:
            try:
                self.storage_manager = StorageManager(jwt_token=jwt, gateway_url=gateway)
            except Exception as e:
                rprint(f"[yellow]⚠️  IPFS storage not available: {e}[/yellow]")
                self.storage_manager = None
        else:
            self.storage_manager = None
    
    def _initialize_payment_manager(self, enabled: bool):
        """Initialize payment processing."""
        if enabled:
            try:
                self.payment_manager = PaymentManager(
                    network=self.network,
                    wallet_manager=self.wallet_manager
                )
                rprint(f"[green]💳 Multi-payment support: {len(self.payment_manager.supported_payment_methods)} methods available[/green]")
            except Exception as e:
                rprint(f"[yellow]⚠️  Payment processing not available: {e}[/yellow]")
                self.payment_manager = None
        else:
            self.payment_manager = None
    
    def _initialize_process_integrity(self, enabled: bool):
        """Initialize process integrity verification."""
        if enabled:
            try:
                self.process_integrity = ProcessIntegrityVerifier(
                    agent_name=self.agent_name,
                    storage_manager=self.storage_manager
                )
            except Exception as e:
                rprint(f"[yellow]⚠️  Process integrity not available: {e}[/yellow]")
                self.process_integrity = None
        else:
            self.process_integrity = None
    
    def _initialize_ap2_integration(self, enabled: bool):
        """Initialize Google AP2 integration."""
        if enabled:
            try:
                self.google_ap2 = GoogleAP2Integration(agent_name=self.agent_name)
                
                # Initialize A2A-x402 extension if payment manager is available
                if self.payment_manager:
                    self.a2a_x402 = A2AX402Extension(
                        agent_name=self.agent_name,
                        network=self.network,
                        payment_manager=self.payment_manager
                    )
                    rprint(f"[green]🔗 Google AP2 + A2A-x402 integration enabled[/green]")
                else:
                    self.a2a_x402 = None
                    rprint(f"[green]📝 Google AP2 integration enabled (x402 requires payments)[/green]")
                    
            except Exception as e:
                rprint(f"[yellow]⚠️  AP2 integration not available: {e}[/yellow]")
                self.google_ap2 = None
                self.a2a_x402 = None
        else:
            self.google_ap2 = None
            self.a2a_x402 = None
    
    def _initialize_chaos_agent(self):
        """Initialize core ChaosChain agent."""
        try:
            self.chaos_agent = ChaosAgent(
                agent_domain=self.agent_domain,
                wallet_manager=self.wallet_manager,
                network=self.network
            )
        except Exception as e:
            raise ChaosChainSDKError(f"Failed to initialize ChaosChain agent: {str(e)}")
    
    # === IDENTITY MANAGEMENT ===
    
    def register_identity(self) -> Tuple[AgentID, TransactionHash]:
        """
        Register agent identity on ERC-8004 IdentityRegistry.
        
        Returns:
            Tuple of (agent_id, transaction_hash)
        """
        try:
            return self.chaos_agent.register_agent()
        except Exception as e:
            raise AgentRegistrationError(f"Identity registration failed: {str(e)}")
    
    def get_agent_id(self) -> Optional[AgentID]:
        """
        Get the agent's on-chain ID.
        
        Returns:
            Agent ID if registered, None otherwise
        """
        return self.chaos_agent.get_agent_id()
    
    def get_agent_identity(self) -> AgentIdentity:
        """
        Get complete agent identity information.
        
        Returns:
            AgentIdentity object with all identity details
        """
        agent_id = self.get_agent_id()
        if not agent_id:
            raise AgentRegistrationError("Agent not registered")
        
        return AgentIdentity(
            agent_id=agent_id,
            agent_name=self.agent_name,
            agent_domain=self.agent_domain,
            wallet_address=self.wallet_address,
            registration_tx="registered",  # Would get from chain in production
            network=self.network
        )
    
    # === PROCESS INTEGRITY ===
    
    def register_integrity_checked_function(self, func: callable, function_name: str = None) -> str:
        """
        Register a function for integrity checking.
        
        Args:
            func: Function to register
            function_name: Optional custom name
            
        Returns:
            Code hash of the registered function
        """
        if not self.process_integrity:
            raise IntegrityVerificationError("Process integrity not enabled")
        
        return self.process_integrity.register_function(func, function_name)
    
    async def execute_with_integrity_proof(
        self, 
        function_name: str, 
        inputs: Dict[str, Any],
        require_proof: bool = True
    ) -> Tuple[Any, Optional[IntegrityProof]]:
        """
        Execute a registered function with integrity proof generation.
        
        Args:
            function_name: Name of the registered function
            inputs: Function input parameters
            require_proof: Whether to generate integrity proof
            
        Returns:
            Tuple of (function_result, integrity_proof)
        """
        if not self.process_integrity:
            raise IntegrityVerificationError("Process integrity not enabled")
        
        return await self.process_integrity.execute_with_proof(
            function_name, inputs, require_proof
        )
    
    # === GOOGLE AP2 INTEGRATION ===
    
    def create_intent_mandate(
        self,
        user_description: str,
        merchants: Optional[List[str]] = None,
        skus: Optional[List[str]] = None,
        requires_refundability: bool = False,
        expiry_minutes: int = 60
    ) -> GoogleAP2IntegrationResult:
        """
        Create Google AP2 Intent Mandate for user authorization.
        
        Args:
            user_description: Natural language description of intent
            merchants: Allowed merchants (optional)
            skus: Specific SKUs (optional)
            requires_refundability: Whether items must be refundable
            expiry_minutes: Minutes until intent expires
            
        Returns:
            GoogleAP2IntegrationResult with IntentMandate
        """
        if not self.google_ap2:
            raise PaymentError("Google AP2 integration not enabled")
        
        return self.google_ap2.create_intent_mandate(
            user_description=user_description,
            merchants=merchants,
            skus=skus,
            requires_refundability=requires_refundability,
            expiry_minutes=expiry_minutes
        )
    
    def create_cart_mandate(
        self,
        cart_id: str,
        items: List[Dict[str, Any]],
        total_amount: float,
        currency: str = "USD",
        merchant_name: Optional[str] = None,
        expiry_minutes: int = 15
    ) -> GoogleAP2IntegrationResult:
        """
        Create Google AP2 Cart Mandate with JWT signing.
        
        Args:
            cart_id: Unique cart identifier
            items: List of items in cart
            total_amount: Total cart amount
            currency: Currency code
            merchant_name: Name of merchant
            expiry_minutes: Minutes until cart expires
            
        Returns:
            GoogleAP2IntegrationResult with CartMandate and JWT
        """
        if not self.google_ap2:
            raise PaymentError("Google AP2 integration not enabled")
        
        return self.google_ap2.create_cart_mandate(
            cart_id=cart_id,
            items=items,
            total_amount=total_amount,
            currency=currency,
            merchant_name=merchant_name or self.agent_name,
            expiry_minutes=expiry_minutes
        )
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """
        Verify Google AP2 JWT token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Decoded payload if valid, empty dict if invalid
        """
        if not self.google_ap2:
            raise PaymentError("Google AP2 integration not enabled")
        
        return self.google_ap2.verify_jwt_token(token)
    
    # === A2A-X402 EXTENSION ===
    
    def create_x402_payment_request(
        self,
        cart_id: str,
        total_amount: float,
        currency: str,
        items: List[Dict[str, Any]],
        settlement_address: str = None
    ) -> Dict[str, Any]:
        """
        Create A2A-x402 payment request with multi-payment support.
        
        Args:
            cart_id: Cart identifier
            total_amount: Total payment amount
            currency: Payment currency
            items: List of items
            settlement_address: Crypto settlement address
            
        Returns:
            X402PaymentRequest object
        """
        if not self.a2a_x402:
            raise PaymentError("A2A-x402 extension not enabled")
        
        # Use agent's wallet address as settlement address if not provided
        if not settlement_address:
            settlement_address = self.wallet_address
        
        return self.a2a_x402.create_enhanced_payment_request(
            cart_id=cart_id,
            total_amount=total_amount,
            currency=currency,
            items=items,
            settlement_address=settlement_address
        )
    
    def execute_x402_crypto_payment(
        self,
        payment_request: Dict[str, Any],
        payer_agent: str,
        service_description: str = "Agent Service"
    ) -> Dict[str, Any]:
        """
        Execute A2A-x402 crypto payment.
        
        Args:
            payment_request: x402 payment request
            payer_agent: Name of paying agent
            service_description: Service description
            
        Returns:
            X402PaymentResponse with transaction details
        """
        if not self.a2a_x402:
            raise PaymentError("A2A-x402 extension not enabled")
        
        return self.a2a_x402.execute_x402_payment(
            payment_request=payment_request,
            payer_agent=payer_agent,
            service_description=service_description
        )
    
    def execute_traditional_payment(
        self,
        payment_method: str,
        amount: float,
        currency: str,
        payment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute traditional payment method (cards, Google Pay, etc.).
        
        Args:
            payment_method: W3C payment method identifier
            amount: Payment amount
            currency: Payment currency
            payment_data: Method-specific payment data
            
        Returns:
            TraditionalPaymentResponse with transaction details
        """
        if not self.a2a_x402:
            raise PaymentError("A2A-x402 extension not enabled")
        
        return self.a2a_x402.execute_traditional_payment(
            payment_method=payment_method,
            amount=amount,
            currency=currency,
            payment_data=payment_data
        )

    # === PAYMENT PROCESSING ===
    
    def create_payment_request(
        self, 
        to_agent: str, 
        amount: float, 
        service_type: str = "agent_service",
        currency: str = "USDC"
    ) -> Dict[str, Any]:
        """
        Create a payment request for agent services.
        
        Args:
            to_agent: Name of the receiving agent
            amount: Payment amount
            service_type: Type of service being paid for
            currency: Payment currency
            
        Returns:
            Payment request dictionary
        """
        if not self.payment_manager:
            raise PaymentError("Payment processing not enabled")
        
        return self.payment_manager.create_x402_payment_request(
            from_agent=self.agent_name,
            to_agent=to_agent,
            amount=amount,
            currency=currency,
            service_description=f"{service_type.replace('_', ' ').title()} Service"
        )
    
    def execute_payment(
        self, 
        payment_request: Dict[str, Any] = None,
        to_agent: str = None,
        amount: float = None,
        service_type: str = "agent_service"
    ) -> PaymentProof:
        """
        Execute a payment using A2A-x402 protocol.
        
        Args:
            payment_request: Pre-created payment request, or
            to_agent: Name of receiving agent (if creating new request)
            amount: Payment amount (if creating new request)
            service_type: Service type (if creating new request)
            
        Returns:
            Payment proof with transaction details
        """
        if not self.payment_manager:
            raise PaymentError("Payment processing not enabled")
        
        # Create payment request if not provided
        if not payment_request:
            if not to_agent or amount is None:
                raise PaymentError("Either payment_request or (to_agent, amount) must be provided")
            payment_request = self.create_payment_request(to_agent, amount, service_type)
        
        return self.payment_manager.execute_x402_payment(payment_request)
    
    def get_supported_payment_methods(self) -> List[str]:
        """
        Get list of all supported payment methods (W3C compliant).
        
        Returns:
            List of W3C payment method identifiers
        """
        if not self.payment_manager:
            return []
        
        return self.payment_manager.get_supported_payment_methods()
    
    # === STORAGE MANAGEMENT ===
    
    def store_evidence(
        self, 
        data: Dict[str, Any], 
        evidence_type: str = "evidence",
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Store evidence data on IPFS.
        
        Args:
            data: Data to store
            evidence_type: Type of evidence
            metadata: Optional metadata
            
        Returns:
            IPFS CID if successful, None otherwise
        """
        if not self.storage_manager:
            rprint("[yellow]⚠️  Storage not available[/yellow]")
            return None
        
        filename = f"{evidence_type}_{self.agent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Add agent metadata
        storage_metadata = {
            "agent_name": self.agent_name,
            "agent_domain": self.agent_domain,
            "evidence_type": evidence_type,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        if metadata:
            storage_metadata.update(metadata)
        
        return self.storage_manager.upload_json(data, filename, storage_metadata)
    
    def retrieve_evidence(self, cid: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve evidence data from IPFS.
        
        Args:
            cid: IPFS Content Identifier
            
        Returns:
            Retrieved data if successful, None otherwise
        """
        if not self.storage_manager:
            return None
        
        try:
            return self.storage_manager.retrieve_json(cid)
        except Exception as e:
            rprint(f"[red]❌ Failed to retrieve evidence: {e}[/red]")
            return None
    
    # === VALIDATION ===
    
    def request_validation(self, validator_agent_id: AgentID, data_hash: str) -> TransactionHash:
        """
        Request validation from another agent via ERC-8004.
        
        Args:
            validator_agent_id: ID of the validator agent
            data_hash: Hash of data to validate
            
        Returns:
            Transaction hash
        """
        return self.chaos_agent.request_validation(validator_agent_id, data_hash)
    
    def submit_feedback(self, agent_id: AgentID, score: int, feedback: str) -> TransactionHash:
        """
        Submit feedback for another agent via ERC-8004.
        
        Args:
            agent_id: Target agent ID
            score: Feedback score (0-100)
            feedback: Feedback text
            
        Returns:
            Transaction hash
        """
        return self.chaos_agent.submit_feedback(agent_id, score, feedback)
    
    def submit_validation_response(self, data_hash: str, score: int) -> TransactionHash:
        """
        Submit a validation response with score via ValidationRegistry.
        
        Args:
            data_hash: Hash of the data that was validated
            score: Validation score (0-100)
            
        Returns:
            Transaction hash
        """
        return self.chaos_agent.submit_validation_response(data_hash, score)
    
    # === EVIDENCE PACKAGES ===
    
    def create_evidence_package(
        self,
        work_proof: Dict[str, Any],
        integrity_proof: IntegrityProof = None,
        payment_proofs: List[PaymentProof] = None,
        validation_results: List[ValidationResult] = None
    ) -> EvidencePackage:
        """
        Create a comprehensive evidence package for Proof of Agency.
        
        Args:
            work_proof: Evidence of work performed
            integrity_proof: Process integrity proof
            payment_proofs: List of payment proofs
            validation_results: List of validation results
            
        Returns:
            Complete evidence package
        """
        import uuid
        
        package = EvidencePackage(
            package_id=f"evidence_{uuid.uuid4().hex[:8]}",
            agent_identity=self.get_agent_identity(),
            work_proof=work_proof,
            integrity_proof=integrity_proof,
            payment_proofs=payment_proofs or [],
            validation_results=validation_results or []
        )
        
        # Store on IPFS if available
        if self.storage_manager:
            package_data = {
                "package_id": package.package_id,
                "agent_identity": {
                    "agent_id": package.agent_identity.agent_id,
                    "agent_name": package.agent_identity.agent_name,
                    "agent_domain": package.agent_identity.agent_domain,
                    "wallet_address": package.agent_identity.wallet_address,
                    "network": package.agent_identity.network.value
                },
                "work_proof": package.work_proof,
                "integrity_proof": package.integrity_proof.__dict__ if package.integrity_proof else None,
                "payment_proofs": [proof.__dict__ for proof in package.payment_proofs],
                "validation_results": [result.__dict__ for result in package.validation_results],
                "created_at": package.created_at.isoformat()
            }
            
            cid = self.store_evidence(package_data, "evidence_package")
            if cid:
                package.ipfs_cid = cid
        
        return package
    
    # === PROPERTIES ===
    
    @property
    def wallet_address(self) -> str:
        """Get the agent's wallet address."""
        return self.wallet_manager.get_wallet_address(self.agent_name)
    
    @property
    def is_registered(self) -> bool:
        """Check if the agent is registered on-chain."""
        return self.get_agent_id() is not None
    
    @property
    def network_info(self) -> Dict[str, Any]:
        """Get network information."""
        return {
            "network": self.network.value,
            "chain_id": self.wallet_manager.chain_id,
            "connected": self.wallet_manager.is_connected,
            "wallet_address": self.wallet_address
        }
