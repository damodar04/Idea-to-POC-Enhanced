import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("TAVILY_API_KEY")
if key:
    print(f"Tavily Key found: {key[:5]}...")
else:
    print("Tavily Key NOT found.")
