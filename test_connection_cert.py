import os
import certifi
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

try:
    models = client.models.list()
    print("Connection successful with certifi.")
except Exception as e:
    print("Connection failed:")
    print(type(e).__name__)
    print(str(e))