import asyncio
from config import settings
from logging_config import setup_logging, get_logger

setup_logging(level=settings.log_level)
logger = get_logger(__name__)

from agents.planner import PlannerAgent
from agents.researcher import ResearcherAgent
from agents.writer import WriterAgent


async def main():
    topic = "Türkiye'de elektrikli araç pazarı"

    planner = PlannerAgent()
    researcher = ResearcherAgent()
    writer = WriterAgent()

    print("1) Planlama yapılıyor...")
    subtasks = await planner.run(topic)
    print(f"Alt görevler: {subtasks}\n")

    print("2) Araştırma yapılıyor (paralel)...")
    findings = await researcher.research_all(subtasks)
    print("Araştırma tamamlandı.\n")

    print("3) Rapor yazılıyor...")
    report = await writer.run(topic, findings)

    print("\n=== FİNAL RAPOR ===\n")
    print(report)

    with open("rapor.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("\n(Rapor 'rapor.md' dosyasına kaydedildi)")


if __name__ == "__main__":
    asyncio.run(main())