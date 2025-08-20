# ERC-8004 Frontend Implementation

This frontend application demonstrates the ERC-8004 Trustless Agents standard, which extends the Agent-to-Agent (A2A) Protocol with a trust layer that allows participants to discover, choose, and interact with agents across organizational boundaries without pre-existing trust.

## Overview

The ERC-8004 standard introduces three lightweight, on-chain registries:

1. **Identity Registry**: A minimal on-chain handle that resolves to an agent's off-chain AgentCard, providing every agent with a portable, censorship-resistant identifier.

2. **Reputation Registry**: A standard interface for posting and fetching attestations. Scoring and aggregation will likely occur off-chain, enabling an ecosystem of specialized services.

3. **Validation Registry**: Generic hooks for requesting and recording independent checks through economic staking (validators re-running the job) or cryptographic proofs (TEEs attestations).

## Demo Application

The demo application provides an interactive way to experience the ERC-8004 standard in action. It guides users through the following steps:

1. **Connect Wallet**: Connect your Ethereum wallet to interact with the ERC-8004 contracts.

2. **Register Agent**: Register as an agent in the Identity Registry, providing a domain and wallet address.

3. **Reputation Feedback**: Authorize feedback between a client and server agent using the Reputation Registry.

4. **Validation Request**: Request validation of a task by a validator agent using the Validation Registry.

## Project Structure

```
src/
├── components/
│   ├── AgentCard.tsx           # Component to display agent information
│   ├── AgentRegistration.tsx   # Component for registering agents
│   ├── ERC8004Demo.tsx         # Main demo component with step-by-step flow
│   ├── ReputationFeedback.tsx  # Component for reputation feedback
│   └── ValidationRequest.tsx   # Component for validation requests
├── contracts/
│   ├── abis.ts                 # Contract ABIs for the three registries
│   ├── config.ts               # Contract addresses and network configuration
│   └── hooks.ts                # React hooks for contract interactions
├── pages/
│   ├── ERC8004DemoPage.tsx     # Demo page component
│   └── HomePage.tsx            # Home page component
├── App.tsx                     # Main application component
├── index.css                   # Global styles
└── main.tsx                    # Application entry point
```

## Contract Interactions

The application interacts with the three ERC-8004 registries using the following hooks:

### Identity Registry

- `useRegisterAgent`: Register a new agent with a domain and address
- `useGetAgent`: Get agent information by ID

### Reputation Registry

- `useAcceptFeedback`: Authorize feedback between a client and server agent

### Validation Registry

- `useRequestValidation`: Request validation of a task by a validator agent

## Getting Started

1. Clone the repository
2. Install dependencies: `npm install`
3. Start the development server: `npm run dev`
4. Open your browser to the URL shown in the terminal (typically http://localhost:5173/)

## Deployment

To build the application for production:

```bash
npm run build
```

The built files will be in the `dist` directory and can be deployed to any static hosting service.

## Configuration

To use the application with your own ERC-8004 contracts, update the contract addresses in `src/contracts/config.ts`:

```typescript
export const CONTRACT_ADDRESSES = {
  identityRegistry: "YOUR_IDENTITY_REGISTRY_ADDRESS",
  reputationRegistry: "YOUR_REPUTATION_REGISTRY_ADDRESS",
  validationRegistry: "YOUR_VALIDATION_REGISTRY_ADDRESS"
};
```

## Learn More

To learn more about the ERC-8004 standard, visit [EIP-8004](https://eips.ethereum.org/EIPS/eip-8004).

