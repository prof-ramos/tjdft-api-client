# Guia UV - TJDFT API Client

> Este projeto usa **UV** como gerenciador de pacotes 100% Python

---

## 📋 O que é UV?

[UV](https://docs.astral.sh/uv/) é um gerenciador de pacotes Python extremamente rápido (escrito em Rust), criado pela Astral (mesma equipe do Ruff). É **10-100x mais rápido** que pip e pip-tools.

### Vantagens

- ⚡ **10-100x mais rápido** que pip
- 🔒 **Lock file automático** (uv.lock)
- 📦 **Resolver determinístico**
- 🐍 **Gerenciamento de versões Python**
- 🧪 **Ambientes virtuais integrados**
- 🎯 **Drop-in replacement** para pip

---

## 🚀 Instalação

### Instalar UV

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ou via pip
pip install uv

# Ou via pipx
pipx install uv
```

### Verificar Instalação

```bash
uv --version
# uv 0.10.4 (ou superior)
```

---

## 📦 Setup do Projeto

### Clonar e Configurar

```bash
# Clonar repositório
git clone https://github.com/prof-ramos/tjdft-api-client.git
cd tjdft-api-client

# Criar venv e instalar dependências (automático)
uv sync

# Isso cria:
# - .venv/ (ambiente virtual)
# - uv.lock (lock file)
```

### Com Python Específico

```bash
# Usar Python 3.12
uv sync --python 3.12

# Ou especificar no .python-version
echo "3.12" > .python-version
uv sync
```

---

## 🎯 Comandos Principais

### Instalação

```bash
# Instalar todas as dependências
uv sync

# Instalar apenas dependências de produção
uv sync --no-dev

# Instalar com extras
uv sync --extra async --extra ai

# Instalar tudo
uv sync --all-extras
```

### Adicionar Dependências

```bash
# Adicionar dependência de produção
uv add requests

# Adicionar dependência de desenvolvimento
uv add --dev pytest

# Adicionar com versão específica
uv add "requests>=2.28.0"

# Adicionar com extra
uv add "aiohttp>=3.9.0" --optional async
```

### Remover Dependências

```bash
# Remover dependência
uv remove requests

# Remover dependência de dev
uv remove --dev pytest
```

### Atualizar Dependências

```bash
# Atualizar todas
uv sync --upgrade

# Atualizar pacote específico
uv sync --upgrade-package requests
```

---

## 🏃 Executar

### Scripts Python

```bash
# Executar script
uv run python script.py

# Executar módulo
uv run python -m tjdft.client

# Executar com argumentos
uv run python examples/busca_jurisprudencia.py --query "dano moral"
```

### Testes

```bash
# Executar testes
uv run pytest

# Com verbose
uv run pytest -v

# Teste específico
uv run pytest tests/test_client.py

# Com cobertura
uv run pytest --cov=src/tjdft
```

### Formatação e Linting

```bash
# Formatar com Black
uv run black src/ tests/

# Linting com Ruff
uv run ruff check src/ tests/

# Type checking com MyPy
uv run mypy src/
```

---

## 🔧 Desenvolvimento

### Criar Novo Ambiente

```bash
# Remover ambiente antigo
rm -rf .venv

# Criar novo
uv sync
```

### Ativar Ambiente Virtual

```bash
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# Ou usar uv run (sem ativar)
uv run python script.py
```

### Ver Dependências

```bash
# Listar dependências instaladas
uv pip list

# Ver árvore de dependências
uv pip tree

# Ver detalhes de pacote
uv pip show requests
```

---

## 📦 Build e Publicação

### Build do Pacote

```bash
# Build com UV
uv build

# Resultado em dist/
# - tjdft-0.4.0-py3-none-any.whl
# - tjdft-0.4.0.tar.gz
```

### Publicar no PyPI

```bash
# Publicar no PyPI
uv publish

# Publicar no TestPyPI
uv publish --index-url https://test.pypi.org/simple/
```

---

## 🔄 Migração de pip/poetry

### De requirements.txt

```bash
# Instalar do requirements.txt
uv pip install -r requirements.txt

# Depois adicionar ao pyproject.toml
uv add $(cat requirements.txt | grep -v "^#")
```

### De Poetry

```bash
# UV lê pyproject.toml automaticamente
# Apenas execute:
uv sync
```

### De Pipenv

```bash
# Converter Pipfile para requirements.txt
pipenv requirements > requirements.txt

# Depois usar UV
uv pip install -r requirements.txt
```

---

## 🎨 Configuração Avançada

### pyproject.toml

```toml
[tool.uv]
# Dependências de desenvolvimento
dev-dependencies = [
    "pytest>=7.0.0",
    "black>=23.0.0",
]

# Índices customizados
[[tool.uv.index]]
name = "private"
url = "https://pypi.example.com/simple"
```

### Variáveis de Ambiente

```bash
# UV_CACHE_DIR - Diretório de cache
export UV_CACHE_DIR="/path/to/cache"

# UV_INDEX_URL - Índice PyPI customizado
export UV_INDEX_URL="https://pypi.org/simple"

# UV_NO_CACHE - Desabilitar cache
export UV_NO_CACHE=1
```

---

## 🚀 CI/CD com UV

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install UV
        uses: astral-sh/setup-uv@v4
        with:
          version: "0.10.4"
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      
      - name: Install dependencies
        run: uv sync --all-extras
      
      - name: Run tests
        run: uv run pytest
      
      - name: Run linting
        run: |
          uv run ruff check src/
          uv run black --check src/
```

### GitLab CI

```yaml
test:
  image: python:3.12
  before_script:
    - pip install uv
    - uv sync
  script:
    - uv run pytest
```

---

## 🐛 Troubleshooting

### Erro: "No matching distribution found"

```bash
# Atualizar índice do PyPI
uv sync --refresh
```

### Erro: "Python version not found"

```bash
# Instalar Python via UV
uv python install 3.12

# Listar Pythons disponíveis
uv python list
```

### Erro: "Lock file out of date"

```bash
# Regenerar lock file
uv sync --reinstall
```

### Limpar Cache

```bash
# Limpar cache do UV
uv cache clean

# Ver tamanho do cache
uv cache dir
```

---

## 📊 Comparação de Performance

| Comando | pip | UV | Speedup |
|---------|-----|-----|---------|
| `install` (cold cache) | 8.2s | 0.16s | **51x** |
| `install` (warm cache) | 1.4s | 0.01s | **140x** |
| `resolve` | 3.1s | 0.03s | **103x** |
| `lock` | N/A | 0.02s | - |

---

## 🔗 Links Úteis

- [UV Documentation](https://docs.astral.sh/uv/)
- [UV GitHub](https://github.com/astral-sh/uv)
- [UV vs pip](https://docs.astral.sh/uv/#comparison-to-pip)
- [UV Blog](https://astral.sh/blog/uv-unified-python-packaging)

---

## 💡 Dicas

1. **Use `uv run`** em vez de ativar o venv manualmente
2. **Commit o `uv.lock`** para reprodutibilidade
3. **Use `.python-version`** para especificar versão
4. **`uv sync --upgrade`** para atualizar tudo
5. **`uv add --dev`** para dependências de desenvolvimento
6. **Use extras** (`uv sync --extra ai`) para features opcionais

---

## 📝 Exemplos Práticos

### Buscar Jurisprudência

```bash
# Buscar com script
uv run python examples/busca_jurisprudencia.py

# Buscar interativamente
uv run python -c "
from tjdft import TJDFTClient
client = TJDFTClient()
resultados = client.pesquisar(query='dano moral', tamanho=10)
for r in resultados:
    print(r['processo'])
"
```

### Testar Performance

```bash
# Benchmark
uv run python tests/test_performance.py

# Com verbose
uv run pytest tests/test_performance.py -v -s
```

### Contar Tokens

```bash
# Exemplo de contagem
uv run python examples/contagem_tokens.py
```

---

## 🎯 Checklist de Migração

- [x] ✅ Criar `pyproject.toml` com dependências
- [x] ✅ Criar `.python-version` (3.12)
- [x] ✅ Remover `requirements.txt`
- [x] ✅ Remover `.venv` antigo
- [x] ✅ Executar `uv sync`
- [x] ✅ Testar imports
- [x] ✅ Commit `uv.lock`
- [x] ✅ Atualizar README

---

**Versão UV:** 0.10.4+  
**Python:** 3.8-3.12  
**Atualizado:** 2026-03-02
