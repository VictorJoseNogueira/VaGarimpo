# Scrapper de Vagas — 99Freelas

## Visão Geral

Sistema de coleta e triagem automatizada de vagas publicadas no [99Freelas](https://www.99freelas.com.br). O projeto utiliza automação de navegador para extrair listagens e detalhes de projetos, persiste os dados em MongoDB e aplica filtros heurísticos (palavras banidas) e semânticos via modelos de linguagem (Groq). O ponto de entrada `main.py` orquestra dois pipelines independentes — scraping e processamento com LLM — que podem ser executados isoladamente ou em sequência.

## Tecnologias Utilizadas

| Tecnologia | Uso no projeto |
| --- | --- |
| **Python 3.11+** | Linguagem base e orquestração via CLI |
| **Playwright** | Automação headless do Chromium para navegação e extração de dados no site |
| **MongoEngine** | ODM para modelagem e persistência de documentos no MongoDB |
| **PyMongo** | Tratamento de erros de conexão (`ServerSelectionTimeoutError`) |
| **python-dotenv** | Carregamento de variáveis de ambiente a partir de `.env` |
| **Groq API** | Chamadas a LLMs para pontuação e filtragem de vagas (`AgentManager`) |

## Estrutura do Projeto

```
scrapper/
├── main.py                 # Ponto de entrada: coordena scraper e get-job
└── src/
    ├── core/
    │   ├── database.py     # Conexão e desconexão com MongoDB (MongoEngine)
    │   └── logger.py       # Logger centralizado (console colorido + arquivo)
    ├── scraper/
    │   ├── scrapper.py     # Classe scrapper99Freela: coleta e persistência
    │   └── get_json.py     # Utilitário para extrair JSON de textos mistos
    ├── services/
    │   ├── agente.py       # Cliente Groq com rotação de modelos e retries
    │   ├── get_job.py      # Pipeline de filtro LLM sobre vagas já salvas
    │   └── is_json.py      # Limpeza e parse de respostas JSON vindas do LLM
    ├── database/
    │   └── db_service.py   # CRUD: criar, ler, atualizar e excluir vagas
    ├── models/
    │   └── job_model.py    # Schema MongoEngine (JobData, LlmResponse, etc.)
    └── assets/prompts/     # Prompts de sistema para os agentes de filtro
```

**Fluxo de dados:** o scraper coleta links e metadados → `db_service.post_a_job` grava em `jobs_collection` → `get_job.JobFilterManager` lê vagas pendentes de score → `AgentManager` consulta a Groq → resultados são gravados em `llm_response.first_match`.

## Configuração e Instalação

### Pré-requisitos

- Python 3.11 ou superior
- Instância MongoDB acessível
- Conta e chave de API na [Groq](https://console.groq.com/) (necessária apenas para o modo `get-job`)

### Passo a passo

1. **Clone o repositório e acesse o diretório do projeto.**

2. **Crie e ative um ambiente virtual:**

```bash
python -m venv venv
source venv/bin/activate
```

3. **Instale as dependências do projeto** (via gerenciador de pacotes do seu ambiente) e **instale os navegadores do Playwright:**

```bash
pip install -r requirements.txt
python -m playwright install
```

4. **Configure as variáveis de ambiente** criando um arquivo `.env` na raiz do projeto:

```env
# Obrigatória — string de conexão MongoDB
MONGO_URI=mongodb://usuario:senha@host:27017/nome_do_banco

# Obrigatória para o pipeline get-job — chave da API Groq
GROQ_API_KEY=sua_chave_aqui

# Opcionais
JSON_PATH=src/data/projects.json
LOG_PATH=src/scraper.log
LOG_LEVEL=INFO
APP_MODE=all
```

> **Segurança:** nunca commite o arquivo `.env` nem exponha credenciais em logs ou documentação pública.

5. **Execute o projeto** a partir da raiz (garanta que `PYTHONPATH` inclua o diretório raiz — o `main.py` configura isso automaticamente ao delegar subprocessos):

```bash
python main.py
```

## Endpoints / Funcionalidades Principais

Este projeto **não expõe uma API REST**. A interface principal é a linha de comando via `main.py` e a execução direta dos módulos.

### Modos de execução (`main.py`)

| Modo | Comando | Descrição |
| --- | --- | --- |
| `scraper` | `python main.py --mode scraper` | Executa apenas o coletor Playwright (`src.scraper.scrapper`) |
| `get-job` | `python main.py --mode get-job` | Executa apenas o filtro LLM (`src.services.get_job`) |
| `all` | `python main.py --mode all` | Executa scraper e, em seguida, get-job (padrão; pode ser definido por `APP_MODE`) |

### Pipeline de scraping (`scrapper99Freela`)

| Etapa | Método | Comportamento |
| --- | --- | --- |
| Coleta de links | `scrap_page_get_links()` | Navega páginas paginadas do 99Freelas, ignora projetos já existentes no banco e filtra títulos com palavras banidas (PHP, WordPress, e-commerce, etc.) |
| Coleta de detalhes | `scrap_page_get_data()` | Para cada link válido, extrai descrição, habilidades, nome do contratante e tabela de detalhes (categoria, orçamento, propostas, etc.) |
| Persistência | `save_mongodb()` | Grava cada vaga via `post_a_job`, respeitando unicidade do campo `link` |

Execução isolada do scraper:

```bash
python -m src.scraper.scrapper
```

### Pipeline de filtro LLM (`JobFilterManager`)

| Etapa | Método | Comportamento |
| --- | --- | --- |
| Primeiro filtro | `run_first_filter()` | Para cada vaga sem score válido, envia título e descrição ao `AgentManager` com o prompt `first_filter.txt`; persiste raciocínio e score em `llm_response.first_match` |

Execução isolada do filtro:

```bash
python -m src.services.get_job
```

### Operações de banco (`db_service`)

| Função | Descrição |
| --- | --- |
| `post_a_job(data)` | Cria documento `JobData`; ignora duplicatas pelo campo `link` |
| `read_specific_job(url)` | Retorna vaga pelo link ou `None` |
| `read_all_jobs()` | Lista todas as vagas da coleção `jobs_collection` |
| `update_a_job(job_id, data)` | Atualização parcial via operadores MongoEngine (`set__...`) |
| `update_a_job_url(url, data)` | Atualização por URL |
| `delete_a_job(url)` | Remove vaga pelo link |

### Agente Groq (`AgentManager`)

- Modelos em rotação: `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `openai/gpt-oss-120b`, `openai/gpt-oss-20b`
- Até 4 tentativas com troca automática de modelo em caso de falha
- Temperatura `0.0`, máximo de `2048` tokens por resposta
