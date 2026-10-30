# 🏎️ OpenF1 API e Endpoints

A plataforma consome a API pública e aberta do **OpenF1** (`https://api.openf1.org/v1`), sem necessidade de chave de API, respeitando o limite de **~3 requisições por segundo**.

---

## 📊 Endpoints Integrados

| Recurso | Endpoint | Extrator Responsável | Particionamento Parquet |
| :--- | :--- | :--- | :--- |
| **Reuniões / GPs** | `/meetings` | `CalendarExtractor` | `year=YYYY` |
| **Sessões** | `/sessions` | `CalendarExtractor` | Arquivo único |
| **Pilotos** | `/drivers` | `RaceInfoExtractor` | `session_key=SS` |
| **Voltas** | `/laps` | `TimingExtractor` | `session_key=SS` |
| **Pit Stops** | `/pit` | `TimingExtractor` | `session_key=SS` |
| **Stints de Pneu** | `/stints` | `TimingExtractor` | `session_key=SS` |
| **Meteorologia** | `/weather` | `RaceInfoExtractor` | `session_key=SS` |
| **Direção de Prova**| `/race_control` | `RaceInfoExtractor` | `session_key=SS` |
| **Telemetria** | `/car_data` | `TelemetryExtractor` | `session_key=SS/driver_number=DD` |
| **Coordenadas 3D** | `/location` | `TelemetryExtractor` | `session_key=SS` |

---

## ⏱️ Política de Rate Limiting e Retries

- **Taxa Segura**: 3.0 req/s configurada via `OPENF1_RATE_LIMIT_RPS`.
- **Timeouts Explícitos**: Conexão (5.0s), Leitura (30.0s).
- **Backoff Exponencial**: Retentativas automáticas para status HTTP 429, 500, 502, 503 e 504.
