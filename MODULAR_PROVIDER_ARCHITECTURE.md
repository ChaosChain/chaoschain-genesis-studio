# Modular Provider Architecture

## Overview

The SDK now has a clean, modular provider architecture that makes it easy to add new service providers for storage, compute, and other services.

## Directory Structure

```
sdk/chaoschain_sdk/
├── providers/
│   ├── storage/           # Storage providers
│   │   ├── __init__.py
│   │   ├── base.py        # Base interfaces
│   │   ├── ipfs_local.py  # Local IPFS node
│   │   ├── ipfs_pinata.py # Pinata IPFS
│   │   ├── irys.py        # Irys programmable datachain
│   │   ├── zerog_storage.py  # 0G Storage (CLI-based) ✨ NEW
│   │   └── zerog_grpc.py  # 0G Storage (gRPC, deprecated)
│   │
│   └── compute/           # Compute providers
│       ├── __init__.py
│       ├── base.py        # Base interfaces
│       └── zerog_compute.py  # 0G Compute Network ✨ NEW
│
├── compute_providers.py   # Legacy (for backwards compatibility)
└── storage_backends.py    # Legacy (for backwards compatibility)
```

## Usage

### 0G Storage (CLI-based)

```python
from chaoschain_sdk.providers.storage import ZeroGStorage

storage = ZeroGStorage(
    storage_node=os.getenv("ZEROG_STORAGE_NODE"),
    private_key=os.getenv("ZEROG_TESTNET_PRIVATE_KEY")
)

# Upload
result = storage.put(b"data")
print(f"Stored at: {result.uri}")
print(f"Root Hash: {result.metadata['root_hash']}")
print(f"TX Hash: {result.metadata['tx_hash']}")

# Download
data, metadata = storage.get(result.uri)
```

**Requirements:**
- Install 0G Storage CLI: `cargo install --git https://github.com/0glabs/0g-storage-client`
- Set `ZEROG_STORAGE_NODE` (e.g., `http://3.101.147.150:5678`)
- Set `ZEROG_TESTNET_PRIVATE_KEY`

### 0G Compute (Node.js SDK)

```python
from chaoschain_sdk.providers.compute import ZeroGInference

inference = ZeroGInference(
    private_key=os.getenv("ZEROG_TESTNET_PRIVATE_KEY"),
    evm_rpc=os.getenv("ZEROG_TESTNET_RPC_URL")
)

# Execute LLM inference
result = inference.execute_llm_inference(
    prompt="What is 2+2?",
    model="gpt-oss-120b"
)

print(f"Answer: {result.output}")
print(f"Chat ID: {result.metadata['chat_id']}")
print(f"TEE Verified: {result.metadata['verified']}")
```

**Requirements:**
- Install Node.js dependencies: `pnpm add @0glabs/0g-serving-broker @types/crypto-js crypto-js`
- Set `ZEROG_TESTNET_PRIVATE_KEY`
- Set `ZEROG_TESTNET_RPC_URL`

## Adding New Providers

### 1. Create Provider File

Create a new file in the appropriate directory:

```
providers/storage/new_provider.py
```

or

```
providers/compute/new_provider.py
```

### 2. Implement the Interface

For storage providers, implement `StorageBackend`:

```python
from .base import StorageBackend, StorageResult
from typing import Optional, Dict, Tuple

class NewStorageProvider:
    def __init__(self, **config):
        self._available = True  # Check if provider is available
    
    @property
    def provider_name(self) -> str:
        return "new-storage"
    
    @property
    def is_available(self) -> bool:
        return self._available
    
    def put(self, blob: bytes, **kwargs) -> StorageResult:
        # Upload logic
        return StorageResult(...)
    
    def get(self, uri: str) -> Tuple[bytes, Optional[Dict]]:
        # Download logic
        return data, metadata
```

For compute providers, implement `ComputeBackend`:

```python
from .base import ComputeBackend, ComputeResult

class NewComputeProvider(ComputeBackend):
    def execute_llm_inference(self, prompt: str, model: str) -> ComputeResult:
        # Inference logic
        return ComputeResult(...)
```

### 3. Export from __init__.py

Add your provider to the appropriate `__init__.py`:

```python
from .new_provider import NewStorageProvider

__all__ = [
    # ... existing exports
    'NewStorageProvider',
]
```

### 4. Use in Applications

```python
from chaoschain_sdk.providers.storage import NewStorageProvider

storage = NewStorageProvider(api_key="...")
result = storage.put(b"data")
```

## Benefits

1. **Clean Separation**: Each provider is self-contained
2. **Easy to Add**: Just implement the interface
3. **No Breaking Changes**: Legacy imports still work
4. **Pluggable**: Use only what you need
5. **Testable**: Mock providers easily
6. **Discoverable**: Clear import paths

## Migration Guide

### Old Imports

```python
from chaoschain_sdk.compute_providers import ZeroGInference
```

### New Imports (Recommended)

```python
from chaoschain_sdk.providers.compute import ZeroGInference
```

Both work! The old imports are maintained for backwards compatibility.

## Environment Variables

### 0G Storage
- `ZEROG_STORAGE_NODE`: Storage node RPC URL
- `ZEROG_TESTNET_PRIVATE_KEY`: Private key for transactions

### 0G Compute
- `ZEROG_TESTNET_PRIVATE_KEY`: Private key for inference
- `ZEROG_TESTNET_RPC_URL`: EVM RPC URL

## What's Next?

Ready to add:
- Chainlink Functions (compute)
- Morpheus Network (compute)
- Filecoin (storage)
- Arweave (storage)
- More providers as needed!

Each new provider is just a new file in `providers/storage/` or `providers/compute/`.
