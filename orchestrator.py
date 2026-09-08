"""
Orchestrator: planner -> researcher -> writer zincirini yönetir.
FastAPI katmanı bu fonksiyonu çağıracak.
"""

from agents.planner import plan
from agents.researcher import research_all
from agents.writer import write_report


async def run_research_pipeline(topic: str) -> dict:
    """
    Tam pipeline'ı çalıştırır ve tüm ara/final sonuçları döner.
    (İleride debug/gösterim için subtasks ve findings'i de saklamak işimize yarayacak.)
    """
    subtasks = await plan(topic)
    findings = await research_all(subtasks)
    report = await write_report(topic, findings)

    return {
        "topic": topic,
        "subtasks": subtasks,
        "findings": findings,
        "report": report,
    }