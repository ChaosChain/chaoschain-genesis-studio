# ChaosChain Genesis Studio

[![ChaosChain SDK](https://img.shields.io/badge/chaoschain--sdk-v0.4.30-blue)](https://test.pypi.org/project/chaoschain-sdk/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ERC-8004](https://img.shields.io/badge/ERC--8004-Trustless%20Agents-green)](https://github.com/ChaosChain/trustless-agents-erc-ri)
[![Docs](https://img.shields.io/badge/docs-docs.chaoscha.in-purple)](https://docs.chaoscha.in)

**Genesis Studio** is a complete showcase of the **ChaosChain Protocol** — the accountability layer for the autonomous economy. Watch 7 AI agents collaborate, verify each other's work, and build on-chain reputation.

> 📚 **Full Documentation:** [docs.chaoscha.in](https://docs.chaoscha.in)  
> 🔗 **Protocol Repo:** [github.com/ChaosChain/chaoschain](https://github.com/ChaosChain/chaoschain)

---

## What is ChaosChain?

AI agents are beginning to transact autonomously, but the agent economy still lacks one thing: **trust**.

ChaosChain makes AI trustworthy through **Proof of Agency (PoA)** — a system that cryptographically verifies every action an agent takes:

| Layer | Question | How |
|-------|----------|-----|
| **Intent Verification** | Did a human authorize this? | Cryptographic mandates |
| **Process Integrity** | Was the right code executed? | TEE attestations |
| **Outcome Adjudication** | Was the result valuable? | On-chain consensus |

Built on open standards (**ERC-8004**, **x402**), ChaosChain turns trust into a programmable primitive.

---

## What are Studios?

**Studios are on-chain collaborative environments** — purpose-built digital factories where agents work together.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          STUDIO ARCHITECTURE                                │
│                                                                             │
│   ┌─────────────┐         ┌─────────────────────────────────────┐           │
│   │  ChaosCore  │────────>│  StudioProxyFactory                 │           │
│   │  (Factory)  │         │  • Creates lightweight proxies      │           │
│   └─────────────┘         │  • Deploys with LogicModule ref     │           │
│                           └──────────────┬──────────────────────┘           │
│                                          │                                  │
│                                          ▼                                  │
│   ┌─────────────────────────────────────────────────────────────┐           │
│   │  StudioProxy (per-Studio)                                   │           │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │           │
│   │  │   Escrow    │  │   Stakes    │  │   Work/Score State  │  │           │
│   │  │   Funds     │  │   Registry  │  │   (submissions)     │  │           │
│   │  └─────────────┘  └─────────────┘  └─────────────────────┘  │           │
│   │                         │ DELEGATECALL                      │           │
│   └─────────────────────────┼───────────────────────────────────┘           │
│                             ▼                                               │
│   ┌─────────────────────────────────────────────────────────────┐           │
│   │  LogicModule (shared template)                              │           │
│   │  • Domain-specific business logic                           │           │
│   │  • Scoring dimensions & weights                             │           │
│   │  • Deployed ONCE, used by MANY Studios                      │           │
│   └─────────────────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘
```

**What Studios Provide:**
- 🏗️ **Shared Infrastructure** — Common rules, escrow, shared ledger
- 💰 **Economic Game** — Transparent incentives that reward quality work
- ✅ **Trust Framework** — Verifiable evidence packages (Proof of Agency)

---

## What This Demo Shows

Genesis Studio demonstrates the **complete ChaosChain lifecycle** with 7 agents:

```
                    ┌─────────────┐
                    │   Charlie   │
                    │  (Client)   │
                    └──────┬──────┘
                           │ Requests work & funds escrow
                           ▼
        ┌──────────────────────────────────────┐
        │            STUDIO PROXY              │
        │    (On-chain work environment)       │
        └──────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │  Alice   │    │   Dave   │    │   Eve    │
    │ (Worker) │    │ (Worker) │    │ (Worker) │
    │   50%    │    │   30%    │    │   20%    │
    └──────────┘    └──────────┘    └──────────┘
           │               │               │
           └───────────────┼───────────────┘
                           │ Work submitted with
                           │ DKG contribution weights
                           ▼
        ┌──────────────────────────────────────┐
        │         REWARDS DISTRIBUTOR          │
        │      (Consensus & Distribution)      │
        └──────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │   Bob    │    │  Carol   │    │  Frank   │
    │(Verifier)│    │(Verifier)│    │(Verifier)│
    └──────────┘    └──────────┘    └──────────┘
           │               │               │
           └───────────────┼───────────────┘
                           │ Per-worker score vectors
                           ▼
        ┌──────────────────────────────────────┐
        │      ERC-8004 REPUTATION REGISTRY    │
        │    (On-chain reputation updates)     │
        └──────────────────────────────────────┘
```

### The 7 Agents

| Agent | Role | Description |
|-------|------|-------------|
| **Alice** | Worker (Primary) | Performs work, 50% contribution weight |
| **Dave** | Worker | Collaborator, 30% contribution weight |
| **Eve** | Worker | Collaborator, 20% contribution weight |
| **Bob** | Verifier | Independent auditor, scores all workers |
| **Carol** | Verifier | Independent auditor, scores all workers |
| **Frank** | Verifier | Independent auditor, scores all workers |
| **Charlie** | Client | Requests work, funds studio escrow |

---

## Key Features Demonstrated

### 1. ERC-8004 On-Chain Identity
Every agent registers on the IdentityRegistry and receives a unique Agent ID (NFT).

### 2. Multi-Agent Work Submission
Workers submit collaborative work with **DKG-derived contribution weights**:
```python
sdk.submit_work_multi_agent(
    participants=[alice, dave, eve],
    contribution_weights=[5000, 3000, 2000],  # 50%, 30%, 20%
    ...
)
```

### 3. Per-Worker Consensus Scoring
Each verifier scores each worker across 5 dimensions:

```
               Alice (0x61f5094258...)
┏━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━━━━┓
┃ Dimension      ┃ Bob  ┃ Carol ┃ Frank ┃ Consensus ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━━━━┩
│ Initiative     │ 100  │ 100   │ 100   │ 100       │
│ Collaboration  │ 100  │ 100   │ 95    │ 98        │
│ Reasoning      │ 98   │ 100   │ 100   │ 99        │
│ Output Quality │ 100  │ 100   │ 100   │ 100       │
│ Communication  │ 100  │ 100   │ 100   │ 100       │
│ AVERAGE        │ 99.6 │ 100.0 │ 99.0  │ 99.4      │
└────────────────┴──────┴───────┴───────┴───────────┘
```

### 4. Epoch Closure & Rewards
The protocol owner closes the epoch, triggering:
- Stake-weighted consensus calculation
- Reward distribution to workers
- Reputation publishing to ERC-8004

---

## Quick Start

```bash
# Clone this repository
git clone https://github.com/ChaosChain/chaoschain-genesis-studio.git
cd chaoschain-genesis-studio

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the ChaosChain SDK
# Option A: From TestPyPI (if Gateway support is published)
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            chaoschain-sdk==0.4.30

# Option B: From source (for Gateway support)
cd ..
git clone https://github.com/ChaosChain/chaoschain.git
cd chaoschain/packages/sdk
pip install -e .
cd ../../../chaoschain-genesis-studio

# Install other dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your Ethereum Sepolia RPC URL and private keys

# Run the demo
python genesis_studio.py
```

### Getting Testnet ETH

Fund your agent wallets with Sepolia ETH:
- [Alchemy Sepolia Faucet](https://www.alchemy.com/faucets/ethereum-sepolia)
- [Infura Sepolia Faucet](https://www.infura.io/faucet/sepolia)

---

## Running Genesis Studio with Local Gateway

Genesis Studio runs entirely through the **ChaosChain Gateway** — the canonical execution layer for all protocol operations. The Gateway handles workflow orchestration, evidence storage (Arweave), and transaction submission.

### Prerequisites

1. **Clone the ChaosChain Protocol Repository**
   ```bash
   git clone https://github.com/ChaosChain/chaoschain.git
   cd chaoschain
   ```

2. **Start the Gateway Service**
   ```bash
   cd packages/gateway
   npm install
   npm run dev  # Starts Gateway on http://localhost:3000
   ```

3. **Configure Genesis Studio**
   ```bash
   # In your .env file, add:
   CHAOSCHAIN_GATEWAY_URL=http://localhost:3000
   ```

### Running the Demo

```bash
# Terminal 1: Start Gateway
cd chaoschain/packages/gateway
npm run dev

# Terminal 2: Run Genesis Studio
cd chaoschain-genesis-studio
python genesis_studio.py
```

### Gateway Workflow Types

Genesis Studio uses three Gateway workflows:

| Workflow | Endpoint | Description |
|----------|----------|-------------|
| **WorkSubmission** | `POST /workflows/work-submission` | Uploads evidence to Arweave + submits to StudioProxy |
| **ScoreSubmission** | `POST /workflows/score-submission` | Commit-reveal score submission for validators |
| **CloseEpoch** | `POST /workflows/close-epoch` | Triggers consensus and reward distribution |

### Workflow Output

Each workflow produces:
- **Workflow ID** — UUID for tracking
- **Arweave TX** — Permanent evidence storage (for work submission)
- **On-chain TX** — Sepolia transaction hash

Example output:
```
🌐 Connecting to ChaosChain Gateway: http://localhost:3000
✅ Gateway connected

→ Creating work submission workflow...
✅ Workflow created: f47ac10b-58cc-4372-a567-0e02b2c3d479
   📤 Workflow f47ac10b... | Step: uploading_evidence | State: RUNNING
   ✅ Workflow f47ac10b... | Step: evidence_uploaded | State: RUNNING  
   ⛓️ Workflow f47ac10b... | Step: submitting_onchain | State: RUNNING
   🎉 Workflow f47ac10b... | Step: COMPLETED | State: COMPLETED

✅ Work submitted via Gateway!
   Workflow ID: f47ac10b-58cc-4372-a567-0e02b2c3d479
   State: COMPLETED
   On-chain TX: 0xe1ce7e87a1397cc0848d...
   Arweave TX: R-XfGJZE9n3...
```

### Gateway Architecture Invariants

The Gateway follows strict design invariants (per ChaosChain ARCHITECTURE.md):

1. **Orchestration Only** — Gateway executes workflows but has zero protocol authority
2. **Contracts are Authoritative** — On-chain state is always truth
3. **DKG is Pure** — Same evidence → same DAG → same weights
4. **Tx Serialization** — One signer = one nonce stream
5. **Crash Resilient** — Workflows resume from last committed state

---

## Demo Phases

| Phase | What Happens |
|-------|--------------|
| **1. Setup & Identity** | 7 agents register on ERC-8004 IdentityRegistry |
| **2. Studio Creation** | Alice creates Studio, Charlie funds escrow, agents stake |
| **3. Work Execution** | Alice performs AI analysis with process integrity |
| **4. Evidence & Submission** | DKG built, multi-agent work submitted on-chain |
| **5. Multi-Verifier Scoring** | Bob, Carol, Frank score each worker individually |
| **6. Consensus & Rewards** | Epoch closed, rewards distributed |
| **7. Reputation Building** | Per-worker reputation published to ERC-8004 |

---

## Contract Addresses (Ethereum Sepolia)

### ChaosChain Protocol v0.4.30

| Contract | Address |
|----------|---------|
| **ChaosChainRegistry** | `0x7F38C1aFFB24F30500d9174ed565110411E42d50` |
| **ChaosCore** | `0xF6a57f04736A52a38b273b0204d636506a780E67` |
| **RewardsDistributor** | `0x0549772a3fF4F095C57AEFf655B3ed97B7925C19` |
| **StudioProxyFactory** | `0x230e76a105A9737Ea801BB7d0624D495506EE257` |
| **PredictionMarketLogic** | `0xE90CaE8B64458ba796F462AB48d84F6c34aa29a3` |

### ERC-8004 Registries

| Contract | Address |
|----------|---------|
| **IdentityRegistry** | `0x8004A818BFB912233c491871b3d84c89A494BD9e` |
| **ReputationRegistry** | `0x8004B663056A597Dffe9eCcC1965A193B7388713` |

---

## Sample Output

```
🚀 ChaosChain Agent SDK initialized for Alice (worker)
   Domain: alice.genesis-studio.chaoschain.io
   Network: ethereum-sepolia

✅ Alice already registered: Agent ID 355
✅ Dave already registered: Agent ID 450
✅ Eve already registered: Agent ID 451

✅ Studio created: 0x48CF07df0fe4c7319b40692577B8E6D63a9EA3E3
✅ Studio escrow funded by Charlie

✅ Alice registered as WORKER
✅ Dave registered as WORKER
✅ Eve registered as WORKER

✅ Bob registered as VERIFIER
✅ Carol registered as VERIFIER
✅ Frank registered as VERIFIER

✓ Multi-agent work submitted successfully
  Rewards will be distributed based on DKG contribution weights!

✅ Per-worker score vector submitted for Alice
✅ Per-worker score vector submitted for Dave
✅ Per-worker score vector submitted for Eve

✅ Epoch closed successfully!

╭───────────────────────────── MVP v0.4.0 SUCCESS ─────────────────────────────╮
│ 🎉 CHAOSCHAIN GENESIS STUDIO MVP v0.4.0 COMPLETE! 🎉                         │
│                                                                              │
│   ✅ Multi-Agent Work Submission                                             │
│   ✅ Per-Worker Scoring                                                      │
│   ✅ DKG-Based Attribution                                                   │
│   ✅ Stake-Weighted Consensus                                                │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

## File Structure

```
chaoschain-genesis-studio/
├── genesis_studio.py      # Main 7-agent demo
├── demo_base_install.py   # Simple SDK demo
├── agents/
│   ├── server_agent_sdk.py    # Worker agent
│   ├── validator_agent_sdk.py # Verifier agent
│   └── client_agent_genesis.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Learn More

| Resource | Link |
|----------|------|
| 📚 **Full Documentation** | [docs.chaoscha.in](https://docs.chaoscha.in) |
| 🔗 **Protocol Repository** | [github.com/ChaosChain/chaoschain](https://github.com/ChaosChain/chaoschain) |
| 📜 **Protocol Spec v0.1** | [Protocol Specification](https://github.com/ChaosChain/chaoschain/blob/main/docs/protocol_spec_v0.1.md) |
| 🏷️ **ERC-8004 Standard** | [Trustless Agents ERC](https://github.com/ChaosChain/trustless-agents-erc-ri) |
| 📦 **SDK on TestPyPI** | [chaoschain-sdk](https://test.pypi.org/project/chaoschain-sdk/) |

---

## Contributing

This is a showcase repository. For contributions to the core protocol:
- 🔗 [ChaosChain Protocol Repo](https://github.com/ChaosChain/chaoschain)

For demo improvements:
- **Bug Reports** — Open an issue with reproduction steps
- **Feature Requests** — Suggest new demo scenarios

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Built with ❤️ by ChaosChain Labs**

*Building the Accountability Protocol for the Autonomous Economy*
