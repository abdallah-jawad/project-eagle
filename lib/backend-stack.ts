import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import { DeploymentStack } from './deployment-stack';
import { deploymentConfig } from '../config/deployment-config';

export interface BackendStackProps extends cdk.StackProps {
  environment: string;
}

export class BackendStack extends cdk.Stack {
  public readonly apiEndpoint: string;

  constructor(scope: Construct, id: string, props: BackendStackProps) {
    super(scope, id, props);

    const vpc = new ec2.Vpc(this, 'BackendVpc', {
      maxAzs: 2,
      natGateways: 1, 
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

    // Allow inbound traffic on port 8080
    securityGroup.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.tcp(8080),
      'Allow traffic on port 8080'
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
        iam.ManagedPolicy.fromAwsManagedPolicyName('AWSCodeDeployFullAccess'),
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
        'appconfig:*'
      ],
      resources: ['*']
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
        `*`,
      ],
    }));

    // Add JWT secret permissions
    role.addToPolicy(new iam.PolicyStatement({
      actions: [
        'secretsmanager:GetSecretValue',
      ],
      resources: [`*`],
    }));

    // Add full KMS permissions
    role.addToPolicy(new iam.PolicyStatement({
      actions: [
        'kms:Decrypt',
        'kms:DescribeKey',
        'kms:Encrypt',
        'kms:ReEncrypt*',
        'kms:GenerateDataKey*',
        'kms:CreateGrant',
        'kms:ListGrants',
        'kms:RevokeGrant'
      ],
      resources: ['*']
    }));

    role.addToPolicy(new iam.PolicyStatement({
      actions: [
        's3:GetObject',
        's3:GetObjectVersion',
        's3:ListBucket',
        's3:ListAllMyBuckets'
      ],
      resources: [
        'arn:aws:s3:::*',
        'arn:aws:s3:::*/*'
      ]
    }));

    // Create EC2 instance
    const instance = new ec2.Instance(this, 'BackendInstance', {
      vpc,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PUBLIC,
      },
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.SMALL),
      machineImage: ec2.MachineImage.latestAmazonLinux2(),
      securityGroup,
      role,
      userData: ec2.UserData.forLinux(),
    });

    // Add tags to the instance
    cdk.Tags.of(instance).add('Name', 'BackendInstance');
    cdk.Tags.of(instance).add('Environment', 'production');
    cdk.Tags.of(instance).add('Stack', 'backend');

    // Add improved user data script with better logging
    instance.userData.addCommands(
      '#!/bin/bash',
      '# UserData Version: 1.0',
      'exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1',
      'echo "User data script started execution."'
    );

    // Update system and install required packages
    instance.userData.addCommands(
      'echo "Updating system and installing required packages..." >> /var/log/user-data.log',
      'yum update -y >> /var/log/user-data.log 2>&1',
      'yum install -y ruby wget python3 python3-pip unzip aws-cli >> /var/log/user-data.log 2>&1',
      'echo "System updated and required packages installed." >> /var/log/user-data.log'
    );

    // Install and configure CodeDeploy agent
    instance.userData.addCommands(
      'echo "Installing CodeDeploy agent..." >> /var/log/user-data.log',
      'REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/region) >> /var/log/user-data.log 2>&1',
      'wget https://aws-codedeploy-${REGION}.s3.amazonaws.com/latest/install >> /var/log/user-data.log 2>&1',
      'chmod +x ./install >> /var/log/user-data.log 2>&1',
      './install auto >> /var/log/user-data.log 2>&1',
      'service codedeploy-agent start >> /var/log/user-data.log 2>&1',
      'echo "CodeDeploy agent installed and started." >> /var/log/user-data.log'
    );

    // Create application directory
    instance.userData.addCommands(
      'echo "Creating application directory..." >> /var/log/user-data.log',
      'mkdir -p /opt/backend >> /var/log/user-data.log 2>&1',
      'chown -R ec2-user:ec2-user /opt/backend >> /var/log/user-data.log 2>&1',
      'echo "Application directory created." >> /var/log/user-data.log'
    );

    // Create deployment stack
    new DeploymentStack(this, 'BackendDeploymentStack', {
      instance,
      github: deploymentConfig.github,
      watchDirectory: 'backend',
      applicationName: 'BackendApplication',
      pipelineName: 'BackendPipeline'
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