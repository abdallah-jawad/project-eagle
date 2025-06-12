import boto3
import os
from botocore.exceptions import ClientError

_jwt_secret = None

def get_jwt_secret():
    """Retrieve JWT secret from AWS Secrets Manager"""
    global _jwt_secret
    if _jwt_secret is None:
        session = boto3.session.Session()
        client = session.client(
            'secretsmanager',
            region_name='us-east-1'  # Explicitly set the region
        )
        
        try:
            secret_name = "dev/jwt-secret"
            response = client.get_secret_value(SecretId=secret_name)
            secret = response['SecretString']
            _jwt_secret = secret
        except ClientError as e:
            print(f"Error retrieving secret: {e}")
            raise
    
    return _jwt_secret

def get_users_dynamodb_table():
    """Get DynamoDB table resource"""
    dynamodb = boto3.resource('dynamodb')
    table_name = "users"
    return dynamodb.Table(table_name) 