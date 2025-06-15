import boto3
import json
from typing import Dict, Any
from ..config import AWS_REGION

def get_appconfig_client():
    """Get an AppConfig client"""
    return boto3.client('appconfigdata', region_name=AWS_REGION)

def get_camera_configs() -> Dict[str, Any]:
    """
    Fetch camera configurations from AppConfig
    """
    client = get_appconfig_client()
    
    # Start a configuration session
    session = client.start_configuration_session(
        ApplicationIdentifier='computer-vision-app',
        EnvironmentIdentifier='dev',
        ConfigurationProfileIdentifier='computer-vision-config'
    )
    
    # Get the configuration
    response = client.get_latest_configuration(
        ConfigurationToken=session['InitialConfigurationToken']
    )
    
    # Parse the configuration
    if response['Configuration']:
        config_str = response['Configuration'].read().decode('utf-8')
        return json.loads(config_str)
    
    return {"cameras": []} 