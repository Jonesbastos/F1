# ⚙️ Pipelines & Interface CLI

A plataforma disponibiliza orquestradores modulares e uma interface de linha de comando (`CLI`) rápida e padronizada.

---

## 🛠️ Utilização da CLI

O ponto de entrada CLI é o arquivo `src/f1/main.py`.

### Processar Sessão Única (Padrão: Mais recente)

```bash
poetry run python -m f1.main --session-key latest
```

### Processar Sessão com Telemetria do Piloto 1 (Verstappen)

```bash
poetry run python -m f1.main --session-key 9158 --include-telemetry --telemetry-driver 1
```

### Processar Temporada Histórica Completa

```bash
# Ingerir todos os GPs da temporada de 2024
poetry run python -m f1.main --year 2024

# Ingerir todos os GPs de 2024 no Brasil
poetry run python -m f1.main --year 2024 --country Brazil
```

---

## 🏎️ Dashboard Web Local

A plataforma inclui uma interface gráfica interativa servida localmente em `http://localhost:8080`:

```bash
# Iniciar o dashboard via task
poetry run task dashboard

# Ou diretamente pelo módulo Python
poetry run python -m f1.dashboard.app --port 8080
```

---

## 📋 Parâmetros da CLI

| Argumento | Tipo | Descrição | Padrão |
| :--- | :--- | :--- | :--- |
| `--session-key` | `str` | Identificador da sessão ou `latest` | `None` (assume `latest` no modo sessão) |
| `--year` | `int` | Temporada anual para ingestão em lote | `None` |
| `--country` | `str` | Filtro geográfico de país | `None` |
| `--include-telemetry` | flag | Habilita ingestão de dados veiculares (~3.7 Hz) | `False` |
| `--telemetry-driver` | `int` | Filtra telemetria apenas para um piloto | `None` |

---

## 📂 Estrutura no Data Lake Local

Os conjuntos de dados são armazenados colunarmente sob o diretório definido por `DATA_OUTPUT_DIR` (padrão: `data/processed/`):

```text
data/processed/
├── meetings/year=2024/
├── sessions/
├── drivers/session_key=9158/
├── laps/session_key=9158/
├── fastest_laps/session_key=9158/
├── pit_stops/session_key=9158/
├── pit_stop_metrics/session_key=9158/
├── stints/session_key=9158/
├── weather/session_key=9158/
├── race_control/session_key=9158/
└── telemetry/session_key=9158/driver_number=1/
```
