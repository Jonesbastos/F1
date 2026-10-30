---
name: data-engineering-python
description: Guia definitivo de engenharia de dados em Python com Poetry, Ruff, Pytest, MkDocs Material e padrões de arquitetura corporativa.
---

# SKILL: Engenharia de Dados com Python

Este documento é o guia canônico de arquitetura, desenvolvimento, boas práticas, segurança e qualidade de software para todos os projetos de Engenharia de Dados desenvolvidos em Python pelo time.

Ele serve como instrução imperativa para **agentes de Inteligência Artificial** e como guia de referência técnica para **engenheiros de dados e desenvolvedores**.

---

## 1. Gerenciamento de Ambiente e Dependências — Poetry

O **Poetry** é a ferramenta oficial e obrigatória para gerenciamento de dependências, controle de empacotamento e isolamento de ambientes virtuais (`.venv`).

### 1.1 Regras Obrigatórias e Inegociáveis

1. **Uso exclusivo do Poetry**: É expressamente proibido o uso de `pip install`, `pip uninstall`, `pip freeze` ou `requirements.txt` para manipular dependências do projeto.
2. **Ambiente virtual local (`.venv`)**: O ambiente virtual deve residir obrigatoriamente na raiz do projeto (`projeto/.venv`).
3. **Controle de versão**: Os arquivos `pyproject.toml` e `poetry.lock` devem ser sempre comitados no Git. O diretório `.venv` **nunca** deve ser versionado.
4. **Isolamento de dependências de desenvolvimento**: Ferramentas de lint, teste e documentação (`ruff`, `pytest`, `pytest-cov`, `mkdocs`, etc.) devem ser adicionadas exclusivamente no grupo `dev`.

### 1.2 Configuração Inicial do Ambiente

Para garantir que a virtualenv seja criada dentro da pasta do projeto:

```bash
# Configura o Poetry para criar o diretório .venv na raiz do projeto
poetry config virtualenvs.in-project true --local
```

### 1.3 Comandos Operacionais

```bash
# 1. Instalar todas as dependências declaradas (reproduzindo o lock exato)
poetry install --no-root

# 2. Adicionar uma biblioteca de produção
poetry add pandas pydantic pydantic-settings requests

# 3. Adicionar uma biblioteca de desenvolvimento
poetry add --group dev ruff pytest pytest-cov mkdocs mkdocs-material mkdocstrings[python]

# 4. Remover uma dependência
poetry remove requests
poetry remove --group dev pytest-mock

# 5. Atualizar dependências respeitando o versionamento semântico
poetry update

# 6. Executar comandos no contexto do ambiente virtual
poetry run python -m src.projeto.main
poetry run pytest
poetry run ruff check .
```

---

## 2. Arquitetura Modular e Organização do Projeto

Todo projeto adota o padrão de layout em `src/`, garantindo separação entre o código-fonte instalável e scripts ou configurações de infraestrutura.

### 2.1 Estrutura de Diretórios Canônica

```text
projeto/
├── src/
│   └── projeto/
│       ├── __init__.py
│       ├── main.py                  # Ponto de entrada CLI / acionamento
│       ├── config/                  # Configurações e variáveis de ambiente
│       │   ├── __init__.py
│       │   └── settings.py
│       ├── models/                  # Schemas de dados (Pydantic, Dataclasses)
│       │   ├── __init__.py
│       │   └── records.py
│       ├── extractors/              # Conectores de entrada (APIs, S3, Bancos)
│       │   ├── __init__.py
│       │   └── api_extractor.py
│       ├── transformers/            # Regras de negócio puras e limpeza
│       │   ├── __init__.py
│       │   └── cleaner.py
│       ├── loaders/                 # Carga em destinos (Data Lake, DW, Parquet)
│       │   ├── __init__.py
│       │   └── storage_loader.py
│       ├── pipelines/               # Orquestração do fluxo ETL / ELT
│       │   ├── __init__.py
│       │   └── process_data.py
│       ├── services/                # Clientes e integrações auxiliares
│       │   └── __init__.py
│       └── utils/                   # Utilitários transversais (loggers, datas)
│           ├── __init__.py
│           └── logger.py
├── tests/
│   ├── conftest.py                  # Fixtures compartilhadas
│   ├── unit/                        # Testes unitários isolados
│   │   ├── test_cleaner.py
│   │   └── test_extractor.py
│   └── integration/                 # Testes de integração
│       └── test_pipeline_integration.py
├── docs/                            # Documentação MkDocs
│   ├── index.md
│   ├── architecture.md
│   └── contributing.md
├── .github/
│   └── workflows/
│       └── ci.yml                   # Pipeline de Integração Contínua
├── .env.example                     # Modelo de variáveis de ambiente
├── .gitignore                       # Arquivos ignorados pelo Git
├── .python-version                  # Versão do Python fixada (ex: pyenv/uv)
├── pyproject.toml                   # Manifesto do projeto e ferramentas
├── poetry.lock                      # Trava de dependências determinística
├── mkdocs.yml                       # Configuração da documentação
├── README.md                        # Apresentação do repositório
└── SKILL.md                         # Guia de governança técnica
```

