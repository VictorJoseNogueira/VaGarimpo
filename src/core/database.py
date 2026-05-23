import os

from dotenv import load_dotenv
from mongoengine import connect, disconnect
from pymongo.errors import ServerSelectionTimeoutError

from src.core.logger import logger

load_dotenv()


def db_connect():
    MONGO_URI = os.getenv("MONGO_URI")
    if not MONGO_URI:
        raise ValueError("MONGO_URI não encontrada no arquivo .env")

    if not MONGO_URI:
        logger.critical("MONGO_URI não encontrada no arquivo .env")
        raise ValueError("MONGO_URI não encontrada no arquivo .env")

    try:
        client = connect(host=MONGO_URI)
        client.server_info()
        logger.info("Conectado ao MongoDB com sucesso.")
    except ServerSelectionTimeoutError as e:
        logger.error(
            "Falha de rede ou credenciais incorretas ao conectar ao MongoDB: %s",
            e,
        )
        raise RuntimeError(
            f"Falha de rede ou credenciais incorretas ao conectar ao MongoDB: {e}"
        )


def db_disconnect():
    """
    Chame esta função apenas quando a aplicação estiver sendo encerrada
    (ex: no shutdown event de uma API).
    """
    disconnect()
    logger.info("Conexão com o MongoDB encerrada.")
