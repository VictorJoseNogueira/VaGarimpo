# Roadmap de Testes Unitários - Projeto Scrapper

## 📌 Visão Geral

Este documento define o plano estratégico para implementação de testes unitários no projeto Scrapper, priorizando os módulos críticos e estabelecendo metas de cobertura progressivas.

### ✅ Progresso Atual

**Fase de Preparação Concluída:**
- ✅ Identificação de magic numbers e conversão para constantes
- ✅ Refatoração de `scrap_page_get_data()` para reduzir complexidade (PLR0912, PLR0915, PLR0914)
- ✅ Extração de métodos privados para tarefas específicas
- ✅ Correção de erros de linting (Ruff): PLW1514, PLW1510, E501, PLR6201, PLR6301
- ✅ Formatação de código com Black
- ✅ Código agora está pronto para testes

**Próxima Etapa:** Implementação de testes unitários (Fase 1)

---

## 🎯 Módulos Prioritários a Testar

### Fase 1: Crítica (Iniciar por aqui)

#### 1. **app/services/get_json.py** ⭐⭐⭐
- **Responsabilidade:** Extração de JSON válido do texto retornado pela LLM
- **Função Principal:** `extract_valid_json(text)`
- **Por que é crítica:** Falhas aqui quebram todo o pipeline de processamento
- **Testes necessários:**
  - JSON puro sem extras (deve passar)
  - JSON com texto antes/depois (deve extrair apenas JSON)
  - JSON com markdown ```json ... ``` (deve remover)
  - Texto sem JSON (deve retornar None)
  - JSON malformado (deve capturar JSONDecodeError)
  - Strings vazias/None (deve retornar None)
  - JSON com caracteres especiais UTF-8
- **Cobertura Target:** 90%+
- **Tempo Estimado:** 1h
- **Testes Estimados:** 7-8

#### 2. **app/services/agente.py** ⭐⭐⭐
- **Responsabilidade:** Integração com API Groq para processamento de vagas
- **Função Principal:** `run_agent(user_input)`
- **Por que é crítica:** Integração com serviço externo (caro em API calls)
- **Testes necessários:**
  - API_KEY definida/não definida (deve lançar RuntimeError)
  - Input como string vs dict (ambas devem funcionar)
  - Validação de parametrização correta (model, temperature, max_tokens)
  - Tratamento de exceções da API (timeout, auth error)
  - Conversão dict → JSON string
  - Retorno de string válida
  - Logging de chamadas e erros
- **Cobertura Target:** 85%+
- **Tempo Estimado:** 1.5h
- **Testes Estimados:** 6-7
- **Mocks Necessários:** `Groq`, variáveis de ambiente

#### 3. **app/services/scrapper.py** ⭐⭐⭐
- **Responsabilidade:** Scraping e filtragem de projetos do 99freelas
- **Métodos Principais:**
  - `__init__()` - Inicialização
  - `have_a_banned_word(word)` - Filtragem de palavras-chave bloqueadas ✅ Puro, fácil de testar
  - `scrap_page_get_links()` - Extração de links (requer mock Playwright)
  - `_extract_description()` - ✅ Refatorado (método privado com responsabilidade única)
  - `_extract_skills()` - ✅ Refatorado (staticmethod)
  - `_extract_details()` - ✅ Refatorado (staticmethod)
  - `_extract_user_info()` - ✅ Refatorado (staticmethod)
  - `_process_project_data()` - ✅ Refatorado (orquestrador limpo)
  - `scrap_page_get_data()` - ✅ Refatorado (agora é um orquestrador simples)
  - `save_json()` - Persistência de dados
- **Por que é crítica:** Lógica de negócio de filtragem; Playwright é pesado mockar
- **Melhorias Realizadas:**
  - Redução de complexidade: método original ~150 linhas → 5 linhas + 4 métodos privados
  - Cada método privado tem responsabilidade única
  - Métodos estáticos quando não usam estado da classe
  - Logs consistentes e tratamento de exceções
