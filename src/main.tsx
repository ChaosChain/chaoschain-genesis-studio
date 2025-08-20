import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';
import { configureChains, createClient, WagmiConfig } from 'wagmi';
import { mainnet } from 'wagmi/chains';
import { publicProvider } from 'wagmi/providers/public';
import { InjectedConnector } from 'wagmi/connectors/injected';

const { chains, provider, webSocketProvider } = configureChains(
  [
    mainnet, // Add other chains as needed
  ],
  [
    publicProvider(),
  ]
);

const wagmiClient = createClient({
  autoConnect: true,
  connectors: [
    new InjectedConnector({ chains }),
    // Add other connectors like MetaMask, WalletConnect etc.
  ],
  provider,
  webSocketProvider,
});

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <WagmiConfig client={wagmiClient}>
      <App />
    </WagmiConfig>
  </React.StrictMode>
);

