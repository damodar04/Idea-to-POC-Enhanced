#!/usr/bin/env python3
"""
Script to delete all ideas from the MongoDB database.
This is a utility script for development and testing purposes.

WARNING: This will permanently delete ALL ideas in the database!
"""

import os
import logging
import sys
from datetime import datetime
from services.database import Database, get_ideas_collection
from pymongo.errors import PyMongoError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def confirm_deletion():
    """Request user confirmation before deleting all ideas"""
    print("\n" + "="*70)
    print("WARNING: This will DELETE ALL IDEAS from the database!")
    print("="*70)
    print("\nThis action is IRREVERSIBLE and will permanently remove:")
    print("  • All idea documents")
    print("  • All associated metadata")
    print("  • All conversation history")
    print("  • All AI scores and feedback")
    print("\n" + "="*70)
    
    user_input = input("\nType 'DELETE ALL IDEAS' to confirm deletion (case-sensitive): ").strip()
    
    if user_input == "DELETE ALL IDEAS":
        return True
    else:
        print("Deletion cancelled. No ideas were deleted.")
        return False


def delete_all_ideas():
    """Delete all ideas from the database"""
    try:
        # Connect to database
        logger.info("Connecting to MongoDB...")
        if not Database.connect_db():
            logger.error("Failed to connect to MongoDB")
            return False
        
        # Get ideas collection
        ideas_collection = get_ideas_collection()
        
        # Count existing ideas before deletion
        total_count = ideas_collection.count_documents({})
        if total_count == 0:
            logger.warning("No ideas found in the database")
            Database.close_db()
            return True
        
        logger.info(f"Found {total_count} ideas in the database")
        
        # Request confirmation
        if not confirm_deletion():
            Database.close_db()
            return False
        
        # Delete all ideas
        logger.info("Deleting all ideas...")
        result = ideas_collection.delete_many({})
        
        logger.info(f"Successfully deleted {result.deleted_count} ideas")
        
        # Verify deletion
        remaining = ideas_collection.count_documents({})
        if remaining == 0:
            logger.info("Verification successful: Database is now empty")
        else:
            logger.warning(f"Warning: {remaining} ideas still remain in the database")
        
        # Log deletion event
        logger.info(f"Deletion completed at {datetime.utcnow().isoformat()}")
        
        return True
        
    except PyMongoError as e:
        logger.error(f"MongoDB error during deletion: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False
    finally:
        # Close database connection
        Database.close_db()


def delete_ideas_by_session(session_id: str):
    """Delete ideas from a specific session"""
    try:
        logger.info(f"Connecting to MongoDB...")
        if not Database.connect_db():
            logger.error("Failed to connect to MongoDB")
            return False
        
        ideas_collection = get_ideas_collection()
        
        # Count ideas in session
        count = ideas_collection.count_documents({"session_id": session_id})
        if count == 0:
            logger.warning(f"No ideas found for session: {session_id}")
            Database.close_db()
            return True
        
        logger.info(f"Found {count} ideas in session: {session_id}")
        
        # Request confirmation
        print("\n" + "="*70)
        print(f"This will delete {count} ideas from session: {session_id}")
        print("="*70)
        
        user_input = input(f"\nType 'DELETE' to confirm: ").strip()
        
        if user_input != "DELETE":
            print("Deletion cancelled.")
            Database.close_db()
            return False
        
        # Delete ideas
        logger.info(f"Deleting {count} ideas from session: {session_id}")
        result = ideas_collection.delete_many({"session_id": session_id})
        
        logger.info(f"Successfully deleted {result.deleted_count} ideas from session: {session_id}")
        
        return True
        
    except PyMongoError as e:
        logger.error(f"MongoDB error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False
    finally:
        Database.close_db()


def delete_ideas_by_status(status: str):
    """Delete ideas with a specific status"""
    try:
        logger.info("Connecting to MongoDB...")
        if not Database.connect_db():
            logger.error("Failed to connect to MongoDB")
            return False
        
        ideas_collection = get_ideas_collection()
        
        # Count ideas with status
        count = ideas_collection.count_documents({"status": status})
        if count == 0:
            logger.warning(f"No ideas found with status: {status}")
            Database.close_db()
            return True
        
        logger.info(f"Found {count} ideas with status: {status}")
        
        # Request confirmation
        print("\n" + "="*70)
        print(f"This will delete {count} ideas with status: {status}")
        print("="*70)
        
        user_input = input(f"\nType 'DELETE' to confirm: ").strip()
        
        if user_input != "DELETE":
            print("Deletion cancelled.")
            Database.close_db()
            return False
        
        # Delete ideas
        logger.info(f"Deleting {count} ideas with status: {status}")
        result = ideas_collection.delete_many({"status": status})
        
        logger.info(f"Successfully deleted {result.deleted_count} ideas with status: {status}")
        
        return True
        
    except PyMongoError as e:
        logger.error(f"MongoDB error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False
    finally:
        Database.close_db()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Delete ideas from the MongoDB database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python delete_all_ideas.py --all              # Delete all ideas
  python delete_all_ideas.py --session ABC123   # Delete ideas from session
  python delete_all_ideas.py --status rejected  # Delete rejected ideas
        """
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Delete ALL ideas from the database (requires confirmation)"
    )
    parser.add_argument(
        "--session",
        type=str,
        metavar="SESSION_ID",
        help="Delete ideas from a specific session"
    )
    parser.add_argument(
        "--status",
        type=str,
        metavar="STATUS",
        choices=["submitted", "under_review", "approved", "rejected", "implemented", "completed", "in_progress"],
        help="Delete ideas with a specific status"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.all, args.session, args.status]):
        parser.print_help()
        sys.exit(1)
    
    # Execute deletion
    success = False
    if args.all:
        success = delete_all_ideas()
    elif args.session:
        success = delete_ideas_by_session(args.session)
    elif args.status:
        success = delete_ideas_by_status(args.status)
    
    sys.exit(0 if success else 1)
