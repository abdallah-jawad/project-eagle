import boto3
import os
from botocore.exceptions import ClientError

_jwt_secret = None

def get_jwt_secret():
    """Retrieve JWT secret from AWS Secrets Manager"""
    global _jwt_secret
    if _jwt_secret is None:
        session = boto3.session.Session()
        client = session.client('secretsmanager')
        
        try:
            secret_name = f"{os.getenv('ENVIRONMENT', 'dev')}/jwt-secret"
            response = client.get_secret_value(SecretId=secret_name)
            secret = response['SecretString']
            _jwt_secret = secret
        except ClientError as e:
            print(f"Error retrieving secret: {e}")
            raise
    
    return _jwt_secret

def get_dynamodb_table():
    """Get DynamoDB table resource"""
    dynamodb = boto3.resource('dynamodb')
    table_name = f"{os.getenv('ENVIRONMENT', 'dev')}-users"
    return dynamodb.Table(table_name) 