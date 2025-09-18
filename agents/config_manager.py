"""
Configuration Manager for ChaosChain Genesis Studio

This module provides centralized configuration management for production deployments,
replacing hardcoded values with dynamic, environment-aware configuration.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
from rich import print as rprint

class ChaosChainConfig:
    """
    Production-ready configuration manager for ChaosChain
    
    Supports multiple environments, environment variable substitution,
    and secure configuration management.
    """
    
    def __init__(self, environment: str = "production", config_dir: str = "config"):
        """
        Initialize configuration manager
        
        Args:
            environment: Environment name (production, staging, development)
            config_dir: Directory containing configuration files
        """
        self.environment = environment
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / f"{environment}.json"
        
        # Load configuration
        self.config = self._load_config()
        
        # Substitute environment variables
        self._substitute_env_vars()
        
        rprint(f"[green]✅ Configuration loaded for {environment} environment[/green]")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            rprint(f"[red]❌ Configuration file not found: {self.config_file}[/red]")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            rprint(f"[red]❌ Invalid JSON in configuration file: {e}[/red]")
            return self._get_default_config()
    
    def _substitute_env_vars(self):
        """Substitute environment variables in configuration values"""
        def substitute_recursive(obj):
            if isinstance(obj, dict):
                return {k: substitute_recursive(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [substitute_recursive(item) for item in obj]
            elif isinstance(obj, str) and obj.startswith("env:"):
                env_var = obj[4:]  # Remove "env:" prefix
                return os.getenv(env_var, obj)  # Return original if env var not found
            else:
                return obj
        
        self.config = substitute_recursive(self.config)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for fallback"""
        return {
            "chaoschain": {
                "version": "1.0.0",
                "environment": self.environment,
                "debug": False
            },
            "networks": {
                "default": "base-sepolia"
            },
            "ap2": {
                "enabled": True,
                "jwt_algorithm": "RS256"
            },
            "x402": {
                "enabled": True,
                "protocol_fee_percent": 2.5
            }
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated key path
        
        Args:
            key_path: Dot-separated path (e.g., "networks.base-sepolia.chain_id")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_network_config(self, network: str = None) -> Dict[str, Any]:
        """
        Get network configuration
        
        Args:
            network: Network name (uses default if None)
            
        Returns:
            Network configuration dictionary
        """
        if network is None:
            network = self.get("networks.default", "base-sepolia")
        
        return self.get(f"networks.{network}", {})
    
    def get_ap2_config(self) -> Dict[str, Any]:
        """Get AP2 configuration"""
        return self.get("ap2", {})
    
    def get_x402_config(self) -> Dict[str, Any]:
        """Get x402 configuration"""
        return self.get("x402", {})
    
    def get_a2a_x402_config(self) -> Dict[str, Any]:
        """Get A2A-x402 extension configuration"""
        return self.get("a2a_x402", {})
    
    def get_ipfs_config(self) -> Dict[str, Any]:
        """Get IPFS configuration"""
        return self.get("ipfs", {})
    
    def get_erc8004_config(self) -> Dict[str, Any]:
        """Get ERC-8004 configuration"""
        return self.get("erc8004", {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return self.get("security", {})
    
    def is_enabled(self, feature: str) -> bool:
        """
        Check if a feature is enabled
        
        Args:
            feature: Feature name (e.g., "ap2", "x402", "ipfs")
            
        Returns:
            True if feature is enabled
        """
        return self.get(f"{feature}.enabled", False)
    
    def get_key_storage_path(self) -> str:
        """Get path for key storage"""
        return self.get("security.key_storage_path", "./keys")
    
    def get_treasury_address(self) -> str:
        """Get treasury address for protocol fees"""
        return self.get("x402.treasury_address", "0x20E7B2A2c8969725b88Dd3EF3a11Bc3353C83F70")
    
    def get_protocol_fee_percent(self) -> float:
        """Get protocol fee percentage"""
        return self.get("x402.protocol_fee_percent", 2.5)
    
    def validate_config(self) -> bool:
        """
        Validate configuration for required fields
        
        Returns:
            True if configuration is valid
        """
        required_fields = [
            "chaoschain.version",
            "networks.default",
            "ap2.jwt_algorithm",
            "x402.protocol_fee_percent"
        ]
        
        for field in required_fields:
            if self.get(field) is None:
                rprint(f"[red]❌ Missing required configuration: {field}[/red]")
                return False
        
        rprint(f"[green]✅ Configuration validation passed[/green]")
        return True
    
    def get_agent_domain_template(self) -> str:
        """Get agent domain template"""
        return "{agent_name}.chaoschain-genesis-studio.com"
    
    def format_agent_domain(self, agent_name: str) -> str:
        """Format agent domain for given agent name"""
        template = self.get_agent_domain_template()
        return template.format(agent_name=agent_name.lower())
    
    def get_summary(self) -> Dict[str, Any]:
        """Get configuration summary for display"""
        return {
            "environment": self.environment,
            "version": self.get("chaoschain.version"),
            "default_network": self.get("networks.default"),
            "features_enabled": {
                "ap2": self.is_enabled("ap2"),
                "x402": self.is_enabled("x402"),
                "a2a_x402": self.is_enabled("a2a_x402"),
                "ipfs": self.is_enabled("ipfs"),
                "process_integrity": self.is_enabled("process_integrity")
            },
            "security": {
                "jwt_algorithm": self.get("ap2.jwt_algorithm"),
                "key_storage": self.get_key_storage_path(),
                "https_required": self.get("security.require_https", True)
            }
        }

# Global configuration instance
_config_instance = None

def get_config(environment: str = "production") -> ChaosChainConfig:
    """
    Get global configuration instance
    
    Args:
        environment: Environment name
        
    Returns:
        ChaosChainConfig instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ChaosChainConfig(environment)
    return _config_instance

# Test the configuration manager
if __name__ == "__main__":
    rprint("\n🧪 Testing Configuration Manager")
    rprint("=" * 50)
    
    # Test configuration loading
    config = ChaosChainConfig("production")
    
    # Validate configuration
    config.validate_config()
    
    # Show summary
    summary = config.get_summary()
    rprint(f"\n📋 Configuration Summary:")
    rprint(f"   Environment: {summary['environment']}")
    rprint(f"   Version: {summary['version']}")
    rprint(f"   Network: {summary['default_network']}")
    rprint(f"   Features: {list(summary['features_enabled'].keys())}")
    
    # Test specific configurations
    rprint(f"\n🔧 Network Config:")
    network_config = config.get_network_config()
    rprint(f"   Chain ID: {network_config.get('chain_id')}")
    rprint(f"   Explorer: {network_config.get('explorer')}")
    
    rprint(f"\n🔐 Security Config:")
    rprint(f"   JWT Algorithm: {config.get('ap2.jwt_algorithm')}")
    rprint(f"   Key Storage: {config.get_key_storage_path()}")
    rprint(f"   Protocol Fee: {config.get_protocol_fee_percent()}%")
