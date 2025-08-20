// Contract addresses and network configuration
// For demo purposes, we'll use a testnet (e.g., Sepolia)

export const NETWORK_ID = 11155111; // Sepolia testnet

// These addresses are placeholders - replace with actual deployed contract addresses
export const CONTRACT_ADDRESSES = {
  identityRegistry: "0x1234567890123456789012345678901234567890",
  reputationRegistry: "0x2345678901234567890123456789012345678901",
  validationRegistry: "0x3456789012345678901234567890123456789012"
};

// For demo purposes, we'll use some pre-configured agents
export const DEMO_AGENTS = {
  // Client agent
  client: {
    id: 1,
    domain: "client.example.com",
    address: "0x4567890123456789012345678901234567890123"
  },
  // Server agent
  server: {
    id: 2,
    domain: "server.example.com",
    address: "0x5678901234567890123456789012345678901234"
  },
  // Validator agent
  validator: {
    id: 3,
    domain: "validator.example.com",
    address: "0x6789012345678901234567890123456789012345"
  }
};

