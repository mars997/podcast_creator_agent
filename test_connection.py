import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

try:
    models = client.models.list()
    print("Connection successful.")
    print("First model object received.")
except Exception as e:
    print("Connection failed:")
    print(type(e).__name__)
    print(str(e))