#!/usr/bin/env python3
"""
ChaosChain SDK - BASE INSTALL DEMO
===================================

What this demonstrates:
- ✅ ERC-8004 v1.0 agent identity (MAINNET + Testnet!)
- ✅ x402 v2.0 payment protocol (Coinbase official)
- ✅ x402 Paywall Server (monetize your agent!)
- ✅ Local IPFS storage (no external services)
- ✅ Process integrity verification
- ✅ Wallet creation & management

Requirements:
    pip install chaoschain-sdk

Optional (not required for this demo):
    - Google AP2 (for intent verification)
    - 0G Storage/Compute (for decentralized services)
    - Pinata/Irys (for cloud storage)

This demo shows the CORE functionality that works immediately
after installing the base SDK!
"""

import os
import sys
import warnings
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from datetime import datetime
from dotenv import load_dotenv

# Load .env file FIRST (before any SDK imports)
load_dotenv()

# Suppress Web3.py event parsing warnings (harmless ABI mismatches)
warnings.filterwarnings('ignore', message='.*MismatchedABI.*')
warnings.filterwarnings('ignore', message='.*encountered the following error during processing.*')

console = Console()


def print_header():
    """Print demo header."""
    header = Panel.fit(
        "\n[bold cyan]CHAOSCHAIN SDK - BASE INSTALL DEMO[/bold cyan]\n\n"
        "[yellow]What works out-of-the-box:[/yellow]\n"
        "  ✅ ERC-8004 v1.0 (Identity & Reputation - MAINNET!)\n"
        "  ✅ x402 v2.0 Payment Protocol (Coinbase)\n"
        "  ✅ x402 Paywall Server (monetize services)\n"
        "  ✅ Local IPFS Storage\n"
        "  ✅ Process Integrity Verification\n"
        "  ✅ Wallet Management\n\n"
        "[dim]No external services required![/dim]\n",
        title="🏆 Genesis Studio - Base SDK",
        border_style="cyan"
    )
    console.print(header)


def demo_1_wallet_creation():
    """Demo 1: Create and manage wallets."""
    console.print("\n[bold]📋 Demo 1: Wallet Creation & Management[/bold]")
    console.print("=" * 80)
    
    from chaoschain_sdk import ChaosChainAgentSDK, NetworkConfig
    from chaoschain_sdk.types import AgentRole
    
    # Create SDK instance (auto-creates wallet)
    console.print("🔧 Creating ChaosChain Agent SDK...")
    sdk = ChaosChainAgentSDK(
        agent_name="DemoAgent",
        agent_domain="demo.chaoschain.io",
        agent_role=AgentRole.WORKER,  # Use WORKER (SERVER is deprecated)
        network=NetworkConfig.BASE_SEPOLIA,
        enable_process_integrity=False,  # Keep it simple for demo 1
        enable_ap2=False  # Disable AP2 for base demo
    )
    
    console.print(f"✅ Wallet created!")
    console.print(f"   Address: [green]{sdk.wallet_address}[/green]")
    console.print(f"   Network: [cyan]Base Sepolia[/cyan]")
    
    # Show wallet info table
    table = Table(title="Wallet Details")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Address", sdk.wallet_address)
    table.add_row("Network", "Base Sepolia (Chain ID: 84532)")
    
    # Get balance from wallet manager
    try:
        balance = sdk.wallet_manager.w3.eth.get_balance(sdk.wallet_address)
        balance_eth = sdk.wallet_manager.w3.from_wei(balance, 'ether')
        table.add_row("Balance", f"{balance_eth:.4f} ETH")
    except Exception as e:
        table.add_row("Balance", f"Unable to fetch ({e})")
    
    console.print(table)
    
    return sdk


