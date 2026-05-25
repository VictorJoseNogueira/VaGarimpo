# VaGarimpo — Scraper de Vagas (99Freelas)

## Visão Geral

O **VaGarimpo** automatiza a busca de projetos freelancer no [99Freelas](https://www.99freelas.com.br), filtra oportunidades indesejadas por heurísticas locais e por modelos de linguagem (Groq), persiste tudo no MongoDB e notifica por e-mail as vagas mais compatíveis com o perfil do candidato. O fluxo é dividido em três pipelines independentes — coleta via navegador, triagem com LLM e envio SMTP — orquestrados pelo `main.py`, que pode executar cada etapa isoladamente ou em sequência.

## Tecnologias Utilizadas

| Tecnologia | Uso no projeto |
| --- | --- |
| **Python 3.11+** | Linguagem base, CLI e orquestração de subprocessos |
| **Playwright** | Automação headless do Chromium para listagem e detalhes de projetos |
| **MongoEngine** | ODM: modelagem de `JobData` e operações no MongoDB |
| **PyMongo** | Tratamento de falhas de conexão (`ServerSelectionTimeoutError`) |
| **python-dotenv** | Carregamento de variáveis de ambiente (`.env`) |
| **Groq SDK** | Cliente da API Groq para filtros semânticos (`AgentManager`) |
| **smtplib** | Envio de e-mails (vagas individuais e alerta de volume) |

## Estrutura do Projeto

```
scrapper/
├── main.py                      # Ponto de entrada: modos scraper, get-job, email e all
└── src/
    ├── core/
    │   ├── database.py          # Conexão e desconexão com MongoDB
    │   └── logger.py            # Logger central (console colorido + arquivo)
    ├── scraper/
    │   ├── scrapper.py          # Classe scrapper99Freela: coleta e persistência
    │   └── get_json.py          # Extração de JSON embutido em textos mistos
    ├── services/
    │   ├── agente.py            # Cliente Groq com rotação de modelos e retries
    │   ├── get_job.py           # JobFilterManager: filtros LLM (primeiro e final)
    │   ├── is_json.py           # Limpeza e parse de respostas JSON do LLM
    │   ├── job_selection.py     # Regras de elegibilidade e limite para e-mail
    │   ├── job_email_processor.py  # Orquestra seleção, envio e marcação no banco
    │   └── email_service.py     # Montagem de mensagens e envio SMTP
    ├── database/
    │   └── db_service.py        # CRUD e marcação de vagas enviadas por e-mail
    └── models/
        └── job_model.py         # Schema MongoEngine (JobData, LlmResponse, etc.)
```

**Fluxo de dados:** o scraper coleta links e metadados das páginas do 99Freelas → `post_a_job` grava documentos únicos por `link` → `JobFilterManager` aplica o primeiro filtro (score em `llm_response.first_match`) e, para scores acima de 75, o filtro final (status, match %, proposta, etc.) → `JobEmailProcessor` seleciona vagas com score ≥ 80 ainda não enviadas, dispara e-mails e marca `enviado_email=True` após sucesso.

## Configuração e Instalação

### Pré-requisitos

- Python 3.11 ou superior
- Instância MongoDB acessível
- Chave da API [Groq](https://console.groq.com/) (modo `get-job`)
- Credenciais SMTP ou `DRY_RUN_EMAIL=true` (modo `email`)

### Passo a passo

1. **Clone o repositório e entre no diretório do projeto.**

2. **Crie e ative um ambiente virtual:**

```bash
python -m venv venv
source venv/bin/activate
```

3. **Instale as dependências do projeto** (conforme o gerenciador usado no repositório) **e os navegadores do Playwright:**

```bash
pip install -r requirements.txt
python -m playwright install
```

4. **Crie um arquivo `.env` na raiz** com as variáveis usadas no código:

```env
# Obrigatória — conexão MongoDB
MONGO_URI=mongodb://usuario:senha@host:27017/nome_do_banco

# Obrigatória para get-job — API Groq
GROQ_API_KEY=sua_chave_aqui

# Opcionais — execução e logs
APP_MODE=all
JSON_PATH=src/data/projects.json
LOG_PATH=src/scraper.log
LOG_LEVEL=INFO

# Obrigatórias para envio real de e-mail (modo email)
SMTP_HOST=smtp.exemplo.com
SMTP_USER=usuario@exemplo.com
SMTP_PASSWORD=senha_smtp
EMAIL_TO=destinatario@exemplo.com

# Opcionais — e-mail
SMTP_PORT=587
EMAIL_FROM=usuario@exemplo.com
DRY_RUN_EMAIL=false
```

> **Segurança:** não commite o `.env` nem exponha credenciais em logs ou documentação pública.

5. **Execute a partir da raiz do projeto.** O `main.py` define `PYTHONPATH` automaticamente ao delegar cada módulo:

```bash
python main.py
python main.py --mode scraper
python main.py --mode get-job
python main.py --mode email
python main.py --mode all
```

O modo padrão é `all` (ou o valor de `APP_MODE` no ambiente).

## Endpoints / Funcionalidades Principais

Este projeto **não expõe API REST**. A interface é a linha de comando via `main.py` ou execução direta dos módulos Python.

### Orquestração (`main.py`)

| Modo | Comando | Comportamento |
| --- | --- | --- |
| `scraper` | `python main.py --mode scraper` | Apenas coleta Playwright (`src.scraper.scrapper`) |
| `get-job` | `python main.py --mode get-job` | Apenas filtros LLM (`src.services.get_job`) |
| `email` | `python main.py --mode email` | Seleção e envio de e-mails (`src.services.job_email_processor`) |
| `all` | `python main.py --mode all` | Executa **scraper → get-job → email** em sequência; interrompe se alguma etapa retornar código ≠ 0 |

Execução isolada de cada módulo:

```bash
python -m src.scraper.scrapper
python -m src.services.get_job
python -m src.services.job_email_processor
```

### Pipeline de scraping (`scrapper99Freela`)

| Etapa | Método | Comportamento |
| --- | --- | --- |
| Coleta de links | `scrap_page_get_links()` | Navega páginas paginadas (`max_pages`, padrão 1), ignora URLs já no banco e títulos com palavras banidas (PHP, WordPress, e-commerce, Ruby, .NET, no-code, etc.) |
| Coleta de detalhes | `scrap_page_get_data()` | Por link: descrição, habilidades, nome do contratante e tabela de detalhes (categoria, orçamento, propostas…) mapeada para chaves em inglês |
| Persistência | `save_mongodb()` | Grava cada vaga via `post_a_job`; duplicatas pelo campo `link` são ignoradas |

Ao rodar o módulo diretamente, o fluxo encadeado é: `scrap_page_get_links()` → `scrap_page_get_data()` → `save_mongodb()`, com `db_disconnect()` ao final.

### Pipeline de filtro LLM (`JobFilterManager`)

| Etapa | Método | Comportamento |
| --- | --- | --- |
| Primeiro filtro | `run_first_filter()` | Para vagas sem `llm_response.first_match.score`, envia título e descrição ao agente com prompt `first_filter.txt`; persiste raciocínio e score |
| Filtro final | `run_final_filter()` | Para vagas com score **> 75** e sem `llm_response.status`, usa `final_filter.txt`; persiste status, `match_percentage`, motivação, pontos fortes/fracos, pagamentos e proposta |

O módulo `get_job` executa ambos os filtros na importação. Respostas do LLM passam por `clean_and_parse_json` antes da persistência.

### Pipeline de e-mail (`JobEmailProcessor` + `job_selection`)

| Etapa | Componente | Comportamento |
| --- | --- | --- |
| Seleção | `select_jobs_for_email()` | Vagas com `enviado_email=False` e `first_match.score` ≥ 80; se houver mais de 10, eleva o score mínimo de 5 em 5 até 100; se ainda houver > 10 com score 100, `overflow=True` |
| Overflow | `send_overflow_warning_email()` | Envia apenas alerta de volume excessivo, sem e-mails por vaga |
| Envio | `send_job_email()` | Um e-mail por vaga (título, link, score, status, match %, proposta quando existir) |
| Persistência | `mark_jobs_email_sent()` | Marca `enviado_email=True` apenas nas vagas cujo envio foi bem-sucedido |

Com `DRY_RUN_EMAIL=true` (ou `1` / `yes`), nenhum e-mail é enviado; assunto e corpo são registrados no log.

### Operações de banco (`db_service`)

| Função | Descrição |
| --- | --- |
| `post_a_job(data)` | Cria `JobData`; ignora duplicata de `link` |
| `read_specific_job(url)` | Retorna vaga pelo link ou `None` |
| `read_all_jobs()` | Lista todas as vagas em `jobs_collection` |
| `update_a_job(job_id, data)` | Atualização parcial (`set__...`) por ID |
| `update_a_job_url(url, data)` | Atualização por URL |
| `delete_a_job(url)` | Remove vaga pelo link |
| `mark_jobs_email_sent(job_ids)` | Define `enviado_email=True` em lote |

### Agente Groq (`AgentManager`)

- Modelos em rotação: `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `openai/gpt-oss-120b`, `openai/gpt-oss-20b`
- Até 4 tentativas com troca automática de modelo em falha
- Temperatura `0.0`, máximo de `2048` tokens por resposta
- Requer `GROQ_API_KEY` definida no ambiente
