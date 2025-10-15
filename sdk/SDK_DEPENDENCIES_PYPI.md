# ChaosChain SDK - Dependencies & PyPI Publishing Guide

## Overview

The ChaosChain SDK is designed to be **minimal by default** with **pluggable providers**. This ensures the core SDK can be published to PyPI with minimal dependencies, while users can opt-in to specific providers as needed.

## Dependency Strategy

### ✅ Core SDK (Minimal - Always Installed)

```bash
pip install chaoschain-sdk
```

**Includes:**
- ERC-8004 Protocol (Identity/Reputation/Validation)
- x402 Payment Protocol (Coinbase official)
- Wallet Manager
- Local IPFS Storage (HTTP API only)
- Essential utilities

**Python Dependencies:**
- `web3>=6.0.0`
- `eth-account>=0.8.0`
- `x402>=0.2.1`
- `cryptography>=41.0.0`
- `pyjwt>=2.8.0`
- `requests>=2.28.0`
- `python-dotenv>=1.0.0`
- `rich>=13.0.0`

**NO heavy dependencies** (no gRPC, no protobuf, no Node.js requirements)

---

### 🔌 Pluggable Providers (Optional)

#### Storage Providers

**Pinata IPFS:**
```bash
pip install chaoschain-sdk[pinata]
```

**Irys (Arweave):**
```bash
pip install chaoschain-sdk[irys]
```

**0G Storage:**
```bash
pip install chaoschain-sdk[0g-storage]

# IMPORTANT: Also requires Node.js dependencies
npm install @0glabs/0g-ts-sdk
```

#### Compute Providers

**0G Compute:**
```bash
pip install chaoschain-sdk[0g-compute]

# IMPORTANT: Also requires Node.js dependencies
npm install @0glabs/0g-serving-broker @types/crypto-js@4.2.2 crypto-js@4.2.0
```

**Morpheus:**
```bash
pip install chaoschain-sdk[morpheus]
# Coming soon
```

**Chainlink Functions:**
```bash
pip install chaoschain-sdk[chainlink]
# Coming soon
```

#### Full Stacks

**All Storage Providers:**
```bash
pip install chaoschain-sdk[storage-all]
```

**All Compute Providers:**
```bash
pip install chaoschain-sdk[compute-all]
```

**Everything:**
```bash
pip install chaoschain-sdk[all]
```

---

## 0G Integration Architecture

### Why Node.js Dependencies?

0G provides **official SDKs in TypeScript/Node.js** only:
- `@0glabs/0g-ts-sdk` for Storage
- `@0glabs/0g-serving-broker` for Compute

Instead of reimplementing these in Python (which would be error-prone and hard to maintain), we **use the official SDKs via subprocess**:

```python
# Python wrapper
from chaoschain_sdk.providers.compute import ZeroGInference

inference = ZeroGInference(
    private_key=os.getenv("ZEROG_TESTNET_PRIVATE_KEY"),
    evm_rpc=os.getenv("ZEROG_TESTNET_RPC_URL")
)

# Internally: Calls Node.js via subprocess
result = inference.execute_llm_inference("What is 2+2?")
```

