"""
Bu dosya tüm agent'ların kullanacağı ortak fonksiyonu içerir.
Her agent aslında Gemini'ye "sen şu rolü oynuyorsun, şunu yap" diyen
bir sistem prompt'u + kullanıcı mesajıyla yapılan bir API çağrısıdır.
"""
import certifi
import os

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

from google import genai
from google.genai import types
from google.genai.errors import ClientError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
import logging

from config import settings
from logging_config import get_logger

logger = get_logger(__name__)

client = genai.Client(api_key=settings.google_api_key)


@retry(
    stop=stop_after_attempt(settings.retry_max_attempts),
    wait=wait_exponential(multiplier=2, min=2, max=30),
    retry=retry_if_exception_type(ClientError),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
async def call_agent(system_prompt: str, user_message: str) -> str:
    logger.debug(f"LLM çağrısı yapılıyor, mesaj uzunluğu: {len(user_message)} karakter")
    response = await client.aio.models.generate_content(
        model=settings.model_name,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
        ),
    )
    return response.text