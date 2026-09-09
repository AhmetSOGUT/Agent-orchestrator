"""
PlannerAgent testleri. Gerçek API'ye istek atmıyoruz -
_call_llm metodunu sahte (mock) bir cevapla değiştiriyoruz,
sadece plan() fonksiyonunun JSON'u doğru işleyip işlemediğini test ediyoruz.
"""

import pytest
from agents.planner import PlannerAgent


@pytest.mark.asyncio
async def test_plan_parses_valid_json(mocker):
    """Model düzgün bir JSON listesi döndürdüğünde, doğru parse edilmeli."""
    planner = PlannerAgent()

    # _call_llm'i mock'luyoruz - gerçek API'ye gitmek yerine sahte bir cevap dönecek
    mocker.patch.object(
        planner,
        "_call_llm",
        return_value='["Alt görev 1", "Alt görev 2", "Alt görev 3"]',
    )

    result = await planner.run("test konusu")

    assert result == ["Alt görev 1", "Alt görev 2", "Alt görev 3"]
    assert len(result) == 3


@pytest.mark.asyncio
async def test_plan_handles_markdown_wrapped_json(mocker):
    """Model bazen JSON'u ```json ``` bloğu içine sarıyor - bunu temizleyebilmeliyiz."""
    planner = PlannerAgent()

    mocker.patch.object(
        planner,
        "_call_llm",
        return_value='```json\n["Görev A", "Görev B"]\n```',
    )

    result = await planner.run("test konusu")

    assert result == ["Görev A", "Görev B"]


@pytest.mark.asyncio
async def test_plan_falls_back_on_invalid_json(mocker):
    """Model geçersiz bir cevap dönerse, çökmek yerine konuyu tek elemanlı liste yapmalı."""
    planner = PlannerAgent()

    mocker.patch.object(
        planner,
        "_call_llm",
        return_value="bu geçerli bir JSON değil, sadece düz metin",
    )

    result = await planner.run("yedek konu")

    # Fallback davranışı: parse edilemezse, orijinal konu tek elemanlı liste olarak dönüyor
    assert result == ["yedek konu"]