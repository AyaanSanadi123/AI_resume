import os
from dotenv import load_dotenv
from google import genai

# 1. Load the variables from the .env file into the system
load_dotenv()

# 2. Initialize the client (it automatically finds GEMINI_API_KEY in the environment)
client = genai.Client()

print("Sending ping to Gemini...")

# 3. Send a simple prompt to the model
response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Explain resume parsing in exactly one sentence."
)

print("\nResponse received:")
print(response.text)