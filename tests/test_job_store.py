"""
InMemoryJobStore testleri. Harici bağımlılık yok, doğrudan test edilebilir.
"""

import pytest
from job_store import InMemoryJobStore, JobStatus


@pytest.mark.asyncio
async def test_create_job_sets_pending_status():
    store = InMemoryJobStore()
    await store.create("job-1")

    job = await store.get("job-1")

    assert job is not None
    assert job["status"] == JobStatus.PENDING
    assert job["result"] is None


@pytest.mark.asyncio
async def test_get_nonexistent_job_returns_none():
    store = InMemoryJobStore()

    job = await store.get("olmayan-job-id")

    assert job is None


@pytest.mark.asyncio
async def test_update_changes_job_status():
    store = InMemoryJobStore()
    await store.create("job-2")

    await store.update("job-2", status=JobStatus.RUNNING)
    job = await store.get("job-2")
    assert job["status"] == JobStatus.RUNNING

    await store.update("job-2", status=JobStatus.DONE, result={"rapor": "içerik"})
    job = await store.get("job-2")
    assert job["status"] == JobStatus.DONE
    assert job["result"] == {"rapor": "içerik"}


@pytest.mark.asyncio
async def test_jobs_are_isolated_from_each_other():
    """İki farklı job birbirini etkilememeli."""
    store = InMemoryJobStore()
    await store.create("job-a")
    await store.create("job-b")

    await store.update("job-a", status=JobStatus.DONE)

    job_a = await store.get("job-a")
    job_b = await store.get("job-b")

    assert job_a["status"] == JobStatus.DONE
    assert job_b["status"] == JobStatus.PENDING  # etkilenmemiş olmalı