"""
ChaosChain SDK - Developer toolkit for building agents on the ChaosChain protocol.

The ChaosChain SDK provides developers with everything needed to build autonomous agents
that can interact with the ChaosChain protocol, including:

- ERC-8004 identity, reputation, and validation registries
- AP2 intent verification with Google's official library
- A2A-x402 extension for crypto payments  
- Process integrity verification with cryptographic proofs
- Multi-payment method support (W3C compliant)
- IPFS storage for verifiable evidence
- Production-ready wallet management

Example:
    ```python
    from chaoschain_sdk import ChaosChainAgentSDK
    
    # Initialize your agent
    agent = ChaosChainAgentSDK(
        agent_name="MyAgent",
        agent_domain="myagent.example.com",
        agent_role="server",
        network="base-sepolia"
    )
    
    # Register on ERC-8004
    agent_id, tx_hash = agent.register_identity()
    
    # Execute work with process integrity
    result = agent.execute_with_integrity_proof("my_function", {"param": "value"})
    ```
"""

__version__ = "0.1.0"
__author__ = "ChaosChain"
__email__ = "sumeet.chougule@nethermind.io"

# Core SDK exports
from .core_sdk import ChaosChainAgentSDK
from .chaos_agent import ChaosAgent
from .wallet_manager import WalletManager
from .storage_manager import StorageManager
from .payment_manager import PaymentManager
from .process_integrity import ProcessIntegrityVerifier
from .google_ap2_integration import GoogleAP2Integration, GoogleAP2IntegrationResult
from .a2a_x402_extension import A2AX402Extension
from .exceptions import (
    ChaosChainSDKError,
    AgentRegistrationError,
    PaymentError,
    StorageError,
    IntegrityVerificationError,
)

# Type exports for developers
from .types import (
    AgentRole,
    NetworkConfig,
    PaymentMethod,
    IntegrityProof,
    ValidationResult,
)

__all__ = [
    # Core classes
    "ChaosChainAgentSDK",
    "ChaosAgent", 
    "WalletManager",
    "StorageManager",
    "PaymentManager",
    "ProcessIntegrityVerifier",
    "GoogleAP2Integration",
    "GoogleAP2IntegrationResult",
    "A2AX402Extension",
    
    # Exceptions
    "ChaosChainSDKError",
    "AgentRegistrationError", 
    "PaymentError",
    "StorageError",
    "IntegrityVerificationError",
    
    # Types
    "AgentRole",
    "NetworkConfig", 
    "PaymentMethod",
    "IntegrityProof",
    "ValidationResult",
    
    # Metadata
    "__version__",
    "__author__",
    "__email__",
]
