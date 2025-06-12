#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { ComputerVisionStack } from '../lib/computer-vision-stack';
import { RtspKvsStack } from '../lib/rtsp-kvs-stack';
import { deploymentConfig } from '../config/deployment-config';
import { KvsStack } from '../lib/kvs-stack';
import { AuthStack } from '../lib/auth-stack';
import { BackendStack } from '../lib/backend-stack';

const app = new cdk.App();

const env = {
  account: '091664994886',
  region: 'us-east-1',
  profile: 'eagle'
};

// Create the AuthStack
const authStack = new AuthStack(app, 'AuthStack', {
  environment: deploymentConfig.environment,
  env
});

// Create the BackendStack
const backendStack = new BackendStack(app, 'BackendStack', {
  environment: deploymentConfig.environment,
  env
}); 

// Create the KvsStack
const kvsStack = new KvsStack(app, 'KvsStack', {
  env
});

// Create the RtspKvsStack
const rtspKvsStack = new RtspKvsStack(app, 'RtspKvsStack', {
  myIpAddress: deploymentConfig.myIpAddress,
  keyPairName: deploymentConfig.keyPairName,
  cameraConfigs: {
    ...kvsStack.cameraConfigs,
    appConfigApp: kvsStack.appConfigApp,
    appConfigEnv: kvsStack.appConfigEnv,
    appConfigProfile: kvsStack.appConfigProfile
  },
  env
});

// Create the ComputerVisionStack and pass the VPC from RtspKvsStack and auth resources
const computerVisionStack = new ComputerVisionStack(app, 'ComputerVisionStack', {
  vpc: rtspKvsStack.vpc,
  appConfigApp: kvsStack.appConfigApp,
  appConfigEnv: kvsStack.appConfigEnv,
  appConfigProfile: kvsStack.appConfigProfile,
  cameraConfigs: kvsStack.cameraConfigs,
  environment: deploymentConfig.environment,
  userTable: authStack.userTable,
  jwtSecret: authStack.jwtSecret,
  env
});