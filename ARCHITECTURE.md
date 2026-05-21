# ARCHITECTURE.md

> Descrição da arquitetura e organização atual do projeto "Scrapper".

## Sumário

- Visão Geral
- Árvore de diretórios
- Responsabilidades por pasta/arquivo
- Fluxo principal da aplicação
- Ponto de entrada
- Módulos centrais e descrições
- Dependências e integrações externas
- Contêiner e Docker Compose
- Observações arquiteturais
- Melhorias sugeridas

---

## Visão Geral

O projeto é uma aplicação Python orientada a scripts que coleta dados do 99freelas.com.br, salva esses dados em JSON e processa cada vaga com um agente de linguagem (LLM) usando o cliente `groq`.

A execução é feita por scripts CLI; não há servidor HTTP nem endpoints REST. A arquitetura é monolítica modular, com responsabilidades separadas em módulos `src/services`.

## Árvore de diretórios (visão atual)

```
scrapper/                      # raiz do repositório
├── .dockerignore
├── .env
├── .gitignore
├── ARCHITECTURE.md
├── Dockerfile
├── README.md
├── docker-compose.yml
├── main.py
├── requirements.txt
├── spec_driven_development.md
├── src/
│   ├── core/
│   │   └── logger.py
│   ├── data/
│   │   └── projects.json
│   └── services/
│       ├── agente.py
│       ├── get_job.py
│       ├── get_json.py
│       ├── scrapper.py
│       └── tester.py
└── venv/ (ambiente virtual local)
```

## Responsabilidade de cada pasta

- `src/`
  - Agrupa a lógica principal da aplicação.
- `src/services/`
  - Contém os módulos de scraping, processamento de vagas, agente LLM e extrator de JSON.
- `src/data/`
  - Armazena o arquivo `projects.json` usado como entrada e saída do pipeline.
- `venv/`
  - Ambiente virtual local; não deve ser versionado.

## Responsabilidade dos principais arquivos

- `main.py`
  - Ponto de entrada CLI do projeto. Executa os modos `scraper`, `get-job` ou `all`.
  - Configura `PYTHONPATH` para garantir que `src` seja importável.

- `Dockerfile`
  - Define a imagem Docker para executar o pipeline.
  - Usa a imagem oficial Playwright para Python e instala dependências via `requirements.txt`.
  - Executa `python main.py --mode all` por padrão.

`docker-compose.yml`
  - Define o serviço `scrapper` com volume mounts para o workspace e `main.py`.
  - Carrega variáveis de ambiente de `.env`.

`src/core/logger.py`
  - Configura o logging compartilhado para a aplicação.

`src/scrapper/scrapper.py`
  - Realiza scraping de projetos do 99freelas.
  - Extrai atributos de cada projeto e grava o JSON em `src/data/projects.json`.

`src/services/get_job.py`
  - Processa cada item em `projects.json` que ainda não possui `llm_response`.
  - Envia dados ao agente em `src/services/agente.py` e persiste a resposta.

`src/services/agente.py`
  - Faz a chamada ao cliente `groq.Groq`.
  - Monta prompt e retorna a resposta de texto.

`src/services/get_json.py`
  - Extrai o JSON válido do texto retornado pelo agente.

`src/services/tester.py`
  - Arquivo presente para testes/experimentos, sem fluxo principal ativo.

- `requirements.txt`
  - Lista as dependências Python necessárias para execução.

## Fluxo principal da aplicação

1. Executar o scraper para coletar projetos e gerar/atualizar `src/data/projects.json`.
2. Executar o processamento de vagas para enviar cada projeto ao agente LLM.
3. O resultado é salvo em `src/data/projects.json`, com o campo `llm_response` preenchido para cada item processado.

## Ponto de entrada do sistema

- `main.py` é o entrypoint recomendado.
- Os modos disponíveis são:
  - `scraper`
  - `get-job`
  - `all`
O `main.py` chama `src.scrapper.scrapper` e `src.services.get_job` via `python -m`.

## Dependências importantes e integrações externas

- `playwright` — navegador automatizado para scraping.
- `groq` — cliente LLM para o agente.
- `httpx` — cliente HTTP usado no scraping e chamadas.
- `python-dotenv` — carregamento de variáveis de ambiente.
- `pydantic` — validação/serialização de dados.

Integrações externas:
- 99freelas.com.br — origem dos dados de projetos.
- API Groq — utilizada pelo agente LLM.

## Contêiner e Docker Compose

- O `Dockerfile` está na raiz do projeto.
- A imagem base é a imagem oficial Playwright para Python (`mcr.microsoft.com/playwright/python:v1.43.0-jammy`).
- O serviço `scrapper` no `docker-compose.yml` monta volumes para permitir persistência de dados e acesso ao código local.
- O container não expõe portas, pois o projeto é batch/script-driven.

### Observações sobre Docker

- `docker-compose.yml` monta o workspace inteiro em `/app` e expõe `main.py` no container.
- O Dockerfile cria `/app/src/data` para persistência do `projects.json` quando necessário.
- A execução padrão no container é `python main.py --mode all`.

## Observações arquiteturais

- A arquitetura é monolítica, com separação de responsabilidades em módulos.
- A persistência via JSON é simples, mas limita concorrência e histórico.
- O projeto não possui scheduler nativo; execuções agendadas podem ser feitas externamente com `cron` ou `docker compose run`.
- A ausência de API REST torna o projeto adequado para pipelines de dados em batch.

## Melhorias sugeridas

1. Consolidar o contexto Docker e garantir que `main.py` esteja disponível no container.
2. Considerar armazenamento mais robusto que JSON local (`SQLite`, banco de dados ou armazém em nuvem).
3. Adicionar testes automatizados para os serviços de scraping, agente e parser.
4. Ajustar Playwright para rodar em modo headless em ambientes CI/containers.
5. Documentar claramente as variáveis de ambiente necessárias e proteger `.env`.
2. Converter `src/data` para um armazenamento com transações (SQLite, ou um bucket remoto) para maior confiabilidade.
3. Extrair a lógica de orquestração em `get_job.py` para um módulo testável e criar pequenos testes automatizados.
4. Opcional: criar uma camada de API (FastAPI) para permitir execução controlada via HTTP e exposição de status (health, metrics).
5. Adicionar um `Makefile` ou scripts `docker-compose` para facilitar builds e execuções locais/CI.


## Como manter este documento

- Atualize esta `ARCHITECTURE.md` sempre que a estrutura ou os pontos de entrada mudarem.
- Inclua uma seção `Changelog` com data e resumo de alterações arquiteturais importantes.

---

Generated by static analysis of repository files on 2026-05-18.
