// ABIs for the ERC-8004 contracts
export const IdentityRegistryABI = [
  "event AgentRegistered(uint256 indexed agentId, string agentDomain, address agentAddress)",
  "event AgentUpdated(uint256 indexed agentId, string agentDomain, address agentAddress)",
  "function getAgent(uint256 agentId) external view returns (tuple(uint256 agentId, string agentDomain, address agentAddress) agentInfo)",
  "function resolveByDomain(string calldata agentDomain) external view returns (tuple(uint256 agentId, string agentDomain, address agentAddress) agentInfo)",
  "function resolveByAddress(address agentAddress) external view returns (tuple(uint256 agentId, string agentDomain, address agentAddress) agentInfo)",
  "function getAgentCount() external view returns (uint256 count)",
  "function agentExists(uint256 agentId) external view returns (bool exists)",
  "function REGISTRATION_FEE() external pure returns (uint256 fee)",
  "function newAgent(string calldata agentDomain, address agentAddress) external payable returns (uint256 agentId)",
  "function updateAgent(uint256 agentId, string calldata newAgentDomain, address newAgentAddress) external returns (bool success)"
];

export const ReputationRegistryABI = [
  "event AuthFeedback(uint256 indexed agentClientId, uint256 indexed agentServerId, bytes32 indexed feedbackAuthId)",
  "function isFeedbackAuthorized(uint256 agentClientId, uint256 agentServerId) external view returns (bool isAuthorized, bytes32 feedbackAuthId)",
  "function getFeedbackAuthId(uint256 agentClientId, uint256 agentServerId) external view returns (bytes32 feedbackAuthId)",
  "function acceptFeedback(uint256 agentClientId, uint256 agentServerId) external"
];

export const ValidationRegistryABI = [
  "event ValidationRequestEvent(uint256 indexed agentValidatorId, uint256 indexed agentServerId, bytes32 indexed dataHash)",
  "event ValidationResponseEvent(uint256 indexed agentValidatorId, uint256 indexed agentServerId, bytes32 indexed dataHash, uint8 response)",
  "function getValidationRequest(bytes32 dataHash) external view returns (tuple(uint256 agentValidatorId, uint256 agentServerId, bytes32 dataHash, uint256 timestamp, bool responded) request)",
  "function isValidationPending(bytes32 dataHash) external view returns (bool exists, bool pending)",
  "function getValidationResponse(bytes32 dataHash) external view returns (bool hasResponse, uint8 response)",
  "function getExpirationSlots() external view returns (uint256 slots)",
  "function validationRequest(uint256 agentValidatorId, uint256 agentServerId, bytes32 dataHash) external",
  "function validationResponse(bytes32 dataHash, uint8 response) external"
];

