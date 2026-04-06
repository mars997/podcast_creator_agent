import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if api_key and api_key.startswith("sk-"):
    print("OPENAI_API_KEY loaded successfully.")
else:
    print("OPENAI_API_KEY not found or looks invalid.")