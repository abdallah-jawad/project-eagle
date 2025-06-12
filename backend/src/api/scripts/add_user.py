from passlib.context import CryptContext
from datetime import datetime, UTC
from api.dependencies.aws import get_users_dynamodb_table

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def add_user(email: str, password: str, client_id: str):

    # Get Users DynamoDB table
    table = get_users_dynamodb_table()

    # Hash password
    password_hash = pwd_context.hash(password)

    # Create user document
    user = {
        "email": email,
        "password_hash": password_hash,
        "client_id": client_id,
        "created_at": datetime.now(UTC).isoformat(),
        "last_login": None
    }

    # Insert user
    try:
        table.put_item(Item=user)
        print(f"User {email} added successfully")
    except Exception as e:
        print(f"Error adding user: {e}")

if __name__ == "__main__":

    email = input("Enter email: ")
    password = input("Enter password: ")
    client_id = input("Enter client ID: ")
    
    add_user(email, password, client_id)