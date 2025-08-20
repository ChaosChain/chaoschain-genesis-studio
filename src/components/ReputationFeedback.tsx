import React, { useState } from 'react';
import { useAccount } from 'wagmi';
import { useAcceptFeedback } from '../contracts/hooks';
import { DEMO_AGENTS } from '../contracts/config';

interface ReputationFeedbackProps {
  onFeedbackAuthorized?: (feedbackAuthId: string) => void;
}

const ReputationFeedback: React.FC<ReputationFeedbackProps> = ({ onFeedbackAuthorized }) => {
  const { address } = useAccount();
  const [clientId, setClientId] = useState(DEMO_AGENTS.client.id);
  const [serverId, setServerId] = useState(DEMO_AGENTS.server.id);
  const [isAuthorizing, setIsAuthorizing] = useState(false);
  
  const { write: acceptFeedback, isLoading, isSuccess, data } = useAcceptFeedback(clientId, serverId);

  const handleAuthorizeFeedback = async () => {
    if (!address) return;
    
    setIsAuthorizing(true);
    acceptFeedback?.();
  };

  // When feedback authorization is successful, call the onFeedbackAuthorized callback
  React.useEffect(() => {
    if (isSuccess && data && onFeedbackAuthorized) {
      // In a real implementation, we would get the feedbackAuthId from the transaction receipt
      // For demo purposes, we'll just use a placeholder
      onFeedbackAuthorized('0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef');
    }
    setIsAuthorizing(false);
  }, [isSuccess, data, onFeedbackAuthorized]);

  return (
    <div className="reputation-feedback">
      <h2>Reputation Feedback</h2>
      <p>Authorize feedback between a client and server agent.</p>
      
      <div className="form-group">
        <label htmlFor="clientId">Client Agent ID:</label>
        <input
          type="number"
          id="clientId"
          value={clientId}
          onChange={(e) => setClientId(Number(e.target.value))}
          disabled={isAuthorizing || isLoading}
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="serverId">Server Agent ID:</label>
        <input
          type="number"
          id="serverId"
          value={serverId}
          onChange={(e) => setServerId(Number(e.target.value))}
          disabled={isAuthorizing || isLoading}
        />
      </div>
      
      <button 
        onClick={handleAuthorizeFeedback} 
        disabled={!address || isAuthorizing || isLoading}
      >
        {isAuthorizing || isLoading ? 'Authorizing...' : 'Authorize Feedback'}
      </button>
      
      {isSuccess && (
        <div className="success-message">
          Feedback authorization successful! The client can now provide feedback for this server agent.
        </div>
      )}
    </div>
  );
};

export default ReputationFeedback;

