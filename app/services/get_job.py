import json
import os
from time import sleep
from app.services.agente import run_agent
from datetime import datetime
import math
from app.services.get_json import extract_valid_json
from app.logger import logger

origin_json = os.getenv("JSON_PATH", "app/data/projects.json")

# Carregar dados do arquivo de origem
logger.info("Iniciando processamento de vagas a partir de %s", origin_json)
with open(origin_json) as file:
    data_json = json.load(file)
    start_at = datetime.now()
    n_req = 0
    total_rows = len(data_json)
    limit_pages = 0
    processed = 0
    
    for key, value in data_json.items():
        if limit_pages >= 20:
            break
        
        # Pular se já foi processado (já tem llm_response)
        if isinstance(value, dict) and "llm_response" in value:
            logger.debug("Pulando item já processado: %s", key)
            limit_pages += 1
            continue
            
        if n_req >= 28:
            # Salvar dados no mesmo arquivo
            with open(origin_json, "w", encoding="utf-8") as data_json_file:
                json.dump(data_json, data_json_file, ensure_ascii=False, indent=4)
            logger.info("Dados salvos temporariamente em %s", origin_json)
            
            # Esperar até completar 62 segundos desde start_at
            current_time = datetime.now()
            remaining_time = current_time - start_at
            remaining_time = math.trunc(remaining_time.total_seconds())
            if remaining_time < 62:
                wait_time = 62 - remaining_time
                logger.info("Pausa rate-limit: aguardando %s segundos", wait_time)
                sleep(wait_time)
            
            n_req = 0
            start_at = datetime.now()

        my_input = f"Vaga: {key}\nDados: {value}"

        logger.debug("--- inicio item ---")
        logger.info("Processando item %s/%s: %s", limit_pages+1, total_rows, key)

        # Tentativa de chamada ao agente
        try:
            agent_requisition = run_agent(user_input=my_input)
        except Exception as e:
            logger.error("Falha ao executar run_agent para '%s': %s", key, e)
            if isinstance(value, dict):
                data_json[key]["llm_response"] = {
                    "status": "Erro de Execução",
                    "match_percentage": 0,
                    "motivo": f"O agente falhou com a exceção: {str(e)}",
                    "raw_response": None
                }
            n_req += 1
            limit_pages += 1
            processed += 1
            continue

        saved_json = extract_valid_json(agent_requisition)
        
        if saved_json:
            # Adiciona a resposta do LLM ao item original
            if isinstance(value, dict):
                data_json[key]["llm_response"] = saved_json
                logger.debug("Resposta do agente adicionada para %s", key)
        else:
            # Fallback caso o modelo falhe bizarramente em gerar um JSON
            if isinstance(value, dict):
                data_json[key]["llm_response"] = {
                    "status": "Erro de Formatação",
                    "match_percentage": 0,
                    "motivo": "O modelo não retornou um formato JSON extraível.",
                    "raw_response": (agent_requisition[:200] if agent_requisition else None)
                }
                logger.warning("Resposta do agente inválida/sem JSON para %s", key)
            
        n_req += 1
        limit_pages += 1
        processed += 1


# Salvar dados finais no mesmo arquivo
with open(origin_json, "w", encoding="utf-8") as data_json_file:
    json.dump(data_json, data_json_file, ensure_ascii=False, indent=4)
logger.info("Processamento finalizado: %s itens processados", processed)