### 2.2 Princípios Arquiteturais Obrigatórios

- **Responsabilidade Única (SRP)**: Cada módulo e função deve ter apenas uma razão para mudar. Um extrator não transforma dados; um transformer não executa requisições de rede nem grava em banco.
- **Importações Absolutas**: Todas as importações internas devem iniciar explicitamente a partir de `projeto`:
  ```python
  # CORRETO:
  from projeto.config.settings import get_settings
  from projeto.transformers.cleaner import normalize_payload

  # PROIBIDO:
  from ..config.settings import get_settings
  from transformers.cleaner import normalize_payload
  ```
- **KISS & YAGNI**: Não crie hierarquias complexas de classes abstratas ou factories dinâmicas sem necessidade comprovada. Prefira funções puras e estruturas de dados explícitas.
- **Isolamento de Efeitos Colaterais**: Módulos não devem executar código ao serem importados. A inicialização de recursos (conexões, pipelines) deve ocorrer exclusivamente dentro de funções ou sob o bloco `if __name__ == "__main__":`.
- **`main.py` Magro**: O arquivo `main.py` serve apenas para processar parâmetros de entrada (CLI), carregar configurações e invocar a função orquestradora em `pipelines/`. Nenhuma regra de transformação de dados deve residir em `main.py`.

---

## 3. Padronização de Código com Ruff

O **Ruff** é a única ferramenta de linting, formatação e organização de imports permitida no repositório, substituindo com maior velocidade Flake8, Black e isort.

### 3.1 Diferença entre Conceitos

- **Linting (`ruff check`)**: Análise estática que identifica potenciais bugs, variáveis não utilizadas, violações de complexidade, código morto e desvios de sintaxe.
- **Formatação (`ruff format`)**: Padronização visual determinística do código (espaçamento, quebra de linhas, aspas), garantindo consistência sem alterar a semântica.
- **Organização de Imports (`isort` via regras `I` do Ruff)**: Agrupamento ordenado de imports em blocos lógicos: biblioteca padrão, bibliotecas de terceiros e módulos locais do projeto (`projeto.*`).

### 3.2 Comandos Obrigatórios

```bash
# Verificar problemas de lint e violações de regras
poetry run ruff check .

# Corrigir automaticamente problemas de lint e ordenar imports
poetry run ruff check . --fix

# Formatar o código de acordo com o padrão
poetry run ruff format .

# Verificar em CI se o código está formatado (sem alterar arquivos)
poetry run ruff format --check .
```

---

## 4. Testes Unitários com Pytest

A confiabilidade dos fluxos de dados é garantida por testes automatizados utilizando **pytest** e **pytest-cov**.

### 4.1 Regras de Qualidade e Cobertura

1. **Meta de Cobertura**:
   - **Mínimo obrigatório**: **50%** de cobertura do código localizado em `src/projeto`.
   - **Meta recomendada**: **80%+** em módulos críticos de negócio (`transformers/`, `models/`, `pipelines/`).
   - O comando de teste deve falhar automaticamente caso a cobertura seja inferior a 50% (`--cov-fail-under=50`).
2. **Isolamento Total**: Testes unitários **jamais** devem depender de banco de dados ativo, internet, cloud providers ou sistema de arquivos real. Utilize mocks (`unittest.mock` / fixtures de memória) para simular I/O.
3. **Padrão AAA (Arrange, Act, Assert)**:
   - **Arrange**: Preparar os dados de entrada, dependências e mocks.
   - **Act**: Executar a função ou método testado.
   - **Assert**: Validar rigorosamente o retorno, exceções ou efeitos esperados.
4. **Parametrização**: Cenários múltiplos de validação de dados devem utilizar `pytest.mark.parametrize` para evitar testes duplicados.

### 4.2 Comandos Operacionais

```bash
# Executar todos os testes com validação estrita de cobertura
poetry run pytest

# Executar testes exibindo as linhas que não foram cobertas
poetry run pytest --cov=projeto --cov-report=term-missing

# Executar apenas testes unitários
poetry run pytest tests/unit/
```

---

## 5. Documentação com MkDocs Material

A documentação do projeto deve ser viva, versionada e gerada como site estático utilizando **MkDocs** com o tema **Material for MkDocs**.

### 5.1 Requisitos de Conteúdo