- **Testes necessários:**
  - `have_a_banned_word()`: palavras bloqueadas (php, laravel, ruby, etc.)
  - `have_a_banned_word()`: palavras permitidas (python, javascript, etc.)
  - `have_a_banned_word()`: case-insensitive detection
  - `have_a_banned_word()`: múltiplas palavras na mesma string
  - `_extract_description()`: dados disponíveis vs não disponíveis
  - `_extract_skills()`: lista vazia vs com dados
  - `_extract_details()`: tabela presente vs ausente
  - `_extract_user_info()`: usuário disponível vs não disponível
  - `_process_project_data()`: fluxo completo de processamento
  - Inicialização com parâmetros variados (link, json_path, max_pages)
  - URL normalization (rstrip '/')
  - Validação de lista de palavras bloqueadas
  - Mock de Playwright para `scrap_page_get_links()` (opcional: integração)
- **Cobertura Target:** 85%+ (melhorado devido à refatoração)
- **Tempo Estimado:** 1.5h → 1h (métodos menores são mais rápidos de testar)
- **Testes Estimados:** 8-10 → 12-14 (mais métodos, mais granular)
- **Mocks Necessários:** `sync_playwright`, `os`, `random`
- **Status:** ✅ Código pronto para testes

---

### Fase 2: Importante

#### 4. **app/logger.py** ⭐⭐
- **Responsabilidade:** Configuração centralizada de logging
- **Por que é importante:** Logging é essencial para debugging em produção
- **Testes necessários:**
  - Logger é inicializado corretamente
  - Handlers (stdout e file) são configurados
  - Níveis de log funcionam (DEBUG, INFO, WARNING, ERROR)
  - Persistência de logs em arquivo
  - Fallback se arquivo de log não for criável
  - Formato de mensagem está correto
- **Cobertura Target:** 75%+
- **Tempo Estimado:** 45min
- **Testes Estimados:** 5-6
- **Mocks Necessários:** `os.getenv`, `logging.FileHandler`

#### 5. **main.py** ⭐⭐
- **Responsabilidade:** CLI entry point e orquestração de módulos
- **Funções Principais:**
  - `parse_args()` - Parsing de argumentos CLI
  - `run_module(module_name)` - Execução de módulos via subprocess
  - `main()` - Orquestração principal
- **Por que é importante:** Ponto de entrada; garante fluxo correto
- **Testes necessários:**
  - Parsing: --mode scraper, get-job, all
  - Fallback para variável APP_MODE
  - Retorno de códigos de erro corretos
  - Orquestração: scraper → get-job → all
  - Tratamento de falhas em submódulos
  - PYTHONPATH é definido corretamente
- **Cobertura Target:** 80%+
- **Tempo Estimado:** 1h
- **Testes Estimados:** 5-6
- **Mocks Necessários:** `subprocess.run`, `sys.argv`

---

### Fase 3: Desejável (Mais complexo)

#### 6. **app/services/get_job.py** ⭐
- **Responsabilidade:** Orquestração de processamento de vagas
- **Desafio:** Múltiplas dependências externas (arquivo JSON, sleep, API)
- **Por que é desejável:** Lógica complexa com side effects
- **Testes necessários:**
  - Leitura de arquivo JSON
  - Escrita de arquivo JSON
  - Pular itens já processados (com llm_response)
  - Rate-limiting (pausa a cada 28 requests)
  - Limite de páginas (máximo 20 por execução)
  - Tratamento de exceções do agente
  - Persistência correta de dados
  - Logging de progresso
- **Cobertura Target:** 70%+
- **Tempo Estimado:** 2h
- **Testes Estimados:** 8-10
- **Mocks Necessários:** `json`, `time.sleep`, `run_agent`, `extract_valid_json`

---

## 📦 Dependências de Teste

Adicionar ao projeto:

```
pytest==7.4.3              # Framework de testes
pytest-mock==3.12.0        # Mocks/patches integrados
pytest-cov==4.1.0          # Cobertura de código
freezegun==1.4.0           # Mock de datetime/time
responses==0.24.1          # Mock de HTTP (opcional)
pytest-asyncio==0.23.0     # Para testes async (opcional)
```

