"""
Planner Agent: geniş bir konuyu, araştırılabilir alt görevlere böler.
Çıktısı bir Python listesi (liste of string) olacak şekilde tasarlandı.
"""

import json
from agents.agent import BaseAgent


class PlannerAgent(BaseAgent):
    system_prompt = """Sen bir araştırma planlayıcısısın. Sana bir konu verilecek.
Görevin bu konuyu, her biri bağımsız olarak araştırılabilecek 3 ila 4 alt başlığa bölmek.

KURALLAR:
- Sadece geçerli bir JSON listesi döndür, başka hiçbir açıklama, giriş cümlesi
  veya markdown kod bloğu (```) ekleme.
- Format tam olarak şöyle olmalı: ["alt başlık 1", "alt başlık 2", "alt başlık 3"]
- Alt başlıklar kısa ve net olsun (5-8 kelime).
"""

    async def run(self, topic: str) -> list[str]:
        self.logger.info(f"Planlama başladı: '{topic}'")

        raw_response = await self._call_llm(f"Konu: {topic}")

        cleaned = raw_response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

        try:
            subtasks = json.loads(cleaned)
        except json.JSONDecodeError:
            self.logger.warning(f"Planner JSON parse edilemedi: {raw_response[:200]}")
            subtasks = [topic]

        self.logger.info(f"Planlama tamamlandı: {len(subtasks)} alt görev bulundu")
        return subtasks