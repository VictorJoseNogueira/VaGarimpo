# Documento de Design de Software (SDD) - Refatoração do Scraper 99Freelas

---

## 1. Objetivo

Refatorar a aplicação existente para tornar o scraper do 99Freelas mais robusto, configurável e compatível com execução local e em container Docker.

O sistema deve continuar funcionando via scripts Python no ambiente local (`venv`) e também permitir fácil execução em contêineres com persistência de dados.

## 2. Escopo atual

### 2.1. Componentes existentes

- `app/services/scrapper.py`
  - coleta links e detalhes do site 99Freelas;
  - grava dados em `app/data/projects.json`.
- `app/get_job.py`
  - lê `app/data/projects.json`;
  - chama `app/services.agente.run_agent`;
  - extrai JSON com `app/services/get_json.extract_valid_json`;
  - salva novamente em `app/data/projects.json`.
- `app/services/agente.py`
  - usa `groq.Groq` com `API_KEY` carregada por `dotenv`;
  - cria prompt para avaliação de vagas e retorno estrito em JSON.
- `app/services/get_json.py`
  - extrai e valida JSON em texto livre retornado pelo agente.
- `app/data/projects.json`
  - arquivo de entrada e saída principal.

### 2.2. Comportamento atual

- fluxo baseado em scripts CLI;
- não há API HTTP implementada;
- o caminho do JSON é codificado no código;
- o scraper opera em modo visível (`headless=False`);
- o processamento salva no mesmo arquivo de origem;
- logs são apenas `print()` no console.

## 3. Problemas identificados

- `headless=False` impede execução em Docker sem GUI.
- falta de logging estruturado dificulta diagnóstico.
- caminhos de arquivo rígidos reduzem flexibilidade de configuração.
- `except Exception` genérico oculta erros reais.
- `app/services/agente.py` não valida `API_KEY` antes de usar.
- `data/result2.json` é citado, mas não utilizado pelo código atual.
- não há suporte documentado para persistência de volume em container.

## 4. Requisitos detalhados

### 4.1. Requisitos funcionais

1. O scraper deve coletar projetos, descrição, habilidades, detalhes e nome do cliente.
2. O scraper deve salvar os dados no arquivo de destino configurável.
3. O pipeline de processamento deve carregar o JSON existente e acrescentar `llm_response` em cada projeto.
4. Projetos com `llm_response` já presente devem ser ignorados para evitar duplicação.
5. A extração de JSON deve funcionar mesmo com texto adicional ou blocos de markdown no retorno do agente.
6. O `README.md` deve conter instruções claras para rodar localmente.

### 4.2. Requisitos não funcionais

1. Logging
   - usar `logging` em vez de `print()`;
   - registrar em console e arquivo (`scraper.log` ou similar);
   - usar formato `%(asctime)s - %(levelname)s - %(message)s`;
   - aplicar níveis `INFO`, `WARNING` e `ERROR`.

2. Configuração via ambiente
   - `API_KEY` deve ser lida de variável de ambiente;
   - `JSON_PATH` deve ser configurável, com padrão `app/data/projects.json`;
   - `LOG_PATH` deve ser configurável opcionalmente;
   - permitir `HEADLESS`/`PLAYWRIGHT_HEADLESS` para controlar o navegador.

3. Execução do Playwright
   - iniciar `p.chromium.launch` com `headless=True` por padrão;
   - adicionar argumentos `--no-sandbox`, `--disable-dev-shm-usage` e `--disable-gpu`;
   - garantir compatibilidade com contêiner Linux.

4. Persistência e volumes
   - mapear `./app/data` para o container para preservar `projects.json`;
   - mapear logs para host quando executado em Docker.

5. Robustez
   - capturar erros específicos de Playwright e JSON;
   - continuar processamento mesmo após falha em um item.

## 5. Arquitetura proposta

### 5.1. Componentes a manter/refatorar

- `app/services/scrapper.py`
  - refatorar para aceitar `json_path` e `headless` configuráveis;
  - adicionar logging e tratamento de exceções mais específico.

- `app/get_job.py`
  - refatorar para ler caminho do arquivo de configuração e evitar sobrescrita prematura;
  - adicionar logs de progresso e de erros por item.

- `app/services/agente.py`
  - validar `API_KEY` antes da chamada;
  - manter prompt e estrutura de saída.

- `app/services/get_json.py`
  - garantir extração robusta de JSON mesmo com texto extra.

### 5.2. Fluxo de dados

1. `app/services/scrapper.py` coleta e grava `projects.json`.
2. `app/get_job.py` carrega esse JSON e processa cada projeto.
3. `app/services/agente.run_agent` gera o retorno do LLM.
4. `app/services/get_json.extract_valid_json` sanitiza a resposta.
5. O resultado é salvo de volta em `projects.json`.

## 6. Docker e orquestração

### 6.1. Dockerfile

- basear na imagem oficial `mcr.microsoft.com/playwright/python:<versão>`;
- copiar código e `requirements.txt`;
- instalar dependências e navegadores;
- definir `WORKDIR /app`;
- expor apenas comandos CLI e não nenhuma porta.

### 6.2. docker-compose

- serviço que monta `./app/data:/app/app/data` ou similar;
- montar `./scraper.log:/app/scraper.log` se necessário;
- injetar `API_KEY`, `JSON_PATH`, `LOG_PATH`, `HEADLESS`.

## 7. Entregáveis

1. `spec_driven_development.md` atualizado e alinhado ao código real.
2. `README.md` com instruções de instalação e execução local.
3. `requirements.txt` com dependências.
4. `Dockerfile` e `docker-compose.yml` para execução containerizada.

## 8. Observações

- o projeto atual não implementa endpoints HTTP, portanto não há rota REST a ser documentada.
- `app/services/tester.py` não tem implementação ativa e não entra no fluxo principal.
- o documento deve refletir que `app/data/projects.json` é o arquivo real usado pelo pipeline atual.
