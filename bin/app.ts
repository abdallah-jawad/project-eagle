#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { ComputerVisionStack } from '../lib/computer-vision-stack';
import { RtspKvsStack } from '../lib/rtsp-kvs-stack';
import { deploymentConfig } from '../config/deployment-config';
import { KvsStack } from '../lib/kvs-stack';

const app = new cdk.App();

// Create the KvsStack
const kvsStack = new KvsStack(app, 'KvsStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION
  }
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
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION
  }
});

// Create the ComputerVisionStack and pass the VPC from RtspKvsStack
new ComputerVisionStack(app, 'ComputerVisionStack', {
  vpc: rtspKvsStack.vpc,
  appConfigApp: kvsStack.appConfigApp,
  appConfigEnv: kvsStack.appConfigEnv,
  appConfigProfile: kvsStack.appConfigProfile,
  cameraConfigs: kvsStack.cameraConfigs,
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION
  }
}); 