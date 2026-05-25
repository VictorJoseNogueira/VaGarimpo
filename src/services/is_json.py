import json
import re

from src.core.logger import logger


def clean_and_parse_json(llm_response: str) -> dict | list | None:
    """
    Remove marcações markdown de uma resposta de LLM e
    tenta converter a string em um objeto Python.
    Retorna None se a string não for um JSON válido.
    """
    clean_response = re.sub(r"```(?:json|JSON)?\s*\n|```", "", llm_response).strip()

    try:
        parsed_data = json.loads(clean_response)
        return parsed_data
    except json.JSONDecodeError:
        logger.error("Not a valid JSON response")
        return None
