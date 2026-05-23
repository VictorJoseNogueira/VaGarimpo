import json
import re  # <--- Importe o módulo de Regex

from src.core.logger import logger

JSON_PREVIEW_LENGTH = 200


def extract_valid_json(text):
    """
    Remove textos extras antes ou depois do JSON e limpa blocos markdown.
    """
    try:
        # Encontra o primeiro '{' e o último '}'
        match = re.search(r"(\{.*})", text, re.DOTALL)
        if match:
            json_clean = match.group(1)
            # Valida se é um JSON estruturalmente correto
            parsed = json.loads(json_clean)
            logger.debug(
                "extract_valid_json: sucesso ao parsear JSON com %s chaves",
                len(parsed) if isinstance(parsed, dict) else 0,
            )
            return parsed
        logger.debug("extract_valid_json: nenhum JSON válido encontrado no texto de entrada")
        return None
    except (json.JSONDecodeError, AttributeError):
        snippet = (
            (text[:JSON_PREVIEW_LENGTH] + "...") if isinstance(text, str) else ""
        )
        logger.warning(
            "extract_valid_json: falha ao parsear JSON. trecho: %s", snippet
        )
        return None
