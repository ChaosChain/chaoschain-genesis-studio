"""
0G Storage provider using official 0G Storage CLI.

This provider uses the official 0G Storage CLI (Go binary) for upload/download operations.
The CLI is built from: https://github.com/0gfoundation/0g-storage-client

Features:
- 95% lower costs than AWS S3
- Instant retrieval (200 MBPS)
- Decentralized storage with on-chain data availability
- Perfect for AI datasets and agent evidence trails

Documentation:
- 0G Storage Docs: https://docs.0g.ai/concepts/storage
- CLI Docs: https://docs.0g.ai/developer-hub/building-on-0g/storage/storage-cli

Setup:
    # Clone and build
    git clone https://github.com/0gfoundation/0g-storage-client.git
    cd 0g-storage-client
    go build
    
    # Move to PATH
    mv 0g-storage-client ~/go/bin/
    
Environment Variables:
    ZEROG_TESTNET_PRIVATE_KEY: Private key for signing transactions
    ZEROG_TESTNET_RPC_URL: Blockchain RPC (default: https://evmrpc-testnet.0g.ai)
    ZEROG_STORAGE_INDEXER: Indexer endpoint (default: https://indexer-storage-testnet-turbo.0g.ai/)
    
Note: No ZEROG_STORAGE_NODE needed! The indexer automatically finds optimal nodes.
"""

import os
import json
import hashlib
import subprocess
import tempfile
from typing import Optional, Dict, Tuple
from pathlib import Path
from rich import print as rprint

from .base import StorageBackend, StorageResult


