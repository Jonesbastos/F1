# 🏎️ OpenF1 API — Documentação Resumida

> **Base URL:** `https://api.openf1.org/v1`  
> **Autenticação:** Nenhuma necessária (acesso público e gratuito)  
> **Rate Limit:** ~3 requisições por segundo (Tier comunitário)  
> **Formatos de Saída:** JSON (padrão) | CSV (parâmetro `?csv=true`)  
> **Cobertura Histórica:** Temporada 2023 em diante  

---

## 📌 Parâmetros e Filtros Comuns

A API do OpenF1 permite filtrar quase todos os endpoints através de query parameters na URL.

| Parâmetro        | Tipo    | Descrição                                                              | Exemplo                     |
|------------------|---------|------------------------------------------------------------------------|-----------------------------|
| `session_key`    | integer | Identificador único da sessão (treino, quali, corrida). Aceita `latest`| `session_key=9158`          |
| `meeting_key`    | integer | Identificador único do fim de semana de GP. Aceita `latest`            | `meeting_key=1219`          |
| `driver_number`  | integer | Número oficial do carro do piloto                                      | `driver_number=1`           |
| `date>`, `date<` | string  | Filtro temporal comparativo no padrão ISO 8601 (UTC)                   | `date>=2024-03-02T15:00:00` |
| `csv`            | boolean | Retorna o resultado em CSV ao invés de JSON                            | `csv=true`                  |

> 💡 **Dica de Operadores:** Você pode utilizar operadores de comparação (`>`, `<`, `>=`, `<=`) como sufixo ou prefixo dos parâmetros para criar intervalos numéricos ou de data/hora (ex.: `speed>=300`, `interval<=1.0`).

---

## 🏁 Lista Detalhada de Endpoints

---

### 1. `/meetings` — Fins de Semana de Grande Prêmio
Retorna o calendário e metadados dos eventos (fins de semana de corrida ou testes oficiais).

* **Método:** `GET`
* **Exemplo de Requisição:**
```http
GET https://api.openf1.org/v1/meetings?year=2024&country_name=Brazil
```

| Campo                | Tipo    | Descrição                                             |
|----------------------|---------|-------------------------------------------------------|
| `meeting_key`        | integer | Identificador único do evento                         |
| `meeting_name`       | string  | Nome oficial do evento (ex: *São Paulo Grand Prix*)   |
| `meeting_code`       | string  | Código curto do evento (ex: *BRA*)                    |
| `year`               | integer | Ano da temporada                                      |
| `circuit_key`        | integer | Identificador único do circuito                       |
| `circuit_short_name` | string  | Nome popular da pista (ex: *Interlagos*)              |
| `country_name`       | string  | País onde ocorre o evento                             |
| `country_code`       | string  | Código ISO do país                                    |
| `date_start`         | string  | Data e hora de abertura do evento (ISO 8601 UTC)      |

---

### 2. `/sessions` — Sessões de Pista
Detalhes sobre cada sessão específica de um evento (Treinos Livres, Qualificação, Sprint e Corrida Principal).

* **Método:** `GET`
* **Exemplo de Requisição:**
```http
GET https://api.openf1.org/v1/sessions?meeting_key=latest
```

| Campo                | Tipo    | Descrição                                                   |
|----------------------|---------|-------------------------------------------------------------|
| `session_key`        | integer | ID único da sessão (chave primária para a maioria dos dados)|
| `session_name`       | string  | Nome da sessão (*Practice 1*, *Qualifying*, *Race*, etc.)  |
| `session_type`       | string  | Classificação do tipo (*Practice*, *Qualifying*, *Race*)   |
| `meeting_key`        | integer | ID do evento pai a que esta sessão pertence                |
| `date_start`         | string  | Timestamp de início da sessão                               |
| `date_end`           | string  | Timestamp de encerramento da sessão                         |
| `gmt_offset`         | string  | Diferença de fuso horário local em relação ao GMT          |

---

### 3. `/drivers` — Grid de Pilotos
Relação de pilotos inscritos em uma sessão com dados biográficos, fotos e equipe.

* **Método:** `GET`
* **Exemplo de Requisição:**
```http
GET https://api.openf1.org/v1/drivers?session_key=latest
```

| Campo            | Tipo    | Descrição                                              |
|------------------|---------|--------------------------------------------------------|
| `driver_number`  | integer | Número oficial do piloto no carro (ex: `1`, `44`, `16`)|
| `full_name`      | string  | Nome completo (ex: *Max Verstappen*)                   |
| `broadcast_name` | string  | Formato exibido nas transmissões de TV (*M VERSTAPPEN*)|
| `name_acronym`   | string  | Sigla de três letras oficial (*VER*, *HAM*, *LEC*)     |
| `team_name`      | string  | Nome oficial do construtor/equipe                      |
| `team_colour`    | string  | Código HEX da cor da equipe (ex: `3671C6`)             |
| `headshot_url`   | string  | Link direto para a foto oficial do piloto              |

