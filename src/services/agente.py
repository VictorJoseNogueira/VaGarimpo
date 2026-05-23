import json
import os

from dotenv import load_dotenv
from groq import Groq

from src.core.logger import logger

# ruff: noqa: E501

AGENT_TEMPERATURE = 0.0
AGENT_MAX_TOKENS = 2048
JSON_DUMP_INDENT = 4

load_dotenv()

API_KEY = os.getenv("API_KEY")
models =  [
    "allam-2-7b",
    "canopylabs/orpheus-arabic-saudi",
    "canopylabs/orpheus-v1-english",
    "groq/compound",
    "groq/compound-mini",
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "meta-llama/llama-prompt-guard-2-22m",
    "meta-llama/llama-prompt-guard-2-86m",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "openai/gpt-oss-safeguard-20b",
    "qwen/qwen3-32b",
    "whisper-large-v3",
    "whisper-large-v3-turbo"
  ]


model_llama_3_3_70b_versatile = "llama-3.3-70b-versatile"
model_llama_3_1_8b_instant = "llama-3.1-8b-instant"

class change_model:
    def __init__(self,position, data):
        self.current_position = 0
        self.current_model = data[self.current_position]
        self.total_models = len(data)

    def next_model(self):
        if self.current_position >= self.total_models - 1:
            self.current_position = 0
        else:
            self.current_position += 1

def run_agent(agent: str, user_input: dict | str) -> str:
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
    custom_agent = agent
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
