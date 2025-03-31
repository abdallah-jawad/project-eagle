# Project Eagle

A CDK application for a computer vision solution built by @Abdulla Khalid and @Manaf Al-Nakeeb

## Architecture

The application currently consists of two main stacks, many more to come:

1. **RTSP to KVS Stack**: Streams RTSP camera feeds to Amazon Kinesis Video Streams
2. **Computer Vision Stack**: Processes the video streams using computer vision models

### RTSP to KVS Stack

- Creates a single VPC for all customers
- Sets up a single EC2 instance to handle all camera streams
- Creates Kinesis Video Streams for each camera
- Automatically sizes the EC2 instance based on total camera count
- Uses Ubuntu Server 22.04 with GStreamer for video processing

### Computer Vision Stack

- TBD...

## Configuration

The application uses a configuration system to manage customers and their cameras:

### Customer Configuration (`config/customer-configs.ts`)
```typescript
{
  id: string;
  name: string;
  cameras: CameraConfig[];
  region: string;
}
```

### Camera Configuration
```typescript
{
  id: string;
  name: string;
  rtspUrl: string;
  streamName: string;
  resolution?: {
    width: number;
    height: number;
  };
  fps?: number;
  bitrate?: number;
  location?: string;
  description?: string;
}
```

### System Configuration (`config/system-config.ts`)
- Defines instance types and their capabilities
- Sets default configurations
- Manages system-wide settings

## Prerequisites

- Node.js 20 or later
- AWS CDK CLI
- AWS CLI configured with appropriate credentials
- An AWS account with appropriate permissions

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd project-eagle
```

2. Install dependencies:
```bash
npm install
```

## Deployment

1. Configure deployment settings:
   - Open `config/deployment-config.ts`
   - Update `myIpAddress` with your IP address
   - Update `keyPairName` with your AWS EC2 key pair name

2. Validate the stacks:
```bash
# This will:
# 1. Build the TypeScript code
# 2. Run ESLint to check code style and potential issues
# 3. Synthesize the CloudFormation templates
npm run cdk-build

# To see what changes would be made without deploying:
cdk diff
```

3. Deploy the stacks:
```bash
cdk deploy RtspKvsStack
cdk deploy ComputerVisionStack
```

## Monitoring

- CloudWatch Logs for EC2 instance and Lambda functions
- CloudWatch Metrics for Kinesis Video Streams
- Instance metrics for CPU, memory, and network usage

## Security

- SSH access restricted to specified IP address
- IAM roles with least privilege principle
- Encrypted storage volumes
- Security groups with minimal required access

## Cost Optimization

- Single EC2 instance for all customers
- Shared VPC and networking resources
- Instance type automatically selected based on camera count

## Troubleshooting

1. Check CloudWatch Logs for errors
2. Verify RTSP URLs are accessible
3. Check instance metrics for resource constraints
4. Review security group settings

## License

This project is licensed under the MIT License - see the LICENSE file for details.