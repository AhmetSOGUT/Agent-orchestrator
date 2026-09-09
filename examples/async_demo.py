"""
Bu dosya sadece ÖĞRENME amaçlı - gerçek projede kullanmayacağız.
Amaç: async/await neden bize lazım, senkron koddan farkı ne, görmek.

Senaryo: 3 tane "researcher agent" var, her biri web'de arama yapıyor
diyelim ve her arama 2 saniye sürüyor (gerçekte LLM/API çağrısı olacak).
"""

import asyncio
import time


# ------------------------------------------------------------------
# 1) SENKRON (SIRALI) VERSİYON - klasik Python, birbirini bekler
# ------------------------------------------------------------------
def research_sync(topic: str) -> str:
    print(f"  [SYNC] '{topic}' araştırılıyor...")
    time.sleep(2)  # burada gerçek bir API çağrısı olsaydı, 2 saniye "bekleriz"
    return f"'{topic}' hakkında bulgular"


def run_sync_version():
    print("\n=== SENKRON ÇALIŞTIRMA ===")
    start = time.time()

    topics = ["elektrikli araç fiyatları", "şarj altyapısı", "devlet teşvikleri"]
    results = [research_sync(t) for t in topics]  # her biri sırayla, birbirini bekleyerek

    elapsed = time.time() - start
    print(f"Sonuçlar: {results}")
    print(f"Toplam süre: {elapsed:.1f} saniye  <-- 3 x 2sn = ~6 saniye")


# ------------------------------------------------------------------
# 2) ASENKRON (PARALEL) VERSİYON - await ile "bekleme" sırasında
#    Python başka işe geçebiliyor, hepsi AYNI ANDA başlıyor
# ------------------------------------------------------------------
async def research_async(topic: str) -> str:
    print(f"  [ASYNC] '{topic}' araştırılıyor...")
    await asyncio.sleep(2)  # "bekliyorum ama bu sırada başka agent çalışabilir"
    return f"'{topic}' hakkında bulgular"


async def run_async_version():
    print("\n=== ASENKRON (PARALEL) ÇALIŞTIRMA ===")
    start = time.time()

    topics = ["elektrikli araç fiyatları", "şarj altyapısı", "devlet teşvikleri"]
    # asyncio.gather = "hepsini aynı anda başlat, hepsi bitince sonuçları topla"
    results = await asyncio.gather(*(research_async(t) for t in topics))

    elapsed = time.time() - start
    print(f"Sonuçlar: {results}")
    print(f"Toplam süre: {elapsed:.1f} saniye  <-- 3'ü de aynı anda, ~2 saniye")


if __name__ == "__main__":
    run_sync_version()
    asyncio.run(run_async_version())