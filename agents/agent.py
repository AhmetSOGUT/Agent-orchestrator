from abc import ABC, abstractmethod
from agents.base import call_agent
from logging_config import get_logger


class BaseAgent(ABC):
    """
    Tüm agent'ların ortak atası. Her agent kendi rolünü (system_prompt)
    ve kendi mantığını (run metodu) tanımlar, ama LLM çağırma altyapısını
    (call_agent) ve logging kurulumunu buradan miras alır.
    """

    system_prompt: str = ""  # her alt sınıf kendi prompt'unu buraya yazacak

    def __init__(self):
        # self.__class__.__module__ -> örn "agents.planner", logger ismini otomatik verir
        self.logger = get_logger(self.__class__.__module__)

    async def _call_llm(self, user_message: str) -> str:
        """Alt sınıfların LLM'e istek atmak için kullanacağı ortak metot."""
        return await call_agent(
            system_prompt=self.system_prompt,
            user_message=user_message,
        )

    @abstractmethod
    async def run(self, *args, **kwargs):
        """Her agent kendi ana mantığını burada tanımlamak zorunda."""
        raise NotImplementedError