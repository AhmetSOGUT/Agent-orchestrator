"""
Bu dosya tüm agent'ların kullanacağı ortak fonksiyonu içerir.
Her agent aslında Gemini'ye "sen şu rolü oynuyorsun, şunu yap" diyen
bir sistem prompt'u + kullanıcı mesajıyla yapılan bir API çağrısıdır.
"""
import os
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

from google import genai
from google.genai import types
from google.genai.errors import ClientError
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL = "gemini-flash-lite-latest"


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=30),
    retry=retry_if_exception_type(ClientError),
)
async def call_agent(system_prompt: str, user_message: str) -> str:
    response = await client.aio.models.generate_content(
        model=MODEL,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
        ),
    )
    return response.text