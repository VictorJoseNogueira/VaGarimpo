from dataclasses import dataclass

from src.core.logger import logger
from src.models.job_model import JobData

MIN_SCORE = 80
MAX_SCORE = 100
MAX_JOBS_TO_SEND = 10
SCORE_INCREMENT = 5


@dataclass(frozen=True)
class JobSelectionResult:
    jobs: list[JobData]
    overflow: bool
    min_score_used: int


def fetch_eligible_jobs(min_score: int) -> list[JobData]:
    """Vagas com score >= min_score, ainda não enviadas por e-mail."""
    jobs = list(
        JobData.objects(
            enviado_email=False,
            llm_response__first_match__score__gte=min_score,
        ).order_by("-scrapp_at")
    )
    logger.debug(
        "[job_selection] Consulta min_score=%s: %s vaga(s) elegível(eis).",
        min_score,
        len(jobs),
    )
    return jobs


def select_jobs_for_email() -> JobSelectionResult:
    """
    Seleciona vagas para envio individual ou sinaliza overflow.

    - Filtro inicial: score >= 80 e enviado_email == False.
    - Se houver mais de 10, eleva o score de 5 em 5 até 100.
    - Se em score 100 ainda houver mais de 10, retorna overflow=True.
    - Caso contrário, retorna até 10 vagas (as mais recentes).
    """
    logger.info("[job_selection] Iniciando seleção de vagas para e-mail.")
    min_score = MIN_SCORE
    pool: list[JobData] = []

    while min_score <= MAX_SCORE:
        pool = fetch_eligible_jobs(min_score)

        if len(pool) <= MAX_JOBS_TO_SEND:
            selected = pool[:MAX_JOBS_TO_SEND]
            logger.info(
                "[job_selection] Selecionadas %s vaga(s) (min_score=%s, overflow=False).",  # noqa: E501
                len(selected),
                min_score,
            )
            return JobSelectionResult(
                jobs=selected,
                overflow=False,
                min_score_used=min_score,
            )

        if min_score >= MAX_SCORE:
            logger.warning(
                "[job_selection] Overflow: %s vaga(s) com score >= %s "
                "(limite de envio: %s).",
                len(pool),
                MAX_SCORE,
                MAX_JOBS_TO_SEND,
            )
            return JobSelectionResult(
                jobs=[],
                overflow=True,
                min_score_used=MAX_SCORE,
            )

        next_score = min_score + SCORE_INCREMENT
        logger.info(
            "[job_selection] Pool com %s vaga(s) excede limite %s; "
            "elevando min_score de %s para %s.",
            len(pool),
            MAX_JOBS_TO_SEND,
            min_score,
            next_score,
        )
        min_score = next_score

    logger.debug(
        "[job_selection] Loop encerrado sem retorno antecipado; retorno vazio."
    )
    return JobSelectionResult(jobs=[], overflow=False, min_score_used=MAX_SCORE)
