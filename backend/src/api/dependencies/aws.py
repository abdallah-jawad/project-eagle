import boto3
import os
from botocore.exceptions import ClientError
from ..config import AWS_REGION, JWT_SECRET_NAME, DYNAMODB_TABLE_NAME

_jwt_secret = None

def get_jwt_secret():
    """Retrieve JWT secret from AWS Secrets Manager"""
    global _jwt_secret
    if _jwt_secret is None:
        session = boto3.session.Session()
        client = session.client(
            'secretsmanager',
            region_name=AWS_REGION
        )
        
        try:
            response = client.get_secret_value(SecretId=JWT_SECRET_NAME)
            secret = response['SecretString']
            _jwt_secret = secret
        except ClientError as e:
            print(f"Error retrieving secret: {e}")
            raise
    
    return _jwt_secret

def get_users_dynamodb_table():
    """Get DynamoDB table resource"""
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    return dynamodb.Table(DYNAMODB_TABLE_NAME) 