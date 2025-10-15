"""
0G Storage provider using official 0G TypeScript SDK.

This provider uses the @0glabs/0g-ts-sdk for direct storage operations via Node.js,
similar to how we use the 0G Compute SDK for inference.

Features:
- 95% lower costs than AWS S3
- Instant retrieval (200 MBPS)
- Decentralized storage with on-chain data availability
- Perfect for AI datasets and agent evidence trails

Documentation:
- 0G Storage Docs: https://docs.0g.ai/concepts/storage
- TypeScript SDK: https://www.npmjs.com/package/@0glabs/0g-ts-sdk

Setup:
    # Install 0G Storage SDK (run in project root or SDK directory)
    pnpm add @0glabs/0g-ts-sdk
    
    # Or with npm
    npm install @0glabs/0g-ts-sdk
    
Environment Variables:
    ZEROG_STORAGE_NODE: Storage node RPC URL (e.g., http://3.101.147.150:5678)
    ZEROG_TESTNET_PRIVATE_KEY: Private key for storage operations
    ZEROG_TESTNET_RPC_URL: EVM RPC URL (e.g., https://evmrpc-testnet.0g.ai)
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
    0G Storage provider using TypeScript SDK via Node.js.
    
    Uses the official @0glabs/0g-ts-sdk for upload/download operations.
    Data is stored on the decentralized 0G Storage Network with on-chain DA.
    
    Configuration:
    - ZEROG_STORAGE_NODE: Storage node RPC URL
    - ZEROG_TESTNET_PRIVATE_KEY: Private key for signing transactions
    - ZEROG_TESTNET_RPC_URL: EVM RPC URL
    """
    
    def __init__(
        self,
        storage_node: Optional[str] = None,
        private_key: Optional[str] = None,
        evm_rpc: Optional[str] = None
    ):
        self.storage_node = storage_node or os.getenv('ZEROG_STORAGE_NODE')
        self.private_key = private_key or os.getenv('ZEROG_TESTNET_PRIVATE_KEY')
        self.evm_rpc = evm_rpc or os.getenv('ZEROG_TESTNET_RPC_URL', 'https://evmrpc-testnet.0g.ai')
        
        # Check if 0G SDK is available
        self._available = False
        
        if not self.storage_node:
            rprint("[yellow]⚠️  ZEROG_STORAGE_NODE not set[/yellow]")
            rprint("[cyan]   Set ZEROG_STORAGE_NODE to use 0G Storage[/cyan]")
            return
        
        if not self.private_key:
            rprint("[yellow]⚠️  ZEROG_TESTNET_PRIVATE_KEY not set[/yellow]")
            return
        
        # Check for Node.js and 0G SDK
        try:
            # Test if Node.js is available
            result = subprocess.run(
                ['node', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Test if 0G SDK is installed
                test_script = """
const fs = require('fs');
try {
    require('@0glabs/0g-ts-sdk');
    console.log('available');
} catch (e) {
    console.log('not_installed');
}
"""
                result = subprocess.run(
                    ['node', '-e', test_script],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if 'available' in result.stdout:
                    self._available = True
                    rprint(f"[green]✅ 0G Storage SDK available via TypeScript[/green]")
                    rprint(f"[cyan]   Storage Node: {self.storage_node}[/cyan]")
                else:
                    rprint("[yellow]⚠️  @0glabs/0g-ts-sdk not installed[/yellow]")
                    rprint("[cyan]📘 Install: pnpm add @0glabs/0g-ts-sdk[/cyan]")
            else:
                rprint("[yellow]⚠️  Node.js not found[/yellow]")
                rprint("[cyan]📘 Install Node.js: https://nodejs.org/[/cyan]")
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            rprint("[yellow]⚠️  Node.js not available[/yellow]")
            rprint("[cyan]📘 Install Node.js to use 0G Storage[/cyan]")
    
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
        Upload data to 0G Storage using TypeScript SDK.
        
        Args:
            blob: Data to store (binary)
            mime: Optional MIME type
            tags: Optional metadata tags (stored as JSON string)
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
                error="0G Storage SDK not available"
            )
        
        try:
            # Write data to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as tmp:
                tmp.write(blob)
                tmp_path = tmp.name
            
            # Compute hash for reference
            data_hash = self._compute_hash(blob)
            
            rprint(f"[yellow]📤 Uploading {len(blob)} bytes to 0G Storage...[/yellow]")
            
            # Create Node.js script for upload
            upload_script = f"""
const {{ Indexer, ZgFile }} = require('@0glabs/0g-ts-sdk');
const {{ ethers }} = require('ethers');
const fs = require('fs');

async function upload() {{
    try {{
        // Setup provider and wallet
        const provider = new ethers.JsonRpcProvider('{self.evm_rpc}');
        const wallet = new ethers.Wallet('{self.private_key}', provider);
        
        // Create indexer instance
        const indexer = new Indexer('{self.storage_node}');
        
        // Read file
        const buffer = fs.readFileSync('{tmp_path}');
        
        // Create ZgFile
        const file = new ZgFile(buffer);
        
        // Upload file
        const [tx, error] = await indexer.upload(file, 0, wallet);
        
        if (error) {{
            console.error(JSON.stringify({{
                success: false,
                error: error.message || error.toString()
            }}));
            process.exit(1);
        }}
        
        // Wait for transaction
        const receipt = await tx.wait();
        
        console.log(JSON.stringify({{
            success: true,
            root_hash: file.merkleRoot(),
            tx_hash: receipt.hash,
            size: buffer.length
        }}));
        
    }} catch (error) {{
        console.error(JSON.stringify({{
            success: false,
            error: error.message || error.toString()
        }}));
        process.exit(1);
    }}
}}

upload();
"""
            
            # Execute upload
            result = subprocess.run(
                ['node', '-e', upload_script],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes for large files
            )
            
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)
            
            # Parse result (get last line which is JSON)
            stdout_lines = result.stdout.strip().split('\n')
            json_line = stdout_lines[-1] if stdout_lines else '{}'
            
            try:
                upload_result = json.loads(json_line)
            except json.JSONDecodeError as e:
                rprint(f"[red]Failed to parse 0G Storage response:[/red]")
                rprint(f"[yellow]stdout: {result.stdout[:500]}[/yellow]")
                rprint(f"[yellow]stderr: {result.stderr[:500]}[/yellow]")
                return StorageResult(
                    success=False,
                    uri="",
                    hash=data_hash,
                    provider="0G_Storage",
                    error=f"Invalid JSON response: {e}"
                )
            
            if not upload_result.get('success'):
                error_msg = upload_result.get('error', 'Upload failed')
                rprint(f"[red]❌ Upload failed: {error_msg}[/red]")
                return StorageResult(
                    success=False,
                    uri="",
                    hash=data_hash,
                    provider="0G_Storage",
                    error=error_msg
                )
            
            root_hash = upload_result['root_hash']
            tx_hash = upload_result['tx_hash']
            
            # Build URI (0G uses root hash as identifier)
            uri = f"0g://{root_hash}"
            
            rprint(f"[green]✅ Uploaded to 0G Storage[/green]")
            rprint(f"[cyan]   Root Hash: {root_hash}[/cyan]")
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
        Retrieve data from 0G Storage using TypeScript SDK.
        
        Args:
            uri: URI of the data (e.g., "0g://0x..." or just the root hash)
        
        Returns:
            Tuple of (data bytes, metadata dict)
        
        Raises:
            Exception: If retrieval fails
        """
        if not self._available:
            raise Exception("0G Storage SDK not available")
        
        try:
            # Extract root hash from URI
            root_hash = uri.replace('0g://', '').strip()
            
            # Create temp file for download
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.bin')
            tmp_path = tmp_file.name
            tmp_file.close()
            
            rprint(f"[yellow]📥 Downloading from 0G Storage: {root_hash[:16]}...[/yellow]")
            
            # Create Node.js script for download
            download_script = f"""
const {{ Downloader }} = require('@0glabs/0g-ts-sdk');
const fs = require('fs');

async function download() {{
    try {{
        // Create downloader instance
        const downloader = new Downloader('{self.storage_node}');
        
        // Download file by root hash
        const buffer = await downloader.downloadFile('{root_hash}');
        
        if (!buffer) {{
            console.error(JSON.stringify({{
                success: false,
                error: 'File not found'
            }}));
            process.exit(1);
        }}
        
        // Write to temp file
        fs.writeFileSync('{tmp_path}', buffer);
        
        console.log(JSON.stringify({{
            success: true,
            size: buffer.length
        }}));
        
    }} catch (error) {{
        console.error(JSON.stringify({{
            success: false,
            error: error.message || error.toString()
        }}));
        process.exit(1);
    }}
}}

download();
"""
            
            # Execute download
            result = subprocess.run(
                ['node', '-e', download_script],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )
            
            # Parse result
            stdout_lines = result.stdout.strip().split('\n')
            json_line = stdout_lines[-1] if stdout_lines else '{}'
            
            try:
                download_result = json.loads(json_line)
            except json.JSONDecodeError:
                Path(tmp_path).unlink(missing_ok=True)
                rprint(f"[red]Failed to parse 0G Storage response:[/red]")
                rprint(f"[yellow]stderr: {result.stderr[:500]}[/yellow]")
                raise Exception("Invalid JSON response from download")
            
            if not download_result.get('success'):
                Path(tmp_path).unlink(missing_ok=True)
                error_msg = download_result.get('error', 'Download failed')
                rprint(f"[red]❌ Download failed: {error_msg}[/red]")
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

