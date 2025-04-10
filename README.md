# Project Eagle

A comprehensive computer vision and machine learning system for real-time object detection and tracking.

## Project Structure

```
project-eagle/
├── computer-vision/         # Computer Vision Application
│   ├── src/                # Source code
│   │   ├── main.py        # Main application entry point
│   │   ├── setup.sh       # EC2 instance setup script
│   │   └── computer_vision.service  # Systemd service file
│   └── test/              # Test files
│
├── rtsp-kvs/              # RTSP to KVS Application
│   ├── src/              # Source code
│   │   └── ...          # RTSP to KVS application files
│   └── test/            # Test files
│
├── lib/                  # Infrastructure stacks
│   ├── computer-vision-stack.ts
│   ├── rtsp-kvs-stack.ts
│   └── utils/
│       └── instance-type-utils.ts
│
├── config/               # Shared configuration files
│   └── deployment-config.ts
├── bin/                 # CDK app entry point
├── cdk.json            # CDK configuration
├── package.json        # Node.js dependencies
└── tsconfig.json      # TypeScript configuration
```

## Prerequisites

- Node.js (v14 or later)
- AWS CLI configured with appropriate credentials
- Python 3.8 or later
- AWS CDK CLI

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Configure deployment settings in `config/deployment-config.ts`:
   - Set your AWS region
   - Configure your IP address for SSH access
   - Set your EC2 key pair name

3. Build the TypeScript code:
   ```bash
   npm run build
   ```

## Deployment

1. Deploy the infrastructure:
   ```bash
   # Deploy Computer Vision stack
   cdk deploy computer-vision
   
   # Deploy RTSP to KVS stack
   cdk deploy rtsp-kvs
   ```

2. The deployment will create:
   - A VPC with public and private subnets
   - EC2 instances for computer vision processing and RTSP streaming
   - Security groups and IAM roles
   - Systemd services for automatic startup

## Applications

### Computer Vision Application

The computer vision application runs as a systemd service on the EC2 instance. It:
- Processes video streams in real-time
- Performs object detection and tracking
- Logs events and statistics

### RTSP to KVS Application

The RTSP to KVS application:
- Connects to RTSP camera feeds
- Streams video to Amazon Kinesis Video Streams
- Manages multiple camera connections

### Service Management

Both applications run as systemd services. You can manage them using:
```bash
# For Computer Vision service
sudo systemctl status computer-vision.service
sudo systemctl start computer-vision.service
sudo systemctl stop computer-vision.service
sudo systemctl restart computer-vision.service

# For RTSP to KVS service
sudo systemctl status rtsp-kvs.service
sudo systemctl start rtsp-kvs.service
sudo systemctl stop rtsp-kvs.service
sudo systemctl restart rtsp-kvs.service
```

## Development

1. Make changes to the application code in respective `src/` directories
2. Update infrastructure code in the root `lib/` directory
3. Deploy changes using `cdk deploy`

## Testing

Run the test suite:
```bash
npm test
```

## Security

- SSH access is restricted to specified IP addresses
- EC2 instances use IAM roles with minimal required permissions
- Security groups are configured with least-privilege access

## License

This project is licensed under the MIT License - see the LICENSE file for details.