class ZeroGStorage:
    """
    0G Storage provider using official Go CLI.
    
    Uses the official 0G Storage CLI for upload/download operations.
    The CLI automatically uses the indexer to find optimal storage nodes.
    
    Configuration:
    - ZEROG_TESTNET_PRIVATE_KEY: Private key for signing transactions
    - ZEROG_TESTNET_RPC_URL: Blockchain RPC endpoint (default: testnet)
    - ZEROG_STORAGE_INDEXER: Indexer endpoint (default: testnet)
    
    Note: No manual storage node configuration needed!
    """
    
    def __init__(
        self,
        private_key: Optional[str] = None,
        rpc_url: Optional[str] = None,
        indexer_url: Optional[str] = None
    ):
        self.private_key = private_key or os.getenv('ZEROG_TESTNET_PRIVATE_KEY')
        self.rpc_url = rpc_url or os.getenv('ZEROG_TESTNET_RPC_URL', 'https://evmrpc-testnet.0g.ai')
        self.indexer_url = indexer_url or os.getenv('ZEROG_STORAGE_INDEXER', 'https://indexer-storage-testnet-turbo.0g.ai/')
        
        # Check if 0G CLI is available
        self._available = False
        self._cli_path = None
        
        if not self.private_key:
            rprint("[yellow]⚠️  ZEROG_TESTNET_PRIVATE_KEY not set[/yellow]")
            rprint("[cyan]   Set ZEROG_TESTNET_PRIVATE_KEY to use 0G Storage[/cyan]")
            return
        
        # Check for 0G Storage CLI
        cli_locations = [
            '0g-storage-client',  # In PATH
            '~/go/bin/0g-storage-client',  # Go bin
            './0g-storage-client',  # Local
        ]
        
        for cli in cli_locations:
            try:
                expanded_path = os.path.expanduser(cli)
                result = subprocess.run(
                    [expanded_path, '--help'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and 'upload' in result.stdout:
                    self._cli_path = expanded_path
                    self._available = True
                    rprint(f"[green]✅ 0G Storage CLI available[/green]")
                    rprint(f"[cyan]   RPC: {self.rpc_url}[/cyan]")
                    rprint(f"[cyan]   Indexer: {self.indexer_url}[/cyan]")
                    break
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        
        if not self._available:
            # Silent failure - only warn in genesis_studio.py
            pass
    
    @property
    def provider_name(self) -> str:
        return "0g-storage"
    
    @property
    def is_available(self) -> bool:
        return self._available
    
    def _compute_hash(self, data: bytes) -> str:
        """Compute KECCAK-256 hash for consistency."""
        return '0x' + hashlib.sha3_256(data).hexdigest()
    
    def put(
        self,
        blob: bytes,
        *,
        mime: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        idempotency_key: Optional[str] = None
    ) -> StorageResult:
        """
        Upload data to 0G Storage using CLI.
        
        Uses: 0g-storage-client upload --url <rpc> --key <key> --indexer <indexer> --file <file>
        
        Args:
            blob: Data to store (binary)
            mime: Optional MIME type (stored in metadata)
            tags: Optional metadata tags
            idempotency_key: Not used
        
        Returns:
            StorageResult with root hash and transaction details
        """
        if not self._available:
            return StorageResult(
                success=False,
                uri="",
                hash="",
                provider="0G_Storage",
                error="0G Storage CLI not available"
            )
        
        try:
            # Write data to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as tmp:
                tmp.write(blob)
                tmp_path = tmp.name
            
            # Compute hash for reference
            data_hash = self._compute_hash(blob)
            
            rprint(f"[yellow]📤 Uploading {len(blob)} bytes to 0G Storage...[/yellow]")
            
            # Build CLI command (from docs)
            cmd = [
                self._cli_path,
                'upload',
                '--url', self.rpc_url,
                '--key', self.private_key,
                '--indexer', self.indexer_url,
                '--file', tmp_path,
                '--log-level', 'error',  # Reduce noise
            ]
            
            # Execute upload
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes for large files
            )
            
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Upload failed"
                rprint(f"[red]❌ Upload failed: {error_msg[:200]}[/red]")
                return StorageResult(
                    success=False,
                    uri="",
                    hash=data_hash,
                    provider="0G_Storage",
                    error=error_msg
                )
            
            # Parse CLI output for root hash and tx hash
            output = result.stdout + result.stderr
            root_hash = ""
            tx_hash = ""
            
            # CLI outputs: "Root hash: 0x..." and "Transaction: 0x..."
            for line in output.split('\n'):
                line_lower = line.lower()
                if 'root' in line_lower and '0x' in line:
                    # Extract hex string
                    parts = line.split('0x')
                    if len(parts) > 1:
                        root_hash = '0x' + parts[1].split()[0].strip()
                elif ('transaction' in line_lower or 'tx' in line_lower) and '0x' in line:
                    parts = line.split('0x')
                    if len(parts) > 1:
                        tx_hash = '0x' + parts[1].split()[0].strip()
            
            if not root_hash:
                # Fallback: use data hash if CLI didn't output root
                root_hash = data_hash
            
            # Build URI
            uri = f"0g://{root_hash}"
            
            rprint(f"[green]✅ Uploaded to 0G Storage[/green]")
            rprint(f"[cyan]   Root Hash: {root_hash}[/cyan]")
            if tx_hash:
                rprint(f"[cyan]   TX Hash: {tx_hash}[/cyan]")
                rprint(f"[cyan]   View: https://chainscan-newton.0g.ai/tx/{tx_hash}[/cyan]")
            
            return StorageResult(
                success=True,
                uri=uri,
                hash=data_hash,
                provider="0G_Storage",
                metadata={
                    "root_hash": root_hash,
                    "tx_hash": tx_hash,
                    "size": len(blob),
                    "mime_type": mime,
                    "tags": tags or {}
                }
            )
            
        except subprocess.TimeoutExpired:
            if 'tmp_path' in locals():
                Path(tmp_path).unlink(missing_ok=True)
            error_msg = "Upload timed out after 5 minutes"
            rprint(f"[red]❌ {error_msg}[/red]")
            return StorageResult(
                success=False,
                uri="",
                hash="",
                provider="0G_Storage",
                error=error_msg
            )
        except Exception as e:
            if 'tmp_path' in locals():
                Path(tmp_path).unlink(missing_ok=True)
            error_msg = f"Upload error: {str(e)}"
            rprint(f"[red]❌ {error_msg}[/red]")
            return StorageResult(
                success=False,
                uri="",
                hash="",
                provider="0G_Storage",
                error=error_msg
            )
    
    def get(self, uri: str) -> Tuple[bytes, Optional[Dict]]:
        """
        Retrieve data from 0G Storage using CLI.
        
        Uses: 0g-storage-client download --indexer <indexer> --root <root> --file <file>
        
        Args:
            uri: URI of the data (e.g., "0g://0x..." or just the root hash)
        
        Returns:
            Tuple of (data bytes, metadata dict)
        
        Raises:
            Exception: If retrieval fails
        """
        if not self._available:
            raise Exception("0G Storage CLI not available")
        
        try:
            # Extract root hash from URI
            root_hash = uri.replace('0g://', '').strip()
            
            # Create temp file for download
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.bin')
            tmp_path = tmp_file.name
            tmp_file.close()
            
            rprint(f"[yellow]📥 Downloading from 0G Storage: {root_hash[:16]}...[/yellow]")
            
            # Build CLI command (from docs)
            cmd = [
                self._cli_path,
                'download',
                '--indexer', self.indexer_url,
                '--root', root_hash,
                '--file', tmp_path,
                '--log-level', 'error',
            ]
            
            # Execute download
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )
            
            if result.returncode != 0:
                Path(tmp_path).unlink(missing_ok=True)
                error_msg = result.stderr or result.stdout or "Download failed"
                rprint(f"[red]❌ Download failed: {error_msg[:200]}[/red]")
                raise Exception(error_msg)
            
            # Read downloaded data
            with open(tmp_path, 'rb') as f:
                data = f.read()
            
            # Clean up
            Path(tmp_path).unlink(missing_ok=True)
            
            rprint(f"[green]✅ Downloaded {len(data)} bytes from 0G Storage[/green]")
            
            # Build metadata
            metadata = {
                "root_hash": root_hash,
                "size": len(data),
                "data_hash": self._compute_hash(data)
            }
            
            return data, metadata
            
        except subprocess.TimeoutExpired:
            if 'tmp_path' in locals():
                Path(tmp_path).unlink(missing_ok=True)
            error_msg = "Download timed out after 5 minutes"
            rprint(f"[red]❌ {error_msg}[/red]")
            raise Exception(error_msg)
        except Exception as e:
            if 'tmp_path' in locals():
                Path(tmp_path).unlink(missing_ok=True)
            raise
    
    def verify(self, uri: str, expected_hash: str) -> bool:
        """
        Verify data integrity in 0G Storage.
        
        Downloads the data and computes hash locally.
        
        Args:
            uri: URI of the data to verify
            expected_hash: Expected KECCAK-256 hash
        
        Returns:
            True if data matches expected hash
        """
        try:
            data, _ = self.get(uri)
            actual_hash = self._compute_hash(data)
            
            if actual_hash == expected_hash:
                rprint(f"[green]✅ Data integrity verified[/green]")
                return True
            else:
                rprint(f"[red]❌ Data integrity check failed[/red]")
                rprint(f"[red]   Expected: {expected_hash}[/red]")
                rprint(f"[red]   Actual: {actual_hash}[/red]")
                return False
        except Exception as e:
            rprint(f"[red]❌ Verification failed: {str(e)}[/red]")
            return False
    
    def delete(self, uri: str, idempotency_key: Optional[str] = None) -> bool:
        """
        Delete is not supported in 0G Storage (immutable by design).
        
        Returns:
            False (deletion not supported)
        """
        rprint("[yellow]⚠️  0G Storage is immutable - delete not supported[/yellow]")
        return False

