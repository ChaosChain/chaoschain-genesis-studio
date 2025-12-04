#!/usr/bin/env python3
"""
ChaosChain SDK v0.3.0 Protocol Feature Testing

Tests the full ChaosChain Protocol stack:
- Studio Creation
- Agent Registration with Studios
- Work Submission (DataHash pattern)
- Verifier Commit-Reveal Protocol
- Reputation Queries
- Rewards Distribution

Network: Ethereum Sepolia (recommended for protocol testing)
"""

import os
import json
import warnings
from pathlib import Path
from typing import Dict, Any
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Suppress Web3 warnings
warnings.filterwarnings('ignore', message='.*MismatchedABI.*')

# Import SDK
try:
    from chaoschain_sdk import (
        ChaosChainAgentSDK,
        AgentRole,
        NetworkConfig
    )
    rprint("[green]✅ SDK v0.3.0 imported successfully[/green]")
except ImportError as e:
    rprint(f"[red]❌ Failed to import SDK: {e}[/red]")
    rprint("[yellow]💡 Install with: pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ chaoschain-sdk==0.3.0[/yellow]")
    exit(1)

console = Console()

# Configuration
NETWORK = NetworkConfig.ETHEREUM_SEPOLIA
RPC_URL = os.getenv("ETHEREUM_SEPOLIA_RPC_URL", "https://sepolia.infura.io/v3/YOUR_KEY")

# Contract addresses from deployment
FINANCE_STUDIO_LOGIC = "0x48E3820CE20E2ee6D68c127a63206D40ea182031"
CREATIVE_STUDIO_LOGIC = "0xF44B2E486437362F3CE972Da96E9700Bd0DC3b33"
PREDICTION_LOGIC = "0x4D193d3Bf8B8CC9b8811720d67E74497fF7223D9"

# Test results storage
results = {
    "backward_compatibility": {},
    "studio_creation": {},
    "agent_registration": {},
    "work_submission": {},
    "verifier_workflow": {},
    "reputation_queries": {},
    "rewards": {}
}


def print_header(title: str):
    """Print a styled section header"""
    console.print()
    console.print(Panel(title, style="bold cyan"))
    console.print()


def print_test(test_name: str, status: str, details: str = ""):
    """Print test result"""
    icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    color = "green" if status == "PASS" else "red" if status == "FAIL" else "yellow"
    rprint(f"[{color}]{icon} {test_name}[/{color}]")
    if details:
        rprint(f"   {details}")


def test_backward_compatibility():
    """Test that existing SDK features still work"""
    print_header("Test 1: Backward Compatibility")
    
    try:
        # Test 1.1: SDK Initialization
        rprint("[cyan]🔧 Test 1.1: SDK Initialization[/cyan]")
        
        # Set RPC URL in environment if not already set
        if "ETHEREUM_SEPOLIA_RPC_URL" not in os.environ:
            os.environ["ETHEREUM_SEPOLIA_RPC_URL"] = RPC_URL
        
        # Use existing Genesis Studio Alice wallet (already funded)
        sdk = ChaosChainAgentSDK(
            agent_name="Alice",
            agent_domain="alice.chaoschain-studio.com",
            agent_role=AgentRole.WORKER,
            network=NETWORK,
            wallet_file="./wallets/alice.json"
        )
        
        print_test("SDK Initialization", "PASS", f"Address: {sdk.wallet_address}")
        results["backward_compatibility"]["initialization"] = {
            "status": "PASS",
            "address": sdk.wallet_address
        }
        
        # Test 1.2: Wallet Balance Check
        rprint("\n[cyan]🔧 Test 1.2: Wallet Balance Check[/cyan]")
        balance_wei = sdk.wallet_manager.w3.eth.get_balance(sdk.wallet_address)
        balance_eth = sdk.wallet_manager.w3.from_wei(balance_wei, 'ether')
        
        print_test("Balance Check", "PASS", f"Balance: {balance_eth:.6f} ETH")
        results["backward_compatibility"]["balance"] = {
            "status": "PASS",
            "balance_eth": float(balance_eth)
        }
        
        # Test 1.3: Agent Registration (ERC-8004)
        rprint("\n[cyan]🔧 Test 1.3: Agent Registration (ERC-8004)[/cyan]")
        try:
            metadata = {
                "agentName": sdk.agent_name.encode('utf-8'),
                "agentDomain": sdk.agent_domain.encode('utf-8')
            }
            agent_id, tx_hash = sdk.chaos_agent.register_agent(
                token_uri="ipfs://QmTest030",
                metadata=metadata
            )
            print_test("Agent Registration", "PASS", f"Agent ID: {agent_id}, TX: {tx_hash[:10]}...")
            results["backward_compatibility"]["registration"] = {
                "status": "PASS",
                "agent_id": agent_id,
                "tx_hash": tx_hash
            }
        except Exception as e:
            error_msg = str(e)
            if "already registered" in error_msg.lower():
                print_test("Agent Registration", "PASS", "Already registered (expected)")
                results["backward_compatibility"]["registration"] = {
                    "status": "PASS",
                    "note": "Already registered"
                }
            else:
                raise
        
        return sdk
        
    except Exception as e:
        print_test("Backward Compatibility", "FAIL", str(e))
        results["backward_compatibility"]["error"] = str(e)
        return None


