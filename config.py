import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-goes-here'
    MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/your-database-name'
    # Add other configuration settings here
