from src.core.database import db_connect, db_disconnect
from src.core.logger import logger
from src.database.db_service import mark_jobs_email_sent
from src.models.job_model import JobData
from src.services.email_service import send_job_email, send_overflow_warning_email
from src.services.job_selection import (
    MAX_JOBS_TO_SEND,
    MIN_SCORE,
    JobSelectionResult,
    select_jobs_for_email,
)


class JobEmailProcessor:
    @staticmethod
    def run() -> JobSelectionResult:
        logger.info("[job_email] Iniciando pipeline de envio de e-mails.")
        result = select_jobs_for_email()
        logger.debug(
            "[job_email] Seleção concluída: %s vaga(s), overflow=%s, "
            "min_score_used=%s.",
            len(result.jobs),
            result.overflow,
            result.min_score_used,
        )

        if result.overflow:
            logger.warning(
                "[job_email] Mais de %s vagas com score >= %s e "
                "enviado_email=False. Enviando apenas alerta de volume.",
                MAX_JOBS_TO_SEND,
                result.min_score_used,
            )
            if send_overflow_warning_email():
                logger.info("[job_email] Alerta de overflow enviado com sucesso.")
            else:
                logger.error("[job_email] Falha ao enviar alerta de overflow.")
            return result

        if not result.jobs:
            logger.info(
                "[job_email] Nenhuma vaga elegível (score >= %s, enviado_email=False).",  # noqa: E501
                MIN_SCORE,
            )
            return result

        logger.info(
            "[job_email] Enviando e-mails para %s vaga(s) (min_score=%s).",
            len(result.jobs),
            result.min_score_used,
        )

        sent_ids: list[str] = []
        for job in result.jobs:
            logger.debug(
                "[job_email] Tentativa de envio id=%s: %s",
                job.id,
                job.title,
            )
            if send_job_email(job):
                sent_ids.append(str(job.id))
                logger.debug("[job_email] E-mail confirmado para id=%s.", job.id)
            else:
                logger.warning(
                    "[job_email] Falha no envio para id=%s: %s",
                    job.id,
                    job.title,
                )

        failed_count = len(result.jobs) - len(sent_ids)
        if sent_ids:
            updated = mark_jobs_email_sent(sent_ids)
            logger.info(
                "[job_email] %s vaga(s) enviada(s) e marcada(s) no banco "
                "(score mínimo: %s, registros atualizados: %s).",
                len(sent_ids),
                result.min_score_used,
                updated,
            )
            logger.debug("[job_email] IDs marcados enviado_email=True: %s", sent_ids)

        if failed_count:
            logger.warning(
                "[job_email] %s de %s e-mail(s) não enviado(s).",
                failed_count,
                len(result.jobs),
            )

        if result.jobs and not sent_ids:
            logger.error(
                "[job_email] Nenhum e-mail enviado em %s tentativa(s).",
                len(result.jobs),
            )

        logger.info("[job_email] Pipeline de envio finalizado.")
        return result


def format_jobs_report(jobs: list[JobData]) -> None:
    if not jobs:
        print(f"Nenhuma vaga elegível (score >= {MIN_SCORE}, enviado_email=False).")
        return

    print(f"Total: {len(jobs)} vaga(s)\n")
    for job in jobs:
        score = job.llm_response.first_match.score
        print("-" * 60)
        print(f"Título: {job.title}")
        print(f"Link:   {job.link}")
        print(f"Score:  {score}")
        if job.llm_response.status:
            print(f"Status: {job.llm_response.status}")
        print()


def main() -> None:
    logger.info("[job_email] Módulo job_email_processor iniciado.")
    db_connect()
    try:
        processor = JobEmailProcessor()
        result = processor.run()
        if not result.overflow:
            format_jobs_report(result.jobs)
    except Exception:
        logger.critical(
            "[job_email] Falha irrecuperável no pipeline de e-mail.",
            exc_info=True,
        )
        raise
    finally:
        db_disconnect()
        logger.debug("[job_email] Conexão com o banco encerrada.")


if __name__ == "__main__":
    main()