def demo_2_erc8004_identity(sdk):
    """Demo 2: ERC-8004 identity registration."""
    console.print("\n[bold]📋 Demo 2: ERC-8004 Identity Registration[/bold]")
    console.print("=" * 80)
    
    console.print("\n[dim]ERC-8004 is now available on MAINNET and multiple testnets![/dim]")
    console.print("[dim]Networks: Ethereum Mainnet, Sepolia, Base, Optimism, Linea, Hedera, BSC, Mode[/dim]\n")
    
    console.print("🔧 Registering agent on ERC-8004 IdentityRegistry...")
    
    try:
        # Register agent identity (uses SDK's register_identity method)
        agent_id, tx_hash = sdk.register_identity()
        
        console.print(f"✅ Agent registered!")
        console.print(f"   Transaction: [green]{tx_hash}[/green]")
        console.print(f"   Agent ID: [green]{agent_id}[/green]")
        console.print(f"   View: [cyan]https://8004scan.io/agents/{sdk.wallet_address}[/cyan]")
        
        return agent_id
        
    except Exception as e:
        error_str = str(e).lower()
        if "insufficient funds" in error_str or "balance 0" in error_str:
            console.print("⚠️  Wallet needs testnet ETH for gas fees")
            console.print(f"   Wallet: [cyan]{sdk.wallet_address}[/cyan]")
            console.print(f"   Balance: [yellow]0.0000 ETH[/yellow]")
        elif "already registered" in error_str or "revert" in error_str:
            console.print("✅ Agent already registered!")
            console.print(f"   Wallet: [cyan]{sdk.wallet_address}[/cyan]")
            # Try to get the existing agent ID
            try:
                existing_id = sdk.chaos_agent.get_agent_id()
                if existing_id:
                    console.print(f"   Agent ID: [green]{existing_id}[/green]")
                    return existing_id
            except:
                pass
        else:
            console.print(f"⚠️  Registration error: {e}")
        
        console.print("\n[bold]💰 To register on-chain:[/bold]")
        console.print("   1. Get testnet ETH: [cyan]https://docs.base.org/base-chain/tools/network-faucets[/cyan]")
        console.print(f"   2. Send to: [green]{sdk.wallet_address}[/green]")
        console.print("   3. Run this demo again")
        return None


def demo_2b_mainnet_option():
    """Demo 2b: Show mainnet registration option."""
    console.print("\n[bold]📋 Demo 2b: ERC-8004 Mainnet Registration (Production)[/bold]")
    console.print("=" * 80)
    
    console.print("\n[yellow]For PRODUCTION agents, register on Ethereum Mainnet:[/yellow]\n")
    
    code_example = """
from chaoschain_sdk import ChaosChainAgentSDK, NetworkConfig

# Production mainnet registration (~$2-5 gas)
sdk = ChaosChainAgentSDK(
    agent_name="MyProductionAgent",
    agent_domain="myagent.com",
    network=NetworkConfig.ETHEREUM_MAINNET,  # 👈 MAINNET
    private_key="0x..."  # Your mainnet key
)

agent_id, tx = sdk.register_identity()
print(f"✅ Agent #{agent_id} on Ethereum Mainnet!")
print(f"🔗 https://etherscan.io/tx/{tx}")
print(f"📊 https://8004scan.io/agents/mainnet/{agent_id}")
"""
    
    console.print(Panel(code_example, title="Mainnet Registration Example", border_style="green"))
    
    # Show mainnet contract addresses
    table = Table(title="ERC-8004 Mainnet Contracts")
    table.add_column("Contract", style="cyan")
    table.add_column("Address", style="green")
    table.add_row("IdentityRegistry", "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432")
    table.add_row("ReputationRegistry", "0x8004BAa17C55a88189AE136b182e5fdA19dE9b63")
    console.print(table)


def demo_3_storage(sdk):
    """Demo 3: Local IPFS storage."""
    console.print("\n[bold]📋 Demo 3: Local IPFS Storage[/bold]")
    console.print("=" * 80)
    
    console.print("🔧 Testing local IPFS storage...")
    
    # Create test data
    test_data = {
        "message": "Hello from ChaosChain SDK!",
        "timestamp": datetime.now().isoformat(),
        "demo": "base_install"
    }
    
    try:
        # Store data
        console.print("📤 Storing data to local IPFS...")
        import json
        result = sdk.storage_manager.put(json.dumps(test_data).encode())
        
        if result.success:
            console.print(f"✅ Data stored!")
            console.print(f"   URI: [green]{result.uri}[/green]")
            
            # Retrieve data
            console.print("📥 Retrieving data from local IPFS...")
            retrieved = sdk.storage_manager.get(result.uri)
            
            if retrieved:
                console.print("✅ Data retrieved successfully!")
            else:
                console.print("⚠️  Could not retrieve data")
        else:
            console.print(f"⚠️  Storage failed: {result.error}")
            
    except Exception as e:
        console.print(f"⚠️  Local IPFS not running: {e}")
        console.print("   To enable: install IPFS Desktop or run `ipfs daemon`")
        console.print("   Download: https://docs.ipfs.tech/install/")