### Instalação:
```bash
pip install -r requirements-dev.txt
```

---

## 📁 Estrutura de Diretórios para Testes

```
scrapper/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Fixtures compartilhadas
│   ├── test_get_json.py            # 7-8 testes
│   ├── test_agente.py              # 6-7 testes
│   ├── test_scrapper.py            # 8-10 testes
│   ├── test_logger.py              # 5-6 testes
│   ├── test_main.py                # 5-6 testes
│   ├── test_get_job.py             # 8-10 testes
│   └── fixtures/
│       ├── sample_jobs.json        # Dados de teste
│       ├── mock_responses.json     # Respostas mock de LLM
│       └── mock_html_pages.py      # HTML mock para Playwright
├── requirements-dev.txt            # Dependências de desenvolvimento
└── pytest.ini                       # Configuração do pytest
```

---

## 📊 Roadmap de Implementação

| Fase | Módulo | # Testes | Cobertura | Tempo | Status |
|------|--------|----------|-----------|-------|--------|
| 1 | get_json.py | 7 | 90% | 1h | ⏳ Próximo |
| 1 | agente.py | 6 | 85% | 1.5h | ⏳ Próximo |
| 1 | scrapper.py | 14 | 85% | 1h | ⏳ Próximo (código refatorado) |
| 2 | logger.py | 5 | 75% | 45min | ⏳ Não iniciado |
| 2 | main.py | 6 | 80% | 1h | ⏳ Não iniciado |
| 3 | get_job.py | 8 | 70% | 2h | ⏳ Não iniciado |
| | **TOTAL** | **46** | **81%** | **7.5h** | |

---

## 🔄 Metas Progressivas (Atualizado)

### Fase de Preparação (Concluída) ✅
**Tempo gasto:** ~2h
- Refatoração de código para padrões testáveis
- Remoção de magic numbers
- Redução de complexidade ciclomática
- Correção de todos os erros Ruff

### Sprint 1 - Fase 1 (Em andamento)
**Tempo estimado:** 3h
- Implementar testes para **get_json.py** + **agente.py**
- Cobertura esperada: 85%+
- Resultado: Pipeline de dados funcionando com confiança
- ✅ Código está pronto (sem dependências complexas)

### Sprint 2 - Fase 1-2
**Tempo estimado:** 4h
- Completar **scrapper.py** (agora mais fácil com métodos privados)
- Implementar **logger.py** e **main.py**
- Cobertura esperada: 82%+
- Resultado: Testes críticos e CLI validados

### Sprint 3 - Fase 2-3
**Tempo estimado:** 2h
- Implementar **get_job.py**
- Refinar cobertura geral
- Cobertura esperada: 75%+
- Resultado: Cobertura completa do projeto

---

## ✅ Checklist de Implementação

### Fase de Preparação (Concluída)
- [x] Identificar magic numbers no código
- [x] Converter magic numbers em constantes nomeadas
- [x] Refatorar método `scrap_page_get_data()` para reduzir complexidade
- [x] Extrair métodos privados com responsabilidade única
- [x] Converter métodos sem estado para staticmethod
- [x] Corrigir erros de linting (Ruff)
- [x] Formatar código com Black
- [x] Criar TESTING_ROADMAP.md detalhado

### Fase 1 - Testes Críticos
- [ ] Criar diretório `tests/`
- [ ] Criar `tests/__init__.py`
- [ ] Criar `tests/conftest.py` com fixtures base
- [ ] Implementar testes de **get_json.py** (7 testes)
- [ ] Implementar testes de **agente.py** (6 testes)
- [ ] Implementar testes de **scrapper.py** (14 testes)
- [ ] Atingir 85%+ cobertura na Fase 1

### Fase 2 - Testes Importantes
- [ ] Implementar testes de **logger.py** (5 testes)
- [ ] Implementar testes de **main.py** (6 testes)
- [ ] Atingir 80%+ cobertura geral

### Fase 3 - Testes Completos
- [ ] Implementar testes de **get_job.py** (8 testes)
- [ ] Atingir 75%+ cobertura total

