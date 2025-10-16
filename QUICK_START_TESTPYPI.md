# Quick Start: Testing ChaosChain SDK on TestPyPI

## 🚀 3-Step Process

### 1. Copy SDK to ChaosChain Repo

```bash
# Option A: If you have a separate chaoschain repo
cd /Users/sumeet/Desktop/ChaosChain_labs/chaoschain-genesis-studio
cp -r sdk/ /path/to/chaoschain-sdk-repo/
cd /path/to/chaoschain-sdk-repo

# Option B: Create standalone SDK repo
mkdir -p ~/chaoschain-sdk
cp -r sdk/* ~/chaoschain-sdk/
cd ~/chaoschain-sdk
git init
git add .
git commit -m "Initial commit: ChaosChain SDK v0.2.0"
```

### 2. Upload to TestPyPI

```bash
# Install twine (if needed)
pip install twine

# Build package
python -m build

# Upload to TestPyPI
# Get your API token from: https://test.pypi.org/manage/account/#api-tokens
python -m twine upload --repository testpypi dist/*

# When prompted:
# Username: __token__
# Password: pypi-... (your TestPyPI token)
```

### 3. Test Installation

```bash
# Create fresh virtual environment
python3 -m venv test-env
source test-env/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    chaoschain-sdk

# Test it works!
python3 << 'EOF'
from chaoschain_sdk import ChaosChainAgentSDK, NetworkConfig, AgentRole
print("✅ ChaosChain SDK imported successfully!")

# Try creating an agent
agent = ChaosChainAgentSDK(
    agent_name="TestAgent",
    agent_domain="test.example.com",
    agent_role=AgentRole.CLIENT,
    network=NetworkConfig.BASE_SEPOLIA
)
print(f"✅ Agent created: {agent.wallet_address}")
print("\n🎉 ChaosChain SDK works perfectly on TestPyPI!")
EOF
```

---

## 📦 Testing Optional Providers

### Test Pinata
```bash
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    chaoschain-sdk[pinata]

python -c "from chaoschain_sdk.providers.storage import PinataStorage; print('✅ Pinata works')"
```

### Test 0G (requires external CLI)
```bash
# Install Python package
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    chaoschain-sdk[0g]

# Install 0G CLI separately (documented in README)
# git clone https://github.com/0gfoundation/0g-storage-client.git
# cd 0g-storage-client && go build
```

### Test Phala TEE
```bash
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    chaoschain-sdk[phala-tee]

python -c "from chaoschain_sdk.providers.tee import TEEProvider; print('✅ TEE infrastructure ready')"
```

---

## ✅ If Everything Works

### Upload to Production PyPI

```bash
# Get production API token from: https://pypi.org/manage/account/#api-tokens
python -m twine upload dist/*

# When prompted:
# Username: __token__
# Password: pypi-... (your production PyPI token)
```

### Users Can Now Install

```bash
# Simple installation
pip install chaoschain-sdk

# With optional providers
pip install chaoschain-sdk[0g,pinata,phala-tee]
```

---

## 🎉 Success Metrics

**You'll know it works if:**
- ✅ TestPyPI upload succeeds
- ✅ Fresh install works
- ✅ SDK imports without errors
- ✅ Agent creation works
- ✅ Optional providers load correctly

**Then you're ready for production PyPI!** 🚀

---

## 🆘 Troubleshooting

### "Package already exists"
- Increment version in `pyproject.toml`
- Rebuild: `python -m build`
- Re-upload

### "Dependencies not found"
- Make sure `--extra-index-url https://pypi.org/simple/` is included
- TestPyPI doesn't mirror all PyPI packages

### "Import errors"
- Check Python version (requires >=3.9)
- Verify all dependencies installed
- Check for typos in import statements

---

## 📋 Full Checklist

See `SDK_PYPI_CHECKLIST.md` for comprehensive guide including:
- Pre-move verification
- Post-publication steps
- Documentation updates
- Announcement strategy
- Version management

**Your SDK is ready! Ship it!** 💪

