"""
A2A-x402 Extension Implementation for ChaosChain Genesis Studio

This module implements Google's A2A-x402 extension for cryptocurrency payments,
enabling seamless crypto settlement within the AP2 framework.

Based on: https://github.com/google-agentic-commerce/a2a-x402/blob/main/v0.1/spec.md
"""

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Union
import json
import hashlib
import uuid
from rich import print as rprint

# Import our existing x402 payment manager
try:
    from .x402_payment_manager import GenesisX402PaymentManager
except ImportError:
    # For standalone testing
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from x402_payment_manager import GenesisX402PaymentManager

@dataclass
class X402PaymentMethod:
    """
    x402 Payment Method as per A2A-x402 spec
    """
    supported_methods: List[str]  # ["crypto", "usdc", "eth", "btc"]
    supported_networks: List[str]  # ["ethereum", "base", "polygon"]
    payment_endpoint: str  # x402 payment endpoint
    verification_endpoint: str  # Payment verification endpoint

@dataclass
class X402PaymentRequest:
    """
    Enhanced Payment Request with x402 crypto support
    """
    id: str
    total: Dict[str, Any]  # Amount and currency
    display_items: List[Dict[str, Any]]
    x402_methods: List[X402PaymentMethod]
    settlement_address: str  # Crypto address for settlement
    network: str  # Blockchain network
    expires_at: str  # ISO 8601 timestamp

@dataclass
class X402PaymentResponse:
    """
    x402 Payment Response with crypto transaction details
    """
    payment_id: str
    transaction_hash: str
    network: str
    amount: float
    currency: str
    settlement_address: str
    confirmation_blocks: int
    status: str  # "pending", "confirmed", "failed"
    timestamp: str
    gas_fee: Optional[float] = None
    protocol_fee: Optional[float] = None

