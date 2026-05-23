# Scrapper de Vagas — Coletor 99Freelas

Visão geral
------------
Projeto Python para coleta (scraping) de vagas do site 99Freelas, salvando os dados em MongoDB. Fornece um scraper baseado em Playwright, persistência via MongoEngine/MongoDB e um pequeno agente que usa Groq para chamadas a LLMs.

Pré-requisitos
--------------
- Python 3.11+ (recomendado)
- Um ambiente virtual (venv, virtualenv, etc.)
- MongoDB acessível e variável de ambiente `MONGO_URI` configurada
- Variável `API_KEY` para o agente (quando usar `src.services.agente`) 
- Playwright: navegadores instalados via `python -m playwright install`

Instalação
----------
1. Crie e ative um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate
```

2. Instale dependências (antes ajustar `requirements.txt` conforme auditoria abaixo):

```bash
pip install -r requirements.txt
# além disso, instale navegadores do Playwright
python -m playwright install
```


Uso
---
Executar o ponto de entrada:

```bash
python main.py --mode scraper      # roda somente o scraper
python main.py --mode get-job     # roda somente o módulo get-job (arquivo em src/services/get_job.py)
python main.py --mode all         # executa scraper e get-job (padrão)
```

Variáveis de ambiente importantes
- `MONGO_URI` — string de conexão com MongoDB (obrigatória para gravação)
- `API_KEY` — chave para o agente Groq (se utilizar `src/services.agente`)
- `JSON_PATH` — caminho para salvar JSONs (opcional; padrão `src/data/projects.json`)
- `LOG_PATH` — caminho do arquivo de log (opcional)

Estrutura do projeto
--------------------
- `main.py` — ponto de entrada que coordena execução dos módulos.
- `src/` — código-fonte do projeto
  - `src/core/logger.py` — configuração de logging (console + arquivo)
  - `src/core/database.py` — helper para conexão com MongoDB
  - `src/scrapper/` — scraper principal e utilitários
    - `scrapper.py` — classe `scrapper99Freela` que usa Playwright e grava no MongoDB
    - `get_json.py` — utilitário para extrair JSON de textos
  - `src/services/` — serviços auxiliares
    - `db_service.py` — funções de persistência (post/read/update/delete)
    - `agente.py` — cliente simples para chamadas Groq (LLM)
    - `get_job.py` — (excluído do escopo da auditoria por instrução do contexto)
  - `src/models/job_model.py` — modelos `mongoengine` para os documentos de vagas
  - `src/assets/prompts/agent_prompt.txt` — prompt usado pelo agente

Auditoria de dependências (`requirements.txt`)
-------------------------------------------

Resumo da varredura do código (.py em `main.py` e `src/`, excluindo `get_job.py`): imports detectados que demandam pacotes externos:

- `python-dotenv` (import: `from dotenv import load_dotenv`) — usado
- `playwright` (import: `from playwright.sync_api import sync_playwright`) — usado
- `pymongo` (import: `from pymongo.errors import ServerSelectionTimeoutError`) — usado
- `groq` (import: `from groq import Groq`) — usado
- `mongoengine` (import: `from mongoengine import ...`) — usado, mas ausente em `requirements.txt`

Análise comparativa com o `requirements.txt` atual

- Mantém (recomendado manter):
  - `python-dotenv`
  - `playwright`
  - `pymongo`
  - `groq`

- Adicionar (necessário no `requirements.txt`):
  - `mongoengine`  # utilizado em `src/core/database.py` e `src/models/job_model.py`

- Remover (parecem não ser usados pelo código escaneado):
  - Pacotes do ecossistema spaCy e NLP listados que não são usados: `spacy`, `thinc`, `blis`, `murmurhash`, `preshed`, `srsly`, `spacy-legacy`, `spacy-loggers`, `pt_core_news_sm` (modelo), `wasabi`, `catalogue`, `confection`, `mdurl`, `markdown-it-py`, `MarkupSafe` (provavelmente transitiva)
  - Pacotes relacionados a ferramentas/linters/auxiliares que não aparecem no código: `ruff`, `taskipy`, `lazy-model`, `packaging`, `typing-inspection`, `typing_extensions`, `annotated-doc`, `annotated-types`
  - Outros não referenciados no código: `httpx`, `httpcore`, `anyio`, `requests`, `rich`, `Pygments`, `psutil`, `motor`, `beanie`, `smart_open`

Observações e recomendações
-------------------------
- Há pacotes listados que parecem ser dependências de outro projeto (por exemplo, muitos pacotes do ecossistema spaCy) — mantenha-os apenas se você pretende usar funcionalidades de NLP; caso contrário, remover do `requirements.txt` reduzirá o tamanho do ambiente.
- Adicione `mongoengine` ao `requirements.txt`. Exemplo:

```text
mongoengine>=1.0.0
```

- Se for usar `playwright`, lembre-se de executar `python -m playwright install` após instalar as dependências.
- Se preferir, gere um novo `requirements.txt` reprojetado com somente as dependências necessárias para execução atual:

Manter apenas o essencial (exemplo mínimo sugerido):

```text
python-dotenv
playwright
pymongo
groq
mongoengine
```

Próximos passos sugeridos
------------------------
- Confirmar se pretende manter módulos de NLP; se não, atualizar `requirements.txt` removendo pacotes supérfluos.
- Adicionar `mongoengine` ao `requirements.txt` e rodar `pip install -r requirements.txt`.
- Executar testes locais com `MONGO_URI` configurada.

Arquivo criado
-------------
Criei este arquivo de documentação e auditoria: [README.md](README.md)

Se desejar, atualizo o `requirements.txt` automaticamente com as mudanças recomendadas.

| Sigla | Significado em Inglês | Significado em Português |
| --- | --- | --- |
| RPM | Requests per minute | Solicitações por minuto |
| RPD | Requests per day | Solicitações por dia |
| TPM | Tokens per minute | Tokens por minuto |
| TPD | Tokens per day | Tokens por dia |
| ASH | Audio seconds per hour | Segundos de áudio por hora |
| ASD | Audio seconds per day | Segundos de áudio por dia |
| ITPM | Input tokens per minute | Tokens de entrada por minuto |
| OTPM | Output tokens per minute | Tokens de saída por minuto |

| Model | RPM | RPD | TPM | TPD | ASH | ASD |
| --- | --- | --- | --- | --- | --- | --- |
| allam-2-7b | 30 | 7K | 6K | 500K | - | - |
| canopylabs/orpheus-arabic-saudi | 10 | 100 | 1.2K | 3.6K | - | - |
| canopylabs/orpheus-v1-english | 10 | 100 | 1.2K | 3.6K | - | - |
| groq/compound | 30 | 250 | 70K | - | - | - |
| groq/compound-mini | 30 | 250 | 70K | - | - | - |
| llama-3.1-8b-instant | 30 | 14.4K | 6K | 500K | - | - |
| llama-3.3-70b-versatile | 30 | 1K | 12K | 100K | - | - |
| meta-llama/llama-4-scout-17b-16e-instruct | 30 | 1K | 30K | 500K | - | - |
| meta-llama/llama-prompt-guard-2-22m | 30 | 14.4K | 15K | 500K | - | - |
| meta-llama/llama-prompt-guard-2-86m | 30 | 14.4K | 15K | 500K | - | - |
| openai/gpt-oss-120b | 30 | 1K | 8K | 200K | - | - |
| openai/gpt-oss-20b | 30 | 1K | 8K | 200K | - | - |
| openai/gpt-oss-safeguard-20b | 30 | 1K | 8K | 200K | - | - |
| qwen/qwen3-32b | 60 | 1K | 6K | 500K | - | - |
| whisper-large-v3 | 20 | 2K | - | - | 7.2K | 28.8K |
| whisper-large-v3-turbo | 20 | 2K | - | - | 7.2K | 28.8K |
