from src.core.database import db_connect
from src.core.logger import logger
from src.database.db_service import read_all_jobs, update_a_job
from src.services.agente import AgentManager
from src.services.is_json import clean_and_parse_json

FIRST_FILTER_SCORE_THRESHOLD = 75
DEFAULT_FIRST_MATCH_SCORE = 0
DEFAULT_MATCH_PERCENTAGE = 0.0

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

    def _get_final_filter_status(self, job):
        """Retorna o status do segundo filtro, se já existir."""
        try:
            return job.llm_response.status
        except AttributeError:
            return None

    @staticmethod
    def _parse_score(value) -> int:
        """Converte o score do LLM para inteiro compatível com IntField."""
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return DEFAULT_FIRST_MATCH_SCORE

    @staticmethod
    def _parse_match_percentage(value) -> float:
        """Converte match_percentage do LLM para FloatField."""
        try:
            return float(value)
        except (TypeError, ValueError):
            return DEFAULT_MATCH_PERCENTAGE

    def _build_final_update_data(self, json_response: dict | None) -> dict:
        if not json_response:
            return {
                "set__llm_response__status": "ERROR RESPONSE",
                "set__llm_response__match_percentage": DEFAULT_MATCH_PERCENTAGE,
                "set__llm_response__motivation": "ERROR RESPONSE",
                "set__llm_response__strengths": [],
                "set__llm_response__weaknesses": [],
                "set__llm_response__payments": "ERROR RESPONSE",
                "set__llm_response__proposta": "ERROR RESPONSE",
            }
        return {
            "set__llm_response__status": json_response.get("status", "ERROR"),
            "set__llm_response__match_percentage": self._parse_match_percentage(
                json_response.get("match_percentage", DEFAULT_FIRST_MATCH_SCORE)
            ),
            "set__llm_response__motivation": json_response.get("motivation", ""),
            "set__llm_response__strengths": json_response.get("strengths", []),
            "set__llm_response__weaknesses": json_response.get("weaknesses", []),
            "set__llm_response__payments": json_response.get("payments", ""),
            "set__llm_response__proposta": json_response.get("proposal", ""),
        }

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

            # Se o score já foi definido, não reprocessa
            if score is not None:
                continue

            # Execução do agente
            response = self.first_agent.execute(user_input=str(job_dict))
            json_response = clean_and_parse_json(response)

            # Uso do .get() previne KeyError caso a formatação do LLM falhe
            if not json_response:
                update_data = {
                    "set__llm_response__first_match__raciocinio_passo_a_passo": "ERROR RESPONSE",  # noqa E501
                    "set__llm_response__first_match__score": DEFAULT_FIRST_MATCH_SCORE,  # noqa E501
                }
            else:
                update_data = {
                    "set__llm_response__first_match__raciocinio_passo_a_passo": json_response.get(  # noqa E501
                        "raciocinio_passo_a_passo", "Campo omitido pelo LLM"
                    ),
                    "set__llm_response__first_match__score": self._parse_score(
                        json_response.get("score", DEFAULT_FIRST_MATCH_SCORE)
                    ),
                }

            # Correção: acessando o ID do job como propriedade de objeto
            update_a_job(job_id=job.id, data=update_data)
            logger.info(
                f"Atualizando job: {job.title} | Score: {update_data['set__llm_response__first_match__score']}"  # noqa E501
            )
        logger.info(f"Total de jobs processados: {len(self.jobs)}")
        return self

    def run_final_filter(self):
        """Processa a etapa final quando o score do primeiro filtro supera o limiar."""
        self.jobs = read_all_jobs()
        processed_count = 0
        for job in self.jobs:
            score = self._get_first_match_score(job)
            if score is None or score <= FIRST_FILTER_SCORE_THRESHOLD:
                continue

            if self._get_final_filter_status(job) is not None:
                continue

            job_dict = {
                "title": getattr(job, "title", "Título não informado"),
                "description": getattr(
                    job, "description", "Descrição não informada"
                ),
            }
            response = self.final_agent.execute(user_input=str(job_dict))
            json_response = clean_and_parse_json(response)
            update_data = self._build_final_update_data(json_response)
            update_a_job(job_id=job.id, data=update_data)
            processed_count += 1
            logger.info(
                f"Atualizando job: {job.title} | Status: {update_data['set__llm_response__status']} | Match Percentage: {update_data['set__llm_response__match_percentage']}"  # noqa E501
            )
        logger.info(f"Total de jobs na lista: {len(self.jobs)}")
        logger.info(
            f"Total de jobs processados no filtro final (score > {FIRST_FILTER_SCORE_THRESHOLD}): {processed_count}"
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
manager.run_final_filter()