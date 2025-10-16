# Contributing a TEE Provider to ChaosChain SDK

## Welcome!

We're excited about community contributions to add TEE (Trusted Execution Environment) support! Hardware-verified agent identities are crucial for production ERC-8004 deployments.

## Why TEE Providers Matter

TEE providers enable:
- ✅ Hardware-attested key generation
- ✅ Cryptographic proof of execution
- ✅ Enhanced ERC-8004 reputation
- ✅ Production-grade security
- ✅ Verifiable agent actions

## Integration Structure

### Directory Layout

```
sdk/chaoschain_sdk/providers/tee/
├── __init__.py         # TEE provider registry
├── base.py             # TEEProvider protocol
├── phala_dstack.py     # Your implementation goes here
└── README.md           # Provider documentation
```

### Step-by-Step Integration

#### 1. **Fork & Clone**

```bash
git clone https://github.com/YOUR_USERNAME/chaoschain-genesis-studio.git
cd chaoschain-genesis-studio
git checkout -b feature/phala-tee-integration
```

#### 2. **Add Your Provider**

Create `sdk/chaoschain_sdk/providers/tee/phala_dstack.py`:

```python
"""
Phala dstack TEE Provider
Hardware-verified agent authentication using Phala Cloud CVMs.
"""

from typing import Dict, Any
from .base import TEEProvider, TEEKeypair, TEESignature

try:
    from dstack_sdk import DstackClient
except ImportError:
    raise ImportError(
        "Phala dstack TEE requires dstack-sdk.\n"
        "Install with: pip install chaoschain-sdk[phala-tee]"
    )

class PhalaDstackTEE:
    """
    Phala dstack TEE authentication provider.
    
    Provides hardware-attested key generation and signing for
    ERC-8004 agents running in Phala Cloud Confidential VMs.
    
    Example:
        ```python
        tee = PhalaDstackTEE()
        keypair = tee.generate_key()
        signature = tee.sign(b"agent action", keypair)
        ```
    """
    
    def __init__(self):
        self.client = DstackClient()
        self._provider_name = "phala-dstack"
    
    @property
    def provider_name(self) -> str:
        return self._provider_name
    
    @property
    def is_available(self) -> bool:
        """Check if running in a Phala CVM."""
        try:
            self.client.get_attestation_report()
            return True
        except:
            return False
    
    def generate_key(self, **kwargs) -> TEEKeypair:
        """Generate TEE-attested keypair."""
        # Your implementation from tee_auth.py
        ...
    
    def sign(self, message: bytes, keypair: TEEKeypair) -> TEESignature:
        """Sign with TEE attestation."""
        # Your implementation from tee_auth.py
        ...
    
    def verify_attestation(self, signature: TEESignature) -> bool:
        """Verify TEE attestation."""
        # Your implementation from tee_auth.py
        ...
    
    def get_attestation_report(self) -> Dict[str, Any]:
        """Get CVM attestation report."""
        return self.client.get_attestation_report()
```

#### 3. **Export Your Provider**

Update `sdk/chaoschain_sdk/providers/tee/__init__.py`:

```python
__all__ = [
    'TEEProvider',
    'PhalaDstackTEE',  # Add your provider
]

# Add lazy import function
def get_phala_dstack_tee():
    """Get Phala dstack TEE provider."""
    try:
        from .phala_dstack import PhalaDstackTEE
        return PhalaDstackTEE
    except ImportError:
        raise ImportError(
            "Phala dstack TEE requires dstack-sdk.\n"
            "Install with: pip install chaoschain-sdk[phala-tee]"
        )
```

#### 4. **Add Dependencies**

Already done! `pyproject.toml` includes:

```toml
[project.optional-dependencies]
phala-tee = [
    "dstack-sdk>=0.1.0",
]
```

#### 5. **Add Tests**

Create `sdk/tests/test_tee_phala.py`:

```python
import pytest
from chaoschain_sdk.providers.tee import get_phala_dstack_tee

def test_phala_tee_available():
    """Test Phala TEE provider loads."""
    PhalaTEE = get_phala_dstack_tee()
    assert PhalaTEE is not None

def test_phala_tee_key_generation():
    """Test TEE key generation."""
    PhalaTEE = get_phala_dstack_tee()
    tee = PhalaTEE()
    
    if not tee.is_available:
        pytest.skip("Not running in Phala CVM")
    
    keypair = tee.generate_key()
    assert keypair.public_key is not None
    assert keypair.attestation is not None

# Add more tests...
```

#### 6. **Update Documentation**

Add usage example to `sdk/README.md`:

```markdown
### TEE-Verified Agents (Phala Cloud)

```python
from chaoschain_sdk import ChaosChainAgentSDK
from chaoschain_sdk.providers.tee import get_phala_dstack_tee

# Initialize TEE provider
PhalaTEE = get_phala_dstack_tee()
tee = PhalaTEE()

# Generate TEE-attested keys
keypair = tee.generate_key()

# Create agent with TEE signing
agent = ChaosChainAgentSDK(
    agent_name="SecureAgent",
    network="base-sepolia",
    tee_provider=tee,
    tee_keypair=keypair
)

# All agent actions now include TEE attestations!
```

```

#### 7. **Submit PR**

```bash
git add sdk/chaoschain_sdk/providers/tee/phala_dstack.py
git add sdk/tests/test_tee_phala.py
git add sdk/README.md
git commit -m "feat: Add Phala dstack TEE provider for hardware-verified agents"
git push origin feature/phala-tee-integration
```

Open a PR at: https://github.com/ChaosChain/chaoschain-genesis-studio/pulls

## Integration Points with ERC-8004

Your TEE provider will integrate at these levels:

### 1. **Agent Registration**
```python
# Submit TEE attestation with on-chain identity
agent_id, tx_hash = agent.register_identity(
    tee_attestation=tee.get_attestation_report()
)
```

### 2. **Action Signing**
```python
# Every agent action includes TEE proof
signature = tee.sign(action_data, keypair)
# signature.attestation includes CVM measurements
```

### 3. **Validation**
```python
# Validators verify TEE attestations
is_valid = tee.verify_attestation(signature)
# Check CVM measurements, platform config, etc.
```

### 4. **Reputation**
```python
# TEE-verified actions build stronger reputation
# ERC-8004 contract tracks TEE vs non-TEE actions
```

## Testing Your Integration

### Local Testing

```bash
# Install dev dependencies
pip install -e "sdk[dev,phala-tee]"

# Run tests
pytest sdk/tests/test_tee_phala.py
```

### CVM Testing

Deploy to Phala Cloud and run:

```bash
python3 genesis_studio.py --tee-provider phala-dstack
```

## Benefits of Contributing

- ✅ Your code gets production use
- ✅ SDK becomes best TEE-enabled ERC-8004 toolkit
- ✅ Community recognition
- ✅ Shape the standard for TEE-verified agents

## Questions?

Open an issue or reach out:
- GitHub Issues: https://github.com/ChaosChain/chaoschain-genesis-studio/issues
- Email: sumeet.chougule@nethermind.io

We're here to help! 🚀
