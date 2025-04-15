#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { ComputerVisionStack } from '../lib/computer-vision-stack';
import { RtspKvsStack } from '../lib/rtsp-kvs-stack';
import { deploymentConfig } from '../config/deployment-config';

const app = new cdk.App();

// Create the RtspKvsStack first
const rtspKvsStack = new RtspKvsStack(app, 'RtspKvsStack', {
  myIpAddress: deploymentConfig.myIpAddress,
  keyPairName: deploymentConfig.keyPairName,
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION
  }
});

// Create the ComputerVisionStack and pass the VPC from RtspKvsStack
new ComputerVisionStack(app, 'ComputerVisionStack', {
  vpc: undefined,
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION
  }
}); 