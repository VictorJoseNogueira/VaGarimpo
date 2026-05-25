from src.core.database import db_connect
from src.core.logger import logger
from src.database.db_service import read_all_jobs, update_a_job
from src.services.agente import AgentManager
from src.services.is_json import clean_and_parse_json

db_connect()


def load_prompt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


class JobFilterManager:
    def __init__(self, first_filter_prompt: str, final_filter_prompt: str):
        self.jobs = read_all_jobs()
        self.first_agent = AgentManager(system_prompt=first_filter_prompt)
        self.final_agent = AgentManager(system_prompt=final_filter_prompt)

    def _get_first_match_score(self, job):
        """Método auxiliar seguro para extrair o score evitando AttributeError."""
        try:
            return job.llm_response.first_match.score
        except AttributeError:
            return None

    def run_first_filter(self):
        """Processa a primeira etapa do filtro usando o state interno da classe."""
        for job in self.jobs:
            job_dict = {
                "title": getattr(job, "title", "Título não informado"),
                "description": getattr(
                    job, "description", "Descrição não informada"
                ),
            }

            score = self._get_first_match_score(job)

            # Se o score for válido, não reprocessa
            if score is not None and score != "ERROR RESPONSE":
                continue

            # Execução do agente
            response = self.first_agent.execute(user_input=str(job_dict))
            json_response = clean_and_parse_json(response)

            # Uso do .get() previne KeyError caso a formatação do LLM falhe
            if not json_response:
                update_data = {
                    "set__llm_response__first_match__raciocinio_passo_a_passo": "ERROR RESPONSE",  # noqa E501
                    "set__llm_response__first_match__score": "ERROR RESPONSE",  # noqa E501
                }
            else:
                update_data = {
                    "set__llm_response__first_match__raciocinio_passo_a_passo": json_response.get(  # noqa E501
                        "raciocinio_passo_a_passo", "Campo omitido pelo LLM"
                    ),
                    "set__llm_response__first_match__score": str(
                        json_response.get("score", "ERROR")
                    ),
                }

            # Correção: acessando o ID do job como propriedade de objeto
            update_a_job(job_id=job.id, data=update_data)
            logger.info(
                f"Atualizando job: {job.title} | Score: {update_data['set__llm_response__first_match__score']}"  # noqa E501
            )

        return self


# Instanciação correta
prompt_first = load_prompt("src/assets/prompts/first_filter.txt")
prompt_final = load_prompt("src/assets/prompts/final_filter.txt")

# Inicializa o gerenciador e roda a fase específica
manager = JobFilterManager(
    first_filter_prompt=prompt_first, final_filter_prompt=prompt_final
)
manager.run_first_filter()
