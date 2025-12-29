import pymongo
import logging
from config import MONGODB_URL, MONGODB_DATABASE, MONGODB_COLLECTION

logger = logging.getLogger(__name__)

class Database:
    """Database connection manager for MongoDB"""
    
    _client = None
    _db = None
    _collection = None
    
    @classmethod
    def connect_db(cls):
        """Establish connection to MongoDB"""
        try:
            if cls._client is None:
                cls._client = pymongo.MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
                # Verify connection
                cls._client.server_info()
                
                cls._db = cls._client[MONGODB_DATABASE]
                cls._collection = cls._db[MONGODB_COLLECTION]
                logger.info("MongoDB connection established successfully.")
                return True
            else:
                # Already connected
                return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            cls._client = None
            cls._db = None
            cls._collection = None
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
            raise Exception("Failed to connect to MongoDB")
    return Database._collection


# Initialize connection on module import