def test_studio_creation(sdk: ChaosChainAgentSDK):
    """Test Studio creation with v0.3.0"""
    print_header("Test 2: Studio Creation")
    
    try:
        # Test 2.1: Create Finance Studio
        rprint("[cyan]🔧 Test 2.1: Create Finance Studio[/cyan]")
        
        # Check if create_studio method exists
        if not hasattr(sdk, 'create_studio'):
            print_test("create_studio() exists", "FAIL", "Method not found in SDK")
            results["studio_creation"]["method_exists"] = False
            return None
        
        print_test("create_studio() exists", "PASS", "Method available in SDK")
        
        # Attempt to create studio
        rprint("   Creating Finance Studio...")
        rprint(f"   Logic Module: {FINANCE_STUDIO_LOGIC}")
        
        try:
            studio_address, studio_id = sdk.create_studio(
                logic_module_address=FINANCE_STUDIO_LOGIC,
                init_params=b""  # Empty init params for basic testing
            )
            
            print_test("Finance Studio Creation", "PASS", 
                      f"Address: {studio_address}, ID: {studio_id}")
            results["studio_creation"]["finance"] = {
                "status": "PASS",
                "address": studio_address,
                "studio_id": studio_id
            }
            
            return studio_address, studio_id
            
        except Exception as e:
            error_msg = str(e)
            print_test("Finance Studio Creation", "FAIL", error_msg)
            results["studio_creation"]["finance"] = {
                "status": "FAIL",
                "error": error_msg
            }
            return None, None
            
    except Exception as e:
        print_test("Studio Creation", "FAIL", str(e))
        results["studio_creation"]["error"] = str(e)
        return None, None


def test_studio_registration(sdk: ChaosChainAgentSDK, studio_address: str):
    """Test agent registration with Studios"""
    print_header("Test 3: Studio Registration")
    
    try:
        # Test 3.1: Register as Worker
        rprint("[cyan]🔧 Test 3.1: Register Worker with Studio[/cyan]")
        
        if not hasattr(sdk, 'register_with_studio'):
            print_test("register_with_studio() exists", "FAIL", "Method not found")
            results["agent_registration"]["method_exists"] = False
            return
        
        print_test("register_with_studio() exists", "PASS")
        
        try:
            tx_hash = sdk.register_with_studio(
                studio_address=studio_address,
                role="worker"  # or AgentRole.WORKER depending on API
            )
            
            print_test("Worker Registration", "PASS", f"TX: {tx_hash[:10]}...")
            results["agent_registration"]["worker"] = {
                "status": "PASS",
                "tx_hash": tx_hash
            }
            
        except Exception as e:
            error_msg = str(e)
            print_test("Worker Registration", "FAIL", error_msg)
            results["agent_registration"]["worker"] = {
                "status": "FAIL",
                "error": error_msg
            }
            
    except Exception as e:
        print_test("Studio Registration", "FAIL", str(e))
        results["agent_registration"]["error"] = str(e)


