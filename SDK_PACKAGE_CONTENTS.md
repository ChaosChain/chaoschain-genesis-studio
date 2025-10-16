# ChaosChain SDK v0.2.0 - Package Contents

## 📦 What Gets Published to PyPI

### Core Package (Always Included)
```
pip install chaoschain-sdk
```

#### File Structure:
```
chaoschain_sdk/
├── __init__.py              # Main exports
├── types.py                 # Core types (NetworkConfig, AgentRole, etc.)
├── exceptions.py            # Core exceptions
│
├── core_sdk.py              # ChaosChainAgentSDK (main entry point)
├── chaos_agent.py           # ERC-8004 implementation
├── wallet_manager.py        # Secure wallet management
├── x402_payment_manager.py  # Coinbase x402 protocol
├── x402_server.py           # x402 paywall server
├── process_integrity.py     # SHA3-256 verification
│
├── payment_manager.py       # Legacy payment manager
├── google_ap2_integration.py # Google AP2 support
├── a2a_x402_extension.py    # A2A-x402 extension
│
├── storage_backends.py      # Storage backend implementations
├── compute_providers.py     # Compute provider implementations
│
├── contracts/               # ERC-8004 contract ABIs
│   └── ERC8004.json
│
├── proto/                   # gRPC proto files (for 0G)
│   ├── __init__.py
│   ├── zerog_bridge_pb2.py
│   └── zerog_bridge_pb2_grpc.py
│
└── providers/               # Pluggable provider system
    │
    ├── storage/             # Storage providers
    │   ├── __init__.py
    │   ├── base.py          # StorageProvider protocol
    │   ├── ipfs_local.py    # Local IPFS (always available)
    │   ├── ipfs_pinata.py   # Pinata IPFS [pinata]
    │   ├── irys.py          # Arweave via Irys [irys]
    │   ├── zerog_storage.py # 0G Storage [0g-storage]
    │   └── zerog_grpc.py    # Legacy 0G gRPC
    │
    ├── compute/             # Compute providers
    │   ├── __init__.py
    │   ├── base.py          # ComputeProvider protocol
    │   └── zerog_compute.py # 0G Compute [0g-compute]
    │
    └── tee/                 # TEE providers
        ├── __init__.py
        ├── base.py          # TEEProvider protocol
        └── README.md        # TEE integration guide
```

### Package Metadata
```toml
name = "chaoschain-sdk"
version = "0.2.0"
description = "Production-ready SDK for building agents on the ChaosChain protocol"
requires-python = ">=3.9"
```

---

## 🔧 Core Dependencies (Always Installed)

```
web3>=6.0.0              # Ethereum interaction
eth-account>=0.8.0       # Account management
x402>=0.2.1              # Coinbase payment protocol
cryptography>=41.0.0     # Encryption
pyjwt>=2.8.0             # JWT tokens
requests>=2.28.0         # HTTP client
python-dotenv>=1.0.0     # Environment variables
rich>=13.0.0             # Pretty printing
```

**Total core dependencies: 8 packages**

---

## 🔌 Optional Dependencies

### Storage Providers

#### `[pinata]`
```bash
pip install chaoschain-sdk[pinata]
```
- Adds: `httpx>=0.24.0`
- Enables: Pinata IPFS storage

#### `[irys]`
```bash
pip install chaoschain-sdk[irys]
```
- Adds: `httpx>=0.24.0`
- Enables: Arweave storage via Irys

#### `[ipfs]`
```bash
pip install chaoschain-sdk[ipfs]
```
- Adds: `ipfshttpclient>=0.8.0`
- Enables: Enhanced IPFS client

#### `[0g-storage]`
```bash
pip install chaoschain-sdk[0g-storage]
```
- Adds: No Python dependencies
- **Requires external tool:** 0G Storage Go CLI
- Installation:
  ```bash
  git clone https://github.com/0gfoundation/0g-storage-client.git
  cd 0g-storage-client && go build
  export PATH=$PATH:$(pwd)
  ```

### Compute Providers

#### `[0g-compute]`
```bash
pip install chaoschain-sdk[0g-compute]
```
- Adds: No Python dependencies
- **Requires external tools:** Node.js packages
- Installation:
  ```bash
  npm install @0glabs/0g-serving-broker @types/crypto-js crypto-js
  ```

