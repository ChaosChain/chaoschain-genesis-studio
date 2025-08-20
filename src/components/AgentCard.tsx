import React from 'react';

interface AgentCardProps {
  agentId: number;
  agentDomain: string;
  agentAddress: string;
  trustModels?: string[];
  skills?: string[];
}

const AgentCard: React.FC<AgentCardProps> = ({ 
  agentId, 
  agentDomain, 
  agentAddress,
  trustModels = ['feedback', 'inference-validation', 'tee-attestation'],
  skills = ['text-generation', 'image-generation', 'code-generation']
}) => {
  return (
    <div className="agent-card">
      <h3>Agent #{agentId}</h3>
      
      <div className="agent-info">
        <div className="info-row">
          <span className="label">Domain:</span>
          <span className="value">{agentDomain}</span>
        </div>
        
        <div className="info-row">
          <span className="label">Address:</span>
          <span className="value">{`${agentAddress.substring(0, 6)}...${agentAddress.substring(agentAddress.length - 4)}`}</span>
        </div>
        
        <div className="info-row">
          <span className="label">Trust Models:</span>
          <div className="tags">
            {trustModels.map((model, index) => (
              <span key={index} className="tag trust-model">{model}</span>
            ))}
          </div>
        </div>
        
        <div className="info-row">
          <span className="label">Skills:</span>
          <div className="tags">
            {skills.map((skill, index) => (
              <span key={index} className="tag skill">{skill}</span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentCard;

