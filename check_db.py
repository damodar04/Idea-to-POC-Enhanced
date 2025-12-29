import pymongo
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB URL from env
mongodb_url = os.getenv("MONGODB_URL")

print(f"Checking connection to: {mongodb_url}")

if not mongodb_url:
    print("FAILURE: MONGODB_URL not found in .env file")
    sys.exit(1)

try:
    client = pymongo.MongoClient(mongodb_url, serverSelectionTimeoutMS=5000)
    server_info = client.server_info() 
    print("SUCCESS: Connected to MongoDB Atlas/Database!")
    print(f"Server version: {server_info.get('version')}")
except Exception as e:
    print(f"FAILURE: Could not connect to MongoDB. Error: {e}")
    sys.exit(1)
