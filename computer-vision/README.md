# Computer Vision Service

This service provides functionality for processing video streams from Amazon Kinesis Video Streams (KVS).

## Features

- Connect to Amazon Kinesis Video Streams
- Retrieve individual frames from KVS streams
- Stream and process video data in chunks
- Process video frames using OpenCV

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from dependencies.kvs import KVSClient

# Initialize the KVS client
kvs_client = KVSClient()

# Get a single frame from a stream
frame_data = kvs_client.get_frame('your-stream-name')
```

### Streaming and Processing Video

```python
from dependencies.kvs import KVSClient

# Initialize the KVS client
kvs_client = KVSClient()

# Get a media stream generator
media_stream = kvs_client.get_media_stream('your-stream-name')

# Process each chunk in the stream
for chunk in media_stream:
    # Extract the data from the chunk
    data = chunk['data']
    timestamp = chunk['timestamp']
    stream_name = chunk['stream_name']
    
    # Process the chunk data (e.g., decode video frames)
    # ...
```

## AWS Configuration

Make sure you have the following AWS permissions:

- `kinesisvideo:DescribeStream`
- `kinesisvideo:GetDataEndpoint`
- `kinesisvideo:GetMedia`

You can configure AWS credentials using one of the following methods:

1. Environment variables:
   ```
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=your_region
   ```

2. AWS credentials file:
   ```
   ~/.aws/credentials
   ```

3. IAM role (if running on AWS infrastructure)

## License

This project is licensed under the MIT License - see the LICENSE file for details. 