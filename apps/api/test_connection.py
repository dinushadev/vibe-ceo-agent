import os
import asyncio
from google import genai
from dotenv import load_dotenv

load_dotenv("/Users/nandika/WS/ADK_capstone/vibe_ceo/apps/api/.env")

async def test_connect():
    print("Testing connection to Gemini Live API...")
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("Error: GOOGLE_API_KEY not found in environment")
            return

        client = genai.Client(
            http_options={'api_version': 'v1alpha'}
        )
        model_id = "gemini-2.5-flash-native-audio-preview-09-2025"
        config = {"response_modalities": ["AUDIO"]}
        
        print(f"Connecting to model: {model_id}")
        async with client.aio.live.connect(model=model_id, config=config) as session:
            print("Successfully connected to Gemini Live API")
            
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connect())
