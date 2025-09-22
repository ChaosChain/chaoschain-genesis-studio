# ChaosChain SDK

**Developer SDK for building agents on the ChaosChain protocol**

[![PyPI version](https://badge.fury.io/py/chaoschain-sdk.svg)](https://badge.fury.io/py/chaoschain-sdk)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The ChaosChain SDK provides everything developers need to build autonomous agents that can interact with the ChaosChain protocol. **Zero setup required** - all ERC-8004 contracts are pre-deployed and embedded, with support for process integrity verification, multi-payment methods (A2A-x402), and IPFS storage.

## Quick Start

### Installation

```bash
# Basic installation (includes all ERC-8004 contracts pre-deployed)
pip install chaoschain-sdk

# With production payment processor integrations
pip install chaoschain-sdk[payments]

# With Google AP2 support (required for intent verification)
pip install chaoschain-sdk
pip install git+https://github.com/google-agentic-commerce/AP2.git@main

# With development tools
pip install chaoschain-sdk[dev]

# Full installation (all features)
pip install chaoschain-sdk[payments,dev]
pip install git+https://github.com/google-agentic-commerce/AP2.git@main
```

> **Zero Setup**: All ERC-8004 contracts are pre-deployed on Base Sepolia, Ethereum Sepolia, and Optimism Sepolia. No deployment or configuration needed!
> 
> **Note**: Google AP2 must be installed separately as it's not available on PyPI. This is required for intent verification features.

### Basic Usage

```python
from chaoschain_sdk import ChaosChainAgentSDK, NetworkConfig, AgentRole

# Initialize your agent with full Triple-Verified Stack
# Uses pre-deployed contracts automatically - no setup needed!
sdk = ChaosChainAgentSDK(
    agent_name="MyAgent",
    agent_domain="myagent.example.com", 
    agent_role="server",  # or AgentRole.SERVER
    network="base-sepolia",  # or NetworkConfig.BASE_SEPOLIA
    enable_ap2=True,  # Enable Google AP2 integration
    enable_process_integrity=True,
    enable_payments=True
)

# 1. Create Google AP2 Intent Mandate (Layer 1: User Authorization)
intent_result = sdk.create_intent_mandate(
    user_description="Find me a good AI analysis service under $10",
    merchants=["TrustedAnalytics", "AIServices"],
    expiry_minutes=60
)

# 2. Register on ERC-8004 (Identity Layer)
agent_id, tx_hash = sdk.register_identity()
print(f"Agent registered with ID: {agent_id}")

# 3. Execute work with process integrity (Layer 2: Execution Verification)
@sdk.process_integrity.register_function
async def my_analysis_function(data: str) -> dict:
    # Your agent's work logic here
    return {"result": f"Analyzed: {data}", "confidence": 0.95}

result, proof = await sdk.execute_with_integrity_proof(
    "my_analysis_function",
    {"data": "market_data"}
)

# 4. Create AP2 Cart Mandate with JWT signing
cart_result = sdk.create_cart_mandate(
    cart_id="cart_123",
    items=[{"name": "AI Analysis", "price": 5.0}],
    total_amount=5.0,
    currency="USD"
)

# 5. Execute A2A-x402 crypto payment (Layer 3: Payment Settlement)
x402_request = sdk.create_x402_payment_request(
    cart_id="payment_cart_456",
    total_amount=5.0,
    currency="USDC",
    items=[{"name": "AI Analysis Service", "price": 5.0}]
)

# 6. Store comprehensive evidence on IPFS
evidence_cid = sdk.store_evidence({
    "intent_mandate": intent_result.intent_mandate.model_dump() if intent_result.success else None,
    "cart_mandate": cart_result.cart_mandate.model_dump() if cart_result.success else None,
    "analysis": result,
    "integrity_proof": proof.__dict__,
    "x402_request": x402_request.__dict__
})

print(f"🎉 Triple-Verified Stack complete! Evidence: {evidence_cid}")
```

## Architecture

The ChaosChain SDK implements the **Triple-Verified Stack**:

```
Layer 3: ChaosChain Adjudication     🎯 "Was outcome valuable?"
Layer 2: ChaosChain Process Integrity ⚡ "Was code executed right?"  
Layer 1: Google AP2 Intent           📝 "Did human authorize?"

ChaosChain runs 2 out of 3 verification layers!
```

##  Core Features

### ✅ ERC-8004 Registry Integration (Pre-Deployed)
- **Identity Registry**: On-chain agent registration and discovery
- **Reputation Registry**: Feedback and reputation management  
- **Validation Registry**: Peer validation and consensus
- **Zero Setup**: All contracts pre-deployed with embedded addresses

### ✅ Process Integrity Verification
- Cryptographic proof of correct code execution
- Function registration and integrity checking
- IPFS storage for verifiable evidence

### ✅ Multi-Payment Support (W3C Compliant)
- **5 Payment Methods**: Full W3C Payment Request API compliance
  - `basic-card`: **Integration template** for Stripe (requires API implementation)
  - `https://google.com/pay`: **Integration template** for Google Pay (requires merchant setup)
  - `https://apple.com/apple-pay`: **Integration template** for Apple Pay (requires certificates)
  - `https://paypal.com`: **Integration template** for PayPal (requires API implementation)
  - `https://a2a.org/x402`: **LIVE crypto payments** (real USDC on Base Sepolia)
- **Crypto Ready**: Real USDC transfers work out-of-the-box
- **Traditional Ready**: Production-ready templates (developers add API integrations)
- **Protocol Fees**: Automatic 2.5% fee collection to ChaosChain treasury

### ✅ Production-Ready Infrastructure
- **Multi-Network**: Ethereum, Base, Optimism Sepolia testnets
- **Pre-Deployed Contracts**: Real contract addresses embedded - no deployment needed
- **Secure Wallets**: Automatic wallet generation and management
- **IPFS Storage**: Pinata integration for permanent evidence storage
- **Error Handling**: Comprehensive exception handling and logging

## Supported Networks

| Network | Chain ID | Status | Contracts Pre-Deployed |
|---------|----------|--------|------------------------|
| Base Sepolia | 84532 | ✅ Active | ✅ ERC-8004 Suite (Embedded) |
| Ethereum Sepolia | 11155111 | ✅ Active | ✅ ERC-8004 Suite (Embedded) |
| Optimism Sepolia | 11155420 | ✅ Active | ✅ ERC-8004 Suite (Embedded) |

> **Ready to Use**: All contract addresses are embedded in the SDK. Just `pip install` and start building!

## Payment Methods: Real Integrations + Demo Mode

### ✅ **LIVE & WORKING (Out-of-the-Box)**
| Method | W3C Identifier | Status | Settlement |
|--------|---------------|--------|------------|
| A2A-x402 Crypto | `https://a2a.org/x402` | ✅ **LIVE** | **Real USDC Transfers on Base Sepolia** |

### 🔧 **REAL API INTEGRATIONS (Add Your Credentials)**
| Method | W3C Identifier | Status | What You Need |
|--------|---------------|--------|---------------|
| Basic Cards | `basic-card` | ✅ **REAL** Stripe API | Add `STRIPE_SECRET_KEY` |
| PayPal | `https://paypal.com` | ✅ **REAL** PayPal API | Add `PAYPAL_CLIENT_ID` + `PAYPAL_CLIENT_SECRET` |
| Google Pay | `https://google.com/pay` | ✅ **REAL** Token Validation | Add `GOOGLE_PAY_MERCHANT_ID` |
| Apple Pay | `https://apple.com/apple-pay` | ✅ **REAL** Token Validation | Add `APPLE_PAY_MERCHANT_ID` |

**Key Features:**
- **Real API Calls**: All payment methods use actual API integrations
- **Token Validation**: Google Pay and Apple Pay validate real payment tokens
- **Gateway Integration**: Google Pay and Apple Pay can process via Stripe or other gateways
- **Demo Mode**: Automatically falls back to demo mode if credentials not provided
- **Production Ready**: Add your API keys and process real payments immediately
- **Clear Feedback**: Console output shows whether using real APIs or demo mode

## 🛠️ Advanced Usage

### Process Integrity with Custom Functions

```python
# Register a function for integrity checking
@sdk.process_integrity.register_function
async def complex_analysis(params: dict) -> dict:
    # Your complex analysis logic
    result = perform_analysis(params)
    return {
        "analysis": result,
        "timestamp": datetime.now().isoformat(),
        "confidence": calculate_confidence(result)
    }

# Execute with cryptographic proof
result, integrity_proof = await sdk.execute_with_integrity_proof(
    "complex_analysis",
    {"market_data": data, "timeframe": "1d"}
)

print(f"Proof ID: {integrity_proof.proof_id}")
print(f"Code Hash: {integrity_proof.code_hash}")
print(f"IPFS CID: {integrity_proof.ipfs_cid}")
```

### Multi-Payment Method Support (W3C Compliant)

The SDK supports 5 W3C-compliant payment methods:

```python
# 1. Basic Card Payment (Visa, Mastercard, Amex, Discover)
card_payment = sdk.execute_traditional_payment(
    payment_method="basic-card",
    amount=25.99,
    currency="USD",
    payment_data={
        "cardNumber": "4111111111111111",
        "cardType": "visa",
        "expiryMonth": "12",
        "expiryYear": "2025",
        "cvv": "123"
    }
)

# 2. Google Pay
google_pay_result = sdk.execute_traditional_payment(
    payment_method="https://google.com/pay",
    amount=25.99,
    currency="USD",
    payment_data={
        "googleTransactionId": "gpay_txn_123456",
        "paymentMethodType": "CARD"
    }
)

# 3. Apple Pay
apple_pay_result = sdk.execute_traditional_payment(
    payment_method="https://apple.com/apple-pay",
    amount=25.99,
    currency="USD",
    payment_data={
        "transactionIdentifier": "apay_txn_789012",
        "paymentMethod": {
            "displayName": "Visa ••••1234",
            "network": "Visa"
        }
    }
)

# 4. PayPal
paypal_result = sdk.execute_traditional_payment(
    payment_method="https://paypal.com",
    amount=25.99,
    currency="USD",
    payment_data={
        "paypalTransactionId": "pp_txn_345678",
        "payerEmail": "user@example.com"
    }
)

# 5. A2A-x402 Crypto Payment (USDC on Base Sepolia)
x402_request = sdk.create_x402_payment_request(
    cart_id="crypto_cart_123",
    total_amount=25.99,
    currency="USDC",
    items=[{"name": "AI Analysis Service", "price": 25.99}]
)

crypto_payment = sdk.execute_x402_crypto_payment(
    payment_request=x402_request,
    payer_agent="PayerAgent",
    service_description="AI Analysis Service"
)

print(f"Crypto Payment: {crypto_payment.transaction_hash}")
print(f"Settlement Address: {crypto_payment.settlement_address}")
print(f"Protocol Fee: ${crypto_payment.protocol_fee}")

# Get all supported payment methods
supported_methods = sdk.get_supported_payment_methods()
print(f"Supported W3C Payment Methods: {supported_methods}")
# Output: ['basic-card', 'https://google.com/pay', 'https://apple.com/apple-pay', 
#          'https://paypal.com', 'https://a2a.org/x402']
```

### Evidence Package Creation

```python
# Create comprehensive evidence package
evidence_package = sdk.create_evidence_package(
    work_proof={
        "service_type": "market_analysis",
        "input_data": input_params,
        "output_data": analysis_result,
        "execution_time": execution_duration
    },
    integrity_proof=integrity_proof,
    payment_proofs=[payment_proof],
    validation_results=validation_results
)

print(f"Evidence Package ID: {evidence_package.package_id}")
print(f"IPFS CID: {evidence_package.ipfs_cid}")
```

### Validation Workflow

```python
# Request validation from another agent
validator_agent_id = 8  # On-chain ID of validator
data_hash = "0x" + hashlib.sha256(json.dumps(analysis_result).encode()).hexdigest()

validation_tx = sdk.request_validation(validator_agent_id, data_hash)
print(f"Validation requested: {validation_tx}")

# Submit feedback for another agent
feedback_tx = sdk.submit_feedback(
    agent_id=validator_agent_id,
    score=95,
    feedback="Excellent validation quality and fast response time"
)
```

## Security & Configuration

### Environment Variables

Create a `.env` file with your configuration:

```bash
# Network Configuration
NETWORK=base-sepolia
BASE_SEPOLIA_RPC_URL=https://base-sepolia.g.alchemy.com/v2/YOUR_API_KEY

# IPFS Storage (Pinata)
PINATA_JWT=your_pinata_jwt_token
PINATA_GATEWAY=https://your-gateway.mypinata.cloud

# Payment Processor Integrations (Production)
# Stripe (for basic-card payments)
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key

# Google Pay (for Google Pay payments)
GOOGLE_PAY_MERCHANT_ID=merchant.your-domain.com
GOOGLE_PAY_ENVIRONMENT=PRODUCTION

# Apple Pay (for Apple Pay payments)
APPLE_PAY_MERCHANT_ID=merchant.your-domain.com
APPLE_PAY_CERTIFICATE_PATH=/path/to/apple-pay-cert.pem

# PayPal (for PayPal payments)
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
PAYPAL_ENVIRONMENT=live

# Optional: Custom wallet file
CHAOSCHAIN_WALLET_FILE=my_agent_wallets.json
```

### Wallet Security

The SDK automatically generates and manages secure wallets:

```python
# Wallets are stored in chaoschain_wallets.json (gitignored by default)
# Each agent gets a unique wallet with private key management
sdk = ChaosChainAgentSDK(
    agent_name="MyAgent",
    agent_domain="myagent.example.com",
    agent_role=AgentRole.SERVER,
    wallet_file="custom_wallets.json"  # Optional custom file
)

print(f"Agent wallet: {sdk.wallet_address}")
print(f"Network: {sdk.network_info}")
```

##  Testing & Development

### Running Tests

```bash
# Install development dependencies
pip install chaoschain-sdk[dev]

# Run tests
pytest tests/

# Run with coverage
pytest --cov=chaoschain_sdk tests/
```

### Local Development

```bash
# Clone the repository
git clone https://github.com/ChaosChain/chaoschain
cd chaoschain/packages/sdk

# Install in development mode
pip install -e .

# Run the example
python examples/basic_agent.py
```

## API Reference

### ChaosChainAgentSDK

The main SDK class providing all functionality:

#### Constructor
```python
ChaosChainAgentSDK(
    agent_name: str,
    agent_domain: str, 
    agent_role: AgentRole | str,  # "server", "validator", "client" or enum
    network: NetworkConfig | str = "base-sepolia",  # or enum
    enable_process_integrity: bool = True,
    enable_payments: bool = True,
    enable_storage: bool = True,
    enable_ap2: bool = True,
    wallet_file: str = None,
    storage_jwt: str = None,
    storage_gateway: str = None
)
```

#### Core Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `register_identity()` | Register agent on ERC-8004 | `(agent_id, tx_hash)` |
| `execute_with_integrity_proof()` | Execute function with proof | `(result, proof)` |
| `execute_payment()` | Process A2A-x402 payment | `PaymentProof` |
| `execute_traditional_payment()` | Process traditional payment | `PaymentResponse` |
| `execute_x402_crypto_payment()` | Process crypto payment | `X402PaymentResponse` |
| `get_supported_payment_methods()` | Get W3C payment methods | `List[str]` |
| `create_intent_mandate()` | Create AP2 intent mandate | `GoogleAP2IntegrationResult` |
| `create_cart_mandate()` | Create AP2 cart mandate | `GoogleAP2IntegrationResult` |
| `store_evidence()` | Store data on IPFS | `cid` |
| `create_evidence_package()` | Create proof package | `EvidencePackage` |
| `request_validation()` | Request peer validation | `tx_hash` |

### Types

The SDK provides comprehensive type definitions:

```python
from chaoschain_sdk import (
    AgentRole,           # SERVER, VALIDATOR, CLIENT
    NetworkConfig,       # BASE_SEPOLIA, ETHEREUM_SEPOLIA, etc.
    PaymentMethod,       # BASIC_CARD, GOOGLE_PAY, A2A_X402, etc.
    IntegrityProof,      # Process integrity proof
    PaymentProof,        # Payment transaction proof
    EvidencePackage,     # Comprehensive evidence package
    AgentIdentity        # Agent identity information
)
```

##  Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- **Homepage**: [https://chaoscha.in](https://chaoscha.in)
- **Documentation**: [https://docs.chaoscha.in](https://docs.chaoscha.in)
- **GitHub**: [https://github.com/ChaosChain/chaoschain](https://github.com/ChaosChain/chaoschain)
- **PyPI**: [https://pypi.org/project/chaoschain-sdk/](https://pypi.org/project/chaoschain-sdk/)

## Support

- **Issues**: [GitHub Issues](https://github.com/ChaosChain/chaoschain/issues)
- **Discord**: [ChaosChain Community](https://discord.gg/chaoschain)
- **Email**: [hello@chaoschain.com](mailto:hello@)

---

**Building the future of trustworthy autonomous services.**