"""
Job Store soyutlaması. app/main.py sadece bu interface'i bilir,
gerçekte hafızada mı yoksa Redis'te mi tutulduğunu bilmesine gerek yok.
İleride Redis'e geçmek istersek, sadece RedisJobStore diye yeni bir
sınıf yazıp aşağıdaki get_job_store() fonksiyonunda onu döndürmemiz yeterli.
"""

from abc import ABC, abstractmethod
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class JobStore(ABC):
    """Job'ları saklamak/okumak için soyut arayüz (interface)."""

    @abstractmethod
    async def create(self, job_id: str) -> None:
        """Yeni bir job kaydı oluşturur, başlangıç durumu PENDING."""
        raise NotImplementedError

    @abstractmethod
    async def get(self, job_id: str) -> dict | None:
        """Job'ın mevcut durumunu/sonucunu döner. Yoksa None."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, job_id: str, **fields) -> None:
        """Job'ın durumunu/sonucunu/hatasını günceller."""
        raise NotImplementedError


class InMemoryJobStore(JobStore):
    """
    Basit, hafızada tutan implementasyon. Küçük projeler/geliştirme için yeterli.
    Production'da RedisJobStore gibi kalıcı bir alternatifle değiştirilebilir.
    """

    def __init__(self):
        self._jobs: dict[str, dict] = {}

    async def create(self, job_id: str) -> None:
        self._jobs[job_id] = {"status": JobStatus.PENDING, "result": None}

    async def get(self, job_id: str) -> dict | None:
        return self._jobs.get(job_id)

    async def update(self, job_id: str, **fields) -> None:
        if job_id in self._jobs:
            self._jobs[job_id].update(fields)


# Tek bir global instance - tüm uygulama bunu kullanacak.
# İleride Redis'e geçersek burada "job_store = RedisJobStore(...)" yazmamız yeterli olacak.
job_store: JobStore = InMemoryJobStore()