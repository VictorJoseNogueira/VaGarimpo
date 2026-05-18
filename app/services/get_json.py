import json
import math
import os
import re  # <--- Importe o módulo de Regex
from datetime import datetime
from time import sleep
from app.services.agente import run_agent
from app.logger import logger

def extract_valid_json(text):
    """
    Remove textos extras antes ou depois do JSON e limpa blocos markdown.
    """
    try:
        # Encontra o primeiro '{' e o último '}'
        match = re.search(r'(\{.*})', text, re.DOTALL)
        if match:
            json_clean = match.group(1)
            # Valida se é um JSON estruturalmente correto
            parsed = json.loads(json_clean)
            logger.debug("extract_valid_json: sucesso ao parsear JSON com %s chaves", len(parsed) if isinstance(parsed, dict) else 0)
            return parsed
        return None
    except (json.JSONDecodeError, AttributeError):
        snippet = (text[:200] + '...') if isinstance(text, str) else ''
        logger.warning("extract_valid_json: falha ao parsear JSON. trecho: %s", snippet)
        return None
    
