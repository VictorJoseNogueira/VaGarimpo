import json
import re  # <--- Importe o módulo de Regex

from src.core.logger import logger

JSON_PREVIEW_LENGTH = 200


def _parse_json_match(text: str):
    """Extrai e valida o primeiro objeto JSON encontrado no texto."""
    match = re.search(r"(\{.*})", text, re.DOTALL)
    if not match:
        logger.debug(
            "extract_valid_json: nenhum JSON válido encontrado no texto de entrada"
        )
        return None
    parsed = json.loads(match.group(1))
    logger.debug(
        "extract_valid_json: sucesso ao parsear JSON com %s chaves",
        len(parsed) if isinstance(parsed, dict) else 0,
    )
    return parsed


def extract_valid_json(text):
    """
    Remove textos extras antes ou depois do JSON e limpa blocos markdown.
    """
    try:
        return _parse_json_match(text)
    except (json.JSONDecodeError, AttributeError):
        snippet = (
            (text[:JSON_PREVIEW_LENGTH] + "...") if isinstance(text, str) else ""
        )
        logger.warning(
            "extract_valid_json: falha ao parsear JSON. trecho: %s", snippet
        )
        return None
