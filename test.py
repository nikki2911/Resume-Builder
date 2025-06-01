import os
from dotenv import load_dotenv
from google.genai.types import Part, GenerateContentConfig, HarmCategory, HarmBlockThreshold
from google.genai import Client

load_dotenv()

file_path = "Nikita Kapadiya.pdf"
with open(file_path, 'rb') as f:
    file_data = f.read()

client = Client(api_key=os.environ.get("API_KEY"))
tokens = client.models.count_tokens(model="gemini-2.0-flash-001", contents=[
    Part.from_bytes(data=file_data, mime_type="application/pdf")
])

if tokens.total_tokens < 1000 :
    response = client.models.generate_content(model="gemini-2.0-flash-001", contents=[
        Part.from_bytes(data=file_data, mime_type="application/pdf"),
        "Enhance my resume based on genai developer role"
    ],
    config=GenerateContentConfig(max_output_tokens=1000))
    print("response : ",response.text)
