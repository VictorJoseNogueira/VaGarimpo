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
