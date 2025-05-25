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
    owner: process.env.GITHUB_OWNER || 'your-github-username',
    repo: process.env.GITHUB_REPO || 'project-eagle',
    branch: process.env.GITHUB_BRANCH || 'main',
    tokenSecretName: process.env.GITHUB_TOKEN_SECRET_NAME || 'github-token'
  }
}; 