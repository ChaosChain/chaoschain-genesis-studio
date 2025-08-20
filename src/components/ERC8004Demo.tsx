import React, { useState } from 'react';
import { useAccount } from 'wagmi';
import AgentRegistration from './AgentRegistration';
import ReputationFeedback from './ReputationFeedback';
import ValidationRequest from './ValidationRequest';
import AgentCard from './AgentCard';
import { DEMO_AGENTS } from '../contracts/config';

enum DemoStep {
  CONNECT_WALLET = 0,
  REGISTER_AGENT = 1,
  REPUTATION_FEEDBACK = 2,
  VALIDATION_REQUEST = 3,
  DEMO_COMPLETE = 4
}

const ERC8004Demo: React.FC = () => {
  const { address, isConnected } = useAccount();
  const [currentStep, setCurrentStep] = useState<DemoStep>(DemoStep.CONNECT_WALLET);
  const [registeredAgentId, setRegisteredAgentId] = useState<number | null>(null);
  const [feedbackAuthId, setFeedbackAuthId] = useState<string | null>(null);
  const [validationDataHash, setValidationDataHash] = useState<string | null>(null);

  // Move to the next step when wallet is connected
  React.useEffect(() => {
    if (isConnected && currentStep === DemoStep.CONNECT_WALLET) {
      setCurrentStep(DemoStep.REGISTER_AGENT);
    }
  }, [isConnected, currentStep]);

  const handleAgentRegistered = (agentId: number) => {
    setRegisteredAgentId(agentId);
    setCurrentStep(DemoStep.REPUTATION_FEEDBACK);
  };

  const handleFeedbackAuthorized = (authId: string) => {
    setFeedbackAuthId(authId);
    setCurrentStep(DemoStep.VALIDATION_REQUEST);
  };

  const handleValidationRequested = (dataHash: string) => {
    setValidationDataHash(dataHash);
    setCurrentStep(DemoStep.DEMO_COMPLETE);
  };

  const resetDemo = () => {
    setCurrentStep(DemoStep.REGISTER_AGENT);
    setRegisteredAgentId(null);
    setFeedbackAuthId(null);
    setValidationDataHash(null);
  };

  return (
    <div className="erc8004-demo">
      <h1>ERC-8004 Trustless Agents Demo</h1>
      
      <div className="demo-progress">
        <div className={`step ${currentStep >= DemoStep.CONNECT_WALLET ? 'active' : ''}`}>
          1. Connect Wallet
        </div>
        <div className={`step ${currentStep >= DemoStep.REGISTER_AGENT ? 'active' : ''}`}>
          2. Register Agent
        </div>
        <div className={`step ${currentStep >= DemoStep.REPUTATION_FEEDBACK ? 'active' : ''}`}>
          3. Reputation Feedback
        </div>
        <div className={`step ${currentStep >= DemoStep.VALIDATION_REQUEST ? 'active' : ''}`}>
          4. Validation Request
        </div>
        <div className={`step ${currentStep >= DemoStep.DEMO_COMPLETE ? 'active' : ''}`}>
          5. Complete
        </div>
      </div>
      
      <div className="demo-content">
        {!isConnected ? (
          <div className="connect-wallet-step">
            <h2>Step 1: Connect Your Wallet</h2>
            <p>Please connect your wallet to begin the ERC-8004 demo.</p>
          </div>
        ) : (
          <>
            {currentStep === DemoStep.REGISTER_AGENT && (
              <div className="register-agent-step">
                <h2>Step 2: Register as an Agent</h2>
                <AgentRegistration onRegister={handleAgentRegistered} />
              </div>
            )}
            
            {currentStep === DemoStep.REPUTATION_FEEDBACK && (
              <div className="reputation-feedback-step">
                <h2>Step 3: Authorize Reputation Feedback</h2>
                <p>Now that you're registered as Agent #{registeredAgentId}, authorize feedback between a client and server agent.</p>
                <ReputationFeedback onFeedbackAuthorized={handleFeedbackAuthorized} />
              </div>
            )}
            
            {currentStep === DemoStep.VALIDATION_REQUEST && (
              <div className="validation-request-step">
                <h2>Step 4: Request Task Validation</h2>
                <p>Feedback has been authorized with ID: {feedbackAuthId?.substring(0, 10)}...</p>
                <p>Now, request validation of a task by a validator agent.</p>
                <ValidationRequest onValidationRequested={handleValidationRequested} />
              </div>
            )}
            
            {currentStep === DemoStep.DEMO_COMPLETE && (
              <div className="demo-complete-step">
                <h2>Demo Complete!</h2>
                <p>Congratulations! You've successfully completed the ERC-8004 Trustless Agents demo.</p>
                <p>You've experienced the three core components of the ERC-8004 standard:</p>
                
                <div className="demo-summary">
                  <div className="summary-item">
                    <h3>1. Identity Registry</h3>
                    <p>You registered as Agent #{registeredAgentId}</p>
                    <AgentCard 
                      agentId={registeredAgentId || 0}
                      agentDomain={`your-agent-${registeredAgentId}.example.com`}
                      agentAddress={address || ''}
                    />
                  </div>
                  
                  <div className="summary-item">
                    <h3>2. Reputation Registry</h3>
                    <p>You authorized feedback between Client Agent #{DEMO_AGENTS.client.id} and Server Agent #{DEMO_AGENTS.server.id}</p>
                    <p>Feedback Authorization ID: {feedbackAuthId?.substring(0, 10)}...</p>
                  </div>
                  
                  <div className="summary-item">
                    <h3>3. Validation Registry</h3>
                    <p>You requested validation from Validator Agent #{DEMO_AGENTS.validator.id} for Server Agent #{DEMO_AGENTS.server.id}</p>
                    <p>Data Hash: {validationDataHash?.substring(0, 10)}...</p>
                  </div>
                </div>
                
                <button onClick={resetDemo}>Restart Demo</button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default ERC8004Demo;