### Infraestrutura
- [ ] Criar `requirements-dev.txt` com dependências de teste
- [ ] Criar `pytest.ini` com configuração
- [ ] Criar `tests/fixtures/` com dados de teste
- [ ] Configurar `pytest.ini`
- [ ] Adicionar comando `make test` ou script
- [ ] Configurar CI/CD (GitHub Actions)
- [ ] Gerar relatório de cobertura
- [ ] Atualizar README com badge de testes

---

## 🚀 Próximos Passos

1. **Preparação (15min)**
   ```bash
   # Criar requirements-dev.txt
   # Criar estrutura de diretórios tests/
   # Criar conftest.py
   ```

2. **Implementação Fase 1 (3h)**
   - Começar por `get_json.py` (mais simples, sem dependências externas)
   - Seguir com `agente.py` (mocks de API)
   - Completar com `scrapper.py` (mocks de Playwright)

3. **Validação**
   ```bash
   pytest tests/ --cov=app --cov-report=html
   ```

4. **CI/CD**
   - Adicionar workflow GitHub Actions para rodar testes em cada PR
   - Bloquear merges com cobertura < 75%

---

## 📚 Referências

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-mock](https://pytest-mock.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

---

## 🏗️ Estrutura de Código Atual (Melhorado)

### scrapper.py - Antes vs Depois

**Antes:**
- `scrap_page_get_data()`: ~150 linhas, múltiplas responsabilidades
- Complexidade ciclomática: PLR0912, PLR0915, PLR0914 (erros Ruff)
- Difícil de testar, muito aninhamento

**Depois:**
- `scrap_page_get_data()`: ~15 linhas (orquestrador simples)
- `_extract_description()`: método privado ~30 linhas
- `_extract_skills()`: staticmethod ~25 linhas
- `_extract_details()`: staticmethod ~30 linhas
- `_extract_user_info()`: staticmethod ~25 linhas
- `_process_project_data()`: método privado ~15 linhas
- **Resultado:** Código muito mais testável e mantível

### Constantes Extraídas

**scrapper.py:**
- `DEFAULT_MAX_PAGES = 1`
- `DEFAULT_INITIAL_MAX_PAGES = 5`
- `DEFAULT_PAGE_NUMBER = 1`
- `MILLISECONDS_IN_SECOND = 1000`
- `PLAYWRIGHT_WAIT_MIN_SECONDS = 2.5`
- `PLAYWRIGHT_WAIT_MAX_SECONDS = 5`
- `PLAYWRIGHT_WAIT_TIMEOUT_MS = 5000`
- `PLAYWRIGHT_LAUNCH_ARGS = [...]`
- `JSON_DUMP_INDENT = 4`

**get_job.py:**
- `MAX_ITEMS_PER_RUN = 20`
- `MAX_REQUESTS_BEFORE_RATE_LIMIT = 28`
- `RATE_LIMIT_WINDOW_SECONDS = 62`
- `JSON_DUMP_INDENT = 4`

**agente.py:**
- `AGENT_TEMPERATURE = 0.5`
- `AGENT_MAX_TOKENS = 2048`
- `JSON_DUMP_INDENT = 4`

**get_json.py:**
- `JSON_PREVIEW_LENGTH = 200`

### Erros Ruff Corrigidos

- ✅ **PLW1514** (get_job.py): Adicionado `encoding="utf-8"` na abertura de arquivo
- ✅ **PLW1510** (main.py): Adicionado `check=False` em `subprocess.run()`
- ✅ **E501** (main.py): Quebrada string longa em múltiplas linhas
- ✅ **PLR6201** (main.py): Tuplas convertidas para sets em verificações
- ✅ **PLR0912, PLR0915, PLR0914** (scrapper.py): Redução de complexidade
- ✅ **PLR6301** (scrapper.py): Métodos sem estado convertidos para staticmethod

---

**Última atualização:** 18 de maio de 2026
**Responsável:** Roadmap de Testes
**Status:** 🟡 Fase de Preparação Completa → Pronto para Testes


