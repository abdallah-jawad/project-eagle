export interface DeploymentConfig {
  myIpAddress: string;
  keyPairName: string;
}

export const deploymentConfig: DeploymentConfig = {
  myIpAddress: '70.175.157.61',  
  keyPairName: 'ingestion-server-access-key'
}; 