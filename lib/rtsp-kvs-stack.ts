import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as appconfig from 'aws-cdk-lib/aws-appconfig';
import * as path from 'path';
import { Asset } from 'aws-cdk-lib/aws-s3-assets';
import { Construct } from 'constructs';
import { InstanceTypeUtils } from './utils/instance-type-utils';
import { CameraConfig } from './interfaces/camera-config';

export interface RtspKvsStackProps extends cdk.StackProps {
  myIpAddress: string;
  keyPairName: string;
  cameraConfigs: CameraConfig & {
    appConfigApp: appconfig.CfnApplication;
    appConfigEnv: appconfig.CfnEnvironment;
    appConfigProfile: appconfig.CfnConfigurationProfile;
  };
}

export class RtspKvsStack extends cdk.Stack {
  public readonly vpc: ec2.IVpc;
  
  constructor(scope: Construct, id: string, props: RtspKvsStackProps) {
    super(scope, id, props);

    // Create a single VPC for all cameras
    this.vpc = new ec2.Vpc(this, 'VPC', {
      vpcName: 'KVS Cloud Gateway VPC',
      natGateways: 0,
      createInternetGateway: true,
      subnetConfiguration: [{
        cidrMask: 24,
        name: "Application",
        subnetType: ec2.SubnetType.PUBLIC
      }]
    });

    // Create a single security group for all instances
    const securityGroup = new ec2.SecurityGroup(this, 'SecurityGroup', {
      vpc: this.vpc,
      description: 'Allow SSH (TCP port 22) in',
      allowAllOutbound: true
    });

    // Allow SSH from EC2 Instance Connect service
    securityGroup.addIngressRule(
      ec2.Peer.prefixList('pl-0e4bcff02b13bef1e'),
      ec2.Port.tcp(22),
      'Allow EC2 Instance Connect'
    );

    // Allow SSH from your IP
    securityGroup.addIngressRule(
      ec2.Peer.ipv4(`${props.myIpAddress}/32`),
      ec2.Port.tcp(22),
      'Allow SSH Access'
    );

    // Create a single IAM role for all instances
    const role = new iam.Role(this, 'ec2Role', {
      assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
      roleName: 'kvsCloudGatewayInstanceRole',
    });

    // Add EC2 Instance Connect permissions
    role.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSSMManagedInstanceCore'));
    role.addToPolicy(new iam.PolicyStatement({
      actions: [
        'ec2-instance-connect:SendSSHPublicKey'
      ],
      resources: ['*']
    }));

    // Add broad KVS permissions to the role
    role.addToPolicy(new iam.PolicyStatement({
      resources: ['*'],
      actions: [
        'kinesisvideo:PutMedia',
        'kinesisvideo:DescribeStream',
        'kinesisvideo:GetDataEndpoint',
        'kinesisvideo:TagStream',
        'kinesisvideo:CreateStream',
        'kinesisvideo:DeleteStream',
        'kinesisvideo:ListStreams',
        'kinesisvideo:UpdateStream'
      ]
    }));

    // Add AppConfig permissions to the role
    role.addToPolicy(new iam.PolicyStatement({
      actions: [
        'appconfig:GetConfiguration',
        'appconfig:StartConfigurationSession',
        'appconfig:GetLatestConfiguration'
      ],
      resources: [
        `arn:aws:appconfig:${this.region}:${this.account}:application/${props.cameraConfigs.appConfigApp.ref}/environment/${props.cameraConfigs.appConfigEnv.ref}/configuration/${props.cameraConfigs.appConfigProfile.ref}`
      ]
    }));

    // Calculate total number of enabled cameras
    const totalCameras = props.cameraConfigs.cameras.filter(camera => camera.enabled).length;
    
    // Calculate required instance type based on total cameras
    const requiredInstanceType = InstanceTypeUtils.calculateInstanceType(totalCameras);
    console.log(`Using instance type ${requiredInstanceType} for ${totalCameras} total cameras`);

    // Use Ubuntu Server 22.04
    const ami = ec2.MachineImage.genericLinux({
      'us-east-1': 'ami-0d192a81a9bee8a6e',     
    });

    const rootVolume: ec2.BlockDevice = {
      deviceName: '/dev/sda1',
      volume: ec2.BlockDeviceVolume.ebs(50, {encrypted: true, deleteOnTermination: true}),
    };

    // Create a single EC2 instance to handle all cameras
    const ec2Instance = new ec2.Instance(this, 'Instance', {
      instanceName: 'kvs-rtsp-cloud-gateway',
      vpc: this.vpc,
      instanceType: InstanceTypeUtils.getEc2InstanceType(props.cameraConfigs),
      machineImage: ami,
      securityGroup: securityGroup,
      keyName: props.keyPairName,
      role: role,
      blockDevices: [rootVolume],
      propagateTagsToVolumeOnCreation: true,
    });

    // Setup instance with required software
    ec2Instance.userData.addCommands('sudo apt update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata');
    ec2Instance.userData.addCommands('sudo apt install unzip -y');
    ec2Instance.userData.addCommands(`curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
      unzip awscliv2.zip && \
      sudo ./aws/install && \
      rm awscliv2.zip`);

    // Install EC2 Instance Connect
    ec2Instance.userData.addCommands('sudo apt-get install -y ec2-instance-connect');
    ec2Instance.userData.addCommands('sudo systemctl enable ec2-instance-connect');
    ec2Instance.userData.addCommands('sudo systemctl start ec2-instance-connect');

    // Install required packages for KVS producer SDK
    ec2Instance.userData.addCommands(`sudo apt-get install -y \
      libssl-dev \
      git \
      libcurl4-openssl-dev \
      liblog4cplus-dev \
      libgstreamer1.0-dev \
      libgstreamer-plugins-base1.0-dev \
      gstreamer1.0-plugins-base-apps \
      gstreamer1.0-plugins-bad \
      gstreamer1.0-plugins-good \
      gstreamer1.0-plugins-ugly \
      gstreamer1.0-tools \
      build-essential \
      autoconf \
      automake  \
      bison \
      bzip2 \
      cmake \
      curl \
      diffutils \
      flex \
      jq \
      make`);

    // Create AWS credentials directory for ubuntu user
    ec2Instance.userData.addCommands('sudo mkdir -p /home/ubuntu/.aws');
    ec2Instance.userData.addCommands('sudo chown ubuntu:ubuntu /home/ubuntu/.aws');

    // Create kvs_log_configuration file for ubuntu user
    ec2Instance.userData.addCommands('sudo touch /home/ubuntu/kvs_log_configuration');
    ec2Instance.userData.addCommands('sudo chown ubuntu:ubuntu /home/ubuntu/kvs_log_configuration');

    // Create an asset that will be used as part of User Data to run on first load
    const installKvsProducerSdkScript = new Asset(this, 'InstallKvsProducerSdkScript', { 
      path: path.join(__dirname, '../rtsp-kvs/src/config.sh') 
    });
    const serviceFile = new Asset(this, 'KvsServiceFile', { 
      path: path.join(__dirname, '../rtsp-kvs/src/stream-rtsp-to-kvs.service') 
    });
    const executionScript = new Asset(this, 'KvsExecutionScript', { 
      path: path.join(__dirname, '../rtsp-kvs/src/stream-rtsp-to-kvs.sh') 
    });
    const updateConfigScript = new Asset(this, 'UpdateConfigScript', {
      path: path.join(__dirname, '../rtsp-kvs/src/update-config.sh')
    });

    installKvsProducerSdkScript.grantRead(ec2Instance.role);
    serviceFile.grantRead(ec2Instance.role);
    executionScript.grantRead(ec2Instance.role);
    updateConfigScript.grantRead(ec2Instance.role);

    const installKvsProducerSdkScriptLocalPath = ec2Instance.userData.addS3DownloadCommand({
      bucket: installKvsProducerSdkScript.bucket,
      bucketKey: installKvsProducerSdkScript.s3ObjectKey,
    });

    ec2Instance.userData.addS3DownloadCommand({
      bucket: serviceFile.bucket,
      bucketKey: serviceFile.s3ObjectKey,
      localFile: '/etc/systemd/system/stream-rtsp-to-kvs.service'
    });

    ec2Instance.userData.addS3DownloadCommand({
      bucket: executionScript.bucket,
      bucketKey: executionScript.s3ObjectKey,
      localFile: '/home/ubuntu/stream-rtsp-to-kvs.sh'
    });

    ec2Instance.userData.addS3DownloadCommand({
      bucket: updateConfigScript.bucket,
      bucketKey: updateConfigScript.s3ObjectKey,
      localFile: '/home/ubuntu/update-config.sh'
    });

    // Make the update script executable
    ec2Instance.userData.addCommands('sudo chmod +x /home/ubuntu/update-config.sh');

    // Run the update-config script to get initial configuration
    ec2Instance.userData.addCommands('/home/ubuntu/update-config.sh');

    ec2Instance.userData.addExecuteFileCommand({
      filePath: installKvsProducerSdkScriptLocalPath,
      arguments: '--verbose -y'
    });
    
    ec2Instance.userData.addCommands('sudo chmod 755 /home/ubuntu/stream-rtsp-to-kvs.sh');
    ec2Instance.userData.addCommands('sudo systemctl daemon-reload');
    ec2Instance.userData.addCommands('sudo systemctl enable stream-rtsp-to-kvs.service');
    ec2Instance.userData.addCommands('sudo systemctl start stream-rtsp-to-kvs.service');
  }
} 