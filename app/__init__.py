from flask import Flask
from pymongo import MongoClient
from dotenv import load_dotenv
import os


app = Flask(__name__)
load_dotenv()

# Initialize MongoDB client
client = MongoClient(os.environ.get('DB_CONNECTION_STRING'))
print('Connected to M')
db = client.get_database('Loop_Stores')

from app import routes