def demo_4_process_integrity():
    """Demo 4: Process integrity verification."""
    console.print("\n[bold]📋 Demo 4: Process Integrity Verification[/bold]")
    console.print("=" * 80)
    
    from chaoschain_sdk import ChaosChainAgentSDK, NetworkConfig
    from chaoschain_sdk.types import AgentRole
    
    console.print("🔧 Creating SDK with process integrity enabled...")
    
    sdk = ChaosChainAgentSDK(
        agent_name="IntegrityDemo",
        agent_domain="integrity.chaoschain.io",
        agent_role=AgentRole.WORKER,
        network=NetworkConfig.BASE_SEPOLIA,
        enable_process_integrity=True,  # Enable process integrity
        enable_ap2=False  # Disable AP2 for base demo
    )
    
    console.print("✅ Process integrity verifier initialized!")
    console.print(f"   Agent: [cyan]{sdk.agent_name}[/cyan]")
    console.print(f"   Verifier: [green]Local ChaosChain Process Integrity[/green]")
    
    console.print("\n[dim]Note: Process integrity generates cryptographic proofs for function executions[/dim]")
    console.print("[dim]      This ensures transparency and verifiability of AI agent operations[/dim]")


def demo_5_x402_payments():
    """Demo 5: x402 v2.0 payment protocol."""
    console.print("\n[bold]📋 Demo 5: x402 v2.0 Payment Protocol (Coinbase)[/bold]")
    console.print("=" * 80)
    
    console.print("\n[yellow]x402 v2.0 - Coinbase's Official HTTP 402 Payment Protocol[/yellow]\n")
    
    # Show x402 v2.0 features
    console.print("[bold]x402 v2.0 Features:[/bold]")
    console.print("   • Direct agent-to-agent payments")
    console.print("   • EIP-3009 signed transfers (gasless for payer)")
    console.print("   • HTTP 402 Payment Required response")
    console.print("   • Facilitator-based settlement")
    console.print("   • USDC support on Base, Ethereum, Optimism")
    
    # Show code example
    code_example = """
from chaoschain_sdk import ChaosChainAgentSDK, NetworkConfig

# SDK includes x402 payment manager automatically
sdk = ChaosChainAgentSDK(
    agent_name="PaymentAgent",
    agent_domain="payment.example.com",
    network=NetworkConfig.BASE_SEPOLIA,
    private_key="0x..."  # Required for signing payments
)

# Execute agent-to-agent payment
result = sdk.execute_x402_payment(
    to_agent="ServiceProvider",
    amount_usdc=1.50,
    service_description="AI Analysis Service"
)

if result["success"]:
    print(f"✅ Payment TX: {result['main_transaction_hash']}")
    print(f"   x402 Header: {result['x402_payment_header'][:30]}...")
"""
    
    console.print(Panel(code_example, title="x402 Payment Example", border_style="cyan"))
    
    console.print("\n[dim]Note: x402 requires a funded wallet with USDC on Base Sepolia[/dim]")
    console.print("[dim]      Get test USDC: https://faucet.circle.com/[/dim]")
    
    return None


def demo_6_x402_paywall_server():
    """Demo 6: x402 Paywall Server - Monetize your AI agent!"""
    console.print("\n[bold]📋 Demo 6: x402 Paywall Server (Monetize Your Agent!)[/bold]")
    console.print("=" * 80)
    
    console.print("\n[yellow]Turn any AI agent into a paid service with HTTP 402![/yellow]\n")
    
    # Check if X402PaywallServer is available
    try:
        from chaoschain_sdk import X402PaywallServer
        console.print("✅ X402PaywallServer is available!\n")
    except ImportError:
        console.print("⚠️  X402PaywallServer requires Flask: pip install flask\n")
    
    code_example = """
from chaoschain_sdk import X402PaywallServer, X402PaymentManager

# Create paywall server
server = X402PaywallServer(
    agent_name="MyAIService",
    payment_manager=payments
)

# Any function can require payment!
@server.require_payment(amount=1.00, description="Generate Image")
def generate_image(request_data):
    prompt = request_data.get("prompt", "")
    # Your AI logic here...
    return {"image_url": "https://...", "prompt": prompt}

@server.require_payment(amount=0.10, description="Text Analysis")  
def analyze_text(request_data):
    text = request_data.get("text", "")
    # Your AI logic here...
    return {"sentiment": "positive", "confidence": 0.95}

# Start the server
server.run(host="0.0.0.0", port=8402)

# Clients access: GET http://localhost:8402/chaoschain/service/generate_image
# Response: 402 Payment Required (with x402 payment instructions)
"""
    
    console.print(Panel(code_example, title="Paywall Server Example", border_style="cyan"))
    
    # Show x402 flow
    console.print("\n[bold]x402 Payment Flow:[/bold]")
    flow_table = Table(show_header=False, box=None)
    flow_table.add_column("Step", style="cyan")
    flow_table.add_column("Description")
    flow_table.add_row("1.", "Client requests service → GET /chaoschain/service/generate_image")
    flow_table.add_row("2.", "Server returns 402 Payment Required with payment instructions")
    flow_table.add_row("3.", "Client creates EIP-3009 signed payment")
    flow_table.add_row("4.", "Client retries with X-PAYMENT header")
    flow_table.add_row("5.", "Server verifies payment via facilitator")
    flow_table.add_row("6.", "Server settles payment on-chain")
    flow_table.add_row("7.", "Server returns service result!")
    console.print(flow_table)


