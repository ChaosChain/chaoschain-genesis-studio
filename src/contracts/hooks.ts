import { useContractRead, useContractWrite, usePrepareContractWrite } from 'wagmi';
import { IdentityRegistryABI, ReputationRegistryABI, ValidationRegistryABI } from './abis';
import { CONTRACT_ADDRESSES } from './config';
import { parseEther } from 'ethers/lib/utils';

// Identity Registry Hooks
export function useRegisterAgent(agentDomain: string, agentAddress: string) {
  const { config } = usePrepareContractWrite({
    address: CONTRACT_ADDRESSES.identityRegistry,
    abi: IdentityRegistryABI,
    functionName: 'newAgent',
    args: [agentDomain, agentAddress],
    overrides: {
      value: parseEther('0.005'), // Registration fee
    },
  });
  
  return useContractWrite(config);
}

export function useGetAgent(agentId: number) {
  return useContractRead({
    address: CONTRACT_ADDRESSES.identityRegistry,
    abi: IdentityRegistryABI,
    functionName: 'getAgent',
    args: [agentId],
  });
}

// Reputation Registry Hooks
export function useAcceptFeedback(clientAgentId: number, serverAgentId: number) {
  const { config } = usePrepareContractWrite({
    address: CONTRACT_ADDRESSES.reputationRegistry,
    abi: ReputationRegistryABI,
    functionName: 'acceptFeedback',
    args: [clientAgentId, serverAgentId],
  });
  
  return useContractWrite(config);
}

// Validation Registry Hooks
export function useRequestValidation(validatorAgentId: number, serverAgentId: number, dataHash: string) {
  const { config } = usePrepareContractWrite({
    address: CONTRACT_ADDRESSES.validationRegistry,
    abi: ValidationRegistryABI,
    functionName: 'validationRequest',
    args: [validatorAgentId, serverAgentId, dataHash],
  });
  
  return useContractWrite(config);
}

