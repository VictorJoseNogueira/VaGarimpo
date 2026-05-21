import os

from dotenv import load_dotenv
from mongoengine import connect, disconnect
from pymongo.errors import ServerSelectionTimeoutError

load_dotenv()


def db_connect():
    MONGO_URI = os.getenv("MONGO_URI")
    if not MONGO_URI:
        raise ValueError("MONGO_URI não encontrada no arquivo .env")

    try:
        client = connect(host=MONGO_URI)
        client.server_info()
        print("Conectado ao MongoDB com sucesso.")
    except ServerSelectionTimeoutError as e:
        raise RuntimeError(
            f"Falha de rede ou credenciais incorretas ao conectar ao MongoDB: {e}"
        )

def db_disconnect():
    """
    Chame esta função apenas quando a aplicação estiver sendo encerrada 
    (ex: no shutdown event de uma API).
    """
    disconnect()
    print("Conexão com o MongoDB encerrada.")