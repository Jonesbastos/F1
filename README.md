# 🏎️ F1 Data Platform

[![CI](https://github.com/Jonesbastos/F1/actions/workflows/ci.yml/badge.svg)](https://github.com/Jonesbastos/F1/actions/workflows/ci.yml)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)

Plataforma de Engenharia de Dados em Python para ingestão, processamento, transformação analítica e modelagem colunar em Parquet de dados da Fórmula 1 utilizando a API pública do **OpenF1**.

---

## 🏗️ Arquitetura

O projeto adota o padrão modular canônico em `src/f1`:

- **`config/`**: Configurações da aplicação validadas via `pydantic-settings`.
- **`models/`**: Contratos de dados e schemas Pydantic v2 (Meetings, Sessions, Drivers, Laps, Telemetry, Pit, Stints, Weather, Race Control).
- **`extractors/`**: Extratores HTTP com política de retry e limitador de taxa (~3 req/s).
- **`transformers/`**: Funções puras de higienização, limites físicos, datas UTC e métricas analíticas.
- **`loaders/`**: Persistência colunar em formato Apache Parquet particionado no padrão Hive.
- **`pipelines/`**: Orquestração por sessão (`SessionPipeline`) e histórica (`HistoricalPipeline`).
- **`utils/`**: Rate limiter thread-safe, logging estruturado e hierarquia de exceções.

---

## ⚡ Instalação e Execução

### 1. Clonar e Instalar com Poetry

```bash
poetry config virtualenvs.in-project true --local
poetry install
```

### 2. Executar Pipelines via CLI

```bash
# Ingerir a última sessão realizada da F1
poetry run python -m f1.main --session-key latest

# Ingerir sessão específica com telemetria veicular
poetry run python -m f1.main --session-key 9158 --include-telemetry --telemetry-driver 1

# Ingerir temporada completa em lote
poetry run python -m f1.main --year 2024 --country Brazil
```

---

## 🧪 Qualidade de Software e Governança

Todas as ferramentas seguem o guia canônico de engenharia de dados do repositório e podem ser executadas através dos atalhos com `taskipy`:

```bash
# Iniciar o Dashboard Web Interativo (http://localhost:8080)
poetry run task dashboard

# Executar suíte de testes com cobertura mínima (>= 50%)
poetry run task test

# Executar linting e checagem de código com Ruff
poetry run task lint

# Formatar código padronizado com Ruff
poetry run task format

# Iniciar servidor local da documentação MkDocs Material (ou `poetry run task docks`)
poetry run task docks

# Compilar documentação estática em modo estrito
poetry run task docks:build

# Executar todos os hooks do pre-commit manualmente
poetry run task precommit
```

---

## 📖 Documentação Completa

A documentação detalhada com arquitetura, referência de endpoints e pipelines pode ser visualizada via MkDocs Material:

```bash
poetry run task docks
```
Acesse `http://127.0.0.1:8000` no seu navegador.
