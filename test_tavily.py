"""Test Tavily API connectivity"""
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('TAVILY_API_KEY')
print(f'Key found: {key[:15]}...')

try:
    client = TavilyClient(api_key=key)
    result = client.search('AI chatbot trends 2024', max_results=2)
    print(f'SUCCESS! Got {len(result.get("results", []))} results')
    answer = result.get("answer")
    if answer:
        print(f'Answer: {answer[:200]}...')
    else:
        print('No answer provided, but search worked!')
except Exception as e:
    print(f'ERROR: {str(e)}')
