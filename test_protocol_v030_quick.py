#!/usr/bin/env python3
"""
ChaosChain SDK v0.3.0 - Quick API Availability Test

Tests if new protocol methods exist without requiring funded wallets or transactions.
This is useful for verifying the SDK API surface before full integration testing.
"""

import warnings
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Suppress warnings
warnings.filterwarnings('ignore')

console = Console()

try:
    from chaoschain_sdk import ChaosChainAgentSDK
    rprint("[green]✅ SDK v0.3.0 imported successfully[/green]")
except ImportError as e:
    rprint(f"[red]❌ Failed to import SDK: {e}[/red]")
    exit(1)


def check_method(obj, method_name: str, category: str):
    """Check if a method exists on an object"""
    exists = hasattr(obj, method_name)
    icon = "✅" if exists else "❌"
    status = "EXISTS" if exists else "MISSING"
    
    return {
        "method": method_name,
        "category": category,
        "exists": exists,
        "icon": icon,
        "status": status
    }


def main():
    console.print(Panel.fit(
        "[bold cyan]ChaosChain SDK v0.3.0 - API Availability Test[/bold cyan]\n"
        "[white]Checking for new protocol methods[/white]",
        border_style="cyan"
    ))
    
    # Expected methods in v0.3.0
    expected_methods = {
        "Studios": [
            ("create_studio", "Create domain-specific Studios"),
            ("register_with_studio", "Join Studios as Worker/Verifier"),
        ],
        "Work Submission": [
            ("submit_work", "Submit work with DataHash pattern"),
        ],
        "Verifier Workflow": [
            ("commit_score", "Commit score (commit phase)"),
            ("reveal_score", "Reveal score (reveal phase)"),
        ],
        "Epoch Management": [
            ("close_epoch", "Close epochs and trigger rewards"),
        ],
        "Rewards": [
            ("get_pending_rewards", "Query pending rewards"),
            ("withdraw_rewards", "Withdraw earned rewards"),
        ],
        "Reputation": [
            ("get_reputation", "Full reputation data"),
            ("get_reputation_summary", "Aggregated reputation stats"),
        ],
    }
    
    rprint("\n[cyan]📦 Checking SDK class methods...[/cyan]\n")
    
    results = []
    
    for category, methods in expected_methods.items():
        rprint(f"\n[bold yellow]{category}:[/bold yellow]")
        for method_name, description in methods:
            result = check_method(ChaosChainAgentSDK, method_name, category)
            results.append(result)
            
            color = "green" if result["exists"] else "red"
            rprint(f"[{color}]{result['icon']} {method_name:<25}[/{color}] - {description}")
    
    # Summary Table
    rprint("\n")
    console.print(Panel("[bold cyan]Summary[/bold cyan]", border_style="cyan"))
    
    table = Table(title="SDK v0.3.0 API Availability")
    table.add_column("Category", style="cyan")
    table.add_column("Methods Found", style="green")
    table.add_column("Total Methods", style="yellow")
    table.add_column("Status", style="magenta")
    
    category_stats = {}
    for result in results:
        cat = result["category"]
        if cat not in category_stats:
            category_stats[cat] = {"found": 0, "total": 0}
        category_stats[cat]["total"] += 1
        if result["exists"]:
            category_stats[cat]["found"] += 1
    
    total_found = 0
    total_methods = 0
    
    for category, stats in category_stats.items():
        found = stats["found"]
        total = stats["total"]
        total_found += found
        total_methods += total
        
        status = "✅ Complete" if found == total else f"⚠️ {total - found} missing"
        table.add_row(category, str(found), str(total), status)
    
    # Overall row
    overall_status = "✅ All Available" if total_found == total_methods else f"⚠️ Partial ({total_found}/{total_methods})"
    table.add_row("[bold]TOTAL[/bold]", f"[bold]{total_found}[/bold]", 
                 f"[bold]{total_methods}[/bold]", f"[bold]{overall_status}[/bold]")
    
    console.print(table)
    
    # Recommendations
    rprint("\n")
    console.print(Panel("[bold cyan]Recommendations[/bold cyan]", border_style="cyan"))
    
    if total_found == total_methods:
        rprint("[green]✅ All expected v0.3.0 protocol methods are available![/green]")
        rprint("[green]   The SDK is ready for full ChaosChain Protocol integration.[/green]")
    else:
        missing_count = total_methods - total_found
        rprint(f"[yellow]⚠️ {missing_count} method(s) missing from the SDK[/yellow]")
        rprint("[yellow]   Some protocol features may not be fully implemented yet.[/yellow]")
        
        rprint("\n[bold]Missing Methods:[/bold]")
        for result in results:
            if not result["exists"]:
                rprint(f"[red]  ❌ {result['method']} ({result['category']})[/red]")
    
    rprint("\n[cyan]📋 Next Steps:[/cyan]")
    if total_found == total_methods:
        rprint("  1. Fund test wallet with Sepolia ETH")
        rprint("  2. Run full integration tests: python test_protocol_v030.py")
        rprint("  3. Integrate into genesis_studio.py")
    else:
        rprint("  1. Check SDK documentation for correct method names")
        rprint("  2. Verify SDK version: pip show chaoschain-sdk")
        rprint("  3. Contact SDK maintainers about missing methods")
    
    rprint("\n[bold green]🎉 API check complete![/bold green]\n")


if __name__ == "__main__":
    main()

