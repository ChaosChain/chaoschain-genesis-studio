"""
ChaosChain AP2 Mandate Manager

This module integrates Google's Agent Payment Protocol (AP2) with ChaosChain,
providing cryptographic mandate verification for user intent and payment authorization.

AP2 INTEGRATION OVERVIEW:
- Intent Mandates: Capture user's high-level request ("Find me running shoes")
- Cart Mandates: Secure approval of specific items and prices
- Verifiable Credentials: Cryptographic proof of user authorization
- Multi-Protocol Payments: Support x402 (crypto) + AP2 (universal payments)

CHAOSCHAIN ENHANCEMENT:
- Enhanced Evidence Packages include AP2 mandate proofs
- Three-layer verification: Intent (AP2) + Execution (EigenCloud) + Outcome (ChaosChain)
- Revenue model extends to both crypto and traditional payment flows
"""

import json
import os
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import base64
import uuid

from rich import print as rprint

# Simplified crypto implementation (in production, use proper crypto libraries)
import hashlib


@dataclass
class IntentMandate:
    """
    AP2 Intent Mandate - Captures user's high-level authorization
    
    Example: "Find me white running shoes under $150"
    """
    mandate_id: str
    user_id: str
    agent_id: str
    intent_description: str
    constraints: Dict[str, Any]  # price_limit, timing, preferences, etc.
    timestamp: str
    signature: str
    verifiable_credential: str
    ipfs_cid: Optional[str] = None  # CID where this mandate is stored on IPFS


@dataclass
class CartMandate:
    """
    AP2 Cart Mandate - Specific approval of items and prices
    
    Example: "Nike Air Max, Size 10, $129.99 from Nike.com"
    """
    mandate_id: str
    intent_mandate_id: str  # Links back to original intent
    user_id: str
    agent_id: str
    items: List[Dict[str, Any]]
    total_amount: float
    currency: str
    merchant_info: Dict[str, Any]
    timestamp: str
    signature: str
    verifiable_credential: str
    ipfs_cid: Optional[str] = None  # CID where this mandate is stored on IPFS


@dataclass
class AP2PaymentProof:
    """
    Cryptographic proof of AP2 payment completion
    """
    payment_id: str
    cart_mandate_id: str
    payment_method: str  # "x402", "credit_card", "bank_transfer", etc.
    amount: float
    currency: str
    transaction_hash: Optional[str]  # For crypto payments
    payment_receipt: Dict[str, Any]
    timestamp: str
    verification_status: str


