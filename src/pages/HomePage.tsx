import React from 'react';
import { Link } from 'react-router-dom';

const HomePage: React.FC = () => {
  return (
    <div className="home-page">
      <header className="hero">
        <h1>ERC-8004: Trustless Agents</h1>
        <p className="subtitle">A standard for discovering agents and establishing trust through reputation and validation</p>
        <Link to="/erc8004-demo" className="cta-button">Try the Demo</Link>
      </header>
      
      <section className="overview">
        <h2>What is ERC-8004?</h2>
        <p>
          ERC-8004 extends the Agent-to-Agent (A2A) Protocol with a trust layer that allows participants to 
          <strong>discover, choose, and interact with agents across organizational boundaries</strong> without pre-existing trust.
        </p>
        <p>
          It introduces three <strong>lightweight, on-chain registries</strong>—Identity, Reputation, and Validation—and 
          leaves application-specific logic to off-chain components.
        </p>
      </section>
      
      <section className="registries">
        <h2>The Three Core Registries</h2>
        
        <div className="registry-card">
          <h3>1. Identity Registry</h3>
          <p>A minimal on-chain handle that resolves to an agent's off-chain AgentCard, providing every agent with a portable, censorship-resistant identifier.</p>
        </div>
        
        <div className="registry-card">
          <h3>2. Reputation Registry</h3>
          <p>A standard interface for posting and fetching attestations. Scoring and aggregation will likely occur off-chain, enabling an ecosystem of specialized services.</p>
        </div>
        
        <div className="registry-card">
          <h3>3. Validation Registry</h3>
          <p>Generic hooks for requesting and recording independent checks through economic staking (validators re-running the job) or cryptographic proofs (TEEs attestations).</p>
        </div>
      </section>
      
      <section className="cta">
        <h2>Experience ERC-8004 in Action</h2>
        <p>Try our interactive demo to see how the three registries work together to create a trustless agent ecosystem.</p>
        <Link to="/erc8004-demo" className="cta-button">Launch Demo</Link>
      </section>
      
      <footer>
        <p>Learn more about ERC-8004 at <a href="https://eips.ethereum.org/EIPS/eip-8004" target="_blank" rel="noopener noreferrer">eips.ethereum.org/EIPS/eip-8004</a></p>
      </footer>
    </div>
  );
};

export default HomePage;
