"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.RtspKvsStack = void 0;
const ec2 = require("aws-cdk-lib/aws-ec2");
const cdk = require("aws-cdk-lib");
const iam = require("aws-cdk-lib/aws-iam");
const kinesisvideo = require("aws-cdk-lib/aws-kinesisvideo");
const path = require("path");
const aws_s3_assets_1 = require("aws-cdk-lib/aws-s3-assets");
const system_config_1 = require("../config/system-config");
const customer_configs_1 = require("../config/customer-configs");
class RtspKvsStack extends cdk.Stack {
    constructor(scope, id, props) {
        super(scope, id, props);
        // Create a single VPC for all customers
        const vpc = new ec2.Vpc(this, 'VPC', {
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
            vpc,
            description: 'Allow SSH (TCP port 22) in',
            allowAllOutbound: true
        });
        securityGroup.addIngressRule(ec2.Peer.ipv4(`${props.myIpAddress}/32`), ec2.Port.tcp(22), 'Allow SSH Access');
        // Create a single IAM role for all instances
        const role = new iam.Role(this, 'ec2Role', {
            assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
            roleName: 'kvsCloudGatewayInstanceRole',
        });
        role.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSSMManagedInstanceCore'));
        // Create KVS streams for all cameras across all customers
        const streams = {};
        customer_configs_1.customerConfigs.forEach(customer => {
            customer.cameras.forEach(camera => {
                streams[camera.streamName] = new kinesisvideo.CfnStream(this, `KvsStream-${camera.streamName}`, {
                    name: camera.streamName,
                    dataRetentionInHours: 24,
                    mediaType: 'video/h264',
                });
            });
        });
        // Add KVS permissions to the role
        role.addToPolicy(new iam.PolicyStatement({
            resources: Object.values(streams).map(stream => stream.attrArn),
            actions: [
                'kinesisvideo:PutMedia',
                'kinesisvideo:DescribeStream',
                'kinesisvideo:GetDataEndpoint',
                'kinesisvideo:TagStream'
            ]
        }));
        // Calculate total number of cameras across all customers
        const totalCameras = customer_configs_1.customerConfigs.reduce((sum, customer) => sum + customer.cameras.length, 0);
        // Calculate required instance type based on total cameras
        const requiredInstanceType = this.calculateInstanceType(totalCameras);
        console.log(`Using instance type ${requiredInstanceType} for ${totalCameras} total cameras`);
        // Use Ubuntu Server 22.04
        const ami = ec2.MachineImage.genericLinux({
            'us-east-1': 'ami-0d192a81a9bee8a6e',
        });
        const rootVolume = {
            deviceName: '/dev/sda1',
            volume: ec2.BlockDeviceVolume.ebs(50, { encrypted: true, deleteOnTermination: true }),
        };
        // Create a single EC2 instance to handle all cameras
        const ec2Instance = new ec2.Instance(this, 'Instance', {
            instanceName: 'kvs-rtsp-cloud-gateway',
            vpc,
            instanceType: ec2.InstanceType.of(ec2.InstanceClass.T3, this.getInstanceSize(requiredInstanceType)),
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
        // Create an asset that will be used as part of User Data to run on first load
        const installKvsProducerSdkScript = new aws_s3_assets_1.Asset(this, 'InstallKvsProducerSdkScript', {
            path: path.join(__dirname, '../src/config.sh')
        });
        const serviceFile = new aws_s3_assets_1.Asset(this, 'KvsServiceFile', {
            path: path.join(__dirname, '../src/stream-rtsp-to-kvs.service')
        });
        const executionScript = new aws_s3_assets_1.Asset(this, 'KvsExecutionScript', {
            path: path.join(__dirname, '../src/stream-rtsp-to-kvs.sh')
        });
        installKvsProducerSdkScript.grantRead(ec2Instance.role);
        serviceFile.grantRead(ec2Instance.role);
        executionScript.grantRead(ec2Instance.role);
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
        // Create a configuration file for all streams
        const streamsConfig = customer_configs_1.customerConfigs.flatMap(customer => customer.cameras.map(camera => ({
            url: camera.rtspUrl,
            streamName: camera.streamName,
            name: camera.name,
            id: camera.id,
            customerId: customer.id,
            customerName: customer.name,
            resolution: camera.resolution,
            fps: camera.fps,
            bitrate: camera.bitrate
        })));
        // Add the streams configuration to the instance
        ec2Instance.userData.addCommands(`echo '${JSON.stringify(streamsConfig)}' > /home/ubuntu/streams-config.json`);
        ec2Instance.userData.addExecuteFileCommand({
            filePath: installKvsProducerSdkScriptLocalPath,
            arguments: '--verbose -y'
        });
        ec2Instance.userData.addCommands('sudo chmod 755 /home/ubuntu/stream-rtsp-to-kvs.sh');
        ec2Instance.userData.addCommands('sudo systemctl daemon-reload');
        ec2Instance.userData.addCommands('sudo systemctl enable stream-rtsp-to-kvs.service');
        ec2Instance.userData.addCommands('sudo systemctl start stream-rtsp-to-kvs.service');
        // Create outputs for connecting
        new cdk.CfnOutput(this, 'IP Address', { value: ec2Instance.instancePublicIp });
        new cdk.CfnOutput(this, 'Key Name', { value: props.keyPairName });
        new cdk.CfnOutput(this, 'Download Key Command', {
            value: 'aws secretsmanager get-secret-value --secret-id ec2-ssh-key/cdk-keypair/private --query SecretString --output text > cdk-key.pem && chmod 400 cdk-key.pem'
        });
        new cdk.CfnOutput(this, 'ssh command', {
            value: 'ssh -i cdk-key.pem -o IdentitiesOnly=yes ec2-user@' + ec2Instance.instancePublicIp
        });
    }
    calculateInstanceType(numCameras) {
        // Find the smallest instance type that can handle the number of cameras
        for (const [type, specs] of Object.entries(system_config_1.systemConfig.instanceTypes)) {
            if (specs.maxCameras >= numCameras) {
                return type;
            }
        }
        // If no instance type can handle the number of cameras, throw an error
        throw new Error(`No instance type available to handle ${numCameras} cameras`);
    }
    getInstanceSize(instanceType) {
        const size = instanceType.split('.')[1].toUpperCase();
        return ec2.InstanceSize[size];
    }
}
exports.RtspKvsStack = RtspKvsStack;
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoicnRzcC1rdnMtc3RhY2suanMiLCJzb3VyY2VSb290IjoiIiwic291cmNlcyI6WyIuLi8uLi9saWIvcnRzcC1rdnMtc3RhY2sudHMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6Ijs7O0FBQUEsMkNBQTJDO0FBQzNDLG1DQUFtQztBQUNuQywyQ0FBMkM7QUFDM0MsNkRBQTZEO0FBQzdELDZCQUE2QjtBQUM3Qiw2REFBa0Q7QUFFbEQsMkRBQXVEO0FBQ3ZELGlFQUE2RDtBQU83RCxNQUFhLFlBQWEsU0FBUSxHQUFHLENBQUMsS0FBSztJQUN6QyxZQUFZLEtBQWdCLEVBQUUsRUFBVSxFQUFFLEtBQXdCO1FBQ2hFLEtBQUssQ0FBQyxLQUFLLEVBQUUsRUFBRSxFQUFFLEtBQUssQ0FBQyxDQUFDO1FBRXhCLHdDQUF3QztRQUN4QyxNQUFNLEdBQUcsR0FBRyxJQUFJLEdBQUcsQ0FBQyxHQUFHLENBQUMsSUFBSSxFQUFFLEtBQUssRUFBRTtZQUNuQyxPQUFPLEVBQUUsdUJBQXVCO1lBQ2hDLFdBQVcsRUFBRSxDQUFDO1lBQ2QscUJBQXFCLEVBQUUsSUFBSTtZQUMzQixtQkFBbUIsRUFBRSxDQUFDO29CQUNwQixRQUFRLEVBQUUsRUFBRTtvQkFDWixJQUFJLEVBQUUsYUFBYTtvQkFDbkIsVUFBVSxFQUFFLEdBQUcsQ0FBQyxVQUFVLENBQUMsTUFBTTtpQkFDbEMsQ0FBQztTQUNILENBQUMsQ0FBQztRQUVILG1EQUFtRDtRQUNuRCxNQUFNLGFBQWEsR0FBRyxJQUFJLEdBQUcsQ0FBQyxhQUFhLENBQUMsSUFBSSxFQUFFLGVBQWUsRUFBRTtZQUNqRSxHQUFHO1lBQ0gsV0FBVyxFQUFFLDRCQUE0QjtZQUN6QyxnQkFBZ0IsRUFBRSxJQUFJO1NBQ3ZCLENBQUMsQ0FBQztRQUNILGFBQWEsQ0FBQyxjQUFjLENBQUMsR0FBRyxDQUFDLElBQUksQ0FBQyxJQUFJLENBQUMsR0FBRyxLQUFLLENBQUMsV0FBVyxLQUFLLENBQUMsRUFBRSxHQUFHLENBQUMsSUFBSSxDQUFDLEdBQUcsQ0FB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QUFDLFVBQVUsSUFBSSxVQUFVLEVBQUU7Z0JBQ2xDLE9BQU8sSUFBSSxDQUFDO2FBQ2I7U0FDRjtRQUNELHVFQUF1RTtRQUN2RSxNQUFNLElBQUksS0FBSyxDQUFDLHdDQUF3QyxVQUFVLFVBQVUsQ0FBQyxDQUFDO0lBQ2hGLENBQUM7SUFFTyxlQUFlLENBQUMsWUFBb0I7UUFDMUMsTUFBTSxJQUFJLEdBQUcsWUFBWSxDQUFDLEtBQUssQ0FBQyxHQUFHLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxXQUFXLEVBQUUsQ0FBQztRQUN0RCxPQUFPLEdBQUcsQ0FBQyxZQUFZLENBQUMsSUFBcUMsQ0FBQyxDQUFDO0lBQ2pFLENBQUM7Q0FDRjtBQS9NRCxvQ0ErTUMiLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQgKiBhcyBlYzIgZnJvbSBcImF3cy1jZGstbGliL2F3cy1lYzJcIjtcclxuaW1wb3J0ICogYXMgY2RrIGZyb20gJ2F3cy1jZGstbGliJztcclxuaW1wb3J0ICogYXMgaWFtIGZyb20gJ2F3cy1jZGstbGliL2F3cy1pYW0nO1xyXG5pbXBvcnQgKiBhcyBraW5lc2lzdmlkZW8gZnJvbSAnYXdzLWNkay1saWIvYXdzLWtpbmVzaXN2aWRlbyc7XHJcbmltcG9ydCAqIGFzIHBhdGggZnJvbSAncGF0aCc7XHJcbmltcG9ydCB7IEFzc2V0IH0gZnJvbSAnYXdzLWNkay1saWIvYXdzLXMzLWFzc2V0cyc7XHJcbmltcG9ydCB7IENvbnN0cnVjdCB9IGZyb20gJ2NvbnN0cnVjdHMnO1xyXG5pbXBvcnQgeyBzeXN0ZW1Db25maWcgfSBmcm9tICcuLi9jb25maWcvc3lzdGVtLWNvbmZpZyc7XHJcbmltcG9ydCB7IGN1c3RvbWVyQ29uZmlncyB9IGZyb20gJy4uL2NvbmZpZy9jdXN0b21lci1jb25maWdzJztcclxuXHJcbmV4cG9ydCBpbnRlcmZhY2UgUnRzcEt2c1N0YWNrUHJvcHMgZXh0ZW5kcyBjZGsuU3RhY2tQcm9wcyB7XHJcbiAgbXlJcEFkZHJlc3M6IHN0cmluZztcclxuICBrZXlQYWlyTmFtZTogc3RyaW5nO1xyXG59XHJcblxyXG5leHBvcnQgY2xhc3MgUnRzcEt2c1N0YWNrIGV4dGVuZHMgY2RrLlN0YWNrIHtcclxuICBjb25zdHJ1Y3RvcihzY29wZTogQ29uc3RydWN0LCBpZDogc3RyaW5nLCBwcm9wczogUnRzcEt2c1N0YWNrUHJvcHMpIHtcclxuICAgIHN1cGVyKHNjb3BlLCBpZCwgcHJvcHMpO1xyXG5cclxuICAgIC8vIENyZWF0ZSBhIHNpbmdsZSBWUEMgZm9yIGFsbCBjdXN0b21lcnNcclxuICAgIGNvbnN0IHZwYyA9IG5ldyBlYzIuVnBjKHRoaXMsICdWUEMnLCB7XHJcbiAgICAgIHZwY05hbWU6ICdLVlMgQ2xvdWQgR2F0ZXdheSBWUEMnLFxyXG4gICAgICBuYXRHYXRld2F5czogMCxcclxuICAgICAgY3JlYXRlSW50ZXJuZXRHYXRld2F5OiB0cnVlLFxyXG4gICAgICBzdWJuZXRDb25maWd1cmF0aW9uOiBbe1xyXG4gICAgICAgIGNpZHJNYXNrOiAyNCxcclxuICAgICAgICBuYW1lOiBcIkFwcGxpY2F0aW9uXCIsXHJcbiAgICAgICAgc3VibmV0VHlwZTogZWMyLlN1Ym5ldFR5cGUuUFVCTElDXHJcbiAgICAgIH1dXHJcbiAgICB9KTtcclxuXHJcbiAgICAvLyBDcmVhdGUgYSBzaW5nbGUgc2VjdXJpdHkgZ3JvdXAgZm9yIGFsbCBpbnN0YW5jZXNcclxuICAgIGNvbnN0IHNlY3VyaXR5R3JvdXAgPSBuZXcgZWMyLlNlY3VyaXR5R3JvdXAodGhpcywgJ1NlY3VyaXR5R3JvdXAnLCB7XHJcbiAgICAgIHZwYyxcclxuICAgICAgZGVzY3JpcHRpb246ICdBbGxvdyBTU0ggKFRDUCBwb3J0IDIyKSBpbicsXHJcbiAgICAgIGFsbG93QWxsT3V0Ym91bmQ6IHRydWVcclxuICAgIH0pO1xyXG4gICAgc2VjdXJpdHlHcm91cC5hZGRJbmdyZXNzUnVsZShlYzIuUGVlci5pcHY0KGAke3Byb3BzLm15SXBBZGRyZXNzfS8zMmApLCBlYzIuUG9ydC50Y3AoMjIpLCAnQWxsb3cgU1NIIEFjY2VzcycpO1xyXG5cclxuICAgIC8vIENyZWF0ZSBhIHNpbmdsZSBJQU0gcm9sZSBmb3IgYWxsIGluc3RhbmNlc1xyXG4gICAgY29uc3Qgcm9sZSA9IG5ldyBpYW0uUm9sZSh0aGlzLCAnZWMyUm9sZScsIHtcclxuICAgICAgYXNzdW1lZEJ5OiBuZXcgaWFtLlNlcnZpY2VQcmluY2lwYWwoJ2VjMi5hbWF6b25hd3MuY29tJyksXHJcbiAgICAgIHJvbGVOYW1lOiAna3ZzQ2xvdWRHYXRld2F5SW5zdGFuY2VSb2xlJyxcclxuICAgIH0pO1xyXG4gICAgcm9sZS5hZGRNYW5hZ2VkUG9saWN5KGlhbS5NYW5hZ2VkUG9saWN5LmZyb21Bd3NNYW5hZ2VkUG9saWN5TmFtZSgnQW1hem9uU1NNTWFuYWdlZEluc3RhbmNlQ29yZScpKTtcclxuXHJcbiAgICAvLyBDcmVhdGUgS1ZTIHN0cmVhbXMgZm9yIGFsbCBjYW1lcmFzIGFjcm9zcyBhbGwgY3VzdG9tZXJzXHJcbiAgICBjb25zdCBzdHJlYW1zOiB7IFtrZXk6IHN0cmluZ106IGtpbmVzaXN2aWRlby5DZm5TdHJlYW0gfSA9IHt9O1xyXG4gICAgY3VzdG9tZXJDb25maWdzLmZvckVhY2goY3VzdG9tZXIgPT4ge1xyXG4gICAgICBjdXN0b21lci5jYW1lcmFzLmZvckVhY2goY2FtZXJhID0+IHtcclxuICAgICAgICBzdHJlYW1zW2NhbWVyYS5zdHJlYW1OYW1lXSA9IG5ldyBraW5lc2lzdmlkZW8uQ2ZuU3RyZWFtKHRoaXMsIGBLdnNTdHJlYW0tJHtjYW1lcmEuc3RyZWFtTmFtZX1gLCB7XHJcbiAgICAgICAgICBuYW1lOiBjYW1lcmEuc3RyZWFtTmFtZSxcclxuICAgICAgICAgIGRhdGFSZXRlbnRpb25JbkhvdXJzOiAyNCxcclxuICAgICAgICAgIG1lZGlhVHlwZTogJ3ZpZGVvL2gyNjQnLFxyXG4gICAgICAgIH0pO1xyXG4gICAgICB9KTtcclxuICAgIH0pO1xyXG5cclxuICAgIC8vIEFkZCBLVlMgcGVybWlzc2lvbnMgdG8gdGhlIHJvbGVcclxuICAgIHJvbGUuYWRkVG9Qb2xpY3kobmV3IGlhbS5Qb2xpY3lTdGF0ZW1lbnQoe1xyXG4gICAgICByZXNvdXJjZXM6IE9iamVjdC52YWx1ZXMoc3RyZWFtcykubWFwKHN0cmVhbSA9PiBzdHJlYW0uYXR0ckFybiksXHJcbiAgICAgIGFjdGlvbnM6IFtcclxuICAgICAgICAna2luZXNpc3ZpZGVvOlB1dE1lZGlhJyxcclxuICAgICAgICAna2luZXNpc3ZpZGVvOkRlc2NyaWJlU3RyZWFtJyxcclxuICAgICAgICAna2luZXNpc3ZpZGVvOkdldERhdGFFbmRwb2ludCcsXHJcbiAgICAgICAgJ2tpbmVzaXN2aWRlbzpUYWdTdHJlYW0nXHJcbiAgICAgIF1cclxuICAgIH0pKTtcclxuXHJcbiAgICAvLyBDYWxjdWxhdGUgdG90YWwgbnVtYmVyIG9mIGNhbWVyYXMgYWNyb3NzIGFsbCBjdXN0b21lcnNcclxuICAgIGNvbnN0IHRvdGFsQ2FtZXJhcyA9IGN1c3RvbWVyQ29uZmlncy5yZWR1Y2UoKHN1bSwgY3VzdG9tZXIpID0+IHN1bSArIGN1c3RvbWVyLmNhbWVyYXMubGVuZ3RoLCAwKTtcclxuICAgIFxyXG4gICAgLy8gQ2FsY3VsYXRlIHJlcXVpcmVkIGluc3RhbmNlIHR5cGUgYmFzZWQgb24gdG90YWwgY2FtZXJhc1xyXG4gICAgY29uc3QgcmVxdWlyZWRJbnN0YW5jZVR5cGUgPSB0aGlzLmNhbGN1bGF0ZUluc3RhbmNlVHlwZSh0b3RhbENhbWVyYXMpO1xyXG4gICAgY29uc29sZS5sb2coYFVzaW5nIGluc3RhbmNlIHR5cGUgJHtyZXF1aXJlZEluc3RhbmNlVHlwZX0gZm9yICR7dG90YWxDYW1lcmFzfSB0b3RhbCBjYW1lcmFzYCk7XHJcblxyXG4gICAgLy8gVXNlIFVidW50dSBTZXJ2ZXIgMjIuMDRcclxuICAgIGNvbnN0IGFtaSA9IGVjMi5NYWNoaW5lSW1hZ2UuZ2VuZXJpY0xpbnV4KHtcclxuICAgICAgJ3VzLWVhc3QtMSc6ICdhbWktMGQxOTJhODFhOWJlZThhNmUnLCAgICAgXHJcbiAgICB9KTtcclxuXHJcbiAgICBjb25zdCByb290Vm9sdW1lOiBlYzIuQmxvY2tEZXZpY2UgPSB7XHJcbiAgICAgIGRldmljZU5hbWU6ICcvZGV2L3NkYTEnLFxyXG4gICAgICB2b2x1bWU6IGVjMi5CbG9ja0RldmljZVZvbHVtZS5lYnMoNTAsIHtlbmNyeXB0ZWQ6IHRydWUsIGRlbGV0ZU9uVGVybWluYXRpb246IHRydWV9KSxcclxuICAgIH07XHJcblxyXG4gICAgLy8gQ3JlYXRlIGEgc2luZ2xlIEVDMiBpbnN0YW5jZSB0byBoYW5kbGUgYWxsIGNhbWVyYXNcclxuICAgIGNvbnN0IGVjMkluc3RhbmNlID0gbmV3IGVjMi5JbnN0YW5jZSh0aGlzLCAnSW5zdGFuY2UnLCB7XHJcbiAgICAgIGluc3RhbmNlTmFtZTogJ2t2cy1ydHNwLWNsb3VkLWdhdGV3YXknLFxyXG4gICAgICB2cGMsXHJcbiAgICAgIGluc3RhbmNlVHlwZTogZWMyLkluc3RhbmNlVHlwZS5vZihcclxuICAgICAgICBlYzIuSW5zdGFuY2VDbGFzcy5UMyxcclxuICAgICAgICB0aGlzLmdldEluc3RhbmNlU2l6ZShyZXF1aXJlZEluc3RhbmNlVHlwZSlcclxuICAgICAgKSxcclxuICAgICAgbWFjaGluZUltYWdlOiBhbWksXHJcbiAgICAgIHNlY3VyaXR5R3JvdXA6IHNlY3VyaXR5R3JvdXAsXHJcbiAgICAgIGtleU5hbWU6IHByb3BzLmtleVBhaXJOYW1lLFxyXG4gICAgICByb2xlOiByb2xlLFxyXG4gICAgICBibG9ja0RldmljZXM6IFtyb290Vm9sdW1lXSxcclxuICAgICAgcHJvcGFnYXRlVGFnc1RvVm9sdW1lT25DcmVhdGlvbjogdHJ1ZSxcclxuICAgIH0pO1xyXG5cclxuICAgIC8vIFNldHVwIGluc3RhbmNlIHdpdGggcmVxdWlyZWQgc29mdHdhcmVcclxuICAgIGVjMkluc3RhbmNlLnVzZXJEYXRhLmFkZENvbW1hbmRzKCdzdWRvIGFwdCB1cGRhdGUgJiYgREVCSUFOX0ZST05URU5EPW5vbmludGVyYWN0aXZlIGFwdC1nZXQgaW5zdGFsbCAteSAtLW5vLWluc3RhbGwtcmVjb21tZW5kcyB0emRhdGEnKTtcclxuICAgIGVjMkluc3RhbmNlLnVzZXJEYXRhLmFkZENvbW1hbmRzKCdzdWRvIGFwdCBpbnN0YWxsIHVuemlwIC15Jyk7XHJcbiAgICBlYzJJbnN0YW5jZS51c2VyRGF0YS5hZGRDb21tYW5kcyhgY3VybCBcImh0dHBzOi8vYXdzY2xpLmFtYXpvbmF3cy5jb20vYXdzY2xpLWV4ZS1saW51eC14ODZfNjQuemlwXCIgLW8gXCJhd3NjbGl2Mi56aXBcIiAmJiBcXFxyXG4gICAgICB1bnppcCBhd3NjbGl2Mi56aXAgJiYgXFxcclxuICAgICAgc3VkbyAuL2F3cy9pbnN0YWxsICYmIFxcXHJcbiAgICAgIHJtIGF3c2NsaXYyLnppcGApO1xyXG5cclxuICAgIGVjMkluc3RhbmNlLnVzZXJEYXRhLmFkZENvbW1hbmRzKGBzdWRvIGFwdC1nZXQgaW5zdGFsbCAteSBcXFxyXG4gICAgICBsaWJzc2wtZGV2IFxcXHJcbiAgICAgIGdpdCBcXFxyXG4gICAgICBsaWJjdXJsNC1vcGVuc3NsLWRldiBcXFxyXG4gICAgICBsaWJsb2c0Y3BsdXMtZGV2IFxcXHJcbiAgICAgIGxpYmdzdHJlYW1lcjEuMC1kZXYgXFxcclxuICAgICAgbGliZ3N0cmVhbWVyLXBsdWdpbnMtYmFzZTEuMC1kZXYgXFxcclxuICAgICAgZ3N0cmVhbWVyMS4wLXBsdWdpbnMtYmFzZS1hcHBzIFxcXHJcbiAgICAgIGdzdHJlYW1lcjEuMC1wbHVnaW5zLWJhZCBcXFxyXG4gICAgICBnc3RyZWFtZXIxLjAtcGx1Z2lucy1nb29kIFxcXHJcbiAgICAgIGdzdHJlYW1lcjEuMC1wbHVnaW5zLXVnbHkgXFxcclxuICAgICAgZ3N0cmVhbWVyMS4wLXRvb2xzIFxcXHJcbiAgICAgIGJ1aWxkLWVzc2VudGlhbCBcXFxyXG4gICAgICBhdXRvY29uZiBcXFxyXG4gICAgICBhdXRvbWFrZSAgXFxcclxuICAgICAgYmlzb24gXFxcclxuICAgICAgYnppcDIgXFxcclxuICAgICAgY21ha2UgXFxcclxuICAgICAgY3VybCBcXFxyXG4gICAgICBkaWZmdXRpbHMgXFxcclxuICAgICAgZmxleCBcXFxyXG4gICAgICBqcSBcXFxyXG4gICAgICBtYWtlYCk7XHJcblxyXG4gICAgLy8gQ3JlYXRlIGFuIGFzc2V0IHRoYXQgd2lsbCBiZSB1c2VkIGFzIHBhcnQgb2YgVXNlciBEYXRhIHRvIHJ1biBvbiBmaXJzdCBsb2FkXHJcbiAgICBjb25zdCBpbnN0YWxsS3ZzUHJvZHVjZXJTZGtTY3JpcHQgPSBuZXcgQXNzZXQodGhpcywgJ0luc3RhbGxLdnNQcm9kdWNlclNka1NjcmlwdCcsIHsgXHJcbiAgICAgIHBhdGg6IHBhdGguam9pbihfX2Rpcm5hbWUsICcuLi9zcmMvY29uZmlnLnNoJykgXHJcbiAgICB9KTtcclxuICAgIGNvbnN0IHNlcnZpY2VGaWxlID0gbmV3IEFzc2V0KHRoaXMsICdLdnNTZXJ2aWNlRmlsZScsIHsgXHJcbiAgICAgIHBhdGg6IHBhdGguam9pbihfX2Rpcm5hbWUsICcuLi9zcmMvc3RyZWFtLXJ0c3AtdG8ta3ZzLnNlcnZpY2UnKSBcclxuICAgIH0pO1xyXG4gICAgY29uc3QgZXhlY3V0aW9uU2NyaXB0ID0gbmV3IEFzc2V0KHRoaXMsICdLdnNFeGVjdXRpb25TY3JpcHQnLCB7IFxyXG4gICAgICBwYXRoOiBwYXRoLmpvaW4oX19kaXJuYW1lLCAnLi4vc3JjL3N0cmVhbS1ydHNwLXRvLWt2cy5zaCcpIFxyXG4gICAgfSk7XHJcblxyXG4gICAgaW5zdGFsbEt2c1Byb2R1Y2VyU2RrU2NyaXB0LmdyYW50UmVhZChlYzJJbnN0YW5jZS5yb2xlKTtcclxuICAgIHNlcnZpY2VGaWxlLmdyYW50UmVhZChlYzJJbnN0YW5jZS5yb2xlKTtcclxuICAgIGV4ZWN1dGlvblNjcmlwdC5ncmFudFJlYWQoZWMySW5zdGFuY2Uucm9sZSk7XHJcblxyXG4gICAgY29uc3QgaW5zdGFsbEt2c1Byb2R1Y2VyU2RrU2NyaXB0TG9jYWxQYXRoID0gZWMySW5zdGFuY2UudXNlckRhdGEuYWRkUzNEb3dubG9hZENvbW1hbmQoe1xyXG4gICAgICBidWNrZXQ6IGluc3RhbGxLdnNQcm9kdWNlclNka1NjcmlwdC5idWNrZXQsXHJcbiAgICAgIGJ1Y2tldEtleTogaW5zdGFsbEt2c1Byb2R1Y2VyU2RrU2NyaXB0LnMzT2JqZWN0S2V5LFxyXG4gICAgfSk7XHJcblxyXG4gICAgZWMySW5zdGFuY2UudXNlckRhdGEuYWRkUzNEb3dubG9hZENvbW1hbmQoe1xyXG4gICAgICBidWNrZXQ6IHNlcnZpY2VGaWxlLmJ1Y2tldCxcclxuICAgICAgYnVja2V0S2V5OiBzZXJ2aWNlRmlsZS5zM09iamVjdEtleSxcclxuICAgICAgbG9jYWxGaWxlOiAnL2V0Yy9zeXN0ZW1kL3N5c3RlbS9zdHJlYW0tcnRzcC10by1rdnMuc2VydmljZSdcclxuICAgIH0pO1xyXG5cclxuICAgIGVjMkluc3RhbmNlLnVzZXJEYXRhLmFkZFMzRG93bmxvYWRDb21tYW5kKHtcclxuICAgICAgYnVja2V0OiBleGVjdXRpb25TY3JpcHQuYnVja2V0LFxyXG4gICAgICBidWNrZXRLZXk6IGV4ZWN1dGlvblNjcmlwdC5zM09iamVjdEtleSxcclxuICAgICAgbG9jYWxGaWxlOiAnL2hvbWUvdWJ1bnR1L3N0cmVhbS1ydHNwLXRvLWt2cy5zaCdcclxuICAgIH0pO1xyXG5cclxuICAgIC8vIENyZWF0ZSBhIGNvbmZpZ3VyYXRpb24gZmlsZSBmb3IgYWxsIHN0cmVhbXNcclxuICAgIGNvbnN0IHN0cmVhbXNDb25maWcgPSBjdXN0b21lckNvbmZpZ3MuZmxhdE1hcChjdXN0b21lciA9PiBcclxuICAgICAgY3VzdG9tZXIuY2FtZXJhcy5tYXAoY2FtZXJhID0+ICh7XHJcbiAgICAgICAgdXJsOiBjYW1lcmEucnRzcFVybCxcclxuICAgICAgICBzdHJlYW1OYW1lOiBjYW1lcmEuc3RyZWFtTmFtZSxcclxuICAgICAgICBuYW1lOiBjYW1lcmEubmFtZSxcclxuICAgICAgICBpZDogY2FtZXJhLmlkLFxyXG4gICAgICAgIGN1c3RvbWVySWQ6IGN1c3RvbWVyLmlkLFxyXG4gICAgICAgIGN1c3RvbWVyTmFtZTogY3VzdG9tZXIubmFtZSxcclxuICAgICAgICByZXNvbHV0aW9uOiBjYW1lcmEucmVzb2x1dGlvbixcclxuICAgICAgICBmcHM6IGNhbWVyYS5mcHMsXHJcbiAgICAgICAgYml0cmF0ZTogY2FtZXJhLmJpdHJhdGVcclxuICAgICAgfSkpXHJcbiAgICApO1xyXG5cclxuICAgIC8vIEFkZCB0aGUgc3RyZWFtcyBjb25maWd1cmF0aW9uIHRvIHRoZSBpbnN0YW5jZVxyXG4gICAgZWMySW5zdGFuY2UudXNlckRhdGEuYWRkQ29tbWFuZHMoXHJcbiAgICAgIGBlY2hvICcke0pTT04uc3RyaW5naWZ5KHN0cmVhbXNDb25maWcpfScgPiAvaG9tZS91YnVudHUvc3RyZWFtcy1jb25maWcuanNvbmBcclxuICAgICk7XHJcblxyXG4gICAgZWMySW5zdGFuY2UudXNlckRhdGEuYWRkRXhlY3V0ZUZpbGVDb21tYW5kKHtcclxuICAgICAgZmlsZVBhdGg6IGluc3RhbGxLdnNQcm9kdWNlclNka1NjcmlwdExvY2FsUGF0aCxcclxuICAgICAgYXJndW1lbnRzOiAnLS12ZXJib3NlIC15J1xyXG4gICAgfSk7XHJcbiAgICBcclxuICAgIGVjMkluc3RhbmNlLnVzZXJEYXRhLmFkZENvbW1hbmRzKCdzdWRvIGNobW9kIDc1NSAvaG9tZS91YnVudHUvc3RyZWFtLXJ0c3AtdG8ta3ZzLnNoJyk7XHJcbiAgICBlYzJJbnN0YW5jZS51c2VyRGF0YS5hZGRDb21tYW5kcygnc3VkbyBzeXN0ZW1jdGwgZGFlbW9uLXJlbG9hZCcpO1xyXG4gICAgZWMySW5zdGFuY2UudXNlckRhdGEuYWRkQ29tbWFuZHMoJ3N1ZG8gc3lzdGVtY3RsIGVuYWJsZSBzdHJlYW0tcnRzcC10by1rdnMuc2VydmljZScpO1xyXG4gICAgZWMySW5zdGFuY2UudXNlckRhdGEuYWRkQ29tbWFuZHMoJ3N1ZG8gc3lzdGVtY3RsIHN0YXJ0IHN0cmVhbS1ydHNwLXRvLWt2cy5zZXJ2aWNlJyk7XHJcblxyXG4gICAgLy8gQ3JlYXRlIG91dHB1dHMgZm9yIGNvbm5lY3RpbmdcclxuICAgIG5ldyBjZGsuQ2ZuT3V0cHV0KHRoaXMsICdJUCBBZGRyZXNzJywgeyB2YWx1ZTogZWMySW5zdGFuY2UuaW5zdGFuY2VQdWJsaWNJcCB9KTtcclxuICAgIG5ldyBjZGsuQ2ZuT3V0cHV0KHRoaXMsICdLZXkgTmFtZScsIHsgdmFsdWU6IHByb3BzLmtleVBhaXJOYW1lIH0pO1xyXG4gICAgbmV3IGNkay5DZm5PdXRwdXQodGhpcywgJ0Rvd25sb2FkIEtleSBDb21tYW5kJywgeyBcclxuICAgICAgdmFsdWU6ICdhd3Mgc2VjcmV0c21hbmFnZXIgZ2V0LXNlY3JldC12YWx1ZSAtLXNlY3JldC1pZCBlYzItc3NoLWtleS9jZGsta2V5cGFpci9wcml2YXRlIC0tcXVlcnkgU2VjcmV0U3RyaW5nIC0tb3V0cHV0IHRleHQgPiBjZGsta2V5LnBlbSAmJiBjaG1vZCA0MDAgY2RrLWtleS5wZW0nIFxyXG4gICAgfSk7XHJcbiAgICBuZXcgY2RrLkNmbk91dHB1dCh0aGlzLCAnc3NoIGNvbW1hbmQnLCB7IFxyXG4gICAgICB2YWx1ZTogJ3NzaCAtaSBjZGsta2V5LnBlbSAtbyBJZGVudGl0aWVzT25seT15ZXMgZWMyLXVzZXJAJyArIGVjMkluc3RhbmNlLmluc3RhbmNlUHVibGljSXAgXHJcbiAgICB9KTtcclxuICB9XHJcblxyXG4gIHByaXZhdGUgY2FsY3VsYXRlSW5zdGFuY2VUeXBlKG51bUNhbWVyYXM6IG51bWJlcik6IHN0cmluZyB7XHJcbiAgICAvLyBGaW5kIHRoZSBzbWFsbGVzdCBpbnN0YW5jZSB0eXBlIHRoYXQgY2FuIGhhbmRsZSB0aGUgbnVtYmVyIG9mIGNhbWVyYXNcclxuICAgIGZvciAoY29uc3QgW3R5cGUsIHNwZWNzXSBvZiBPYmplY3QuZW50cmllcyhzeXN0ZW1Db25maWcuaW5zdGFuY2VUeXBlcykpIHtcclxuICAgICAgaWYgKHNwZWNzLm1heENhbWVyYXMgPj0gbnVtQ2FtZXJhcykge1xyXG4gICAgICAgIHJldHVybiB0eXBlO1xyXG4gICAgICB9XHJcbiAgICB9XHJcbiAgICAvLyBJZiBubyBpbnN0YW5jZSB0eXBlIGNhbiBoYW5kbGUgdGhlIG51bWJlciBvZiBjYW1lcmFzLCB0aHJvdyBhbiBlcnJvclxyXG4gICAgdGhyb3cgbmV3IEVycm9yKGBObyBpbnN0YW5jZSB0eXBlIGF2YWlsYWJsZSB0byBoYW5kbGUgJHtudW1DYW1lcmFzfSBjYW1lcmFzYCk7XHJcbiAgfVxyXG5cclxuICBwcml2YXRlIGdldEluc3RhbmNlU2l6ZShpbnN0YW5jZVR5cGU6IHN0cmluZyk6IGVjMi5JbnN0YW5jZVNpemUge1xyXG4gICAgY29uc3Qgc2l6ZSA9IGluc3RhbmNlVHlwZS5zcGxpdCgnLicpWzFdLnRvVXBwZXJDYXNlKCk7XHJcbiAgICByZXR1cm4gZWMyLkluc3RhbmNlU2l6ZVtzaXplIGFzIGtleW9mIHR5cGVvZiBlYzIuSW5zdGFuY2VTaXplXTtcclxuICB9XHJcbn0gIl19