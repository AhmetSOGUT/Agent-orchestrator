"""
Writer Agent: researcher'lardan gelen dağınık bulguları alır,
tek bir akıcı ve düzenli rapor haline getirir.
"""

from agents.agent import BaseAgent


class WriterAgent(BaseAgent):
    system_prompt = """Sen profesyonel bir rapor yazarısın. Sana bir ana konu ve
bu konunun farklı alt başlıkları hakkında toplanmış ham araştırma notları verilecek.

GÖREVİN:
- Bu notları tek, akıcı ve düzenli bir rapora dönüştürmek.
- Markdown formatı kullan: başlık için #, alt başlıklar için ##.
- Girişte konuyu kısaca tanıt, sonra her alt başlığı ayrı bölüm olarak işle,
  sonunda kısa bir "Sonuç / Değerlendirme" bölümü ekle.
- Ham notları olduğu gibi kopyalama, kendi cümlelerinle daha akıcı hale getir.
- Türkçe yaz.
"""

    async def run(self, topic: str, findings: dict[str, str]) -> str:
        self.logger.info(f"Rapor yazılıyor: '{topic}'")

        findings_text = "\n\n".join(
            f"## {subtopic}\n{finding}" for subtopic, finding in findings.items()
        )

        user_message = f"""Ana konu: {topic}

Toplanan ham araştırma notları:

{findings_text}

Bu notlardan yukarıdaki kurallara uygun bir rapor oluştur."""

        report = await self._call_llm(user_message)
        self.logger.info("Rapor tamamlandı")
        return report