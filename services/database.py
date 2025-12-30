import pymongo
import logging
import time
from config import MONGODB_URL, MONGODB_DATABASE, MONGODB_COLLECTION

logger = logging.getLogger(__name__)

class Database:
    """Database connection manager for MongoDB"""
    
    _client = None
    _db = None
    _collection = None
    _connection_attempts = 0
    _max_retries = 3
    _retry_delay = 2  # seconds
    
    @classmethod
    def connect_db(cls, retry=True):
        """Establish connection to MongoDB with retry logic"""
        # Check if MONGODB_URL is configured
        if not MONGODB_URL:
            logger.error("MONGODB_URL is not set. Cannot connect to MongoDB.")
            logger.error("Please set MONGODB_URL in your environment variables (Render Dashboard → Environment)")
            cls._reset_connection()
            return False
            
        try:
            if cls._client is None:
                # Enhanced connection settings for cloud deployment
                connection_options = {
                    'serverSelectionTimeoutMS': 30000,  # 30 seconds for cloud
                    'connectTimeoutMS': 30000,
                    'socketTimeoutMS': 30000,
                    'maxPoolSize': 50,  # Connection pooling
                    'minPoolSize': 5,
                    'retryWrites': True,
                    'retryReads': True,
                    'w': 'majority',  # Write concern
                }
                
                logger.info(f"Attempting to connect to MongoDB... (Attempt {cls._connection_attempts + 1}/{cls._max_retries})")
                # Log partial URL for debugging (first 50 chars)
                url_preview = MONGODB_URL[:50] + "..." if len(MONGODB_URL) > 50 else MONGODB_URL
                logger.info(f"MongoDB URL: {url_preview}")
                logger.info(f"Database: {MONGODB_DATABASE}, Collection: {MONGODB_COLLECTION}")
                
                cls._client = pymongo.MongoClient(MONGODB_URL, **connection_options)
                
                # Verify connection with server_info
                server_info = cls._client.server_info()
                logger.info(f"MongoDB server version: {server_info.get('version', 'unknown')}")
                
                # Get database and collection
                cls._db = cls._client[MONGODB_DATABASE]
                cls._collection = cls._db[MONGODB_COLLECTION]
                
                # Test the connection by accessing the collection
                cls._collection.find_one({}, limit=1)
                
                cls._connection_attempts = 0  # Reset on success
                logger.info("✅ MongoDB connection established successfully.")
                return True
            else:
                # Check if existing connection is still alive
                try:
                    cls._client.server_info()
                    return True
                except Exception:
                    # Connection is dead, reset and reconnect
                    logger.warning("Existing MongoDB connection is dead. Reconnecting...")
                    cls._client = None
                    cls._db = None
                    cls._collection = None
                    return cls.connect_db(retry=retry)
        except pymongo.errors.ServerSelectionTimeoutError as e:
            cls._connection_attempts += 1
            error_msg = f"Server selection timeout: {e}"
            logger.error(error_msg)
            
            if retry and cls._connection_attempts < cls._max_retries:
                logger.info(f"Retrying connection in {cls._retry_delay} seconds...")
                time.sleep(cls._retry_delay)
                return cls.connect_db(retry=retry)
            else:
                logger.error(f"Failed to connect after {cls._connection_attempts} attempts")
                cls._reset_connection()
                return False
        except pymongo.errors.ConfigurationError as e:
            logger.error(f"MongoDB configuration error: {e}")
            logger.error("Please check your MONGODB_URL format")
            cls._reset_connection()
            return False
        except Exception as e:
            cls._connection_attempts += 1
            error_msg = f"Failed to connect to MongoDB: {type(e).__name__}: {e}"
            logger.error(error_msg)
            
            if retry and cls._connection_attempts < cls._max_retries:
                logger.info(f"Retrying connection in {cls._retry_delay} seconds...")
                time.sleep(cls._retry_delay)
                return cls.connect_db(retry=retry)
            else:
                logger.error(f"Failed to connect after {cls._connection_attempts} attempts")
                cls._reset_connection()
                return False
    
    @classmethod
    def _reset_connection(cls):
        """Reset connection state"""
        cls._client = None
        cls._db = None
        cls._collection = None
    
    @classmethod
    def verify_connection(cls):
        """Verify that the MongoDB connection is active"""
        try:
            if cls._client is None:
                return False
            # Ping the server
            cls._client.admin.command('ping')
            return True
        except Exception as e:
            logger.warning(f"Connection verification failed: {e}")
            return False
    
    @classmethod
    def close_db(cls):
        """Close MongoDB connection"""
        try:
            if cls._client:
                cls._client.close()
                cls._client = None
                cls._db = None
                cls._collection = None
                logger.info("MongoDB connection closed.")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")
    
    @classmethod
    def get_client(cls):
        """Get MongoDB client instance"""
        return cls._client
    
    @classmethod
    def get_db(cls):
        """Get database instance"""
        return cls._db
    
    @classmethod
    def get_collection(cls):
        """Get collection instance"""
        return cls._collection


def get_ideas_collection():
    """Get the ideas collection from MongoDB"""
    if Database._collection is None:
        if not Database.connect_db():
            raise Exception("Failed to connect to MongoDB. Please check your MONGODB_URL and ensure MongoDB Atlas allows connections from Render's IP addresses.")
    
    # Verify connection is still alive
    if not Database.verify_connection():
        logger.warning("Connection lost, reconnecting...")
        if not Database.connect_db():
            raise Exception("Failed to reconnect to MongoDB")
    
    return Database._collection


# Initialize connection on module import
