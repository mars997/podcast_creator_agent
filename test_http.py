import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

headers = {
    "Authorization": f"Bearer {api_key}"
}

try:
    r = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=20)
    print("status_code:", r.status_code)
    print(r.text[:1000])
except Exception as e:
    print(type(e).__name__)
    print(str(e))