"""
Global configuration settings for the application.
"""
import os

# AWS Configuration
AWS_REGION = 'us-east-1'

# API Configuration
API_PREFIX = '/api'
API_V1_PREFIX = f'{API_PREFIX}/v1'

# Security Configuration
JWT_SECRET_NAME = 'jwt-secret'
JWT_ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database Configuration
DYNAMODB_TABLE_NAME = 'users'

# CORS Configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Local development
    "http://localhost:5173",  # Vite default port
    "https://api.neelo.vision",  # Production API
    "https://neelo.vision",     # Production frontend
] 