from app import app
from pymongo import MongoClient
import os 

client = MongoClient(os.environ.get('DB_CONNECTION_STRING'))
db = client.get_database()

# Define your MongoDB collections and data models here
# Example:
# class User:
#     collection = db.users
#     def __init__(self, username, email):
#         self.username = username
#         self.email = email
