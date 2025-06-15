import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import { InstanceTypeUtils } from './utils/instance-type-utils';
import * as path from 'path';
import { Asset } from 'aws-cdk-lib/aws-s3-assets';
import * as appconfig from 'aws-cdk-lib/aws-appconfig';

export interface ComputerVisionStackProps extends cdk.StackProps {
  vpc?: ec2.IVpc;
  environment: string;
}

export class ComputerVisionStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: ComputerVisionStackProps) {
    super(scope, id, props);
    
    // Use the provided VPC or create a new one
    const vpc = props?.vpc || new ec2.Vpc(this, 'ComputerVisionVpc', {
      maxAzs: 2,
      natGateways: 1,
    });

    // Create a security group for the EC2 instance
    const securityGroup = new ec2.SecurityGroup(this, 'ComputerVisionSecurityGroup', {
      vpc,
      description: 'Security group for Computer Vision EC2 instance',
      allowAllOutbound: true,
    });

    // Allow SSH access from EC2 Instance Connect service
    securityGroup.addIngressRule(
      ec2.Peer.prefixList('pl-0e4bcff02b13bef1e'),
      ec2.Port.tcp(22),
      'Allow EC2 Instance Connect'
    );

    // Create an IAM role for the EC2 instance
    const role = new iam.Role(this, 'ComputerVisionEc2Role', {
      assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSSMManagedInstanceCore'),
      ],
    });

    // Add EC2 Instance Connect permissions
    role.addToPolicy(new iam.PolicyStatement({
      actions: [
        'ec2-instance-connect:SendSSHPublicKey'
      ],
      resources: ['*']
    }));

    // Create DynamoDB table for detections
    const detectionsTable = new dynamodb.Table(this, 'DetectionsTable', {
      tableName: 'detections',
      partitionKey: { name: 'timestamp', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'frame_id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      pointInTimeRecovery: true,
    });

    // Add GSI for querying by detection class and timestamp
    detectionsTable.addGlobalSecondaryIndex({
      indexName: 'DetectionClassTimestampIndex',
      partitionKey: { name: 'detection_class', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.STRING },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    // Add broad permissions for AppConfig
    role.addToPolicy(new iam.PolicyStatement({
      actions: [
        'appconfig:*'
      ],
      resources: ['*']
    }));

    // Add broad permissions for DynamoDB
    role.addToPolicy(new iam.PolicyStatement({
      actions: [
        'dynamodb:*'
      ],
      resources: ['*']
    }));

    // Add broad permissions for Secrets Manager
    role.addToPolicy(new iam.PolicyStatement({
      actions: [
        'secretsmanager:*'
      ],
      resources: ['*']
    }));

    // Create assets for our application files
    const appFiles = new Asset(this, 'ComputerVisionAppFiles', {
      path: path.join(__dirname, '..', 'computer-vision/src'),
    });

    // Create asset for requirements.txt
    const requirementsFile = new Asset(this, 'ComputerVisionRequirements', {
      path: path.join(__dirname, '..', 'computer-vision/requirements.txt'),
    });

    // Create the EC2 instance with a larger instance type since we'll be fetching configs at runtime
    const ec2Instance = new ec2.Instance(this, 'ComputerVisionInstance', {
      vpc,
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MEDIUM),
      machineImage: ec2.MachineImage.latestAmazonLinux2(),
      securityGroup,
      role,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PUBLIC,
      },
      instanceName: 'ComputerVisionInstanceV2',
    });

    // Grant the instance permission to read the application files
    appFiles.grantRead(role);
    requirementsFile.grantRead(role);

    // Add user data script
    const userData = ec2Instance.userData;

    // Add shebang and basic logging setup
    userData.addCommands(
      '#!/bin/bash',
      '# UserData Version: 1.0',
      'exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1', // Redirect stdout/stderr to log file and console
      'echo "User data script started execution."'
    );

    // Install required system packages
    userData.addCommands(
      'echo "Installing required system packages..." >> /var/log/user-data.log',
      'yum update -y >> /var/log/user-data.log 2>&1',
      'yum install -y python3 python3-pip unzip aws-cli >> /var/log/user-data.log 2>&1',
      'echo "Required system packages installed." >> /var/log/user-data.log'
    );

    // Download application files
    userData.addS3DownloadCommand({
      bucket: appFiles.bucket,
      bucketKey: appFiles.s3ObjectKey,
      localFile: '/tmp/computer-vision.zip',
    });
    
    // Download requirements.txt
    userData.addS3DownloadCommand({
      bucket: requirementsFile.bucket,
      bucketKey: requirementsFile.s3ObjectKey,
      localFile: '/tmp/requirements.txt',
    });
    
    // Extract application files
    userData.addCommands(
      'echo "Extracting application files..." >> /var/log/user-data.log',
      'mkdir -p /tmp/computer-vision >> /var/log/user-data.log 2>&1',
      'unzip -o /tmp/computer-vision.zip -d /tmp/computer-vision/ >> /var/log/user-data.log 2>&1',
      'chmod +x /tmp/computer-vision/setup.sh >> /var/log/user-data.log 2>&1',
      'echo "Application files extracted." >> /var/log/user-data.log'
    );

    // Install Python packages from requirements.txt
    userData.addCommands(
      'echo "Installing Python packages from requirements.txt..." >> /var/log/user-data.log',
      'pip3 install -r /tmp/requirements.txt >> /var/log/user-data.log 2>&1',
      'echo "Python packages installed." >> /var/log/user-data.log'
    );

    // Run setup script
    userData.addCommands(
      'echo "Running setup script..." >> /var/log/user-data.log',
      'sudo bash /tmp/computer-vision/setup.sh >> /var/log/user-data.log 2>&1',
      'echo "Setup script completed." >> /var/log/user-data.log'
    );
  }
} 