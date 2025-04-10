# Computer Vision Application

A simple Python application that prints "Hello World" indefinitely.

## Project Structure

```
computer-vision/
├── src/
│   ├── computer_vision/
│   │   ├── __init__.py
│   │   └── app.py
│   ├── computer_vision.service
│   ├── setup.sh
│   ├── requirements.txt
│   └── README.md
```

## Installation

1. Copy the application files to the EC2 instance:
   ```bash
   scp -r src/* ec2-user@<ec2-instance-ip>:/tmp/computer-vision/
   ```

2. SSH into the EC2 instance:
   ```bash
   ssh ec2-user@<ec2-instance-ip>
   ```

3. Run the setup script:
   ```bash
   sudo bash /tmp/computer-vision/setup.sh
   ```

## Usage

The application runs as a systemd service. You can control it using the following commands:

- Check service status:
  ```bash
  sudo systemctl status computer-vision.service
  ```

- Stop the service:
  ```bash
  sudo systemctl stop computer-vision.service
  ```

- Start the service:
  ```bash
  sudo systemctl start computer-vision.service
  ```

- Restart the service:
  ```bash
  sudo systemctl restart computer-vision.service
  ```

- View logs:
  ```bash
  sudo journalctl -u computer-vision.service
  ```

## Development

To run the application manually for development:

```bash
cd /home/ec2-user/computer-vision
python3 src/computer_vision/app.py
``` 