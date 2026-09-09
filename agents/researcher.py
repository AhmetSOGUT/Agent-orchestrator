"""
Researcher Agent: verilen TEK bir alt görevi araştırıp özet bilgi döner.
research_all() fonksiyonu, birden fazla alt görevi PARALEL olarak araştırır.
"""
import asyncio
from agents.agent import BaseAgent


class ResearcherAgent(BaseAgent):
    system_prompt = """Sen bir araştırmacısın. Sana bir araştırma başlığı verilecek.
Bu başlık hakkında bildiğin en güncel ve doğru bilgileri, 3-5 cümlelik
öz bir paragrafla özetle. Emin olmadığın rakamları/verileri kesin gibi sunma,
"tahmini olarak" gibi ifadeler kullanabilirsin.
Sadece bilgi paragrafını döndür, başka açıklama ekleme.
"""

    async def run(self, topic: str) -> str:
        self.logger.debug(f"Araştırılıyor: '{topic}'")
        return await self._call_llm(f"Araştırma başlığı: {topic}")

    async def research_all(self, subtasks: list[str]) -> dict[str, str]:
        """Birden fazla alt görevi paralel olarak araştırır."""
        self.logger.info(f"{len(subtasks)} alt görev paralel olarak araştırılıyor...")
        results = await asyncio.gather(*(self.run(t) for t in subtasks))
        self.logger.info("Tüm araştırmalar tamamlandı")
        return dict(zip(subtasks, results))