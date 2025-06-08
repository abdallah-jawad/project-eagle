export interface GitHubConfig {
  owner: string;
  repo: string;
  branch: string;
  tokenSecretName: string;
}

export interface DeploymentConfig {
  environment: string;
  myIpAddress: string;
  keyPairName: string;
  github: GitHubConfig;
}

export const deploymentConfig: DeploymentConfig = {
  environment: process.env.ENVIRONMENT || 'dev',
  myIpAddress: process.env.MY_IP_ADDRESS || '0.0.0.0/32',
  keyPairName: process.env.KEY_PAIR_NAME || 'project-eagle-key',
  github: {
    owner: 'abdallah-jawad',
    repo: 'project-eagle',
    branch: 'main',
    tokenSecretName: 'github-token'
  }
}; 