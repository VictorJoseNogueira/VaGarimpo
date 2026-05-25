from typing import Any

from mongoengine.errors import NotUniqueError

from src.core.logger import logger
from src.models.job_model import JobData


def post_a_job(data: dict[str, Any]) -> None:
    """
    Cria uma nova entrada no banco de dados usando a classe de modelo fornecida.
    """
    try:
        instance = JobData(**data).save()
        logger.debug("Entrada criada com ID: %s", instance.id)
        logger.debug("Dados salvos: %s", instance.to_json())
    except NotUniqueError:
        logger.debug(
            "post_a_job: link '%s' já existe. Ignorando entrada duplicada.",
            data.get("link"),
        )

    except Exception as e:
        raise RuntimeError(f"Erro ao criar entrada no banco de dados: {e}") from e


def read_specific_job(url: str) -> object:
    job = JobData.objects(link=url).first()
    if job:
        return job


def read_all_jobs() -> list[object]:
    return list(JobData.objects())


def update_a_job(job_id: str, data: dict) -> None:
    if not data:
        return
    update_count = JobData.objects(id=job_id).update_one(**data)
    if update_count == 0:
        raise ValueError(f"Job com ID '{job_id}' não encontrado.")


def update_a_job_url(url: str, data: dict) -> None:
    job = JobData.objects(link=url).first()
    if not job:
        raise ValueError(f"Job com url '{url}' não encontrado.")
    if not data:
        return
    job.update(data)


def delete_a_job(url: str):
    job = JobData.objects(link=url).first()
    if job:
        job.delete()
    else:
        raise ValueError(f"Job com url '{url}' não encontrado.")


def mark_jobs_email_sent(job_ids: list[str]) -> int:
    """Marca vagas como enviadas por e-mail para evitar reenvio."""
    if not job_ids:
        return 0
    return JobData.objects(id__in=job_ids).update(set__enviado_email=True)