---

### 4. `/laps` — Voltas e Tempos de Setor
Dados volta a volta com duração total, tempos dos três setores e micro-setores.

* **Método:** `GET`
* **Exemplo de Requisição:**
```http
GET https://api.openf1.org/v1/laps?session_key=9161&driver_number=63&lap_number=8
```

| Campo                | Tipo    | Descrição                                           |
|----------------------|---------|-----------------------------------------------------|
| `lap_number`         | integer | Número da volta na sessão                           |
| `driver_number`      | integer | Número do piloto                                    |
| `lap_duration`       | float   | Duração total da volta em segundos (ex: `87.421`)   |
| `duration_sector_1`  | float   | Tempo registrado no 1º setor                        |
| `duration_sector_2`  | float   | Tempo registrado no 2º setor                        |
| `duration_sector_3`  | float   | Tempo registrado no 3º setor                        |
| `segments_sector_1`  | array   | Micro-setores / status dos trechos no setor 1       |
| `is_pit_out_lap`     | boolean | Indica se a volta foi de saída do pit lane (`true`) |

---

### 5. `/car_data` — Telemetria de Alta Frequência
Dados de telemetria amostrados a ~3.7 Hz diretamente dos sensores do carro.

* **Método:** `GET`
* **Exemplo de Requisição:**
```http
GET https://api.openf1.org/v1/car_data?session_key=latest&driver_number=1&speed>=300
```

| Campo           | Tipo    | Descrição                                                   |
|-----------------|---------|-------------------------------------------------------------|
| `speed`         | integer | Velocidade instantânea do carro em km/h                     |
| `rpm`           | integer | Rotações por minuto do motor                                |
| `gear`          | integer | Marcha engatada (0 = Neutro, 1 a 8)                         |
| `throttle`      | integer | Acelerador pressionado (escala percentual de 0 a 100%)      |
| `brake`         | integer | Aplicação de freio (0 = inativo, 1 ou valor de pressão)     |
| `drs`           | integer | Status do DRS (0 a 14 indicando inativo, elegível ou ativo) |
| `date`          | string  | Timestamp exato da leitura (ISO 8601 UTC)                   |

---

### 6. `/location` — Posição Tridimensional na Pista
Coordenadas espaciais dos carros no circuito atualizadas em ~3.7 Hz.

* **Método:** `GET`
* **Exemplo de Requisição:**
```http
GET https://api.openf1.org/v1/location?session_key=latest&driver_number=44
```

| Campo           | Tipo    | Descrição                                                   |
|-----------------|---------|-------------------------------------------------------------|
| `x`             | float   | Posição no eixo cartesiano X do circuito                    |
| `y`             | float   | Posição no eixo cartesiano Y do circuito                    |
| `z`             | float   | Posição no eixo Z (elevação da pista)                       |
| `driver_number` | integer | Número do piloto                                            |
| `date`          | string  | Timestamp da amostra                                        |

---

### 7. `/positions` — Posição em Tempo Real
Atualizações de posicionamento dos pilotos na ordem da prova (~a cada 4 segundos).

* **Método:** `GET`
* **Exemplo de Requisição:**
```http
GET https://api.openf1.org/v1/positions?session_key=latest&driver_number=1
```

| Campo           | Tipo    | Descrição                                                   |
|-----------------|---------|-------------------------------------------------------------|
| `position`      | integer | Posição corrente na corrida (1 = 1º lugar, etc.)            |
| `driver_number` | integer | Número do piloto                                            |
| `session_key`   | integer | ID da sessão                                                |
| `date`          | string  | Timestamp da atualização                                    |

---

### 8. `/intervals` — Intervalos e Gaps entre Carros
Diferenças temporais de corrida entre pilotos e distância em relação ao líder.

* **Método:** `GET`
* **Exemplo de Requisição:**
```http
GET https://api.openf1.org/v1/intervals?session_key=9165&interval<=0.5
```

| Campo           | Tipo    | Descrição                                                          |
|-----------------|---------|--------------------------------------------------------------------|
| `gap_to_leader` | float   | Distância em segundos para o líder (ou `+1 LAP` se tomou volta)    |
| `interval`      | float   | Distância em segundos para o carro imediatamente à frente          |
| `driver_number` | integer | Número do piloto avaliado                                          |
| `date`          | string  | Timestamp da medição                                               |

---

### 9. `/pit` — Paradas nos Boxes (Pit Stops)
Controle de entradas, saídas e duração dos pit stops.

* **Método:** `GET`
* **Exemplo de Requisição:**
```http
GET https://api.openf1.org/v1/pit?session_key=latest&driver_number=16
```

