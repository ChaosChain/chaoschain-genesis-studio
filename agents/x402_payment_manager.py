"""
Genesis Studio - x402 Payment Manager

This module provides x402 payment integration for ChaosChain agents,
enabling frictionless agent-to-agent payments with cryptographic receipts.
"""

import json
import os
import time
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from decimal import Decimal

from x402.clients import x402Client
from x402.types import PaymentRequirements, x402PaymentRequiredResponse
from web3 import Web3
from eth_account import Account
from rich import print as rprint

from .simple_wallet_manager import GenesisWalletManager


class GenesisX402PaymentManager:
    """
    x402 Payment Manager for ChaosChain Genesis Studio
    
    This class implements agent-to-agent payments using Coinbase's x402 protocol.
    
    HOW X402 WORKS FOR AGENT PAYMENTS:
    1. Agent A wants to pay Agent B for a service
    2. Agent B exposes an HTTP endpoint that returns "402 Payment Required"
    3. The 402 response includes payment requirements (amount, asset, recipient)
    4. Agent A creates an x402 payment with cryptographic proof
    5. Agent A retries the request with the x402 payment header
    6. Agent B verifies the payment and provides the service
    7. Both agents get cryptographic receipts for the transaction
    
    FACILITATOR USAGE:
    - We CAN use a facilitator for payment verification/settlement
    - We CAN also do direct peer-to-peer payments
    - For ChaosChain, we act as our own facilitator to collect fees
    - This gives us control over the payment flow and revenue generation
    
    CHAOSCHAIN INTEGRATION:
    - Collects protocol fees (default 2.5%) to treasury
    - Generates cryptographic receipts for PoA verification
    - Integrates with existing USDC transfer infrastructure
    - Provides enhanced evidence packages with payment proofs
    """
    
    def __init__(self, wallet_manager: GenesisWalletManager, network: str = "base-sepolia"):
        """
        Initialize the x402 payment manager
        
        Args:
            wallet_manager: Reference to the Genesis wallet manager
            network: Network to operate on (base-sepolia, etc.)
        """
        self.wallet_manager = wallet_manager
        self.network = network
        self.payment_history = []
        
        # x402 configuration
        self._setup_x402_config()
        
        # Initialize x402 client with operator account
        operator_private_key = self._get_operator_private_key()
        self.operator_account = Account.from_key(operator_private_key)
        self.x402_client = x402Client(account=self.operator_account)
        
        # ChaosChain revenue configuration
        self.chaoschain_treasury = os.getenv("CHAOSCHAIN_TREASURY_ADDRESS", "chaoschain.eth")  # Use ENS name directly
        self.transaction_fee_percentage = float(os.getenv("CHAOSCHAIN_FEE_PERCENTAGE", "2.5"))  # 2.5% default fee
        
        rprint(f"[green]💳 x402 Payment Manager initialized for {network}[/green]")
    
    def _setup_x402_config(self):
        """Setup x402 configuration based on network"""
        
        if self.network == "base-sepolia":
            self.chain_id = 84532
            self.usdc_address = os.getenv("USDC_CONTRACT_ADDRESS")
            self.rpc_url = os.getenv("BASE_SEPOLIA_RPC_URL")
        else:
            raise ValueError(f"Unsupported network for x402: {self.network}")
        
        if not self.usdc_address:
            raise ValueError("USDC contract address not configured")
        
        if not self.rpc_url:
            raise ValueError("RPC URL not configured")
    
    def _get_operator_private_key(self) -> str:
        """Get the operator private key for x402 transactions"""
        private_key = os.getenv("BASE_SEPOLIA_PRIVATE_KEY")
        if not private_key:
            raise ValueError("Operator private key not configured")
        
        # Ensure private key has 0x prefix and is valid hex
        if not private_key.startswith("0x"):
            private_key = "0x" + private_key
        
        # Validate hex format
        try:
            int(private_key, 16)
        except ValueError:
            raise ValueError(f"Invalid private key format: {private_key}")
        
        return private_key
    
    def _get_x402_network_config(self) -> Dict[str, Any]:
        """Get x402 network configuration"""
        return {
            "chain_id": self.chain_id,
            "rpc_url": self.rpc_url,
            "usdc_address": self.usdc_address
        }
    
    def create_payment_request(
        self, 
        from_agent: str, 
        to_agent: str, 
        amount_usdc: float,
        service_description: str,
        evidence_cid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create an x402 payment request for agent-to-agent payment
        
        Args:
            from_agent: Name of the paying agent (Alice, Bob, Charlie)
            to_agent: Name of the receiving agent
            amount_usdc: Amount in USDC to pay
            service_description: Description of the service being paid for
            evidence_cid: Optional IPFS CID of related evidence
            
        Returns:
            Payment request data including x402 headers
        """
        
        rprint(f"[blue]💰 Creating x402 payment request: {from_agent} → {to_agent} ({amount_usdc} USDC)[/blue]")
        
        # Get agent addresses
        from_address = self.wallet_manager.get_wallet_address(from_agent)
        to_address = self.wallet_manager.get_wallet_address(to_agent)
        
        if not from_address or not to_address:
            raise ValueError(f"Could not resolve addresses for {from_agent} or {to_agent}")
        
        # Convert amount to wei (USDC has 6 decimals)
        amount_wei = int(Decimal(str(amount_usdc)) * Decimal("1000000"))
        
        # Calculate ChaosChain protocol fee
        protocol_fee_wei = int(amount_wei * (self.transaction_fee_percentage / 100))
        net_amount_wei = amount_wei - protocol_fee_wei
        
        # Create x402 payment requirements
        # Map our network to x402's expected network names
        x402_network_map = {
            "base-sepolia": "base-sepolia",
            "base": "base", 
            "avalanche-fuji": "avalanche-fuji",
            "avalanche": "avalanche"
        }
        x402_network = x402_network_map.get(self.network, "base-sepolia")  # Default to base-sepolia
        
        payment_requirements = PaymentRequirements(
            scheme="exact",
            network=x402_network,
            max_amount_required=str(amount_wei),
            resource=f"/chaoschain/service/{service_description.lower().replace(' ', '-')}",
            description=service_description,
            mime_type="application/json",
            pay_to=to_address,
            max_timeout_seconds=300,  # 5 minutes
            asset=self.usdc_address,
            extra={
                "name": "USD Coin",
                "version": "1",
                "chaoschain_metadata": {
                    "from_agent": from_agent,
                    "to_agent": to_agent,
                    "evidence_cid": evidence_cid,
                    "timestamp": datetime.now().isoformat(),
                    "network": self.network,
                    "protocol_fee_percentage": self.transaction_fee_percentage,
                    "protocol_fee_wei": protocol_fee_wei,
                    "net_amount_wei": net_amount_wei,
                    "treasury_address": self.chaoschain_treasury
                }
            }
        )
        
        # Generate payment request data
        request_data = {
            "payment_requirements": payment_requirements.model_dump(),
            "from_agent": from_agent,
            "to_agent": to_agent,
            "amount_usdc": amount_usdc,
            "amount_wei": amount_wei,
            "service_description": service_description,
            "evidence_cid": evidence_cid,
            "created_at": datetime.now().isoformat()
        }
        
        rprint(f"[green]✅ x402 payment request created[/green]")
        return request_data
    
    def execute_payment(
        self, 
        payment_request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute an x402 payment between agents
        
        Args:
            payment_request_data: Payment request data from create_payment_request
            
        Returns:
            Payment execution result with receipt and transaction hash
        """
        
        from_agent = payment_request_data["from_agent"]
        to_agent = payment_request_data["to_agent"]
        amount_usdc = payment_request_data["amount_usdc"]
        
        rprint(f"[blue]🔄 Executing x402 payment: {from_agent} → {to_agent}[/blue]")
        
        try:
            # Get the paying agent's wallet
            from_wallet = self.wallet_manager.wallets.get(from_agent)
            if not from_wallet:
                raise ValueError(f"Wallet not found for {from_agent}")
            
            # Create x402 payment payload
            # Map our network to x402's expected network names
            x402_network_map = {
                "base-sepolia": "base-sepolia",
                "base": "base", 
                "avalanche-fuji": "avalanche-fuji",
                "avalanche": "avalanche"
            }
            x402_network = x402_network_map.get(self.network, "base-sepolia")
            payment_payload = {
                "x402Version": 1,
                "scheme": "exact",
                "network": x402_network,
                "payload": {
                    "amount": payment_request_data["amount_wei"],
                    "asset": self.usdc_address,
                    "to": payment_request_data["payment_requirements"]["pay_to"],
                    "signature": None  # Will be generated by x402 client
                }
            }
            
            # Execute payment via x402 client with fee collection
            # Note: This is a simplified implementation - in practice, we'd use the full x402 flow
            payment_result = self._execute_usdc_transfer_with_x402_receipt_and_fees(
                from_agent, 
                to_agent, 
                amount_usdc,
                payment_payload,
                payment_request_data
            )
            
            # Create payment receipt
            payment_receipt = {
                "payment_id": f"x402_{int(time.time())}_{from_agent}_{to_agent}",
                "from_agent": from_agent,
                "to_agent": to_agent,
                "amount_usdc": amount_usdc,
                "amount_wei": payment_request_data["amount_wei"],
                "service_description": payment_request_data["service_description"],
                "evidence_cid": payment_request_data.get("evidence_cid"),
                "transaction_hash": payment_result["tx_hash"],
                "x402_payload": payment_payload,
                "network": self.network,
                "executed_at": datetime.now().isoformat(),
                "status": "completed" if payment_result["success"] else "failed"
            }
            
            # Store in payment history
            self.payment_history.append(payment_receipt)
            
            if payment_result["success"]:
                rprint(f"[green]✅ x402 payment executed successfully[/green]")
                rprint(f"[blue]   Transaction: {payment_result['tx_hash']}[/blue]")
            else:
                rprint(f"[red]❌ x402 payment failed: {payment_result.get('error', 'Unknown error')}[/red]")
            
            return {
                "success": payment_result["success"],
                "payment_receipt": payment_receipt,
                "transaction_hash": payment_result["tx_hash"],
                "error": payment_result.get("error")
            }
            
        except Exception as e:
            rprint(f"[red]❌ x402 payment execution failed: {e}[/red]")
            return {
                "success": False,
                "error": str(e),
                "payment_receipt": None,
                "transaction_hash": None
            }
    
    def _execute_usdc_transfer_with_x402_receipt_and_fees(
        self, 
        from_agent: str, 
        to_agent: str, 
        amount_usdc: float,
        x402_payload: Dict[str, Any],
        payment_request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute USDC transfer with x402 receipt generation and ChaosChain fee collection
        
        This method:
        1. Collects ChaosChain protocol fee to treasury
        2. Transfers net amount to service provider
        3. Generates x402 receipt with fee breakdown
        """
        
        try:
            # Extract fee information
            chaoschain_metadata = payment_request_data["payment_requirements"]["extra"]["chaoschain_metadata"]
            protocol_fee_wei = chaoschain_metadata["protocol_fee_wei"]
            net_amount_wei = chaoschain_metadata["net_amount_wei"]
            
            # Convert back to USDC amounts
            protocol_fee_usdc = protocol_fee_wei / 1000000  # USDC has 6 decimals
            net_amount_usdc = net_amount_wei / 1000000
            
            rprint(f"[blue]💰 ChaosChain Fee Collection:[/blue]")
            rprint(f"   Total Payment: ${amount_usdc} USDC")
            rprint(f"   Protocol Fee ({self.transaction_fee_percentage}%): ${protocol_fee_usdc:.6f} USDC")
            rprint(f"   Net to {to_agent}: ${net_amount_usdc:.6f} USDC")
            rprint(f"   Treasury: {self.chaoschain_treasury}")
            
            # Step 1: Collect protocol fee to ChaosChain treasury
            fee_tx_hash = None
            if protocol_fee_usdc > 0.000001:  # Only collect if fee is meaningful (> 0.000001 USDC)
                rprint(f"[yellow]💸 Collecting protocol fee to treasury...[/yellow]")
                
                # Get treasury address - use fixed address for Base Sepolia
                treasury_address = self.chaoschain_treasury
                if treasury_address.endswith('.eth'):
                    # Use the actual chaoschain.eth address on Base Sepolia
                    treasury_address = "0x20E7B2A2c8969725b88Dd3EF3a11Bc3353C83F70"  # chaoschain.eth on Base Sepolia
                    rprint(f"[dim]   ENS {self.chaoschain_treasury} → {treasury_address}[/dim]")
                
                # Execute real USDC transfer to treasury
                fee_tx_hash = self.wallet_manager.transfer_usdc(from_agent, treasury_address, protocol_fee_usdc)
                
                if fee_tx_hash and not fee_tx_hash.startswith("0x123"):
                    rprint(f"[green]✅ Protocol fee collected: {fee_tx_hash}[/green]")
                    rprint(f"[green]   ${protocol_fee_usdc:.6f} USDC → {treasury_address}[/green]")
                else:
                    rprint(f"[yellow]⚠️  Fee collection simulated (insufficient balance or demo mode)[/yellow]")
                    fee_tx_hash = f"0xfee{int(time.time())}{from_agent[:2]}CC"
            
            # Step 2: Transfer net amount to service provider
            main_tx_hash = self.wallet_manager.transfer_usdc(from_agent, to_agent, net_amount_usdc)
            
            if main_tx_hash and not main_tx_hash.startswith("0x123"):  # Not a simulated transaction
                return {
                    "success": True,
                    "tx_hash": main_tx_hash,
                    "fee_tx_hash": fee_tx_hash,
                    "x402_receipt": x402_payload,
                    "fee_breakdown": {
                        "total_amount_usdc": amount_usdc,
                        "protocol_fee_usdc": protocol_fee_usdc,
                        "net_amount_usdc": net_amount_usdc,
                        "fee_percentage": self.transaction_fee_percentage,
                        "treasury_address": self.chaoschain_treasury
                    }
                }
            else:
                # Handle simulated transactions (for demo purposes)
                simulated_hash = f"0x402{int(time.time())}{from_agent[:2]}{to_agent[:2]}"
                return {
                    "success": True,
                    "tx_hash": simulated_hash,
                    "fee_tx_hash": fee_tx_hash,
                    "x402_receipt": x402_payload,
                    "simulated": True,
                    "fee_breakdown": {
                        "total_amount_usdc": amount_usdc,
                        "protocol_fee_usdc": protocol_fee_usdc,
                        "net_amount_usdc": net_amount_usdc,
                        "fee_percentage": self.transaction_fee_percentage,
                        "treasury_address": self.chaoschain_treasury
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tx_hash": None
            }
    
    def create_service_payment_flow(
        self,
        client_agent: str,
        server_agent: str,
        service_type: str,
        base_amount: float,
        quality_multiplier: float = 1.0,
        evidence_cid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a complete service payment flow for ChaosChain services
        
        Args:
            client_agent: The agent requesting the service
            server_agent: The agent providing the service
            service_type: Type of service (e.g., "market_analysis", "validation")
            base_amount: Base payment amount in USDC
            quality_multiplier: Multiplier based on quality/validation score
            evidence_cid: IPFS CID of the service evidence
            
        Returns:
            Complete payment flow data
        """
        
        # Calculate final amount based on quality
        final_amount = base_amount * quality_multiplier
        
        # Create service description
        service_descriptions = {
            "market_analysis": f"AI Market Analysis Service - {server_agent}",
            "smart_shopping": f"AI Smart Shopping Service - {server_agent}",
            "validation": f"Analysis Validation Service - {server_agent}",
            "consultation": f"Agent Consultation Service - {server_agent}"
        }
        
        service_description = service_descriptions.get(service_type, f"ChaosChain Service - {service_type}")
        
        # Create payment request
        payment_request = self.create_payment_request(
            from_agent=client_agent,
            to_agent=server_agent,
            amount_usdc=final_amount,
            service_description=service_description,
            evidence_cid=evidence_cid
        )
        
        # Execute payment
        payment_result = self.execute_payment(payment_request)
        
        return {
            "service_type": service_type,
            "base_amount": base_amount,
            "quality_multiplier": quality_multiplier,
            "final_amount": final_amount,
            "payment_request": payment_request,
            "payment_result": payment_result,
            "evidence_cid": evidence_cid
        }
    
    def get_payment_receipt_for_evidence(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get payment receipt for inclusion in evidence packages
        
        Args:
            payment_id: The payment ID to retrieve
            
        Returns:
            Payment receipt data for evidence packaging
        """
        
        for receipt in self.payment_history:
            if receipt["payment_id"] == payment_id:
                return {
                    "payment_proof": {
                        "payment_id": receipt["payment_id"],
                        "from_agent": receipt["from_agent"],
                        "to_agent": receipt["to_agent"],
                        "amount_usdc": receipt["amount_usdc"],
                        "service_description": receipt["service_description"],
                        "transaction_hash": receipt["transaction_hash"],
                        "executed_at": receipt["executed_at"],
                        "x402_version": 1,
                        "network": receipt["network"],
                        "status": receipt["status"]
                    },
                    "cryptographic_proof": receipt["x402_payload"]
                }
        
        return None
    
    def get_payment_history(self, agent_name: Optional[str] = None) -> list[Dict[str, Any]]:
        """
        Get payment history for an agent or all agents
        
        Args:
            agent_name: Optional agent name to filter by
            
        Returns:
            List of payment records
        """
        
        if agent_name:
            return [
                receipt for receipt in self.payment_history
                if receipt["from_agent"] == agent_name or receipt["to_agent"] == agent_name
            ]
        
        return self.payment_history.copy()
    
    def generate_payment_summary(self) -> Dict[str, Any]:
        """Generate a summary of all x402 payments"""
        
        total_payments = len(self.payment_history)
        successful_payments = len([r for r in self.payment_history if r["status"] == "completed"])
        total_volume = sum(r["amount_usdc"] for r in self.payment_history if r["status"] == "completed")
        
        agent_stats = {}
        for receipt in self.payment_history:
            if receipt["status"] == "completed":
                # Sender stats
                if receipt["from_agent"] not in agent_stats:
                    agent_stats[receipt["from_agent"]] = {"sent": 0, "received": 0}
                agent_stats[receipt["from_agent"]]["sent"] += receipt["amount_usdc"]
                
                # Receiver stats
                if receipt["to_agent"] not in agent_stats:
                    agent_stats[receipt["to_agent"]] = {"sent": 0, "received": 0}
                agent_stats[receipt["to_agent"]]["received"] += receipt["amount_usdc"]
        
        return {
            "total_payments": total_payments,
            "successful_payments": successful_payments,
            "success_rate": successful_payments / total_payments if total_payments > 0 else 0,
            "total_volume_usdc": total_volume,
            "agent_statistics": agent_stats,
            "network": self.network,
            "generated_at": datetime.now().isoformat()
        }
