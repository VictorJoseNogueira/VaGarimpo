from src.core.database import db_connect
from src.database.db_service import read_all_jobs
from src.core.logger import logger
from src.services.agente import run_agent


db_connect()
jobs = read_all_jobs()

with open("src/assets/prompts/first_filter.txt", "r", encoding="utf-8") as file:
    first_filter = file.read()

with open("src/assets/prompts/final_filter.txt", "r", encoding="utf-8") as file:
    final_filter = file.read()



for job in jobs:
    job_dict = {}
    job_dict["title"] = job["title"]
    job_dict["description"] = job["description"]
    response = run_agent(agent=first_filter, user_input=job_dict)
    logger.critical(response)
