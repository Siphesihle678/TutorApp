import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
_gemini_key = os.environ.get("GEMINI_API_KEY", "")

client = genai.Client(api_key=_gemini_key)

# Create a dummy PDF or text file
with open("test.txt", "w") as f:
    f.write("This is a test file for the AI Quiz Generator. It contains info about the mitochondria being the powerhouse of the cell.")

print("Uploading file...")
uploaded_file = client.files.upload(file="test.txt")

print("Generating content...")
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[uploaded_file, "Extract the main fact from this document."]
)

print(response.text)

# Cleanup
os.remove("test.txt")
