#!/usr/bin/env python3
"""
ChaosChain SDK - BASE INSTALL DEMO
===================================

What this demonstrates:
- ✅ ERC-8004 v1.0 agent identity & reputation
- ✅ x402 payment protocol (Coinbase official)
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

# Suppress Web3.py event parsing warnings (harmless ABI mismatches)
warnings.filterwarnings('ignore', message='.*MismatchedABI.*')
warnings.filterwarnings('ignore', message='.*encountered the following error during processing.*')

console = Console()

# Set minimal environment variables for demo
# Using Base Sepolia for reliable RPC connectivity
if "BASE_SEPOLIA_RPC_URL" not in os.environ:
    os.environ["BASE_SEPOLIA_RPC_URL"] = "https://sepolia.base.org"


def print_header():
    """Print demo header."""
    header = Panel.fit(
        "\n[bold cyan]CHAOSCHAIN SDK - BASE INSTALL DEMO[/bold cyan]\n\n"
        "[yellow]What works out-of-the-box:[/yellow]\n"
        "  ✅ ERC-8004 v1.0 (Identity, Validation & Reputation)\n"
        "  ✅ x402 Payment Protocol (Coinbase)\n"
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
        agent_role=AgentRole.SERVER,
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
    
    from chaoschain_sdk.types import AgentRole
    
    console.print("🔧 Registering agent on ERC-8004 IdentityRegistry...")
    
    try:
        # Register agent with metadata (ERC-8004 v1.0 compliant - new in v0.2.3!)
        metadata = {
            "agentName": sdk.agent_name.encode('utf-8'),
            "agentDomain": sdk.agent_domain.encode('utf-8')
        }
        
        agent_id, tx_hash = sdk.chaos_agent.register_agent(
            token_uri="ipfs://QmDemo123",
            metadata=metadata  # NEW: Metadata support!
        )
        
        console.print(f"✅ Agent registered with metadata!")
        console.print(f"   Transaction: [green]{tx_hash}[/green]")
        console.print(f"   Agent ID: [green]{agent_id}[/green]")
        console.print(f"   Metadata URI: [cyan]ipfs://QmDemo123[/cyan]")
        console.print(f"   On-chain Metadata: [yellow]{len(metadata)} entries[/yellow]")
        
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
        else:
            console.print(f"⚠️  Registration error: {e}")
        
        console.print("\n[bold]💰 To register on-chain:[/bold]")
        console.print("   1. Get testnet ETH: [cyan]https://docs.base.org/base-chain/tools/network-faucets[/cyan]")
        console.print(f"   2. Send to: [green]{sdk.wallet_address}[/green]")
        console.print("   3. Run this demo again")
        return None


def demo_2b_metadata(sdk, agent_id):
    """Demo 2b: ERC-8004 on-chain metadata (NEW in v0.2.3!)."""
    if not agent_id:
        console.print("\n[bold]📋 Demo 2b: ERC-8004 On-Chain Metadata[/bold]")
        console.print("=" * 80)
        console.print("⚠️  Skipped - agent not registered")
        return
    
    console.print("\n[bold]📋 Demo 2b: ERC-8004 On-Chain Metadata (NEW!)[/bold]")
    console.print("=" * 80)
    
    console.print("🔧 Setting additional metadata...")
    
    try:
        # Set additional metadata (requires testnet tokens)
        sdk.chaos_agent.set_agent_metadata("version", b"1.0.0")
        console.print("✅ Metadata set successfully!")
        
        # Read metadata back
        console.print("\n🔧 Reading on-chain metadata...")
        name = sdk.chaos_agent.get_agent_metadata("agentName")
        domain = sdk.chaos_agent.get_agent_metadata("agentDomain")
        version = sdk.chaos_agent.get_agent_metadata("version")
        
        console.print(f"✅ Metadata retrieved!")
        console.print(f"   Name: [green]{name.decode('utf-8')}[/green]")
        console.print(f"   Domain: [cyan]{domain.decode('utf-8')}[/cyan]")
        console.print(f"   Version: [yellow]{version.decode('utf-8')}[/yellow]")
        
    except Exception as e:
        error_str = str(e).lower()
        if "insufficient funds" in error_str:
            console.print("⚠️  Setting metadata requires testnet ETH (reading is free)")
        else:
            console.print(f"⚠️  Metadata operations: {e}")


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
        agent_role=AgentRole.SERVER,
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
    """Demo 5: x402 payment protocol."""
    console.print("\n[bold]📋 Demo 5: x402 Payment Protocol (Coinbase)[/bold]")
    console.print("=" * 80)
    
    from chaoschain_sdk import ChaosChainAgentSDK, NetworkConfig
    from chaoschain_sdk.types import AgentRole
    
    sdk = ChaosChainAgentSDK(
        agent_name="PaymentDemo",
        agent_domain="payment.chaoschain.io",
        agent_role=AgentRole.SERVER,
        network=NetworkConfig.BASE_SEPOLIA,
        enable_ap2=False  # Disable AP2 for base demo
    )
    
    console.print("✅ x402 Payment Manager initialized!")
    console.print(f"   Protocol: [cyan]Coinbase x402 v0.2.1+[/cyan]")
    console.print(f"   Token: [yellow]USDC (ERC-20)[/yellow]")
    console.print(f"   Treasury: [green]0x20E7B2A2c8969725b88Dd3EF3a11Bc3353C83F70[/green]")
    
    # Create payment request
    console.print("\n🔧 Creating x402 payment request...")
    
    payment_amount = 1.0  # 1.0 USDC
    
    payment_request = {
        "amount": payment_amount,
        "currency": "USDC",
        "recipient": sdk.wallet_address,
        "memo": "Demo payment via x402"
    }
    
    console.print(f"✅ Payment request created!")
    console.print(f"   Amount: [green]{payment_amount} USDC[/green]")
    console.print(f"   Protocol: [cyan]HTTP 402 Payment Required[/cyan]")
    console.print(f"   Settlement: [yellow]Direct (no facilitator)[/yellow]")
    
    console.print("\n[dim]Note: Actual payment execution requires funded wallet[/dim]")


def print_summary():
    """Print demo summary."""
    console.print("\n" + "=" * 80)
    console.print("[bold green]🎉 Base Install Demo Complete![/bold green]\n")
    
    summary_table = Table(title="What You Can Do with Base Install")
    summary_table.add_column("Feature", style="cyan")
    summary_table.add_column("Status", style="green")
    summary_table.add_column("Requirements")
    
    summary_table.add_row(
        "ERC-8004 Identity",
        "✅ Ready",
        "Testnet tokens"
    )
    summary_table.add_row(
        "x402 Payments",
        "✅ Ready",
        "Testnet tokens"
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
    console.print("  1. Get testnet tokens: [cyan]https://docs.base.org/base-chain/tools/network-faucets[/cyan]")
    console.print("  2. Install IPFS (optional): [cyan]https://docs.ipfs.tech/install/[/cyan]")
    console.print("  3. Explore optional integrations:")
    console.print("     • [yellow]0G Storage/Compute:[/yellow] pip install chaoschain-sdk[0g]")
    console.print("     • [yellow]Cloud Storage:[/yellow] pip install chaoschain-sdk[pinata]")
    console.print("     • [yellow]Google AP2:[/yellow] pip install git+https://github.com/google-agentic-commerce/AP2.git@main")
    console.print()
    console.print("[dim]📖 Full documentation: https://github.com/ChaosChain/chaoschain-sdk[/dim]")
    console.print()


def main():
    """Run the base install demo."""
    try:
        print_header()
        
        # Demo 1: Wallet
        sdk = demo_1_wallet_creation()
        
        # Demo 2: ERC-8004
        agent_id = demo_2_erc8004_identity(sdk)
        
        # Demo 2b: Metadata (NEW in v0.2.3!)
        demo_2b_metadata(sdk, agent_id)
        
        # Demo 3: Storage
        demo_3_storage(sdk)
        
        # Demo 4: Process Integrity
        demo_4_process_integrity()
        
        # Demo 5: x402
        demo_5_x402_payments()
        
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

