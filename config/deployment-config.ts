export interface DeploymentConfig {
  myIpAddress: string;
  keyPairName: string;
}

export const deploymentConfig: DeploymentConfig = {
  myIpAddress: '70.175.157.61',  
  keyPairName: 'cdk-keypair'  // Replace with key pair name
}; 