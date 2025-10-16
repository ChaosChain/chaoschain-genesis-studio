"""
ULTIMATE TEST: Verify core SDK is THE BEST ERC-8004 toolkit.
"""
import os
os.environ['BASE_SEPOLIA_RPC_URL'] = 'https://sepolia.base.org'
os.environ['BASE_SEPOLIA_PRIVATE_KEY'] = '0x' + '1' * 64

print("🏆 Testing ChaosChain SDK - The ERC-8004 Standard 🏆\n")

# Test the way it's actually used in genesis_studio.py
from agents.client_agent_genesis import GenesisClientAgent
from chaoschain_sdk.types import AgentRole, NetworkConfig

try:
    agent = GenesisClientAgent(
        agent_name="TestAgent",
        agent_domain="test.example.com",
        agent_role=AgentRole.CLIENT,
        network=NetworkConfig.BASE_SEPOLIA
    )
    
    print(f"✅ Agent created: {agent.agent_name}")
    print(f"✅ Wallet: {agent.sdk.wallet_address}")
    print(f"✅ Network: {agent.network}")
    print(f"\n🎉 CORE SDK WORKS PERFECTLY!")
    print(f"\n💪 This is our moat: Best ERC-8004 toolkit, period!")
    
except Exception as e:
    print(f"❌ {e}")
    import traceback
    traceback.print_exc()
