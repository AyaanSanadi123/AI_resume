from dotenv import load_dotenv
from google import genai
import os
import traceback

print("Starting script...")

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print("API Key found:", api_key is not None)

try:
    client = genai.Client(api_key=api_key)
    print("Client created")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say hello"
    )

    print("Response received")
    print(response)

    print("\n===== TEXT =====")
    print(repr(response.text))

except Exception as e:
    print("\nERROR:")
    traceback.print_exc()