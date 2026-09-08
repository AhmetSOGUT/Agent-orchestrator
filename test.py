import asyncio
from agents.planner import plan
from agents.researcher import research_all
from agents.writer import write_report

async def main():
    topic = "Türkiye'de elektrikli araç pazarı"

    print("1) Planlama yapılıyor...")
    subtasks = await plan(topic)
    print(f"Alt görevler: {subtasks}\n")

    print("2) Araştırma yapılıyor (paralel)...")
    findings = await research_all(subtasks)
    print("Araştırma tamamlandı.\n")

    print("3) Rapor yazılıyor...")
    report = await write_report(topic, findings)

    print("\n=== FİNAL RAPOR ===\n")
    print(report)

    # Raporu dosyaya da kaydedelim
    with open("rapor.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("\n(Rapor 'rapor.md' dosyasına kaydedildi)")

if __name__ == "__main__":
    asyncio.run(main())