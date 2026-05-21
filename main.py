import argparse
import os
import subprocess
import sys
from pathlib import Path

from src.core.logger import logger

ROOT_DIR = Path(__file__).resolve().parent
SCRAPER_MODULE = "src.scrapper.scrapper"
GET_JOB_MODULE = "src.services.get_job"


def run_module(module_name: str) -> int:
    logger.info("[main] Executando módulo %s...", module_name)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT_DIR)
    process = subprocess.run(
        [sys.executable, "-m", module_name],
        cwd=ROOT_DIR,
        env=env,
        check=False,
    )
    return process.returncode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Ponto de entrada para executar o scraper "
            "e o pipeline de processamento de vagas."
        )
    )
    parser.add_argument(
        "--mode",
        choices=["scraper", "get-job", "all"],
        default=os.getenv("APP_MODE", "all"),
        help="Modo de execução: scraper, get-job ou all.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.mode in {"scraper", "all"}:
        code = run_module(SCRAPER_MODULE)
        if code != 0:
            logger.error("[main] Erro no scraper: código de saída %s", code)
            return code

    if args.mode in {"get-job", "all"}:
        code = run_module(GET_JOB_MODULE)
        if code != 0:
            logger.error("[main] Erro no get_job: código de saída %s", code)
            return code

    logger.info("[main] Execução concluída com sucesso.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
