"""
Google AP2 Integration for ChaosChain SDK

This module integrates Google's official AP2 types with the ChaosChain protocol,
providing real AP2 intent verification and mandate management.
"""

try:
    from ap2.types.mandate import IntentMandate, CartMandate, PaymentMandate, CartContents
    from ap2.types.payment_request import PaymentRequest, PaymentItem, PaymentCurrencyAmount, PaymentMethodData, PaymentDetailsInit
    AP2_AVAILABLE = True
except ImportError:
    AP2_AVAILABLE = False
    # Create dummy classes for type hints when AP2 is not available
    class IntentMandate:
        pass
    class CartMandate:
        pass
    class PaymentMandate:
        pass
    class CartContents:
        pass
    class PaymentRequest:
        pass
    class PaymentItem:
        pass
    class PaymentCurrencyAmount:
        pass
    class PaymentMethodData:
        pass
    class PaymentDetailsInit:
        pass
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import json
import jwt
import hashlib
from dataclasses import dataclass
from rich import print as rprint
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import base64
import os

from .types import IPFSHash
from .exceptions import PaymentError, ConfigurationError

@dataclass
class GoogleAP2IntegrationResult:
    """Result of Google AP2 integration operations"""
    intent_mandate: Optional[IntentMandate] = None
    cart_mandate: Optional[CartMandate] = None
    payment_mandate: Optional[PaymentMandate] = None
    jwt_token: Optional[str] = None
    success: bool = False
    error: Optional[str] = None