Todo repositório deve manter na pasta `docs/`:
- **Visão Geral**: Propósito do pipeline, fontes consumidoras e destinos.
- **Arquitetura**: Diagrama de fluxo e divisão de responsabilidades.
- **Instalação e Execução**: Guia passo a passo com Poetry.
- **Variáveis de Ambiente**: Lista de configurações esperadas com descrições.
- **Referência Técnica**: Docstrings em padrão Google Style documentadas com `mkdocstrings`.

### 5.2 Comandos de Execução

```bash
# Iniciar servidor local de desenvolvimento com hot-reload
poetry run mkdocs serve

# Compilar a documentação estática para publicação
poetry run mkdocs build --strict
```

### 5.3 Padrão de Docstrings (Google Style)

```python
def transform_orders(orders: list[dict], min_value: float = 0.0) -> list[dict]:
    """Filtra e normaliza a listagem de pedidos de clientes.

    Aplica deduplicação por identificador e remove transações com valor
    inferior ao parâmetro estipulado.

    Args:
        orders: Lista de dicionários contendo os dados brutos dos pedidos.
        min_value: Valor monetário mínimo aceito no processamento.

    Returns:
        Lista de dicionários contendo os pedidos validados e normalizados.

    Raises:
        ValueError: Caso `min_value` seja um número negativo.
    """
    if min_value < 0:
        raise ValueError("O valor mínimo de corte não pode ser negativo.")
    ...
```

---

## 6. Boas Práticas Específicas de Engenharia de Dados

### 6.1 Idempotência e Prevenção de Duplicidade
- Toda execução de pipeline com os mesmos parâmetros de entrada deve produzir rigorosamente o mesmo resultado final no destino.
- Utilize estratégias de **Overwrite de Partição** (`partition overwrite`) ou **Upsert/Merge** em tabelas finais baseado em chaves primárias ou hash de conteúdo (`surrogate key`).
- Crie camadas de staging temporárias antes de substituir dados de produção.

### 6.2 Gerenciamento de Memória e Processamento em Lotes (Batching)
- Em pipelines que consom grandes volumes, nunca carregue todo o volume em memória com `read_sql()` ou `response.json()` irrestritos.
- Processe em chunks (ex: `chunksize=10000` em pandas ou geradores iterativos com `yield`).
- Escale para **PySpark**, **Polars** ou **DuckDB** quando a volumetria exceder os limites confortáveis de memória da infraestrutura.

### 6.3 Conexões, Retries e Timeouts
- Todas as chamadas de rede externas (APIs, HTTP, SFTP) devem possuir **timeout explícito** (ex: `requests.get(url, timeout=(5, 30))`).
- Adote políticas de retentativa com recuo exponencial (*exponential backoff com jitter*) para lidar com falhas transitórias de infraestrutura.
- Conexões com banco de dados devem utilizar context managers (`with connection_pool.getconn() as conn:`) garantindo fechamento imediato mesmo diante de exceções.

### 6.4 Sanitização e Prevenção de Injeção SQL
- **Nunca concatene strings para construir consultas SQL**.
- Sempre utilize parâmetros vinculados (*parameterized queries / bound parameters*):
  ```python
  # CORRETO:
  cursor.execute("SELECT * FROM sales WHERE execution_date = :dt", {"dt": target_date})

  # CRIME GRAVE:
  cursor.execute(f"SELECT * FROM sales WHERE execution_date = '{target_date}'")
  ```

### 6.5 Tratamento de Datas e Timezones
- Armazene e processe timestamps sempre em formato **UTC** com fuso explícito (`datetime.now(timezone.utc)`).
- Converta para o horário local de negócio apenas na camada final de apresentação/consumo.
- Formate partições temporais de forma padronizada: `ano=YYYY/mes=MM/dia=DD`.

### 6.6 Logs Estruturados e Observabilidade
- **Proibido usar `print()`**: O `print` não carrega contexto, severidade nem metadados de execução.
- Utilize o módulo nativo `logging` configurado para formato JSON ou formato enriquecido (timestamp, módulo, nível de log, mensagem).
- Emita métricas de observabilidade: volumetria extraída, tempo gasto por etapa e registros descartados por erro de schema.

---

## 7. Segurança e Governança de Configurações

1. **Gestão de Segredos**:
   - Nunca comite senhas, tokens, chaves de API ou connection strings em código ou arquivos versionados.
   - Mantenha um arquivo `.env.example` no Git contendo apenas as chaves vazias ou com valores fictícios de exemplo.
   - Utilize a biblioteca `pydantic-settings` para validar tipagem e presença de variáveis de ambiente na inicialização da aplicação (Fail-Fast).
2. **Mascaramento em Logs**:
   - Nunca imprima o payload completo de requisições que contenham credenciais ou dados pessoais identificáveis (PII/LGPD).