def print_summary():
    """Print demo summary."""
    console.print("\n" + "=" * 80)
    console.print("[bold green]🎉 Base Install Demo Complete![/bold green]\n")
    
    summary_table = Table(title="What You Can Do with Base Install")
    summary_table.add_column("Feature", style="cyan")
    summary_table.add_column("Status", style="green")
    summary_table.add_column("Requirements")
    
    summary_table.add_row(
        "ERC-8004 Identity (Mainnet!)",
        "✅ Ready",
        "ETH for gas (~$2-5)"
    )
    summary_table.add_row(
        "ERC-8004 Identity (Testnet)",
        "✅ Ready",
        "Testnet ETH"
    )
    summary_table.add_row(
        "x402 v2.0 Payments",
        "✅ Ready",
        "USDC on Base"
    )
    summary_table.add_row(
        "x402 Paywall Server",
        "✅ Ready",
        "Flask (pip install flask)"
    )
    summary_table.add_row(
        "Local IPFS Storage",
        "✅ Ready",
        "IPFS daemon (optional)"
    )
    summary_table.add_row(
        "Process Integrity",
        "✅ Ready",
        "None"
    )
    summary_table.add_row(
        "Wallet Management",
        "✅ Ready",
        "None"
    )
    
    console.print(summary_table)
    
    console.print("\n[bold]🚀 Next Steps:[/bold]")
    console.print("  1. [bold]For Production:[/bold] Register on Ethereum Mainnet (NetworkConfig.ETHEREUM_MAINNET)")
    console.print("  2. [bold]For Testing:[/bold] Get testnet ETH: [cyan]https://docs.base.org/base-chain/tools/network-faucets[/cyan]")
    console.print("  3. [bold]Monetize:[/bold] Use X402PaywallServer to accept payments for your agent!")
    console.print("  4. [bold]Explore optional integrations:[/bold]")
    console.print("     • [yellow]0G Storage/Compute:[/yellow] pip install chaoschain-sdk[0g]")
    console.print("     • [yellow]Cloud Storage:[/yellow] pip install chaoschain-sdk[pinata]")
    console.print("     • [yellow]Google AP2:[/yellow] pip install git+https://github.com/google-agentic-commerce/AP2.git@main")
    console.print()
    console.print("[dim]📖 Full documentation: https://docs.chaoscha.in[/dim]")
    console.print("[dim]📊 View agents: https://8004scan.io[/dim]")
    console.print()


def main():
    """Run the base install demo."""
    try:
        print_header()
        
        # Demo 1: Wallet
        sdk = demo_1_wallet_creation()
        
        # Demo 2: ERC-8004 (Testnet)
        agent_id = demo_2_erc8004_identity(sdk)
        
        # Demo 2b: ERC-8004 Mainnet option
        demo_2b_mainnet_option()
        
        # Demo 3: Storage
        demo_3_storage(sdk)
        
        # Demo 4: Process Integrity
        demo_4_process_integrity()
        
        # Demo 5: x402 v2.0 Payments
        demo_5_x402_payments()
        
        # Demo 6: x402 Paywall Server
        demo_6_x402_paywall_server()
        
        # Summary
        print_summary()
        
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Demo interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]❌ Demo error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