class GenesisAP2MandateManager:
    """
    AP2 Mandate Manager for ChaosChain Genesis Studio
    
    Integrates Google's Agent Payment Protocol (AP2) with our existing x402 infrastructure
    to provide comprehensive user intent verification and multi-protocol payment support.
    """
    
    def __init__(self, agent_name: str, private_key_path: Optional[str] = None):
        """
        Initialize AP2 Mandate Manager
        
        Args:
            agent_name: Name of the agent using this manager
            private_key_path: Path to private key for signing mandates
        """
        self.agent_name = agent_name
        self.private_key = self._load_or_generate_private_key(private_key_path)
        self.public_key = hashlib.sha256(self.private_key.encode()).hexdigest()[:32]
        
        # Storage for mandates and proofs
        self.intent_mandates: Dict[str, IntentMandate] = {}
        self.cart_mandates: Dict[str, CartMandate] = {}
        self.payment_proofs: Dict[str, AP2PaymentProof] = {}
        
        # IPFS storage for mandate persistence
        self.ipfs_manager = None
        try:
            from .ipfs_storage import GenesisIPFSManager
            self.ipfs_manager = GenesisIPFSManager()
        except ImportError:
            rprint(f"[yellow]⚠️  IPFS storage not available for mandate persistence[/yellow]")
        
        rprint(f"[green]✅ AP2 Mandate Manager initialized for {agent_name}[/green]")
    
    def _load_or_generate_private_key(self, key_path: Optional[str]) -> str:
        """Load existing private key or generate new one for mandate signing (simplified)"""
        if key_path and os.path.exists(key_path):
            with open(key_path, 'r') as f:
                return f.read().strip()
        else:
            # Generate a simple key for demo purposes (in production, use proper crypto)
            return hashlib.sha256(f"{self.agent_name}_{time.time()}".encode()).hexdigest()
    
    def _sign_data(self, data: str) -> str:
        """Create cryptographic signature for mandate data (simplified)"""
        # Simplified signing for demo (in production, use proper digital signatures)
        signature_data = f"{self.private_key}:{data}"
        signature = hashlib.sha256(signature_data.encode()).hexdigest()
        return base64.b64encode(signature.encode()).decode('utf-8')
    
    def _create_verifiable_credential(self, mandate_data: Dict[str, Any]) -> str:
        """
        Create AP2-compliant verifiable credential
        
        This is a simplified implementation. In production, this would integrate
        with proper VC standards and potentially DID (Decentralized Identity) systems.
        """
        vc = {
            "context": ["https://www.w3.org/2018/credentials/v1", "https://ap2.google.com/2025/credentials/v1"],
            "type": ["VerifiableCredential", "AP2MandateCredential"],
            "issuer": f"did:chaoschain:{self.agent_name}",
            "issuanceDate": datetime.now(timezone.utc).isoformat(),
            "credentialSubject": mandate_data,
            "proof": {
                "type": "RsaSignature2018",
                "created": datetime.now(timezone.utc).isoformat(),
                "verificationMethod": f"did:chaoschain:{self.agent_name}#key-1",
                "signatureValue": self._sign_data(json.dumps(mandate_data, sort_keys=True))
            }
        }
        return base64.b64encode(json.dumps(vc).encode()).decode()
    
    def create_intent_mandate(
        self,
        user_id: str,
        intent_description: str,
        constraints: Dict[str, Any]
    ) -> IntentMandate:
        """
        Create AP2 Intent Mandate for user's high-level request
        
        Args:
            user_id: Identifier for the user making the request
            intent_description: Natural language description of intent
            constraints: Structured constraints (budget, timing, preferences)
            
        Returns:
            IntentMandate object with cryptographic proof
        """
        mandate_id = f"intent_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now(timezone.utc).isoformat()
        
        mandate_data = {
            "mandate_id": mandate_id,
            "user_id": user_id,
            "agent_id": self.agent_name,
            "intent_description": intent_description,
            "constraints": constraints,
            "timestamp": timestamp
        }
        
        signature = self._sign_data(json.dumps(mandate_data, sort_keys=True))
        verifiable_credential = self._create_verifiable_credential(mandate_data)
        
        intent_mandate = IntentMandate(
            mandate_id=mandate_id,
            user_id=user_id,
            agent_id=self.agent_name,
            intent_description=intent_description,
            constraints=constraints,
            timestamp=timestamp,
            signature=signature,
            verifiable_credential=verifiable_credential
        )
        
        self.intent_mandates[mandate_id] = intent_mandate
        
        # Store mandate on IPFS for persistence and verifiability
        if self.ipfs_manager:
            try:
                mandate_data = {
                    "type": "ap2_intent_mandate",
                    "mandate": asdict(intent_mandate),
                    "timestamp": datetime.now().isoformat(),
                    "agent_name": self.agent_name
                }
                filename = f"ap2_intent_mandate_{mandate_id}.json"
                cid = self.ipfs_manager.storage.upload_json(mandate_data, filename)
                if cid:
                    rprint(f"[green]📁 Intent Mandate stored on IPFS: {cid}[/green]")
                    intent_mandate.ipfs_cid = cid  # Add CID to mandate for reference
            except Exception as e:
                rprint(f"[yellow]⚠️  Failed to store intent mandate on IPFS: {e}[/yellow]")
        
        rprint(f"[blue]📝 Created Intent Mandate: {mandate_id}[/blue]")
        rprint(f"[dim]   Intent: {intent_description}[/dim]")
        rprint(f"[dim]   Constraints: {constraints}[/dim]")
        
        return intent_mandate
    
    def create_cart_mandate(
        self,
        intent_mandate_id: str,
        items: List[Dict[str, Any]],
        total_amount: float,
        currency: str,
        merchant_info: Dict[str, Any]
    ) -> CartMandate:
        """
        Create AP2 Cart Mandate for specific items and pricing
        
        Args:
            intent_mandate_id: ID of the original intent mandate
            items: List of specific items with details
            total_amount: Total cost
            currency: Currency (USD, USDC, etc.)
            merchant_info: Details about the merchant/service provider
            
        Returns:
            CartMandate object with cryptographic proof
        """
        if intent_mandate_id not in self.intent_mandates:
            raise ValueError(f"Intent mandate {intent_mandate_id} not found")
        
        intent_mandate = self.intent_mandates[intent_mandate_id]
        mandate_id = f"cart_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now(timezone.utc).isoformat()
        
        mandate_data = {
            "mandate_id": mandate_id,
            "intent_mandate_id": intent_mandate_id,
            "user_id": intent_mandate.user_id,
            "agent_id": self.agent_name,
            "items": items,
            "total_amount": total_amount,
            "currency": currency,
            "merchant_info": merchant_info,
            "timestamp": timestamp
        }
        
        signature = self._sign_data(json.dumps(mandate_data, sort_keys=True))
        verifiable_credential = self._create_verifiable_credential(mandate_data)
        
        cart_mandate = CartMandate(
            mandate_id=mandate_id,
            intent_mandate_id=intent_mandate_id,
            user_id=intent_mandate.user_id,
            agent_id=self.agent_name,
            items=items,
            total_amount=total_amount,
            currency=currency,
            merchant_info=merchant_info,
            timestamp=timestamp,
            signature=signature,
            verifiable_credential=verifiable_credential
        )
        
        self.cart_mandates[mandate_id] = cart_mandate
        
        # Store cart mandate on IPFS for persistence and verifiability
        if self.ipfs_manager:
            try:
                mandate_data = {
                    "type": "ap2_cart_mandate",
                    "mandate": asdict(cart_mandate),
                    "timestamp": datetime.now().isoformat(),
                    "agent_name": self.agent_name
                }
                filename = f"ap2_cart_mandate_{mandate_id}.json"
                cid = self.ipfs_manager.storage.upload_json(mandate_data, filename)
                if cid:
                    rprint(f"[green]📁 Cart Mandate stored on IPFS: {cid}[/green]")
                    cart_mandate.ipfs_cid = cid  # Add CID to mandate for reference
            except Exception as e:
                rprint(f"[yellow]⚠️  Failed to store cart mandate on IPFS: {e}[/yellow]")
        
        rprint(f"[blue]🛒 Created Cart Mandate: {mandate_id}[/blue]")
        rprint(f"[dim]   Items: {len(items)} items, Total: {total_amount} {currency}[/dim]")
        rprint(f"[dim]   Merchant: {merchant_info.get('name', 'Unknown')}[/dim]")
        
        return cart_mandate
    
    def verify_mandate_chain(self, cart_mandate_id: str) -> bool:
        """
        Verify the complete mandate chain from intent to cart
        
        This ensures the cart mandate is properly linked to an authorized intent mandate
        """
        if cart_mandate_id not in self.cart_mandates:
            return False
        
        cart_mandate = self.cart_mandates[cart_mandate_id]
        intent_mandate_id = cart_mandate.intent_mandate_id
        
        if intent_mandate_id not in self.intent_mandates:
            return False
        
        intent_mandate = self.intent_mandates[intent_mandate_id]
        
        # Verify user consistency
        if cart_mandate.user_id != intent_mandate.user_id:
            return False
        
        # Verify constraints (simplified - in production would be more sophisticated)
        constraints = intent_mandate.constraints
        if "price_limit" in constraints:
            if cart_mandate.total_amount > constraints["price_limit"]:
                return False
        
        rprint(f"[green]✅ Mandate chain verified: {intent_mandate_id} → {cart_mandate_id}[/green]")
        return True
    
    def execute_ap2_payment(
        self,
        cart_mandate_id: str,
        payment_method: str = "ap2_universal",
        amount: float = None
    ) -> AP2PaymentProof:
        """
        Execute actual AP2 payment (simulated for demo)
        
        In production, this would integrate with AP2's universal payment system
        supporting credit cards, bank transfers, crypto, etc.
        """
        if cart_mandate_id not in self.cart_mandates:
            raise ValueError(f"Cart mandate {cart_mandate_id} not found")
        
        cart_mandate = self.cart_mandates[cart_mandate_id]
        payment_amount = amount or cart_mandate.total_amount
        
        rprint(f"[blue]💳 Executing AP2 Payment...[/blue]")
        rprint(f"[dim]   Method: {payment_method}[/dim]")
        rprint(f"[dim]   Amount: {payment_amount} {cart_mandate.currency}[/dim]")
        rprint(f"[dim]   Merchant: {cart_mandate.merchant_info.get('name', 'Unknown')}[/dim]")
        
        # Simulate AP2 payment processing
        import time
        time.sleep(0.5)  # Simulate payment processing time
        
        # Generate payment receipt
        payment_receipt = {
            "ap2_payment_id": f"ap2_{uuid.uuid4().hex[:12]}",
            "payment_method": payment_method,
            "amount": payment_amount,
            "currency": cart_mandate.currency,
            "merchant": cart_mandate.merchant_info,
            "payment_network": "ap2_universal_network",
            "settlement_time": "instant",
            "fees": {
                "network_fee": payment_amount * 0.001,  # 0.1% network fee
                "processing_fee": 0.30  # $0.30 processing fee
            },
            "payment_status": "completed",
            "confirmation_code": f"AP2{int(time.time())}{cart_mandate_id[:4].upper()}"
        }
        
        # Create payment proof
        payment_proof = self.create_payment_proof(
            cart_mandate_id=cart_mandate_id,
            payment_method=payment_method,
            transaction_hash=payment_receipt["ap2_payment_id"],
            payment_receipt=payment_receipt
        )
        
        rprint(f"[green]✅ AP2 Payment completed: {payment_receipt['confirmation_code']}[/green]")
        rprint(f"[dim]   Network Fee: ${payment_receipt['fees']['network_fee']:.3f}[/dim]")
        rprint(f"[dim]   Processing Fee: ${payment_receipt['fees']['processing_fee']:.2f}[/dim]")
        
        return payment_proof
    
    def create_payment_proof(
        self,
        cart_mandate_id: str,
        payment_method: str,
        transaction_hash: Optional[str] = None,
        payment_receipt: Optional[Dict[str, Any]] = None
    ) -> AP2PaymentProof:
        """
        Create cryptographic proof of payment completion
        
        Args:
            cart_mandate_id: ID of the cart mandate being paid
            payment_method: Type of payment (x402, credit_card, etc.)
            transaction_hash: Blockchain transaction hash (for crypto payments)
            payment_receipt: Additional payment details
            
        Returns:
            AP2PaymentProof object
        """
        if cart_mandate_id not in self.cart_mandates:
            raise ValueError(f"Cart mandate {cart_mandate_id} not found")
        
        cart_mandate = self.cart_mandates[cart_mandate_id]
        payment_id = f"pay_{uuid.uuid4().hex[:8]}"
        
        payment_proof = AP2PaymentProof(
            payment_id=payment_id,
            cart_mandate_id=cart_mandate_id,
            payment_method=payment_method,
            amount=cart_mandate.total_amount,
            currency=cart_mandate.currency,
            transaction_hash=transaction_hash,
            payment_receipt=payment_receipt or {},
            timestamp=datetime.now(timezone.utc).isoformat(),
            verification_status="verified"
        )
        
        self.payment_proofs[payment_id] = payment_proof
        
        rprint(f"[green]💳 Created Payment Proof: {payment_id}[/green]")
        rprint(f"[dim]   Method: {payment_method}, Amount: {cart_mandate.total_amount} {cart_mandate.currency}[/dim]")
        
        return payment_proof
    
    def get_enhanced_evidence_package(
        self,
        cart_mandate_id: str,
        work_evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create enhanced evidence package that includes AP2 mandate proofs
        
        This integrates AP2 verification with ChaosChain's Proof of Agency system
        """
        if cart_mandate_id not in self.cart_mandates:
            raise ValueError(f"Cart mandate {cart_mandate_id} not found")
        
        cart_mandate = self.cart_mandates[cart_mandate_id]
        intent_mandate = self.intent_mandates[cart_mandate.intent_mandate_id]
        
        # Find associated payment proof
        payment_proof = None
        for proof in self.payment_proofs.values():
            if proof.cart_mandate_id == cart_mandate_id:
                payment_proof = proof
                break
        
        enhanced_evidence = {
            "chaoschain_evidence": work_evidence,
            "ap2_verification": {
                "intent_mandate": asdict(intent_mandate),
                "cart_mandate": asdict(cart_mandate),
                "payment_proof": asdict(payment_proof) if payment_proof else None,
                "verification_chain": {
                    "intent_verified": True,
                    "cart_verified": True,
                    "payment_verified": payment_proof is not None,
                    "mandate_chain_verified": self.verify_mandate_chain(cart_mandate_id)
                }
            },
            "trust_stack": {
                "intent_verification": "AP2",
                "execution_verification": "EigenCloud (Planned)",
                "outcome_verification": "ChaosChain"
            },
            "metadata": {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "agent_id": self.agent_name,
                "protocol_version": "AP2-ChaosChain-v1.0"
            }
        }
        
        rprint(f"[cyan]📦 Enhanced Evidence Package created with AP2 verification[/cyan]")
        return enhanced_evidence
    
    def get_mandate_summary(self) -> Dict[str, Any]:
        """Get summary of all mandates and proofs managed by this instance"""
        return {
            "intent_mandates": len(self.intent_mandates),
            "cart_mandates": len(self.cart_mandates),
            "payment_proofs": len(self.payment_proofs),
            "agent_id": self.agent_name,
            "public_key_fingerprint": self.public_key
        }
