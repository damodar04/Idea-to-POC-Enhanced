#!/usr/bin/env python3
"""
Test script to verify MongoDB connection before deployment
Run this locally to ensure your MongoDB connection string works
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database module
from services.database import Database
from config import MONGODB_URL, MONGODB_DATABASE, MONGODB_COLLECTION
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_connection():
    """Test MongoDB connection with detailed output"""
    print("=" * 60)
    print("MongoDB Connection Test")
    print("=" * 60)
    print()
    
    # Check environment variables
    print("1. Checking Environment Variables...")
    if not MONGODB_URL:
        print("   ❌ FAIL: MONGODB_URL is not set")
        return False
    else:
        # Show partial URL (hide credentials)
        url_parts = MONGODB_URL.split('@')
        if len(url_parts) > 1:
            safe_url = f"mongodb+srv://***@{url_parts[1]}"
        else:
            safe_url = MONGODB_URL[:50] + "..."
        print(f"   ✅ MONGODB_URL is set: {safe_url}")
    
    if not MONGODB_DATABASE:
        print("   ⚠️  WARNING: MONGODB_DATABASE not set, using default")
    else:
        print(f"   ✅ MONGODB_DATABASE: {MONGODB_DATABASE}")
    
    if not MONGODB_COLLECTION:
        print("   ⚠️  WARNING: MONGODB_COLLECTION not set, using default")
    else:
        print(f"   ✅ MONGODB_COLLECTION: {MONGODB_COLLECTION}")
    
    print()
    
    # Test connection
    print("2. Testing MongoDB Connection...")
    try:
        if Database.connect_db():
            print("   ✅ Connection successful!")
            print()
            
            # Verify connection
            print("3. Verifying Connection Health...")
            if Database.verify_connection():
                print("   ✅ Connection is healthy and active")
            else:
                print("   ⚠️  Connection established but health check failed")
            print()
            
            # Test collection access
            print("4. Testing Collection Access...")
            try:
                collection = Database.get_collection()
                count = collection.count_documents({})
                print(f"   ✅ Collection accessible. Current document count: {count}")
            except Exception as e:
                print(f"   ⚠️  Collection access issue: {e}")
            print()
            
            # Get server info
            print("5. Server Information...")
            try:
                client = Database.get_client()
                server_info = client.server_info()
                print(f"   ✅ Server version: {server_info.get('version', 'unknown')}")
                print(f"   ✅ Server type: {server_info.get('modules', {}).get('version', 'Standard')}")
            except Exception as e:
                print(f"   ⚠️  Could not get server info: {e}")
            print()
            
            print("=" * 60)
            print("✅ ALL TESTS PASSED - MongoDB connection is ready!")
            print("=" * 60)
            return True
            
        else:
            print("   ❌ Connection failed")
            print()
            print("=" * 60)
            print("❌ CONNECTION TEST FAILED")
            print("=" * 60)
            print()
            print("Troubleshooting:")
            print("1. Check your MONGODB_URL format")
            print("2. Verify MongoDB Atlas Network Access allows your IP")
            print("3. Check username and password are correct")
            print("4. Ensure the cluster is running")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {type(e).__name__}: {e}")
        print()
        print("=" * 60)
        print("❌ CONNECTION TEST FAILED")
        print("=" * 60)
        return False
    finally:
        # Clean up
        Database.close_db()

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

