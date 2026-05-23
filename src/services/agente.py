import json
import os

from dotenv import load_dotenv
from groq import Groq

from src.core.logger import logger

# ruff: noqa: E501

AGENT_TEMPERATURE = 0.5
AGENT_MAX_TOKENS = 2048
JSON_DUMP_INDENT = 4

load_dotenv()

API_KEY = os.getenv("API_KEY")

model_llama_3_3_70b_versatile = "llama-3.3-70b-versatile"
model_llama_3_1_8b_instant = "llama-3.1-8b-instant"

agent_prompt = "# importar prompt"


def run_agent(user_input: dict | str) -> str:
    if not API_KEY:
        logger.error("API_KEY não definida. Aborting run_agent.")
        raise RuntimeError("API_KEY não está definida")

    if isinstance(user_input, dict):
        user_input_str = json.dumps(
            user_input,
            ensure_ascii=False,
            indent=JSON_DUMP_INDENT,
        )
    else:
        user_input_str = str(user_input)

    logger.info("Iniciando chamada ao agente")
    logger.debug("run_agent: tamanho do input=%s", len(user_input_str))
    custom_agent = agent_prompt
    client = Groq(
        api_key=API_KEY,
    )

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": custom_agent,
                },
                {"role": "user", "content": user_input_str},
            ],
            temperature=AGENT_TEMPERATURE,
            max_tokens=AGENT_MAX_TOKENS,
            model=model_llama_3_1_8b_instant,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logger.error("Erro na chamada ao Groq: %s", e)
        raise
