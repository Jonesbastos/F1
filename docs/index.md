# 🏎️ F1 Data Platform

Bem-vindo à documentação oficial da **F1 Data Platform**, uma solução corporativa de Engenharia de Dados desenvolvida em Python para ingestão, transformação e carga analítica (ETL/ELT) de dados da **Fórmula 1**.

---

## 📌 Objetivos da Plataforma

- **Ingestão Resiliente**: Coleta de dados da API pública [OpenF1](https://openf1.org) respeitando rigorosamente o limite de vazão da comunidade (~3 req/s).
- **Padronização e Qualidade**: Validação estrita de contratos de esquema com **Pydantic v2**, higienização de limites físicos e normalização temporal em **UTC**.
- **Armazenamento Otimizado**: Carga analítica em formato colunar **Apache Parquet**, com compressão Snappy e particionamento no formato Hive.
- **Idempotência**: Garantia de que reexecuções de sessões ou GPs produzam o mesmo estado analítico sem duplicação (*partition overwrite*).

---

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.13+
- [Poetry](https://python-poetry.org)

### Instalação

```bash
# 1. Configurar o ambiente virtual local (.venv)
poetry config virtualenvs.in-project true --local

# 2. Instalar dependências completas
poetry install

# 3. Executar pipeline para a última sessão disponível
poetry run python -m f1.main --session-key latest
```

### Qualidade de Código e Automação de Tarefas

```bash
# Executar suíte de testes com cobertura mínima de 50%
poetry run task test

# Verificação estática e linting com Ruff
poetry run task lint

# Formatação determinística de código
poetry run task format

# Iniciar servidor local da documentação MkDocs (atalho: task docks)
poetry run task docks
```
