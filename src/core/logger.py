import logging
import os
import sys

LOG_PATH = os.getenv(
    "LOG_PATH", os.path.join(os.path.dirname(__file__), "..", "scraper.log")
)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logger = logging.getLogger("scrapper")

if not logger.handlers:
    level = getattr(logging, LOG_LEVEL, logging.INFO)
    logger.setLevel(level)
    fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(level)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    try:
        fh = logging.FileHandler(LOG_PATH)
        fh.setLevel(level)
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except Exception:
        # se não conseguir abrir arquivo de log, seguir apenas com stdout
        pass