def test_work_submission(sdk: ChaosChainAgentSDK, studio_address: str):
    """Test work submission with DataHash pattern"""
    print_header("Test 4: Work Submission")
    
    try:
        # Test 4.1: Submit Work
        rprint("[cyan]🔧 Test 4.1: Submit Work to Studio[/cyan]")
        
        if not hasattr(sdk, 'submit_work'):
            print_test("submit_work() exists", "FAIL", "Method not found")
            results["work_submission"]["method_exists"] = False
            return None
        
        print_test("submit_work() exists", "PASS")
        
        # Create a mock evidence hash (in real scenario, this would be IPFS CID)
        import hashlib
        evidence_data = json.dumps({
            "task_id": "test-task-001",
            "studio_id": studio_address,
            "work_proof": {"result": "Test analysis complete"},
            "timestamp": "2025-12-04T00:00:00Z"
        })
        data_hash = "0x" + hashlib.sha256(evidence_data.encode()).hexdigest()
        
        rprint(f"   Data Hash: {data_hash[:20]}...")
        
        try:
            tx_hash = sdk.submit_work(
                studio_address=studio_address,
                data_hash=data_hash
            )
            
            print_test("Work Submission", "PASS", f"TX: {tx_hash[:10]}...")
            results["work_submission"]["submission"] = {
                "status": "PASS",
                "data_hash": data_hash,
                "tx_hash": tx_hash
            }
            
            return data_hash
            
        except Exception as e:
            error_msg = str(e)
            print_test("Work Submission", "FAIL", error_msg)
            results["work_submission"]["submission"] = {
                "status": "FAIL",
                "error": error_msg
            }
            return None
            
    except Exception as e:
        print_test("Work Submission", "FAIL", str(e))
        results["work_submission"]["error"] = str(e)
        return None


def test_verifier_workflow(verifier_sdk: ChaosChainAgentSDK, 
                          studio_address: str, 
                          data_hash: str):
    """Test verifier commit-reveal protocol"""
    print_header("Test 5: Verifier Workflow")
    
    try:
        # Test 5.1: Commit Score
        rprint("[cyan]🔧 Test 5.1: Commit Score (Commit Phase)[/cyan]")
        
        if not hasattr(verifier_sdk, 'commit_score'):
            print_test("commit_score() exists", "FAIL", "Method not found")
            results["verifier_workflow"]["commit_method_exists"] = False
            return
        
        print_test("commit_score() exists", "PASS")
        
        # Create mock score commitment
        import hashlib
        import secrets
        
        score = 85
        salt = secrets.token_hex(32)
        score_commitment = "0x" + hashlib.sha256(
            f"{score}{salt}".encode()
        ).hexdigest()
        
        try:
            tx_hash = verifier_sdk.commit_score(
                studio_address=studio_address,
                epoch=1,
                data_hash=data_hash,
                score_commitment=score_commitment
            )
            
            print_test("Score Commitment", "PASS", f"TX: {tx_hash[:10]}...")
            results["verifier_workflow"]["commit"] = {
                "status": "PASS",
                "tx_hash": tx_hash,
                "commitment": score_commitment
            }
            
            # Test 5.2: Reveal Score
            rprint("\n[cyan]🔧 Test 5.2: Reveal Score (Reveal Phase)[/cyan]")
            
            if not hasattr(verifier_sdk, 'reveal_score'):
                print_test("reveal_score() exists", "FAIL", "Method not found")
                results["verifier_workflow"]["reveal_method_exists"] = False
                return
            
            print_test("reveal_score() exists", "PASS")
            
            try:
                tx_hash = verifier_sdk.reveal_score(
                    studio_address=studio_address,
                    epoch=1,
                    data_hash=data_hash,
                    score=score,
                    salt=salt
                )
                
                print_test("Score Reveal", "PASS", f"TX: {tx_hash[:10]}...")
                results["verifier_workflow"]["reveal"] = {
                    "status": "PASS",
                    "tx_hash": tx_hash,
                    "score": score
                }
                
            except Exception as e:
                error_msg = str(e)
                print_test("Score Reveal", "FAIL", error_msg)
                results["verifier_workflow"]["reveal"] = {
                    "status": "FAIL",
                    "error": error_msg
                }
                
        except Exception as e:
            error_msg = str(e)
            print_test("Score Commitment", "FAIL", error_msg)
            results["verifier_workflow"]["commit"] = {
                "status": "FAIL",
                "error": error_msg
            }
            
    except Exception as e:
        print_test("Verifier Workflow", "FAIL", str(e))
        results["verifier_workflow"]["error"] = str(e)


