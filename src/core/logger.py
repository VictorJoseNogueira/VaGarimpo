import logging
import os
import sys

LOG_PATH = os.getenv(
    "LOG_PATH",
    os.path.join(os.path.dirname(__file__), "..", "scraper.log"),
)

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[94m",  # Azul
        "INFO": "\033[92m",  # Verde
        "WARNING": "\033[93m",  # Amarelo
        "ERROR": "\033[91m",  # Vermelho
        "CRITICAL": "\033[95m",  # Magenta
    }

    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)

        # Inserido %(filename)s no formato
        log_format = (
            f"{color}"
            "%(asctime)s - %(name)s - %(filename)s - %(levelname)s - %(message)s"
            f"{self.RESET}"
        )

        formatter = logging.Formatter(log_format)

        return formatter.format(record)


logger = logging.getLogger("scrapper")

if not logger.handlers:
    level = getattr(logging, LOG_LEVEL, logging.DEBUG)

    logger.setLevel(level)
    logger.propagate = False

    # Console colorido
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(level)
    sh.setFormatter(ColoredFormatter())
    logger.addHandler(sh)

    # Arquivo SEM cor
    try:
        fh = logging.FileHandler(LOG_PATH)
        fh.setLevel(level)

        # Inserido %(filename)s no formato do arquivo também
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(filename)s - %(levelname)s - %(message)s"
        )

        fh.setFormatter(file_formatter)

        logger.addHandler(fh)

    except Exception as e:
        # Tratamento explícito para não suprimir falhas de I/O silenciosamente
        print(f"Falha ao inicializar o FileHandler: {e}", file=sys.stderr)


if __name__ == "__main__":
    logger.debug("Debug")
    logger.info("Info")
    logger.warning("Warning")
    logger.error("Not a valid JSON response")
    logger.critical("Critical")
