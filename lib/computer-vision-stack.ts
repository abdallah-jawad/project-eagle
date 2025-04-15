import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import { deploymentConfig } from '../config/deployment-config';
import { InstanceTypeUtils } from './utils/instance-type-utils';
import * as path from 'path';
import { Asset } from 'aws-cdk-lib/aws-s3-assets';

export interface ComputerVisionStackProps extends cdk.StackProps {
  vpc?: ec2.IVpc;
}

export class ComputerVisionStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: ComputerVisionStackProps) {
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

    // Allow SSH access from the specified IP
    securityGroup.addIngressRule(
      ec2.Peer.ipv4(deploymentConfig.myIpAddress + '/32'),
      ec2.Port.tcp(22),
      'Allow SSH access'
    );

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

    // Get the recommended instance type based on the number of cameras
    const totalCameras = InstanceTypeUtils.calculateTotalCameras();
    const requiredInstanceType = InstanceTypeUtils.getRecommendedInstanceType();
    console.log(`Using instance type ${requiredInstanceType} for ${totalCameras} total cameras`);

    // Create assets for our application files
    const appFiles = new Asset(this, 'ComputerVisionAppFiles', {
      path: path.join(__dirname, '..', 'computer-vision/src'),
    });

    // Create the EC2 instance
    const ec2Instance = new ec2.Instance(this, 'ComputerVisionInstance', {
      vpc,
      instanceType: InstanceTypeUtils.getEc2InstanceType(),
      machineImage: ec2.MachineImage.latestAmazonLinux2(),
      securityGroup,
      role,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PUBLIC,
      },
    });

    // Grant the instance permission to read the application files
    appFiles.grantRead(role);

    // Add user data script
    const userData = ec2Instance.userData;

    // Add shebang and basic logging setup
    userData.addCommands(
      '#!/bin/bash',
      '# UserData Version: 1.0',
      'exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1', // Redirect stdout/stderr to log file and console
      'echo "User data script started execution."'
    );

    // Install required packages
    userData.addCommands(
      'echo "Installing required packages..." >> /var/log/user-data.log',
      'yum update -y >> /var/log/user-data.log 2>&1',
      'yum install -y python3 python3-pip unzip aws-cli >> /var/log/user-data.log 2>&1',
      'echo "Required packages installed." >> /var/log/user-data.log'
    );

    // Download application files
    userData.addS3DownloadCommand({
      bucket: appFiles.bucket,
      bucketKey: appFiles.s3ObjectKey,
      localFile: '/tmp/computer-vision.zip',
    });
    
    // Extract application files
    userData.addCommands(
      'echo "Extracting application files..." >> /var/log/user-data.log',
      'mkdir -p /tmp/computer-vision >> /var/log/user-data.log 2>&1',
      'unzip -o /tmp/computer-vision.zip -d /tmp/computer-vision/ >> /var/log/user-data.log 2>&1',
      'chmod +x /tmp/computer-vision/setup.sh >> /var/log/user-data.log 2>&1',
      'echo "Application files extracted." >> /var/log/user-data.log'
    );

    // Run setup script
    userData.addCommands(
      'echo "Running setup script..." >> /var/log/user-data.log',
      'sudo bash /tmp/computer-vision/setup.sh >> /var/log/user-data.log 2>&1',
      'echo "Setup script completed." >> /var/log/user-data.log'
    );
  }
} 