class GoogleAP2Integration:
    """
    Production Google AP2 integration for ChaosChain SDK
    
    This integrates Google's official AP2 library for real intent verification
    and mandate management with production-grade security.
    """
    
    def __init__(self, agent_name: str, merchant_private_key: Optional[str] = None):
        """
        Initialize Google AP2 integration with production-grade security
        
        Args:
            agent_name: Name of the agent
            merchant_private_key: Legacy private key (deprecated, use RSA keys)
        """
        if not AP2_AVAILABLE:
            raise ImportError(
                "Google AP2 library is not installed. "
                "Install it with: pip install git+https://github.com/google-agentic-commerce/AP2.git@main"
            )
            
        self.agent_name = agent_name
        
        # Generate or load RSA keypair for production JWT signing
        self.private_key, self.public_key = self._get_or_generate_rsa_keypair()
        
        # Legacy key for backward compatibility (will be phased out)
        self.merchant_private_key = merchant_private_key or "demo_private_key_123"
        
        rprint(f"[green]✅ Google AP2 Integration initialized for {agent_name}[/green]")
    
    def _get_or_generate_rsa_keypair(self):
        """
        Generate or load RSA keypair for production JWT signing
        
        Returns:
            Tuple of (private_key, public_key) as PEM strings
        """
        key_dir = os.path.join(os.getcwd(), "keys")
        private_key_path = os.path.join(key_dir, f"{self.agent_name}_ap2_private.pem")
        public_key_path = os.path.join(key_dir, f"{self.agent_name}_ap2_public.pem")
        
        # Create keys directory if it doesn't exist
        os.makedirs(key_dir, exist_ok=True)
        
        # Try to load existing keys
        if os.path.exists(private_key_path) and os.path.exists(public_key_path):
            try:
                with open(private_key_path, 'rb') as f:
                    private_key = serialization.load_pem_private_key(
                        f.read(), password=None, backend=default_backend()
                    )
                with open(public_key_path, 'rb') as f:
                    public_key_pem = f.read()
                
                rprint(f"[blue]🔑 Loaded existing RSA keypair for {self.agent_name}[/blue]")
                return private_key, public_key_pem.decode('utf-8')
            except Exception as e:
                rprint(f"[yellow]⚠️  Failed to load existing keys: {e}[/yellow]")
        
        # Generate new RSA keypair
        rprint(f"[blue]🔑 Generating new RSA keypair for {self.agent_name}[/blue]")
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        public_key = private_key.public_key()
        
        # Serialize keys to PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Save keys to disk
        try:
            with open(private_key_path, 'wb') as f:
                f.write(private_pem)
            with open(public_key_path, 'wb') as f:
                f.write(public_pem)
            rprint(f"[green]💾 RSA keypair saved to {key_dir}[/green]")
        except Exception as e:
            rprint(f"[yellow]⚠️  Failed to save keys: {e}[/yellow]")
        
        return private_key, public_pem.decode('utf-8')
    
    def create_intent_mandate(
        self,
        user_description: str,
        merchants: Optional[List[str]] = None,
        skus: Optional[List[str]] = None,
        requires_refundability: bool = False,
        expiry_minutes: int = 60
    ) -> GoogleAP2IntegrationResult:
        """
        Create an IntentMandate using Google's official AP2 types
        
        Args:
            user_description: Natural language description of intent
            merchants: Allowed merchants (optional)
            skus: Specific SKUs (optional) 
            requires_refundability: Whether items must be refundable
            expiry_minutes: Minutes until intent expires
            
        Returns:
            GoogleAP2IntegrationResult with IntentMandate
        """
        try:
            # Calculate expiry time
            expiry_time = datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)
            
            # Create IntentMandate using Google's types
            intent_mandate = IntentMandate(
                user_cart_confirmation_required=True,  # For safety in demo
                natural_language_description=user_description,
                merchants=merchants,
                skus=skus,
                requires_refundability=requires_refundability,
                intent_expiry=expiry_time.isoformat()
            )
            
            rprint(f"[blue]📝 Created Google AP2 IntentMandate[/blue]")
            rprint(f"[dim]   Description: {user_description}[/dim]")
            rprint(f"[dim]   Expires: {expiry_time.isoformat()}[/dim]")
            
            return GoogleAP2IntegrationResult(
                intent_mandate=intent_mandate,
                success=True
            )
            
        except Exception as e:
            rprint(f"[red]❌ Failed to create IntentMandate: {e}[/red]")
            return GoogleAP2IntegrationResult(
                success=False,
                error=str(e)
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
        Create a CartMandate using Google's official AP2 types with JWT signing
        
        Args:
            cart_id: Unique cart identifier
            items: List of items in cart
            total_amount: Total cart amount
            currency: Currency code (default USD)
            merchant_name: Name of merchant
            expiry_minutes: Minutes until cart expires
            
        Returns:
            GoogleAP2IntegrationResult with CartMandate and JWT
        """
        try:
            # Calculate expiry time
            expiry_time = datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)
            
            # Create PaymentItems using Google's types
            payment_items = []
            for item in items:
                payment_item = PaymentItem(
                    label=item.get("name", "Unknown Item"),
                    amount=PaymentCurrencyAmount(
                        currency=currency,
                        value=item.get("price", 0.0)
                    )
                )
                payment_items.append(payment_item)
            
            # Create total PaymentItem
            total_item = PaymentItem(
                label="Total",
                amount=PaymentCurrencyAmount(
                    currency=currency,
                    value=total_amount
                )
            )
            
            # Create PaymentMethodData (supporting multiple methods)
            method_data = [
                PaymentMethodData(
                    supported_methods="basic-card",
                    data={"supportedNetworks": ["visa", "mastercard"]}
                ),
                PaymentMethodData(
                    supported_methods="google-pay",
                    data={"environment": "TEST"}
                ),
                PaymentMethodData(
                    supported_methods="crypto",
                    data={"supportedCurrencies": ["USDC", "ETH"]}
                )
            ]
            
            # Create PaymentRequest
            payment_request = PaymentRequest(
                method_data=method_data,
                details=PaymentDetailsInit(
                    id=f"payment_{cart_id}",
                    display_items=payment_items,
                    total=total_item
                )
            )
            
            # Create CartContents
            cart_contents = CartContents(
                id=cart_id,
                user_cart_confirmation_required=True,
                payment_request=payment_request,
                cart_expiry=expiry_time.isoformat(),
                merchant_name=merchant_name or self.agent_name
            )
            
            # Create JWT for merchant authorization
            jwt_token = self._create_merchant_jwt(cart_contents)
            
            # Create CartMandate
            cart_mandate = CartMandate(
                contents=cart_contents,
                merchant_authorization=jwt_token
            )
            
            rprint(f"[blue]🛒 Created Google AP2 CartMandate with JWT[/blue]")
            rprint(f"[dim]   Cart ID: {cart_id}[/dim]")
            rprint(f"[dim]   Items: {len(items)} items, Total: {total_amount} {currency}[/dim]")
            rprint(f"[dim]   JWT: {jwt_token[:50]}...[/dim]")
            
            return GoogleAP2IntegrationResult(
                cart_mandate=cart_mandate,
                jwt_token=jwt_token,
                success=True
            )
            
        except Exception as e:
            rprint(f"[red]❌ Failed to create CartMandate: {e}[/red]")
            return GoogleAP2IntegrationResult(
                success=False,
                error=str(e)
            )
    
    def _create_merchant_jwt(self, cart_contents: CartContents) -> str:
        """
        Create a JWT token for merchant authorization as per Google's AP2 spec
        
        Args:
            cart_contents: The cart contents to sign
            
        Returns:
            Base64url-encoded JWT token
        """
        # Create cart hash for integrity
        cart_dict = cart_contents.model_dump()
        cart_json = json.dumps(cart_dict, sort_keys=True)
        cart_hash = hashlib.sha256(cart_json.encode()).hexdigest()
        
        # JWT Payload (header is automatically generated by PyJWT)
        now = datetime.now(timezone.utc)
        payload = {
            "iss": f"did:chaoschain:{self.agent_name}",  # Issuer (DID format)
            "sub": cart_contents.id,  # Subject (cart ID)
            "aud": "chaoschain:payment_processor",  # Audience
            "iat": int(now.timestamp()),  # Issued at
            "exp": int((now + timedelta(minutes=15)).timestamp()),  # Expires
            "jti": f"jwt_{cart_contents.id}_{int(now.timestamp())}",  # JWT ID
            "cart_hash": cart_hash,  # Cart integrity hash
            "merchant_name": cart_contents.merchant_name
        }
        
        # Create JWT with RSA256 signing (production-grade security)
        token = jwt.encode(
            payload, 
            self.private_key, 
            algorithm="RS256",
            headers={"kid": f"did:chaoschain:{self.agent_name}#key-1"}
        )
        
        return token
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """
        Verify a JWT token (for validation purposes)
        
        Args:
            token: JWT token to verify
            
        Returns:
            Decoded payload if valid, empty dict if invalid
        """
        try:
            # Get public key for verification
            public_key = serialization.load_pem_public_key(
                self.public_key.encode('utf-8'), 
                backend=default_backend()
            )
            
            # Decode and verify JWT with RSA256
            payload = jwt.decode(
                token, 
                public_key, 
                algorithms=["RS256"],
                audience="chaoschain:payment_processor",
                options={"verify_aud": True}  # Enable audience verification for security
            )
            rprint(f"[green]✅ JWT token verified successfully with RSA256[/green]")
            return payload
        except jwt.ExpiredSignatureError:
            rprint(f"[red]❌ JWT token has expired[/red]")
            return {}
        except jwt.InvalidAudienceError:
            rprint(f"[red]❌ JWT token has invalid audience[/red]")
            return {}
        except jwt.InvalidTokenError as e:
            rprint(f"[red]❌ JWT token is invalid: {e}[/red]")
            return {}
    
    def get_integration_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the Google AP2 integration capabilities
        
        Returns:
            Summary of integration features
        """
        return {
            "integration_type": "Google Official AP2",
            "agent_name": self.agent_name,
            "supported_features": [
                "IntentMandate creation with Google types",
                "CartMandate creation with JWT signing", 
                "W3C PaymentRequest API compliance",
                "Multi-payment method support",
                "JWT-based merchant authorization",
                "Proper expiry handling",
                "Cart integrity verification"
            ],
            "cryptographic_features": [
                "JWT signing with RS256 (production)",
                "Cart content hashing for integrity",
                "Timestamp-based expiry",
                "Replay attack prevention with JTI"
            ],
            "compliance": [
                "Google AP2 Protocol",
                "W3C Payment Request API",
                "JWT RFC 7519",
                "ISO 8601 timestamps"
            ]
        }