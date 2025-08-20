import React, { useState } from 'react';
import { useAccount } from 'wagmi';
import { useRequestValidation } from '../contracts/hooks';
import { DEMO_AGENTS } from '../contracts/config';

interface ValidationRequestProps {
  onValidationRequested?: (dataHash: string) => void;
}

const ValidationRequest: React.FC<ValidationRequestProps> = ({ onValidationRequested }) => {
  const { address } = useAccount();
  const [validatorId, setValidatorId] = useState(DEMO_AGENTS.validator.id);
  const [serverId, setServerId] = useState(DEMO_AGENTS.server.id);
  const [dataHash, setDataHash] = useState('0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef');
  const [isRequesting, setIsRequesting] = useState(false);
  
  const { write: requestValidation, isLoading, isSuccess, data } = useRequestValidation(validatorId, serverId, dataHash);

  const handleRequestValidation = async () => {
    if (!address) return;
    
    setIsRequesting(true);
    requestValidation?.();
  };

  // When validation request is successful, call the onValidationRequested callback
  React.useEffect(() => {
    if (isSuccess && data && onValidationRequested) {
      onValidationRequested(dataHash);
    }
    setIsRequesting(false);
  }, [isSuccess, data, onValidationRequested, dataHash]);

  return (
    <div className="validation-request">
      <h2>Validation Request</h2>
      <p>Request validation of a task by a validator agent.</p>
      
      <div className="form-group">
        <label htmlFor="validatorId">Validator Agent ID:</label>
        <input
          type="number"
          id="validatorId"
          value={validatorId}
          onChange={(e) => setValidatorId(Number(e.target.value))}
          disabled={isRequesting || isLoading}
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="serverId">Server Agent ID:</label>
        <input
          type="number"
          id="serverId"
          value={serverId}
          onChange={(e) => setServerId(Number(e.target.value))}
          disabled={isRequesting || isLoading}
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="dataHash">Data Hash:</label>
        <input
          type="text"
          id="dataHash"
          value={dataHash}
          onChange={(e) => setDataHash(e.target.value)}
          disabled={isRequesting || isLoading}
          placeholder="0x..."
        />
      </div>
      
      <button 
        onClick={handleRequestValidation} 
        disabled={!address || !dataHash || isRequesting || isLoading}
      >
        {isRequesting || isLoading ? 'Requesting...' : 'Request Validation'}
      </button>
      
      {isSuccess && (
        <div className="success-message">
          Validation request successful! The validator can now validate this task.
        </div>
      )}
    </div>
  );
};

export default ValidationRequest;

