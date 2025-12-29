import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("MONGODB_URL", "NOT_FOUND")
print(f"URL START: {url[:15]}...")
