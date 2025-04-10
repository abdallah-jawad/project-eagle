#!/bin/bash

# Get the instance metadata token
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

# Get the IAM role credentials
PAYLOAD=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/iam/security-credentials/kvsCloudGatewayInstanceRole)

# Set the environment variables
export AWS_ACCESS_KEY_ID=$(echo $PAYLOAD | jq -r .AccessKeyId)
export AWS_SECRET_ACCESS_KEY=$(echo $PAYLOAD | jq -r .SecretAccessKey)
export AWS_SESSION_TOKEN=$(echo $PAYLOAD | jq -r .Token)

# Create AWS credentials file
mkdir -p ~/.aws
cat > ~/.aws/credentials << EOL
[default]
aws_access_key_id = $(echo $PAYLOAD | jq -r .AccessKeyId)
aws_secret_access_key = $(echo $PAYLOAD | jq -r .SecretAccessKey)
aws_session_token = $(echo $PAYLOAD | jq -r .Token)
EOL

# Create log configuration file
touch ~/kvs_log_configuration

# Set the environment variables for KVS producer SDK
export LD_LIBRARY_PATH=/opt/amazon-kinesis-video-streams-producer-sdk-cpp/open-source/local/lib
export GST_PLUGIN_PATH=/opt/amazon-kinesis-video-streams-producer-sdk-cpp/build/
export AWS_DEFAULT_REGION=us-east-1

# Read streams configuration
STREAMS_CONFIG=$(cat /home/ubuntu/streams-config.json)

# Function to start a single stream
start_stream() {
    local url=$1
    local stream_name=$2
    echo "Starting stream from $url to $stream_name"
    
    # Start the GStreamer pipeline in the background
    gst-launch-1.0 -v rtspsrc location=$url short-header=TRUE \
        ! rtph264depay \
        ! h264parse \
        ! kvssink stream-name=$stream_name storage-size=128 > "/tmp/stream_${stream_name}.log" 2>&1 &
    
    # Store the PID
    echo $! > "/tmp/stream_${stream_name}.pid"
    
    # Check if the process started successfully
    sleep 2
    if ! ps -p $(cat "/tmp/stream_${stream_name}.pid") > /dev/null; then
        echo "Failed to start stream $stream_name. Check /tmp/stream_${stream_name}.log for details."
        return 1
    fi
    
    return 0
}

# Start each stream
echo "$STREAMS_CONFIG" | jq -c '.[]' | while read -r stream; do
    url=$(echo "$stream" | jq -r '.url')
    stream_name=$(echo "$stream" | jq -r '.streamName')
    start_stream "$url" "$stream_name"
done

# Wait for all background processes
wait 