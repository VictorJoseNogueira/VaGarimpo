# Scrapper

Este projeto Python coleta projetos e vagas de freelancing do site 99freelas.com.br, salva os dados em JSON e processa cada vaga usando um agente de linguagem (LLM) via `groq`.

## Visão geral

- `main.py` é o entrypoint CLI principal do projeto.
- `app/services/scrapper.py` coleta dados do 99freelas usando Playwright.
- `app/services/get_job.py` processa as vagas em `app/data/projects.json` chamando `app/services/agente.py`.
- `app/services/get_json.py` extrai o JSON válido das respostas de texto do agente.
- Os resultados e dados brutos são armazenados em `app/data/projects.json`.

## Estrutura do projeto

- `main.py` — ponto de entrada que executa os modos `scraper`, `get-job` ou `all`.
- `Dockerfile` — imagem Docker baseada em Playwright para execução do pipeline.
- `docker-compose.yml` — define o serviço `scrapper` com volumes e variáveis de ambiente.
- `requirements.txt` — lista de dependências Python.
- `app/logger.py` — configuração de logging compartilhada.
- `app/services/` — módulos principais de scraping, processamento, agente e parser.
- `app/data/projects.json` — arquivo de dados de entrada/saída.

## Requisitos

- Python 3.11+
- Virtualenv recomendado
- Dependências instaladas via `requirements.txt`
- `playwright` instalado e configurado (navegadores instalados)
- Variável de ambiente `API_KEY` definida para o cliente Groq

## Instalação local

1. Crie e ative um ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Instale os navegadores do Playwright:

```bash
python -m playwright install
```

4. Configure a variável de ambiente:

```bash
export API_KEY="seu_api_key_aqui"
```

> Opcional: use um arquivo `.env` para armazenar `API_KEY` e carregá-lo com `python-dotenv`.

## Execução

### Executar o pipeline completo

```bash
python3 -m main --mode all
```

### Executar apenas o scraper

```bash
python3 -m main --mode scraper
```

### Executar apenas o processamento de vagas

```bash
python3 -m main --mode get-job
```

### Usar Docker Compose

```bash
docker compose run --rm scrapper
```

## Comandos diretos (desenvolvimento)

```bash
python3 app/services/scrapper.py
python3 app/services/get_job.py
```

## Dados gerados

- `app/data/projects.json`
  - Contém os projetos coletados e, após processamento, as respostas do agente em cada item.

## Observações

- Este projeto não expõe endpoints HTTP; é orientado a execução por scripts CLI.
- O `Dockerfile` e `docker-compose.yml` estão configurados para execução em ambiente batch/contêiner.
- `main.py` define `PYTHONPATH` para incluir a raiz do projeto e garantir que `app` seja importável.
- O serviço `scrapper` do Docker Compose monta `./app/data`, `./app` e `./main.py` para permitir execução local com persistência dos dados.

## Notas de arquitetura

- A aplicação é estruturada como um monolito modular: o scraper, o processamento de vagas e o cliente de agente estão separados em módulos.
- A persistência é feita em arquivo JSON local; para produção, considere usar um armazenamento mais robusto como SQLite ou banco de dados.
- O fluxo atual funciona de forma sequencial: coleta -> processa -> salva.

## Dependências principais

- `playwright`
- `groq`
- `httpx`
- `python-dotenv`
- `pydantic`
