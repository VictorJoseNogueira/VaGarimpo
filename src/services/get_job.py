from src.core.database import db_connect
from src.database.db_service import read_all_jobs
from src.core.logger import logger
from src.services.agente import run_agent


db_connect()
jobs = read_all_jobs()
count = 0
for job in jobs:

    test = {}
    test["title"] = job["title"]
    test["description"] = job["description"]
    logger.info("%s", test["title"])
    logger.warning("%s", test["description"])
    #    respondeu = run_agent(user_input=test)
    #    logger.critical(respondeu)
    count+=1
    if count == 3:
        break