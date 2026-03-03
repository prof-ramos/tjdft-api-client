# TJDFT API Client

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![UV](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![API Status](https://img.shields.io/badge/API-Online-brightgreen.svg)](https://jurisdf.tjdft.jus.br/api/v1/pesquisa)

> Cliente Python completo e otimizado para a API de Jurisprudência do TJDFT

---

## 📋 Sumário

- [Características](#-características)
- [Instalação](#-instalação)
- [Uso Rápido](#-uso-rápido)
- [Funcionalidades](#-funcionalidades)
- [Documentação](#-documentação)
- [Exemplos](#-exemplos)
- [API Reference](#-api-reference)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)

---

## ✨ Características

- ✅ **API Pública Oficial** - Sem necessidade de autenticação
- ✅ **Cliente Otimizado** - Cache, rate limiting, retries automáticos
- ✅ **Contagem de Tokens** - Integração com tiktoken para custos OpenAI
- ✅ **Análise de Magistrados** - Perfil decisório e estatísticas
- ✅ **Batch Requests** - Consultas paralelas para melhor performance
- ✅ **Async Support** - Suporte a operações assíncronas com aiohttp
- ✅ **Type Hints** - Código totalmente tipado
- ✅ **Zero Dependencies Core** - Apenas `requests` no básico

---

## 📦 Instalação

### Via UV (recomendado) ⚡

```bash
# Instalar UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clonar e configurar
git clone https://github.com/prof-ramos/tjdft-api-client.git
cd tjdft-api-client
uv sync

# Executar
uv run python -c "from tjdft import TJDFTClient; print('✅ Instalado!')"
```

### Via pip

```bash
pip install git+https://github.com/prof-ramos/tjdft-api-client.git
```

### Extras Opcionais

```bash
# Com suporte async
uv sync --extra async

# Com suporte a IA (OpenAI)
uv sync --extra ai

# Tudo (desenvolvimento completo)
uv sync --all-extras
```

> 📖 Veja [docs/UV.md](docs/UV.md) para guia completo do UV

---

## 🚀 Uso Rápido

### Pesquisa Simples

```python
from tjdft import TJDFTClient

# Criar cliente
client = TJDFTClient()

# Buscar jurisprudência
resultados = client.pesquisar(query="dano moral", tamanho=10)

# Iterar resultados
for r in resultados:
    print(f"Processo: {r['processo']}")
    print(f"Relator: {r['nome_relator']}")
    print(f"Ementa: {r['ementa'][:100]}...")
```

### Com Filtros

```python
from tjdft import TJDFTClient

client = TJDFTClient()

# Filtrar por relator
resultados = client.pesquisar(
    query="tutela de urgência",
    filtros={
        "nomeRelator": "CARMEN BITTENCOURT",
        "descricaoOrgaoJulgador": "8ª Turma Cível"
    },
    tamanho=20
)

print(f"Total: {resultados.total}")
```

### Cliente Otimizado

```python
from tjdft import TJDFTClientOptimized

# Com cache e rate limiting
client = TJDFTClientOptimized(
    cache_ttl=300,        # 5 minutos
    rate_limit=10.0,      # 10 req/s
    max_retries=3
)

# Primeira chamada (API)
r1 = client.pesquisar(query="dano moral")

# Segunda chamada (cache - instantâneo)
r2 = client.pesquisar(query="dano moral")

# Ver métricas
print(client.get_metrics())
```

### Batch Paralelo

```python
from tjdft import TJDFTClientOptimized

client = TJDFTClientOptimized()

consultas = [
    {"query": "dano moral"},
    {"query": "habeas corpus"},
    {"query": "tutela de urgência"},
]

resultados = client.pesquisar_lote(consultas, max_parallel=5)

for i, r in enumerate(resultados):
    print(f"{consultas[i]['query']}: {r.total} resultados")
```

---

## 🎯 Funcionalidades

### Clientes

| Cliente | Descrição | Use Quando |
|---------|-----------|------------|
| `TJDFTClient` | Cliente básico | Uso simples, poucas requisições |
| `TJDFTClientOptimized` | Cliente otimizado | Produção, muitas requisições |

### Recursos

#### Pesquisa

```python
# Básica
resultados = client.pesquisar(query="termo")

# Com filtros
resultados = client.pesquisar(
    query="termo",
    filtros={"nomeRelator": "NOME"}
)

# Por relator
resultados = client.pesquisar_por_relator(query="termo", relator="NOME")

# Por órgão
resultados = client.pesquisar_por_orgao(query="termo", orgao="5ª Turma")

# Por processo
decisao = client.buscar_por_processo("0710649-40.2025.8.07.0000")
```

#### Análise de Magistrados

```python
from tjdft import TJDFTClient, AnaliseMagistrados

client = TJDFTClient()
analise = AnaliseMagistrados()

resultados = client.pesquisar_por_relator(
    query="dano moral",
    relator="CARMEN BITTENCOURT",
    tamanho=100
)

perfil = analise.analisar(resultados.resultados)

print(f"Deferimentos: {perfil.percentual_deferimento:.1%}")
print(f"Indeferimentos: {perfil.percentual_indeferimento:.1%}")
```

#### Contagem de Tokens

```python
from tjdft import TokenCounter

counter = TokenCounter(model="gpt-4o-mini")

# Contar tokens
count = counter.count("Texto jurídico aqui")
print(f"Tokens: {count.tokens}")

# Estimar custo
cost = counter.estimate_cost(
    input_tokens=1000,
    output_tokens=500
)
print(f"Custo: ${cost['total_cost_usd']:.4f}")

# Truncar para limite
texto_truncado = counter.truncate_to_tokens(texto, max_tokens=4000)

# Dividir em chunks
chunks = counter.chunk_text(texto_longo, chunk_size=4000)
```

---

## 📚 Documentação

### Guias Completos

| Documento | Descrição |
|-----------|-----------|
| [**API.md**](docs/API.md) | Documentação completa da API |
| [**EXEMPLOS.md**](docs/EXEMPLOS.md) | Exemplos práticos de uso |
| [**endpoints.md**](docs/endpoints.md) | Endpoints disponíveis |
| [**examples.md**](docs/examples.md) | Exemplos de código |

### Documentação da API

- **Base URL:** `https://jurisdf.tjdft.jus.br/api/v1`
- **Endpoint:** `POST /pesquisa`
- **Autenticação:** Não requerida
- **Formato:** JSON

#### Filtros Disponíveis

| Campo | Descrição |
|-------|-----------|
| `nomeRelator` | Nome do relator |
| `descricaoOrgaoJulgador` | Órgão julgador |
| `processo` | Número do processo |
| `dataPublicacao` | Data de publicação |
| `descricaoClasseCnj` | Classe processual |

---

## 💡 Exemplos

### Buscar Precedentes

```python
from tjdft import TJDFTClientOptimized

client = TJDFTClientOptimized()

resultados = client.pesquisar(
    query="dano moral atraso voo",
    tamanho=20
)

favoraveis = [
    r for r in resultados
    if any(p in r["ementa"].lower() for p in ["deferido", "procedente"])
]

print(f"Precedentes favoráveis: {len(favoraveis)}")
```

### Exportar para CSV

```python
import csv
from tjdft import TJDFTClient

client = TJDFTClient()
resultados = client.pesquisar(query="dano moral", tamanho=50)

with open("jurisprudencias.csv", "w", newline="", encoding="utf-8") as f:
    if resultados:
        writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
        writer.writeheader()
        writer.writerows(resultados.resultados)
```

### Análise com IA

```python
from tjdft import TJDFTClientOptimized, TokenCounter
from openai import OpenAI

client_tjdft = TJDFTClientOptimized()
client_openai = OpenAI()
counter = TokenCounter()

# Buscar
resultados = client_tjdft.pesquisar(query="dano moral", tamanho=5)

# Preparar contexto
contexto = "\n\n".join([r["ementa"] for r in resultados if r.get("ementa")])

# Analisar
response = client_openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": f"Analise estas decisões:\n\n{contexto}"}
    ]
)

print(response.choices[0].message.content)
```

---

## 🔧 API Reference

### TJDFTClient

```python
class TJDFTClient:
    def __init__(timeout: int = 30, user_agent: str = "..."):
        """Inicializa cliente."""
    
    def pesquisar(
        query: str,
        pagina: int = 0,
        tamanho: int = 20,
        filtros: Optional[Dict[str, str]] = None
    ) -> ResultadoBusca:
        """Pesquisa jurisprudência."""
    
    def pesquisar_por_relator(query: str, relator: str) -> ResultadoBusca:
        """Pesquisa por relator."""
    
    def pesquisar_por_orgao(query: str, orgao: str) -> ResultadoBusca:
        """Pesquisa por órgão."""
    
    def buscar_por_processo(numero: str) -> Optional[Dict]:
        """Busca por número de processo."""
```

### TJDFTClientOptimized

```python
class TJDFTClientOptimized(TJDFTClient):
    def __init__(
        timeout: int = 30,
        cache_ttl: int = 300,
        cache_maxsize: int = 1000,
        rate_limit: float = 10.0,
        rate_burst: int = 20,
        max_retries: int = 3,
        enable_compression: bool = True
    ):
        """Cliente otimizado com cache e rate limiting."""
    
    def pesquisar_lote(
        consultas: List[Dict],
        max_parallel: int = 5
    ) -> List[ResultadoBusca]:
        """Executa múltiplas consultas em paralelo."""
    
    async def pesquisar_async(query: str, ...) -> ResultadoBusca:
        """Versão assíncrona."""
    
    def get_metrics() -> Dict[str, Any]:
        """Retorna métricas de performance."""
    
    def clear_cache() -> None:
        """Limpa cache."""
```

### TokenCounter

```python
class TokenCounter:
    def __init__(model: str = "gpt-4o-mini"):
        """Contador de tokens com tiktoken."""
    
    def count(text: str) -> TokenCount:
        """Conta tokens em texto."""
    
    def estimate_cost(
        input_tokens: int,
        output_tokens: int,
        model: Optional[str] = None
    ) -> Dict[str, float]:
        """Estima custo em USD."""
    
    def truncate_to_tokens(text: str, max_tokens: int) -> str:
        """Trunca para limite de tokens."""
    
    def chunk_text(
        text: str,
        chunk_size: int = 4000,
        overlap: int = 200
    ) -> List[str]:
        """Divide texto em chunks."""
```

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Desenvolvimento

```bash
# Clonar
git clone https://github.com/prof-ramos/tjdft-api-client.git
cd tjdft-api-client

# Configurar com UV
uv sync

# Rodar testes
uv run pytest tests/

# Formatar
uv run black src/ tests/

# Lint
uv run ruff check src/ tests/
```

---

## 📄 Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE) para mais informações.

---

## 🔗 Links Úteis

- [TJDFT Oficial](https://www.tjdft.jus.br)
- [Jurisprudência TJDFT](https://www.tjdft.jus.br/consultas/jurisprudencia/jurisprudencia)
- [DataJud CNJ](https://datajud.cnj.jus.br)
- [DadosJusBR](https://dadosjusbr.org)

---

## 📊 Status do Projeto

| Feature | Status |
|---------|--------|
| Cliente básico | ✅ Implementado |
| Cliente otimizado | ✅ Implementado |
| Análise de magistrados | ✅ Implementado |
| Contagem de tokens | ✅ Implementado |
| Async support | ✅ Implementado |
| Testes | ✅ 100% passando |
| Documentação | ✅ Completa |

---

**Autor:** [prof-ramos](https://github.com/prof-ramos)  
**Versão:** 0.3.0  
**Última atualização:** 2026-03-02