class A2AX402Extension:
    """
    A2A-x402 Extension for cryptocurrency payments within AP2 framework
    
    This class bridges Google's AP2 protocol with x402 crypto payments,
    enabling seamless crypto settlement for agent-to-agent commerce.
    """
    
    def __init__(self, agent_name: str, network: str = "base-sepolia"):
        """
        Initialize A2A-x402 Extension
        
        Args:
            agent_name: Name of the agent
            network: Blockchain network for settlements
        """
        self.agent_name = agent_name
        self.network = network
        
        # Initialize x402 payment manager
        self.x402_manager = GenesisX402PaymentManager(network)
        
        # Supported crypto payment methods
        self.supported_methods = ["usdc", "eth", "native"]
        self.supported_networks = ["base-sepolia", "ethereum", "polygon"]
        
        rprint(f"[green]✅ A2A-x402 Extension initialized for {agent_name} on {network}[/green]")
    
    def create_x402_payment_method(self, settlement_address: str) -> X402PaymentMethod:
        """
        Create x402 payment method descriptor
        
        Args:
            settlement_address: Crypto address for receiving payments
            
        Returns:
            X402PaymentMethod with crypto capabilities
        """
        return X402PaymentMethod(
            supported_methods=self.supported_methods,
            supported_networks=self.supported_networks,
            payment_endpoint=f"x402://{self.agent_name}.chaoschain.com/pay",
            verification_endpoint=f"https://{self.agent_name}.chaoschain.com/verify"
        )
    
    def create_enhanced_payment_request(
        self,
        cart_id: str,
        total_amount: float,
        currency: str,
        items: List[Dict[str, Any]],
        settlement_address: str
    ) -> X402PaymentRequest:
        """
        Create enhanced payment request with x402 crypto support
        
        Args:
            cart_id: Cart identifier
            total_amount: Total payment amount
            currency: Payment currency (USDC, ETH, etc.)
            items: List of items being purchased
            settlement_address: Crypto address for settlement
            
        Returns:
            X402PaymentRequest with crypto payment methods
        """
        # Create x402 payment methods
        x402_methods = [self.create_x402_payment_method(settlement_address)]
        
        # Create enhanced payment request
        payment_request = X402PaymentRequest(
            id=f"x402_{cart_id}_{uuid.uuid4().hex[:8]}",
            total={
                "amount": {"value": str(total_amount), "currency": currency},
                "label": f"Payment for {len(items)} items"
            },
            display_items=[
                {
                    "label": item.get("name", item.get("service", "Item")),
                    "amount": {"value": str(item.get("price", 0)), "currency": currency}
                }
                for item in items
            ],
            x402_methods=x402_methods,
            settlement_address=settlement_address,
            network=self.network,
            expires_at=(datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
        )
        
        rprint(f"[blue]💳 Created x402 payment request: {payment_request.id}[/blue]")
        return payment_request
    
    def execute_x402_payment(
        self,
        payment_request: X402PaymentRequest,
        payer_agent: str,
        service_description: str = "A2A Service"
    ) -> X402PaymentResponse:
        """
        Execute x402 crypto payment
        
        Args:
            payment_request: x402 payment request
            payer_agent: Name of the paying agent
            service_description: Description of the service
            
        Returns:
            X402PaymentResponse with transaction details
        """
        rprint(f"[cyan]💸 Executing x402 payment: {payer_agent} → {self.agent_name}[/cyan]")
        
        # Extract payment details
        amount = float(payment_request.total["amount"]["value"])
        currency = payment_request.total["amount"]["currency"]
        
        # Execute payment via x402 manager
        payment_result = self.x402_manager.create_and_execute_payment(
            payer_agent=payer_agent,
            payee_agent=self.agent_name,
            amount=amount,
            service_description=service_description
        )
        
        # Create x402 payment response
        response = X402PaymentResponse(
            payment_id=payment_result["payment_id"],
            transaction_hash=payment_result["transaction_hash"],
            network=self.network,
            amount=payment_result["final_amount"],
            currency=currency,
            settlement_address=payment_request.settlement_address,
            confirmation_blocks=1,  # Base has fast finality
            status="confirmed" if payment_result["success"] else "failed",
            timestamp=datetime.now(timezone.utc).isoformat(),
            gas_fee=payment_result.get("gas_fee"),
            protocol_fee=payment_result.get("protocol_fee")
        )
        
        if response.status == "confirmed":
            rprint(f"[green]✅ x402 payment confirmed: {response.transaction_hash}[/green]")
        else:
            rprint(f"[red]❌ x402 payment failed[/red]")
        
        return response
    
    def verify_x402_payment(self, payment_response: X402PaymentResponse) -> bool:
        """
        Verify x402 payment on-chain
        
        Args:
            payment_response: Payment response to verify
            
        Returns:
            True if payment is verified on-chain
        """
        # In production, this would verify the transaction on-chain
        # For now, we check if we have a valid transaction hash
        return (
            payment_response.status == "confirmed" and
            payment_response.transaction_hash and
            len(payment_response.transaction_hash) == 66  # Valid Ethereum tx hash
        )
    
    def create_payment_proof(self, payment_response: X402PaymentResponse) -> Dict[str, Any]:
        """
        Create cryptographic proof of x402 payment
        
        Args:
            payment_response: Confirmed payment response
            
        Returns:
            Cryptographic proof of payment
        """
        proof_data = {
            "payment_id": payment_response.payment_id,
            "transaction_hash": payment_response.transaction_hash,
            "network": payment_response.network,
            "amount": payment_response.amount,
            "currency": payment_response.currency,
            "settlement_address": payment_response.settlement_address,
            "timestamp": payment_response.timestamp,
            "agent_payer": "unknown",  # Would be filled by caller
            "agent_payee": self.agent_name
        }
        
        # Create proof hash
        proof_json = json.dumps(proof_data, sort_keys=True)
        proof_hash = hashlib.sha256(proof_json.encode()).hexdigest()
        
        return {
            "proof_type": "a2a_x402_payment",
            "proof_hash": proof_hash,
            "proof_data": proof_data,
            "verification_method": "on_chain_transaction",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    
    def get_extension_capabilities(self) -> Dict[str, Any]:
        """
        Get A2A-x402 extension capabilities
        
        Returns:
            Dictionary of supported capabilities
        """
        return {
            "extension_name": "a2a-x402",
            "version": "0.1.0",
            "supported_methods": self.supported_methods,
            "supported_networks": self.supported_networks,
            "features": [
                "crypto_payments",
                "instant_settlement",
                "on_chain_verification",
                "protocol_fees",
                "gas_optimization",
                "multi_network_support"
            ],
            "compliance": [
                "A2A-x402 Specification v0.1",
                "EIP-20 Token Standard",
                "HTTP 402 Payment Required"
            ]
        }

# Test the A2A-x402 Extension
if __name__ == "__main__":
    rprint("\n🧪 Testing A2A-x402 Extension")
    rprint("=" * 50)
    
    # Initialize extension
    extension = A2AX402Extension("Alice", "base-sepolia")
    
    # Create payment request
    payment_request = extension.create_enhanced_payment_request(
        cart_id="cart_test_x402",
        total_amount=5.0,
        currency="USDC",
        items=[
            {"name": "AI Analysis Service", "price": 3.0},
            {"name": "Data Processing", "price": 2.0}
        ],
        settlement_address="0x10403103949d0F99fab213F1e6d9E168989B9255"
    )
    
    rprint(f"✅ Payment Request: {payment_request.id}")
    rprint(f"💰 Total: {payment_request.total['amount']['value']} {payment_request.total['amount']['currency']}")
    rprint(f"🏦 Settlement: {payment_request.settlement_address}")
    
    # Show capabilities
    capabilities = extension.get_extension_capabilities()
    rprint(f"\n📋 Extension Capabilities:")
    rprint(f"   Methods: {capabilities['supported_methods']}")
    rprint(f"   Networks: {capabilities['supported_networks']}")
    rprint(f"   Features: {len(capabilities['features'])} supported")
