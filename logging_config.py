"""
Merkezi logging yapılandırması. Tüm modüller buradan bir logger alacak,
her dosyada elle logging.basicConfig() çağırmayacağız.
"""

import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """
    Uygulama genelinde logging formatını ve seviyesini ayarlar.
    main.py başında bir kere çağrılması yeterli.
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


def get_logger(name: str) -> logging.Logger:
    """
    Her modül kendi adıyla bir logger alır - böylece log satırında
    hangi dosyadan geldiği görülür (agents.planner, app.main gibi).
    """
    return logging.getLogger(name)