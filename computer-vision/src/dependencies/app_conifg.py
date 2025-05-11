import boto3
import json
from datetime import datetime
from typing import List
from models.camera import Camera, NotificationSettings

class AppConfigClient:
    """Client for fetching camera configurations from AWS AppConfig"""
    
    def __init__(self):
        self.client = boto3.client('appconfig')
        self.application = "computer-vision"
        self.environment = "production"
        self.configuration = "camera-config"
        self.client_id = "default"

    def get_camera_configs(self) -> List[Camera]:
        """Fetch camera configurations from AppConfig and return list of Camera objects
        
        Returns:
            List[Camera]: List of camera configuration objects
        """
        try:
            # Get latest configuration from AppConfig
            response = self.client.get_configuration(
                Application=self.application,
                Environment=self.environment, 
                Configuration=self.configuration,
                ClientId=self.client_id
            )
            
            # Parse configuration content
            config_str = response['Content'].read().decode('utf-8')
            config_data = json.loads(config_str)
            
            cameras = []
            for camera_config in config_data['cameras']:
                # Create NotificationSettings object
                notify_settings = NotificationSettings(
                    labels_to_notify_on=camera_config['notification_settings']['labels_to_notify_on'],
                    contact_email=camera_config['notification_settings']['contact_email'],
                    contact_phone=camera_config['notification_settings']['contact_phone'],
                    notify_start_time=datetime.strptime(
                        camera_config['notification_settings']['notify_start_time'], 
                        "%H:%M"
                    ).time(),
                    notify_end_time=datetime.strptime(
                        camera_config['notification_settings']['notify_end_time'],
                        "%H:%M"
                    ).time(),
                    enabled=camera_config['notification_settings']['enabled']
                )
                
                # Create Camera object
                camera = Camera(
                    camera_id=camera_config['camera_id'],
                    client_id=camera_config['client_id'],
                    enabled=camera_config['enabled'],
                    zone=camera_config['zone'],
                    notification_settings=notify_settings,
                    fps=camera_config['fps'],
                    resolution=(
                        camera_config['resolution']['width'],
                        camera_config['resolution']['height']
                    ),
                    capture=None  # VideoCapture object will be initialized later
                )
                cameras.append(camera)
                
            return cameras
            
        except Exception as e:
            raise Exception(f"Failed to fetch camera configs from AppConfig: {str(e)}")

