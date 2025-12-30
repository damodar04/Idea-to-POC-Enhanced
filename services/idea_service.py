from models import IdeaDocument, MetadataDocument, DexKoUserContext, IdeaStatus
from datetime import datetime
from typing import Optional, List
import logging
import pymongo
from config import MONGODB_URL, MONGODB_DATABASE, MONGODB_COLLECTION

logger = logging.getLogger(__name__)

class IdeaService:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.connect()

    def connect(self):
        """Establish connection to MongoDB"""
        if not MONGODB_URL:
            logger.error("MONGODB_URL is not set. Cannot connect to MongoDB.")
            self.collection = None
            return False
            
        try:
            # Use enhanced connection settings for cloud deployment (same as Database class)
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
            
            self.client = pymongo.MongoClient(MONGODB_URL, **connection_options)
            # Verify connection
            self.client.server_info()
            
            self.db = self.client[MONGODB_DATABASE]
            self.collection = self.db[MONGODB_COLLECTION]
            logger.info("MongoDB connection established successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.collection = None
            return False

    def save_idea(self, idea_data: dict) -> str:
        """Save a new idea document"""
        if self.collection is None:
            raise Exception("MongoDB collection not initialized.")
        try:
            # Convert to IdeaDocument format
            idea_doc = self._convert_to_document(idea_data)
            result = self.collection.insert_one(idea_doc.dict(by_alias=True))
            logger.info(f"Idea saved with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to save idea: {e}")
            raise

    def save_or_update_idea(self, session_id: str, idea_data: dict) -> str:
        """Save new idea or update existing one by session_id"""
        if self.collection is None:
            raise Exception("MongoDB collection not initialized.")
        try:
            # Check if idea already exists
            existing_idea = self.get_idea_by_session(session_id)

            if existing_idea:
                # Update existing idea
                update_data = self._prepare_update_data(idea_data)
                success = self.update_idea(session_id, update_data)
                if success:
                    logger.info(f"Idea updated for session {session_id}")
                    return str(existing_idea.id) if hasattr(existing_idea, 'id') else session_id
                else:
                    logger.error(f"Failed to update idea for session {session_id}")
                    raise Exception("Failed to update existing idea")
            else:
                # Create new idea
                idea_data["session_id"] = session_id
                return self.save_idea(idea_data)
        except Exception as e:
            logger.error(f"Failed to save/update idea for session {session_id}: {e}")
            raise

    def update_idea(self, session_id: str, update_data: dict) -> bool:
        """Update existing idea by session_id"""
        if self.collection is None:
            raise Exception("MongoDB collection not initialized.")
        try:
            # Ensure 'updated_at' is always updated
            update_data["metadata.updated_at"] = datetime.utcnow()
            
            result = self.collection.update_one(
                {"session_id": session_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update idea {session_id}: {e}")
            raise

    def get_idea_by_session(self, session_id: str) -> Optional[IdeaDocument]:
        """Retrieve idea by session_id"""
        if self.collection is None:
            raise Exception("MongoDB collection not initialized.")
        try:
            doc = self.collection.find_one({"session_id": session_id})
            if doc:
                return IdeaDocument(**doc)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve idea {session_id}: {e}")
            raise

    def mark_completed(self, session_id: str, final_drafts: dict) -> bool:
        """Mark idea as completed with final drafts"""
        if self.collection is None:
            raise Exception("MongoDB collection not initialized.")
        try:
            update_data = {
                "drafts": final_drafts,
                "status": IdeaStatus.COMPLETED.value,
                "metadata.updated_at": datetime.utcnow()
            }
            return self.update_idea(session_id, update_data)
        except Exception as e:
            logger.error(f"Failed to mark idea {session_id} as completed: {e}")
            raise

    def get_all_ideas(self, limit: int = 50) -> List[IdeaDocument]:
        """Get all ideas with pagination"""
        if self.collection is None:
            raise Exception("MongoDB collection not initialized.")
        try:
            cursor = self.collection.find().sort("metadata.created_at", -1).limit(limit)
            docs = list(cursor)
            return [IdeaDocument(**doc) for doc in docs]
        except Exception as e:
            logger.error(f"Failed to retrieve ideas: {e}")
            raise

    def get_ideas_by_status(self, status: str, limit: int = 50) -> List[IdeaDocument]:
        """Get ideas filtered by status"""
        if self.collection is None:
            raise Exception("MongoDB collection not initialized.")
        try:
            cursor = self.collection.find({"status": status}).sort("metadata.created_at", -1).limit(limit)
            docs = list(cursor)
            return [IdeaDocument(**doc) for doc in docs]
        except Exception as e:
            logger.error(f"Failed to retrieve ideas by status: {e}")
            raise

    def _convert_to_document(self, data: dict) -> IdeaDocument:
        """Convert data dict to IdeaDocument"""
        if not data.get("metadata"):
            data["metadata"] = MetadataDocument()
        return IdeaDocument(**data)

    def _prepare_update_data(self, data: dict) -> dict:
        """Prepare data for MongoDB update, including nested metadata"""
        flat_data = {}

        for key, value in data.items():
            if isinstance(value, dict):
                # Flatten nested dictionaries using dot notation
                for nested_key, nested_value in value.items():
                    flat_data[f"{key}.{nested_key}"] = nested_value
            else:
                flat_data[key] = value
        
        return flat_data

idea_service = IdeaService()