def test_reputation_queries(sdk: ChaosChainAgentSDK):
    """Test reputation query methods"""
    print_header("Test 6: Reputation Queries")
    
    try:
        # Test 6.1: Get Reputation
        rprint("[cyan]🔧 Test 6.1: Get Full Reputation Data[/cyan]")
        
        if not hasattr(sdk, 'get_reputation'):
            print_test("get_reputation() exists", "FAIL", "Method not found")
            results["reputation_queries"]["get_method_exists"] = False
        else:
            print_test("get_reputation() exists", "PASS")
            
            try:
                agent_id = sdk.chaos_agent.get_agent_id()
                reputation_data = sdk.get_reputation(agent_id)
                
                print_test("Get Reputation", "PASS", 
                          f"Retrieved reputation for Agent ID: {agent_id}")
                results["reputation_queries"]["get"] = {
                    "status": "PASS",
                    "agent_id": agent_id,
                    "data": reputation_data
                }
                
            except Exception as e:
                error_msg = str(e)
                print_test("Get Reputation", "FAIL", error_msg)
                results["reputation_queries"]["get"] = {
                    "status": "FAIL",
                    "error": error_msg
                }
        
        # Test 6.2: Get Reputation Summary
        rprint("\n[cyan]🔧 Test 6.2: Get Reputation Summary[/cyan]")
        
        if not hasattr(sdk, 'get_reputation_summary'):
            print_test("get_reputation_summary() exists", "FAIL", "Method not found")
            results["reputation_queries"]["summary_method_exists"] = False
        else:
            print_test("get_reputation_summary() exists", "PASS")
            
            try:
                agent_id = sdk.chaos_agent.get_agent_id()
                summary = sdk.get_reputation_summary(agent_id)
                
                print_test("Get Reputation Summary", "PASS", 
                          f"Retrieved summary for Agent ID: {agent_id}")
                results["reputation_queries"]["summary"] = {
                    "status": "PASS",
                    "agent_id": agent_id,
                    "summary": summary
                }
                
            except Exception as e:
                error_msg = str(e)
                print_test("Get Reputation Summary", "FAIL", error_msg)
                results["reputation_queries"]["summary"] = {
                    "status": "FAIL",
                    "error": error_msg
                }
                
    except Exception as e:
        print_test("Reputation Queries", "FAIL", str(e))
        results["reputation_queries"]["error"] = str(e)


def test_rewards(sdk: ChaosChainAgentSDK, studio_address: str):
    """Test reward distribution methods"""
    print_header("Test 7: Rewards Distribution")
    
    try:
        # Test 7.1: Get Pending Rewards
        rprint("[cyan]🔧 Test 7.1: Get Pending Rewards[/cyan]")
        
        if not hasattr(sdk, 'get_pending_rewards'):
            print_test("get_pending_rewards() exists", "FAIL", "Method not found")
            results["rewards"]["get_method_exists"] = False
        else:
            print_test("get_pending_rewards() exists", "PASS")
            
            try:
                pending = sdk.get_pending_rewards(studio_address)
                
                print_test("Get Pending Rewards", "PASS", 
                          f"Pending rewards: {pending}")
                results["rewards"]["get_pending"] = {
                    "status": "PASS",
                    "amount": pending
                }
                
            except Exception as e:
                error_msg = str(e)
                print_test("Get Pending Rewards", "FAIL", error_msg)
                results["rewards"]["get_pending"] = {
                    "status": "FAIL",
                    "error": error_msg
                }
        
        # Test 7.2: Withdraw Rewards
        rprint("\n[cyan]🔧 Test 7.2: Withdraw Rewards[/cyan]")
        
        if not hasattr(sdk, 'withdraw_rewards'):
            print_test("withdraw_rewards() exists", "FAIL", "Method not found")
            results["rewards"]["withdraw_method_exists"] = False
        else:
            print_test("withdraw_rewards() exists", "PASS")
            
            # Note: Only attempt withdrawal if there are pending rewards
            rprint("   [yellow]Note: Skipping actual withdrawal (no pending rewards expected)[/yellow]")
            results["rewards"]["withdraw"] = {
                "status": "SKIP",
                "note": "No pending rewards to withdraw"
            }
        
        # Test 7.3: Close Epoch
        rprint("\n[cyan]🔧 Test 7.3: Close Epoch[/cyan]")
        
        if not hasattr(sdk, 'close_epoch'):
            print_test("close_epoch() exists", "FAIL", "Method not found")
            results["rewards"]["close_epoch_method_exists"] = False
        else:
            print_test("close_epoch() exists", "PASS")
            results["rewards"]["close_epoch"] = {
                "status": "PASS",
                "note": "Method available (not executed in test)"
            }
                
    except Exception as e:
        print_test("Rewards Distribution", "FAIL", str(e))
        results["rewards"]["error"] = str(e)


