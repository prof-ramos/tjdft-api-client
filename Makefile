# Makefile para TJDFT API Client
# Usa UV como gerenciador de pacotes

.PHONY: install sync test lint format clean build run help

# Default
help:
	@echo "TJDFT API Client - Comandos disponíveis:"
	@echo ""
	@echo "  make install     - Instalar dependências"
	@echo "  make sync        - Sincronizar dependências"
	@echo "  make test        - Executar testes"
	@echo "  make lint        - Executar linting"
	@echo "  make format      - Formatar código"
	@echo "  make check       - Verificar tudo (lint + test)"
	@echo "  make clean       - Limpar arquivos temporários"
	@echo "  make build       - Criar distribuição"
	@echo "  make run         - Executar exemplo interativo"
	@echo ""

# Instalação
install:
	uv sync

sync:
	uv sync --upgrade

# Testes
test:
	uv run pytest tests/ -v

test-coverage:
	uv run pytest tests/ --cov=src/tjdft --cov-report=html

# Linting
lint:
	uv run ruff check src/ tests/

format:
	uv run black src/ tests/

format-check:
	uv run black --check src/ tests/

type-check:
	uv run mypy src/

# Verificação completa
check: lint format-check test
	@echo "✅ Todos os checks passaram!"

# Build
build:
	uv build

# Limpeza
clean:
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	rm -f .coverage

# Execução
run:
	uv run python -c "from tjdft import TJDFTClient; \
		client = TJDFTClient(); \
		r = client.pesquisar(query='dano moral', tamanho=5); \
		print(f'Total: {r.total}'); \
		[print(f'{i+1}. {x[\"processo\"]}') for i, x in enumerate(r)]"

# Exemplos
example-busca:
	uv run python examples/busca_jurisprudencia.py

example-tokens:
	uv run python examples/contagem_tokens.py

example-performance:
	uv run python tests/test_performance.py

# Desenvolvimento
dev-setup:
	uv sync --all-extras
	uv run pre-commit install 2>/dev/null || true

# CI
ci: lint test type-check
	@echo "✅ CI checks completos!"
