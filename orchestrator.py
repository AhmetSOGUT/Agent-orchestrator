"""
Orchestrator: planner -> researcher -> writer zincirini yönetir.
FastAPI katmanı bu fonksiyonu çağıracak.
"""

from agents.planner import PlannerAgent
from agents.researcher import ResearcherAgent
from agents.writer import WriterAgent


async def run_research_pipeline(topic: str) -> dict:
    planner = PlannerAgent()
    researcher = ResearcherAgent()
    writer = WriterAgent()

    subtasks = await planner.run(topic)
    findings = await researcher.research_all(subtasks)
    report = await writer.run(topic, findings)

    return {
        "topic": topic,
        "subtasks": subtasks,
        "findings": findings,
        "report": report,
    }