**Benefits:**
1. ✅ Always uses official, up-to-date SDKs
2. ✅ No need to reimplement complex crypto/networking logic
3. ✅ Easier to maintain (just update npm packages)
4. ✅ Users without 0G can install SDK without Node.js

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│ Python SDK (chaoschain-sdk)                                 │
│                                                              │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ providers/compute/zerog_compute.py                    │   │
│ │                                                        │   │
│ │  1. Generate Node.js script string                    │   │
│ │  2. subprocess.run(['node', '-e', script])            │   │
│ │  3. Parse JSON output                                 │   │
│ │  4. Return ComputeResult                              │   │
│ └──────────────────────────────────────────────────────┘   │
│                           │                                  │
└───────────────────────────┼──────────────────────────────────┘
                            │
                            ▼
           ┌────────────────────────────────┐
           │ Node.js Process (temporary)    │
           │                                 │
           │  const { createZGComputeNetwork│
           │  Broker } = require('@0glabs/ │
           │  0g-serving-broker');          │
           │                                 │
           │  // Execute inference          │
           │  // Print JSON result          │
           └────────────────────────────────┘
```

---

## PyPI Publishing Checklist

### 1. **Ensure No Hard Dependencies on Node.js**

✅ **Core SDK works standalone:**
```bash
pip install chaoschain-sdk
# Works immediately with local IPFS and basic features
# NO Node.js required
```

✅ **0G providers gracefully degrade:**
```python
from chaoschain_sdk.providers.compute import ZeroGInference

inference = ZeroGInference(...)
if not inference.available:
    print("0G SDK not installed, using fallback")
```

### 2. **Update pyproject.toml**

**Current setup is correct:**
- Core dependencies: minimal
- Optional dependencies: clearly marked
- 0G providers: no Python deps (just Node.js requirements in comments)

### 3. **Documentation**

Create `README.md` in SDK directory:
```markdown
# ChaosChain SDK

## Quick Start

```bash
pip install chaoschain-sdk
```

## Optional Features

### 0G Storage & Compute
```bash
# Install SDK
pip install chaoschain-sdk

# Install Node.js dependencies
npm install @0glabs/0g-ts-sdk @0glabs/0g-serving-broker
```

See [Full Documentation](./SDK_DEPENDENCIES_PYPI.md)
```

### 4. **Testing Before Publishing**

```bash
# Test minimal install
python3 -m venv test-env
source test-env/bin/activate
pip install .

# Test 0G install (with Node.js deps)
npm install @0glabs/0g-ts-sdk @0glabs/0g-serving-broker
python3 -c "from chaoschain_sdk.providers.compute import ZeroGInference; print('OK')"
```

### 5. **Publishing to PyPI**

```bash
cd sdk/

# Build distribution
python3 -m build

# Upload to TestPyPI first
python3 -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ chaoschain-sdk

# If all good, upload to PyPI
python3 -m twine upload dist/*
```

---

## Environment Variables

### Core SDK
```bash
# ERC-8004 (Required)
BASE_SEPOLIA_RPC_URL=https://sepolia.base.org
BASE_SEPOLIA_PRIVATE_KEY=0x...
```

### 0G Integration
```bash
# 0G Testnet (Optional - only if using 0G)
ZEROG_TESTNET_RPC_URL=https://evmrpc-testnet.0g.ai
ZEROG_TESTNET_PRIVATE_KEY=0x...  # Same as BASE_SEPOLIA_PRIVATE_KEY is fine
ZEROG_STORAGE_NODE=http://3.101.147.150:5678
```

---

## Dependency Summary

### Python Dependencies (Managed by pip)
- ✅ Core: 8 packages (~50MB)
- ✅ All optional: ~100MB total
- ✅ No C/C++ compilation required
- ✅ Pure Python or wheels available

### External Dependencies (User manages)
- ⚠️ Node.js (optional, only for 0G)
  - Install: https://nodejs.org/
  - Verify: `node --version`
- ⚠️ npm packages (optional, only for 0G)
  - `@0glabs/0g-ts-sdk` (Storage)
  - `@0glabs/0g-serving-broker` (Compute)

---

## Troubleshooting

### "Node.js not found"
```bash
# Install Node.js
# macOS: brew install node
# Ubuntu: apt install nodejs npm
# Windows: Download from nodejs.org

# Verify
node --version  # Should be >= 16.0.0
```

### "Cannot find module '@0glabs/0g-ts-sdk'"
```bash
# Install in project directory
cd /path/to/your/project
npm install @0glabs/0g-ts-sdk

# Or globally
npm install -g @0glabs/0g-ts-sdk
```

### "0G SDK not available"
```python
# Check if provider is available
from chaoschain_sdk.providers.compute import ZeroGInference

inference = ZeroGInference(...)
print(f"Available: {inference.available}")

# If False, install Node.js dependencies
```

---

## Comparison: Our Approach vs Alternatives

### ❌ **Bad Approach 1: Bundle Node.js in Python Package**
- Huge package size (100+ MB)
- Platform-specific wheels
- Hard to maintain

### ❌ **Bad Approach 2: Reimplement 0G SDK in Python**
- Prone to bugs
- Hard to keep in sync with official SDK
- More code to maintain

### ✅ **Our Approach: Use Official SDKs via Subprocess**
- Small Python package
- Always uses official SDKs
- Easy to maintain
- Graceful degradation

---

## Future Considerations

### When More Providers Added

Same pattern for other providers:

```python
# providers/compute/chainlink.py
class ChainlinkFunctions:
    def __init__(self):
        # Check for Chainlink CLI or SDK
        pass
```

```python
# providers/storage/filecoin.py
class FilecoinStorage:
    def __init__(self):
        # Check for Lotus CLI or SDK
        pass
```

### When 0G Releases Python SDK

If 0G ever releases an official Python SDK:
1. Add as optional dependency in `pyproject.toml`
2. Update provider to use native SDK
3. Keep subprocess approach as fallback

---

## Summary

✅ **Core SDK is PyPI-ready**
- Minimal dependencies
- No platform-specific requirements
- Works standalone

✅ **0G Integration is clean**
- Uses official SDKs (no reimplementation)
- Optional (doesn't bloat core SDK)
- Well-documented setup

✅ **Architecture is extensible**
- Easy to add new providers
- Consistent patterns
- User-friendly

**Ready to publish to PyPI! 🚀**