#### `[morpheus]` / `[chainlink]`
- Coming soon

### TEE Providers

#### `[phala-tee]`
```bash
pip install chaoschain-sdk[phala-tee]
```
- Adds: `dstack-sdk>=0.1.0`
- Enables: Phala Cloud CVM TEE attestation
- **Status:** Infrastructure ready, awaiting community contribution

### Convenience Bundles

#### `[0g]` - 0G Full Stack
```bash
pip install chaoschain-sdk[0g]
```
Includes: `[0g-storage, 0g-compute]`

#### `[storage-all]` - All Storage Providers
```bash
pip install chaoschain-sdk[storage-all]
```
Includes: `[pinata, irys, ipfs, 0g-storage]`

#### `[all]` - Everything
```bash
pip install chaoschain-sdk[all]
```
Includes: `[0g, morpheus, chainlink, pinata, irys, ipfs, phala-tee, payments-fiat]`

---

## 📊 Package Size

| File | Size | Description |
|------|------|-------------|
| **Wheel** | 91 KB | Binary distribution |
| **Source** | 86 KB | Source distribution |
| **Installed** | ~500 KB | Total when installed |

**Total PyPI bandwidth per install:** ~91 KB (wheel only)

---

## 🎯 What Each Component Does

### Core SDK (`core_sdk.py`)
- Main entry point: `ChaosChainAgentSDK`
- Orchestrates all components
- Provides unified API

### ERC-8004 (`chaos_agent.py`)
- Identity registration
- Reputation management
- Validation workflows
- Feedback authorization

### x402 (`x402_payment_manager.py`)
- Coinbase payment protocol
- Crypto settlements
- Payment proofs
- Multi-token support

### Wallet Manager (`wallet_manager.py`)
- Key generation
- Secure storage
- Transaction signing
- Multi-wallet support

### Process Integrity (`process_integrity.py`)
- Code hash generation
- Execution verification
- SHA3-256 proofs
- TEE attestation support

### Storage Providers (`providers/storage/`)
- Pluggable storage backends
- Unified Protocol interface
- IPFS, Pinata, Irys, 0G support

### Compute Providers (`providers/compute/`)
- Pluggable compute backends
- TEE-verified execution
- 0G Compute integration

### TEE Providers (`providers/tee/`)
- Hardware-verified identity
- CVM attestation
- Cryptographic proofs

---

## 🚀 Installation Examples

### Minimal Install (ERC-8004 + x402 only)
```bash
pip install chaoschain-sdk
```
**Size:** 91 KB + 8 dependencies
**Use case:** Basic agent identity and payments

### Standard Install (+ Pinata)
```bash
pip install chaoschain-sdk[pinata]
```
**Size:** 91 KB + 9 dependencies
**Use case:** Production agent with IPFS storage

### Power User Install (+ 0G)
```bash
pip install chaoschain-sdk[0g]
# Then install external tools separately
```
**Size:** 91 KB + 8 dependencies (Python only)
**Use case:** Advanced agent with 0G decentralized services

### Full Install (Everything)
```bash
pip install chaoschain-sdk[all]
```
**Size:** 91 KB + ~15 dependencies
**Use case:** Development, testing, maximum flexibility

---

## 📝 Version History

- **v0.2.0** (Current) - PyPI release
  - Clean provider architecture
  - TEE infrastructure
  - 0G Storage/Compute support
  - ERC-8004 v1.0 compliant

- **v0.1.2** (Previous) - Internal release
  - Initial ERC-8004 implementation
  - x402 payment support

---

## 🎉 What Makes This Package Special

✅ **Zero Friction Core**
   - `pip install` just works
   - No C compilation, no Rust, no Go required
   - Perfect for 99% of users

✅ **Pluggable Architecture**
   - Add providers as needed
   - Graceful degradation
   - Expert users can add 0G/others

✅ **Best ERC-8004 Toolkit**
   - Most complete implementation
   - Official x402 support
   - Proven in production

✅ **Community-Ready**
   - TEE provider infrastructure
   - Clear contribution guidelines
   - Modular, extensible design

**This is your moat and distribution channel.** 💪
