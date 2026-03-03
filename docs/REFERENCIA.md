# TJDFT API - Referência Rápida

> Cheatsheet para uso da API de Jurisprudência do TJDFT

---

## 🔗 URLs

```
Base URL:    https://jurisdf.tjdft.jus.br/api/v1
Endpoint:    POST /pesquisa
```

---

## 📤 Requisição

### Headers

```
Content-Type: application/json
Accept: application/json
```

### Body

```json
{
  "query": "termo de busca",
  "pagina": 0,
  "tamanho": 20,
  "termosAcessorios": [
    {"campo": "nomeRelator", "valor": "NOME DO RELATOR"}
  ]
}
```

---

## 🔍 Filtros

| Campo | Exemplo |
|-------|---------|
| `nomeRelator` | `"CARMEN BITTENCOURT"` |
| `descricaoOrgaoJulgador` | `"8ª Turma Cível"` |
| `processo` | `"0710649-40.2025.8.07.0000"` |
| `dataPublicacao` | `"2025-03-25"` |
| `dataJulgamento` | `"2025-03-24"` |
| `descricaoClasseCnj` | `"Procedimento Comum Cível"` |
| `base` | `"acordaos"`, `"decisoes"` |

---

## 📥 Resposta

```json
{
  "hits": 1234,
  "pagina": 0,
  "registros": [
    {
      "uuid": "...",
      "processo": "0710649-40.2025.8.07.0000",
      "nomeRelator": "CARMEN BITTENCOURT",
      "descricaoOrgaoJulgador": "8ª Turma Cível",
      "dataPublicacao": "2025-03-25T03:00:00.000Z",
      "ementa": "EMENTA: ...",
      "inteiroTeor": "...",
      "possuiInteiroTeor": true,
      "descricaoClasseCnj": "Procedimento Comum Cível"
    }
  ]
}
```

---

## 🐍 Python

### Instalação

```bash
pip install git+https://github.com/prof-ramos/tjdft-api-client.git
```

### Básico

```python
from tjdft import TJDFTClient

client = TJDFTClient()
resultados = client.pesquisar(query="dano moral", tamanho=10)

for r in resultados:
    print(r["processo"], r["nome_relator"])
```

### Otimizado

```python
from tjdft import TJDFTClientOptimized

client = TJDFTClientOptimized(
    cache_ttl=300,      # 5 min
    rate_limit=10.0     # 10 req/s
)

r = client.pesquisar(query="termo")
print(client.get_metrics())
```

### Filtros

```python
# Por relator
resultados = client.pesquisar_por_relator(
    query="dano moral",
    relator="CARMEN BITTENCOURT"
)

# Por órgão
resultados = client.pesquisar_por_orgao(
    query="tutela",
    orgao="8ª Turma Cível"
)

# Por processo
decisao = client.buscar_por_processo("0710649-40.2025.8.07.0000")

# Com filtros múltiplos
resultados = client.pesquisar(
    query="dano moral",
    filtros={
        "nomeRelator": "CARMEN BITTENCOURT",
        "descricaoOrgaoJulgador": "8ª Turma Cível"
    }
)
```

### Batch

```python
consultas = [
    {"query": "dano moral"},
    {"query": "habeas corpus"},
]

resultados = client.pesquisar_lote(consultas, max_parallel=5)
```

### Tokens

```python
from tjdft import TokenCounter

counter = TokenCounter()

count = counter.count("Texto jurídico")
print(f"Tokens: {count.tokens}")

cost = counter.estimate_cost(1000, 500)
print(f"Custo: ${cost['total_cost_usd']:.4f}")
```

### Análise

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
```

---

## 💻 cURL

### Simples

```bash
curl -X POST https://jurisdf.tjdft.jus.br/api/v1/pesquisa \
  -H "Content-Type: application/json" \
  -d '{"query": "dano moral", "pagina": 0, "tamanho": 10}'
```

### Com Filtros

```bash
curl -X POST https://jurisdf.tjdft.jus.br/api/v1/pesquisa \
  -H "Content-Type: application/json" \
  -d '{
    "query": "tutela de urgência",
    "pagina": 0,
    "tamanho": 20,
    "termosAcessorios": [
      {"campo": "nomeRelator", "valor": "CARMEN BITTENCOURT"}
    ]
  }'
```

---

## 🟨 JavaScript

```javascript
async function pesquisar(query) {
  const response = await fetch('https://jurisdf.tjdft.jus.br/api/v1/pesquisa', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      query: query,
      pagina: 0,
      tamanho: 20
    })
  });
  
  return response.json();
}

pesquisar('dano moral').then(data => {
  console.log(`Total: ${data.hits}`);
  data.registros.forEach(r => console.log(r.processo));
});
```

---

## ⚠️ Limitações

| Aspecto | Limite |
|---------|--------|
| Rate limit | ~10 req/s (recomendado) |
| Tamanho página | 100 (recomendado) |
| Autenticação | Não requerida |
| Range de datas | ❌ Não suportado |
| Boolean ops | ❌ Não suportado |

---

## 🐛 Tratamento de Erros

```python
import requests
from tjdft import TJDFTClient

client = TJDFTClient()

try:
    resultados = client.pesquisar(query="termo")
except requests.exceptions.Timeout:
    print("Timeout")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        print("Rate limit - aguarde")
    elif e.response.status_code >= 500:
        print("Erro no servidor")
```

---

## 📊 Métricas (Cliente Otimizado)

```python
client = TJDFTClientOptimized()

# ... fazer requisições ...

metrics = client.get_metrics()

print(f"Requisições: {metrics['total_requests']}")
print(f"Cache hits: {metrics['cache_hits']}")
print(f"Taxa de cache: {metrics['cache_hit_ratio']:.1%}")
print(f"Tempo médio: {metrics['avg_response_time_ms']:.1f}ms")
```

---

## 📁 Exportar

### CSV

```python
import csv

with open("jurisprudencias.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
    writer.writeheader()
    writer.writerows(resultados.resultados)
```

### JSON

```python
import json

with open("jurisprudencias.json", "w", encoding="utf-8") as f:
    json.dump(resultados.resultados, f, indent=2, ensure_ascii=False)
```

---

## 📚 Links

- **Repo:** https://github.com/prof-ramos/tjdft-api-client
- **API Docs:** [docs/API.md](docs/API.md)
- **Exemplos:** [docs/EXEMPLOS.md](docs/EXEMPLOS.md)
- **TJDFT:** https://www.tjdft.jus.br

---

**Versão:** 0.3.0 | **Atualizado:** 2026-03-02
