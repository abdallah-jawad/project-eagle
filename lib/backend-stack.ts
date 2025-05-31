import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as appconfig from 'aws-cdk-lib/aws-appconfig';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import { DeploymentStack } from './deployment-stack';
import { deploymentConfig } from '../config/deployment-config';

export interface BackendStackProps extends cdk.StackProps {
  vpc?: ec2.IVpc;
  appConfigApp: appconfig.CfnApplication;
  appConfigEnv: appconfig.CfnEnvironment;
  appConfigProfile: appconfig.CfnConfigurationProfile;
  userTable: dynamodb.Table;
  jwtSecret: secretsmanager.Secret;
  environment: string;
}

export class BackendStack extends cdk.Stack {
  public readonly apiEndpoint: string;

  constructor(scope: Construct, id: string, props: BackendStackProps) {
    super(scope, id, props);

    // Use the provided VPC or create a new one
    const vpc = props?.vpc || new ec2.Vpc(this, 'BackendVpc', {
      maxAzs: 2,
      natGateways: 0, // To keep costs down
    });

    // Create security group
    const securityGroup = new ec2.SecurityGroup(this, 'BackendSecurityGroup', {
      vpc,
      description: 'Security group for backend API',
      allowAllOutbound: true,
    });

    // Allow inbound HTTP traffic
    securityGroup.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.tcp(80),
      'Allow HTTP traffic'
    );

      // Allow SSH from EC2 Instance Connect service
    securityGroup.addIngressRule(
      ec2.Peer.prefixList('pl-0e4bcff02b13bef1e'),
      ec2.Port.tcp(22),
      'Allow EC2 Instance Connect'
    );

    // Create IAM role for EC2
    const role = new iam.Role(this, 'BackendRole', {
      assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSSMManagedInstanceCore'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('AWSCodeDeployRole'),
      ],
    });

      // Add EC2 Instance Connect permissions
      role.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSSMManagedInstanceCore'));
      role.addToPolicy(new iam.PolicyStatement({
        actions: [
          'ec2-instance-connect:SendSSHPublicKey'
        ],
        resources: ['*']
      }));
  

    // Add AppConfig permissions
    role.addToPolicy(new iam.PolicyStatement({
      actions: [
        'appconfig:GetConfiguration',
        'appconfig:StartConfigurationSession',
        'appconfig:GetLatestConfiguration'
      ],
      resources: [
        `arn:aws:appconfig:${this.region}:${this.account}:application/${props.appConfigApp.ref}/environment/${props.appConfigEnv.ref}/configuration/${props.appConfigProfile.ref}`
      ]
    }));

    // Add DynamoDB permissions
    role.addToPolicy(new iam.PolicyStatement({
      actions: [
        'dynamodb:GetItem',
        'dynamodb:PutItem',
        'dynamodb:UpdateItem',
        'dynamodb:DeleteItem',
        'dynamodb:Query',
        'dynamodb:Scan',
      ],
      resources: [
        props.userTable.tableArn,
        `${props.userTable.tableArn}/index/*`,
      ],
    }));

    // Add JWT secret permissions
    role.addToPolicy(new iam.PolicyStatement({
      actions: [
        'secretsmanager:GetSecretValue',
      ],
      resources: [props.jwtSecret.secretArn],
    }));

    // Create EC2 instance
    const instance = new ec2.Instance(this, 'BackendInstance', {
      vpc,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PUBLIC,
      },
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.T4G, ec2.InstanceSize.NANO),
      machineImage: ec2.MachineImage.latestAmazonLinux2({
        cpuType: ec2.AmazonLinuxCpuType.ARM_64,
      }),
      securityGroup,
      role,
      userData: ec2.UserData.forLinux(),
    });

    // Add basic user data to install CodeDeploy agent
    instance.userData.addCommands(
      '#!/bin/bash',
      'yum update -y',
      'yum install -y ruby wget',
      'wget https://aws-codedeploy-${AWS::Region}.s3.amazonaws.com/latest/install',
      'chmod +x ./install',
      './install auto',
      'service codedeploy-agent start'
    );

    // Create deployment stack
    new DeploymentStack(this, 'BackendDeploymentStack', {
      instance,
      github: deploymentConfig.github,
      watchDirectory: 'backend',
      applicationName: 'BackendApplication',
      pipelineName: 'BackendPipeline',
      env: {
        account: this.account,
        region: this.region
      }
    });

    // Store the API endpoint
    this.apiEndpoint = `http://${instance.instancePublicIp}`;

    // Output the API endpoint
    new cdk.CfnOutput(this, 'ApiEndpoint', {
      value: this.apiEndpoint,
      description: 'The URL of the backend API',
    });
  }
} 