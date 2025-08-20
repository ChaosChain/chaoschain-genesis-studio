import React, { useState } from 'react';
import { useAccount } from 'wagmi';
import { useRegisterAgent } from '../contracts/hooks';

interface AgentRegistrationProps {
  onRegister?: (agentId: number) => void;
}

const AgentRegistration: React.FC<AgentRegistrationProps> = ({ onRegister }) => {
  const { address } = useAccount();
  const [domain, setDomain] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);
  const { write: registerAgent, isLoading, isSuccess, data } = useRegisterAgent(domain, address || '');

  const handleRegister = async () => {
    if (!address || !domain) return;
    
    setIsRegistering(true);
    registerAgent?.();
  };

  // When registration is successful, call the onRegister callback
  React.useEffect(() => {
    if (isSuccess && data && onRegister) {
      // In a real implementation, we would get the agentId from the transaction receipt
      // For demo purposes, we'll just use a placeholder
      onRegister(1);
    }
    setIsRegistering(false);
  }, [isSuccess, data, onRegister]);

  return (
    <div className="agent-registration">
      <h2>Register as an Agent</h2>
      <p>Register your wallet address as an ERC-8004 agent.</p>
      
      <div className="form-group">
        <label htmlFor="domain">Agent Domain:</label>
        <input
          type="text"
          id="domain"
          value={domain}
          onChange={(e) => setDomain(e.target.value)}
          placeholder="your-agent.example.com"
          disabled={isRegistering || isLoading}
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="address">Wallet Address:</label>
        <input
          type="text"
          id="address"
          value={address || ''}
          disabled
          placeholder="Connect your wallet first"
        />
      </div>
      
      <button 
        onClick={handleRegister} 
        disabled={!address || !domain || isRegistering || isLoading}
      >
        {isRegistering || isLoading ? 'Registering...' : 'Register Agent'}
      </button>
      
      {isSuccess && (
        <div className="success-message">
          Registration successful! Your agent is now registered on the ERC-8004 Identity Registry.
        </div>
      )}
    </div>
  );
};

export default AgentRegistration;

