"""
Writer Agent: researcher'lardan gelen dağınık bulguları alır,
tek bir akıcı ve düzenli rapor haline getirir.
"""

from agents.base import call_agent

WRITER_SYSTEM_PROMPT = """Sen profesyonel bir rapor yazarısın. Sana bir ana konu ve
bu konunun farklı alt başlıkları hakkında toplanmış ham araştırma notları verilecek.

GÖREVİN:
- Bu notları tek, akıcı ve düzenli bir rapora dönüştürmek.
- Markdown formatı kullan: başlık için #, alt başlıklar için ##.
- Girişte konuyu kısaca tanıt, sonra her alt başlığı ayrı bölüm olarak işle,
  sonunda kısa bir "Sonuç / Değerlendirme" bölümü ekle.
- Ham notları olduğu gibi kopyalama, kendi cümlelerinle daha akıcı hale getir.
- Türkçe yaz.
"""


async def write_report(topic: str, findings: dict[str, str]) -> str:
    """
    findings: {"alt başlık": "araştırma bulgusu", ...}
    Dönüş: tek parça, Markdown formatlı rapor metni.
    """
    # Ham bulguları tek bir metin haline getirip modele veriyoruz
    findings_text = "\n\n".join(
        f"## {subtopic}\n{finding}" for subtopic, finding in findings.items()
    )

    user_message = f"""Ana konu: {topic}

Toplanan ham araştırma notları:

{findings_text}

Bu notlardan yukarıdaki kurallara uygun bir rapor oluştur."""

    report = await call_agent(
        system_prompt=WRITER_SYSTEM_PROMPT,
        user_message=user_message,
    )
    return report