3. **Princípio do Menor Privilégio**:
   - As credenciais de conexão utilizadas por extratores devem ter permissões estritamente restritas a leitura (`SELECT`) em fontes e escrita apenas no schema específico de destino.

---

## 8. Git, Versionamento e Integração Contínua (CI)

### 8.1 Padrão de Mensagens de Commit (Conventional Commits)

Os commits devem ser atômicos e seguir o formato:
- `feat: adiciona extrator de telemetria da api de parceiros`
- `fix: corrige timezone na conversao de data de execucao`
- `test: adiciona testes unitarios para deduplicacao de ordens`
- `refactor: modulariza funcao de carregamento para s3`
- `docs: atualiza guia de configuracao de variaveis de ambiente`
- `chore: atualiza dependencias de desenvolvimento no poetry.lock`

### 8.2 Proteção e Qualidade de Branches

- A branch `main` é protegida. Nenhuma alteração entra sem **Pull Request** e aprovação de pelo menos um revisor.
- O pipeline de CI no GitHub Actions deve ser executado em todo Push e Pull Request, bloqueando o merge caso haja qualquer falha de lint, formatação, teste, cobertura (<50%) ou documentação.

---

## 9. Padrões de Código Python

- **Type Hints**: Todas as assinaturas de funções e métodos devem ser integralmente tipadas (argumentos e retorno).
- **Pathlib**: Manipulação de caminhos e arquivos no sistema operacional deve utilizar `pathlib.Path`, e não `os.path`.
- **Context Managers**: Sempre gerencie arquivos e conexões com blocos `with open(...) as f:`.
- **Tratamento Específico de Exceções**: Capture apenas exceções que você sabe como tratar (ex: `KeyError`, `ValueError`, `requests.Timeout`). Nunca utilize blocos vazios `except:` ou `except Exception: pass`.
- **Valores Padrão Imutáveis**: Nunca use objetos mutáveis (`list`, `dict`) como default de argumentos. Use `None` e inicialize no corpo da função.

---

## 10. Regras de Comportamento para Agentes de IA

Ao atuar neste repositório, qualquer assistente ou agente de inteligência artificial deve cumprir rigorosamente as seguintes diretrizes:

1. **Inspeção Prévia**: Examine a estrutura de arquivos e o `pyproject.toml` antes de sugerir ou editar código.
2. **Respeito à Arquitetura**: Jamais crie arquivos fora da hierarquia modular em `src/projeto/`.
3. **Poetry Exclusivo**: Sempre declare comandos com `poetry run` ou `poetry add`. Nunca mencione `pip install`.
4. **Imports Absolutos**: Use sempre `from projeto.<modulo> import <objeto>`.
5. **Ruff como Padrão Único**: Ao gerar ou refatorar código, certifique-se de que respeita os limites de linha e as regras do Ruff.
6. **Criação Mandatória de Testes**: Para qualquer nova lógica de negócio ou transformação criada, crie os testes unitários correspondentes em `tests/unit/`.
7. **Garantia de Cobertura**: Verifique se a alteração mantém a cobertura geral acima de 50%.
8. **Atualização de Documentação**: Se um parâmetro de configuração for incluído ou alterado, atualize `.env.example`, `settings.py` e os arquivos pertinentes em `docs/`.
9. **Não Invente Bibliotecas**: Utilize prioritariamente a biblioteca padrão do Python ou ferramentas já presentes no `pyproject.toml`. Justifique tecnicamente qualquer nova dependência.
10. **Segurança Incondicional**: Recuse-se a colocar credenciais literais no código.
11. **Honestidade Operacional**: Nunca afirme que um teste ou comando passou com sucesso a menos que ele tenha sido efetivamente executado no ambiente e retornado código 0. Caso não seja possível executar, informe a limitação ao desenvolvedor.

---

## 11. Critérios Obrigatórios de Entrega (Definition of Done)

Uma tarefa só é considerada concluída quando o seguinte checklist for atendido:

- [ ] A arquitetura modular em `src/projeto/` foi respeitada.
- [ ] Todas as dependências novas foram adicionadas via `poetry add`.
- [ ] O código foi verificado e corrigido pelo Ruff (`poetry run ruff check . --fix`).
- [ ] O código foi formatado pelo Ruff (`poetry run ruff format .`).
- [ ] Os testes unitários foram criados/atualizados e aprovados (`poetry run pytest`).
- [ ] A cobertura de testes do pacote `projeto` atingiu o índice mínimo de 50%.
- [ ] A documentação do MkDocs compila sem erros (`poetry run mkdocs build --strict`).
- [ ] Nenhuma credencial ou segredo foi exposto.
- [ ] Arquivos `.env.example` e documentações foram atualizados caso haja novas variáveis de ambiente.
