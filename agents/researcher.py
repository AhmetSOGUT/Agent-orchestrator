"""
Researcher Agent: verilen TEK bir alt görevi araştırıp özet bilgi döner.
research_all() fonksiyonu, birden fazla alt görevi PARALEL olarak araştırır.
"""
import asyncio
from agents.base import call_agent
from logging_config import get_logger

logger = get_logger(__name__)

RESEARCHER_SYSTEM_PROMPT = """Sen bir araştırmacısın. Sana bir araştırma başlığı verilecek.
Bu başlık hakkında bildiğin en güncel ve doğru bilgileri, 3-5 cümlelik
öz bir paragrafla özetle. Emin olmadığın rakamları/verileri kesin gibi sunma,
"tahmini olarak" gibi ifadeler kullanabilirsin.
Sadece bilgi paragrafını döndür, başka açıklama ekleme.
"""


async def research_topic(topic: str) -> str:
    """
    Tek bir alt görevi araştırır, metin özet döner.
    """
    logger.debug(f"Araştırılıyor: '{topic}'")
    result = await call_agent(
        system_prompt=RESEARCHER_SYSTEM_PROMPT,
        user_message=f"Araştırma başlığı: {topic}",
    )
    return result


async def research_all(subtasks: list[str]) -> dict[str, str]:
    """
    Birden fazla alt görevi AYNI ANDA (paralel) araştırır.
    Dönüş: {"alt görev 1": "bulgular...", "alt görev 2": "bulgular..."}
    """
    logger.info(f"{len(subtasks)} alt görev paralel olarak araştırılıyor...")

    # asyncio.gather: tüm research_topic çağrılarını aynı anda başlatır
    results = await asyncio.gather(*(research_topic(t) for t in subtasks))
    logger.info("Tüm araştırmalar tamamlandı")
    # subtasks listesi ile results listesini eşleştirip sözlük yapıyoruz
    return dict(zip(subtasks, results))