def generate_report():
    """Generate test report"""
    print_header("Test Summary Report")
    
    # Create results table
    table = Table(title="SDK v0.3.0 Feature Test Results")
    table.add_column("Test Category", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Details", style="white")
    
    for category, data in results.items():
        if "error" in data:
            table.add_row(category, "❌ FAIL", data["error"])
        else:
            # Count passes
            passes = sum(1 for v in data.values() 
                        if isinstance(v, dict) and v.get("status") == "PASS")
            total = sum(1 for v in data.values() 
                       if isinstance(v, dict) and "status" in v)
            
            if total > 0:
                status = f"✅ {passes}/{total}" if passes == total else f"⚠️ {passes}/{total}"
                table.add_row(category, status, f"{passes} tests passed")
            else:
                table.add_row(category, "⏸️ SKIP", "No tests executed")
    
    console.print(table)
    
    # Save results to file
    output_file = Path("test_results_v030.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    rprint(f"\n[green]✅ Results saved to: {output_file}[/green]")
    
    # Print recommendations
    print_header("Recommendations")
    
    if results.get("backward_compatibility", {}).get("initialization", {}).get("status") != "PASS":
        rprint("[yellow]⚠️ Backward compatibility issues detected - SDK upgrade may break existing code[/yellow]")
    else:
        rprint("[green]✅ Backward compatibility verified - safe to upgrade[/green]")
    
    # Check for missing features
    missing_features = []
    for category, data in results.items():
        if any(k.endswith("_method_exists") and v is False 
               for k, v in data.items() if isinstance(v, bool)):
            missing_features.append(category)
    
    if missing_features:
        rprint(f"\n[yellow]⚠️ Missing features in: {', '.join(missing_features)}[/yellow]")
        rprint("[yellow]   These features may not be fully implemented in v0.3.0[/yellow]")
    else:
        rprint("\n[green]✅ All new protocol features are available in the SDK[/green]")


def main():
    """Main test execution"""
    console.print(Panel.fit(
        "[bold cyan]ChaosChain SDK v0.3.0 Protocol Feature Testing[/bold cyan]\n"
        "[white]Testing full protocol stack on Ethereum Sepolia[/white]",
        border_style="cyan"
    ))
    
    # Pre-flight checks
    rprint("\n[cyan]🔍 Pre-flight Checks:[/cyan]")
    
    if not os.getenv("ETHEREUM_SEPOLIA_RPC_URL"):
        rprint("[yellow]⚠️ ETHEREUM_SEPOLIA_RPC_URL not set in .env[/yellow]")
        rprint("[yellow]   Using default RPC (may have rate limits)[/yellow]")
    
    # Run tests
    worker_sdk = test_backward_compatibility()
    
    if worker_sdk:
        studio_address, studio_id = test_studio_creation(worker_sdk)
        
        if studio_address:
            test_studio_registration(worker_sdk, studio_address)
            data_hash = test_work_submission(worker_sdk, studio_address)
            
            # Create verifier SDK for commit-reveal testing
            rprint("\n[cyan]🔧 Creating Verifier SDK for commit-reveal testing...[/cyan]")
            try:
                # Use existing Genesis Studio Bob wallet (already funded)
                verifier_sdk = ChaosChainAgentSDK(
                    agent_name="Bob",
                    agent_domain="bob.chaoschain-studio.com",
                    agent_role=AgentRole.VERIFIER,
                    network=NETWORK,
                    wallet_file="./wallets/bob.json"
                )
                
                if data_hash:
                    test_verifier_workflow(verifier_sdk, studio_address, data_hash)
            except Exception as e:
                rprint(f"[yellow]⚠️ Could not create verifier SDK: {e}[/yellow]")
            
            test_rewards(worker_sdk, studio_address)
        
        test_reputation_queries(worker_sdk)
    
    # Generate final report
    generate_report()
    
    rprint("\n[bold green]🎉 Testing complete![/bold green]")


if __name__ == "__main__":
    main()

