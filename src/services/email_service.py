import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.core.logger import logger

OVERFLOW_MESSAGE = (
    "Atenção: Há um volume excessivo de vagas altamente compatíveis "
    "(mais de 10 disponíveis). Por favor, verifique o dashboard para "
    "visualizar todas."
)

SMTP_REQUIRED_VARS = ("SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD", "EMAIL_TO")


def _smtp_configured() -> bool:
    missing = [key for key in SMTP_REQUIRED_VARS if not os.getenv(key)]
    if missing:
        logger.debug(
            "[email] SMTP incompleto; variáveis ausentes: %s",
            ", ".join(missing),
        )
        return False
    logger.debug("[email] Configuração SMTP presente.")
    return True


def _build_message(subject: str, body: str) -> MIMEMultipart:
    msg = MIMEMultipart()
    msg["From"] = os.getenv("EMAIL_FROM", os.getenv("SMTP_USER", ""))
    msg["To"] = os.environ["EMAIL_TO"]
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))
    logger.debug(
        "[email] Mensagem montada: From=%s, To=%s, Subject=%s",
        msg["From"],
        msg["To"],
        subject,
    )
    return msg


def send_email(subject: str, body: str) -> bool:
    if os.getenv("DRY_RUN_EMAIL", "").lower() in {"1", "true", "yes"}:
        logger.info("[email] DRY_RUN ativo — assunto: %s", subject)
        logger.debug("[email] DRY_RUN — corpo:\n%s", body)
        return True

    if not _smtp_configured():
        logger.warning(
            "[email] SMTP não configurado. Defina SMTP_HOST, SMTP_USER, "
            "SMTP_PASSWORD e EMAIL_TO no .env (ou use DRY_RUN_EMAIL=true)."
        )
        return False

    msg = _build_message(subject, body)
    host = os.environ["SMTP_HOST"]
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASSWORD"]

    logger.debug("[email] Conectando a %s:%s como %s", host, port, user)
    try:
        with smtplib.SMTP(host, port, timeout=30) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(msg["From"], [msg["To"]], msg.as_string())
        logger.info("[email] Enviado: %s", subject)
        return True
    except Exception:
        logger.exception("[email] Falha ao enviar: %s", subject)
        return False


def build_job_email_body(job) -> str:
    score = job.llm_response.first_match.score
    lines = [
        f"Título: {job.title}",
        f"Link: {job.link}",
        f"Score: {score}",
    ]
    if job.llm_response.status:
        lines.append(f"Status: {job.llm_response.status}")
    if job.llm_response.match_percentage is not None:
        lines.append(f"Match %: {job.llm_response.match_percentage}")
    if job.llm_response.proposta:
        lines.append(f"\nProposta:\n{job.llm_response.proposta}")
    body = "\n".join(lines)
    logger.debug(
        "[email] Corpo montado para vaga id=%s (score=%s, %s caracteres).",
        job.id,
        score,
        len(body),
    )
    return body


def send_job_email(job) -> bool:
    score = job.llm_response.first_match.score
    subject = f"[VaGarimpo] Vaga compatível (score {score}): {job.title[:60]}"
    logger.debug(
        "[email] Preparando envio de vaga id=%s (score=%s): %s",
        job.id,
        score,
        job.title,
    )
    return send_email(subject, build_job_email_body(job))


def send_overflow_warning_email() -> bool:
    subject = "[VaGarimpo] Volume excessivo de vagas compatíveis"
    logger.info("[email] Enviando alerta de overflow de vagas.")
    return send_email(subject, OVERFLOW_MESSAGE)
