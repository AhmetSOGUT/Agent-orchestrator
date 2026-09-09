"""
Merkezi konfigürasyon yönetimi. Tüm environment variable'lar buradan okunur,
başka hiçbir dosyada doğrudan os.getenv() kullanılmaz.

Avantajı: Eksik/yanlış bir env variable varsa uygulama AÇILIRKEN hata verir,
çalışırken ortada patlamak yerine - "fail fast" prensibi.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # .env dosyasından okunacak alanlar - isimler .env'deki isimlerle eşleşmeli
    google_api_key: str

    # Varsayılan değeri olan ayarlar (gerekirse .env'den override edilebilir)
    model_name: str = "gemini-flash-lite-latest"
    max_tokens: int = 1024
    retry_max_attempts: int = 3
    log_level: str = "INFO" 

    # pydantic-settings'e .env dosyasını nereden okuyacağını söylüyoruz
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


# Tek bir global instance - tüm proje bunu import edip kullanacak
settings = Settings()