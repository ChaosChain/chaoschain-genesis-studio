import React from 'react';
import { useAccount, useConnect, useDisconnect } from 'wagmi';
import { InjectedConnector } from 'wagmi/connectors/injected';
import ERC8004Demo from '../components/ERC8004Demo';

const ERC8004DemoPage: React.FC = () => {
  const { address, isConnected } = useAccount();
  const { connect } = useConnect({
    connector: new InjectedConnector(),
  });
  const { disconnect } = useDisconnect();

  return (
    <div className="erc8004-demo-page">
      <div className="wallet-connection">
        {!isConnected ? (
          <button onClick={() => connect()}>Connect Wallet</button>
        ) : (
          <div className="wallet-info">
            <p>Connected as: {address}</p>
            <button onClick={() => disconnect()}>Disconnect</button>
          </div>
        )}
      </div>
      
      <ERC8004Demo />
      
      <div className="demo-footer">
        <p>This is a demonstration of the ERC-8004 Trustless Agents standard.</p>
        <p>Learn more at <a href="https://eips.ethereum.org/EIPS/eip-8004" target="_blank" rel="noopener noreferrer">EIP-8004</a></p>
      </div>
    </div>
  );
};

export default ERC8004DemoPage;