| Campo           | Tipo    | Descrição                                                   |
|-----------------|---------|-------------------------------------------------------------|
| `lap_number`    | integer | Volta em que o pit stop ocorreu                             |
| `pit_duration`  | float   | Duração total no pit lane em segundos                       |
| `stop_duration` | float   | Tempo em que o carro esteve efetivamente imóvel no box      |
| `driver_number` | integer | Número do piloto                                            |
| `date`          | string  | Timestamp de registro da entrada                            |

---

### 10. `/stints` — Gerenciamento e Uso de Pneus
Ciclo de vida dos pneus e histórico de compostos usados em cada stint.

* **Método:** `GET`
* **Exemplo de Requisição:**
```http
GET https://api.openf1.org/v1/stints?session_key=latest&driver_number=1
```

| Campo               | Tipo    | Descrição                                                    |
|---------------------|---------|--------------------------------------------------------------|
| `stint_number`      | integer | Número sequencial do stint (começa em 1)                     |
| `compound`          | string  | Composto (*SOFT*, *MEDIUM*, *HARD*, *INTERMEDIATE*, *WET*)   |
| `tyre_age_at_start` | integer | Idade do pneu em voltas completadas antes do início do stint |
| `lap_start`         | integer | Volta da sessão onde o stint começou                         |
| `lap_end`           | integer | Volta da sessão onde o stint terminou                        |

---

### 11. `/weather` — Dados Meteorológicos da Pista
Leituras ambientais das estações meteorológicas ao redor do autódromo.

* **Método:** `GET`
* **Exemplo de Requisição:**
```http
GET https://api.openf1.org/v1/weather?session_key=latest
```

| Campo               | Tipo    | Descrição                                                   |
|---------------------|---------|-------------------------------------------------------------|
| `air_temperature`   | float   | Temperatura ambiente (°C)                                   |
| `track_temperature` | float   | Temperatura do asfalto (°C)                                 |
| `humidity`          | float   | Umidade relativa do ar (%)                                  |
| `pressure`          | float   | Pressão atmosférica (mbar)                                  |
| `wind_speed`        | float   | Velocidade do vento (m/s)                                   |
| `wind_direction`    | integer | Ângulo de direção do vento (0° a 360°)                      |
| `rainfall`          | integer | Indicador de precipitação (0 = pista seca, 1 = chuva)        |

---

### 12. `/race_control` — Mensagens da Direção de Prova
Incidentes, deliberações dos comissários, acionamento de Safety Car e bandeiras.

* **Método:** `GET`
* **Exemplo de Requisição:**
```http
GET https://api.openf1.org/v1/race_control?session_key=latest&flag=RED
```

| Campo           | Tipo    | Descrição                                                   |
|-----------------|---------|-------------------------------------------------------------|
| `category`      | string  | Categoria (*Flag*, *SafetyCar*, *Drs*, *Investigation*)     |
| `flag`          | string  | Status da bandeira (*GREEN*, *YELLOW*, *RED*, *CHEQUERED*)  |
| `scope`         | string  | Escopo da mensagem (*Track*, *Sector*, *Driver*)            |
| `message`       | string  | Texto descritivo integral emitido pela FIA                  |
| `lap`           | integer | Volta em que o aviso foi publicado                         |
| `driver_number` | integer | Número do piloto advertido ou sob investigação             |

---

### 13. `/team_radio` — Áudios do Rádio das Equipes
Arquivos e registros de mensagens de rádio entre equipe e piloto.

* **Método:** `GET`
* **Exemplo de Requisição:**
```http
GET https://api.openf1.org/v1/team_radio?session_key=latest&driver_number=1
```

| Campo           | Tipo    | Descrição                                                   |
|-----------------|---------|-------------------------------------------------------------|
| `recording_url` | string  | Link direto para reproduzir/baixar o áudio (.mp3)           |
| `driver_number` | integer | Número do carro do piloto                                   |
| `date`          | string  | Timestamp exato da gravação do áudio                        |

---

## 💻 Exemplos Práticos com cURL

```bash
# 1. Consultar todos os pilotos da última sessão realizada
curl -X GET "https://api.openf1.org/v1/drivers?session_key=latest"

# 2. Consultar voltas do piloto #1 (Verstappen) com tempos por setor
curl -X GET "https://api.openf1.org/v1/laps?session_key=latest&driver_number=1"

# 3. Telemetria acima de 310 km/h do piloto #44 (Hamilton)
curl -X GET "https://api.openf1.org/v1/car_data?session_key=latest&driver_number=44&speed>=310"

# 4. Mensagens de bandeira amarela ou vermelha na última sessão
curl -X GET "https://api.openf1.org/v1/race_control?session_key=latest&category=Flag"

# 5. Baixar dados climáticos da sessão em formato CSV
curl -X GET "https://api.openf1.org/v1/weather?session_key=latest&csv=true" -o clima.csv
```

---

> 📖 **Referência Oficial:** [OpenF1 Documentation](https://openf1.org/docs)
