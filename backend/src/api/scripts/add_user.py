import asyncio
import boto3
from passlib.context import CryptContext
from datetime import datetime
import os

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def add_user(email: str, password: str, client_id: str):
    # DynamoDB setup
    dynamodb = boto3.resource('dynamodb')
    table_name = f"{os.getenv('ENVIRONMENT', 'dev')}-users"
    table = dynamodb.Table(table_name)

    # Hash password
    password_hash = pwd_context.hash(password)

    # Create user document
    user = {
        "email": email,
        "password_hash": password_hash,
        "client_id": client_id,
        "created_at": datetime.utcnow().isoformat(),
        "last_login": None
    }

    # Insert user
    try:
        response = table.put_item(Item=user)
        print(f"User {email} added successfully")
    except Exception as e:
        print(f"Error adding user: {e}")

if __name__ == "__main__":
    # Example usage
    email = input("Enter email: ")
    password = input("Enter password: ")
    client_id = input("Enter client ID: ")
    
    asyncio.run(add_user(email, password, client_id)) 