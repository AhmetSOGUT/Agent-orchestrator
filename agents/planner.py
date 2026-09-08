"""
Planner Agent: geniş bir konuyu, araştırılabilir alt görevlere böler.
Çıktısı bir Python listesi (liste of string) olacak şekilde tasarlandı.
"""

import json
from agents.base import call_agent

PLANNER_SYSTEM_PROMPT = """Sen bir araştırma planlayıcısısın. Sana bir konu verilecek.
Görevin bu konuyu, her biri bağımsız olarak araştırılabilecek 3 ila 4 alt başlığa bölmek.

KURALLAR:
- Sadece geçerli bir JSON listesi döndür, başka hiçbir açıklama, giriş cümlesi
  veya markdown kod bloğu (```) ekleme.
- Format tam olarak şöyle olmalı: ["alt başlık 1", "alt başlık 2", "alt başlık 3"]
- Alt başlıklar kısa ve net olsun (5-8 kelime).
"""


async def plan(topic: str) -> list[str]:
    """
    Bir konu alır, alt görevlerden oluşan bir liste döndürür.
    """
    raw_response = await call_agent(
        system_prompt=PLANNER_SYSTEM_PROMPT,
        user_message=f"Konu: {topic}",
    )

    # Model bazen JSON'un etrafına ```json ``` gibi kod bloğu ekleyebiliyor,
    # onu temizliyoruz (güvenlik önlemi).
    cleaned = raw_response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        subtasks = json.loads(cleaned)
    except json.JSONDecodeError:
        # Model JSON formatını bozarsa, en azından çökmemesi için
        # tek elemanlı bir liste döndürüyoruz.
        subtasks = [topic]

    return subtasks