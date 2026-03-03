# Documentação da API de Jurisprudência do TJDFT

> **Versão:** 1.0.0  
> **Última atualização:** 2026-03-02  
> **Status:** Pública (sem autenticação)

---

## 📋 Sumário

- [Visão Geral](#visão-geral)
- [Autenticação](#autenticação)
- [Base URL](#base-url)
- [Endpoints](#endpoints)
  - [Pesquisa de Jurisprudência](#pesquisa-de-jurisprudência)
  - [Filtros Disponíveis](#filtros-disponíveis)
- [Formatos de Dados](#formatos-de-dados)
  - [Requisição](#requisição)
  - [Resposta](#resposta)
  - [Modelos](#modelos)
- [Exemplos de Uso](#exemplos-de-uso)
  - [Python](#python)
  - [cURL](#curl)
  - [JavaScript](#javascript)
- [Códigos de Status](#códigos-de-status)
- [Limitações e Restrições](#limitações-e-restrições)
- [Boas Práticas](#boas-práticas)
- [FAQ](#faq)

---

## Visão Geral

A API de Jurisprudência do Tribunal de Justiça do Distrito Federal e dos Territórios (TJDFT) permite pesquisar decisões judiciais (acórdãos e decisões monocráticas) publicadas pelo tribunal.

### Características

- ✅ **Pública**: Sem necessidade de autenticação
- ✅ **RESTful**: Interface padrão HTTP/JSON
- ✅ **Gratuita**: Sem custos para uso
- ✅ **Tempo Real**: Decisões publicadas recentemente
- ⚠️ **Sem Rate Limit Oficial**: Uso responsável recomendado

### Tipos de Decisões

| Tipo | Descrição |
|------|-----------|
| **Acórdãos** | Decisões colegiadas (turmas, câmaras) |
| **Decisões Monocráticas** | Decisões individuais de desembargadores |
| **Sentenças** | Decisões de primeira instância |

---

## Autenticação

**Não é necessária autenticação.** A API é pública e não requer tokens, chaves ou credenciais.

⚠️ **Importante**: Por ser pública, recomenda-se:
- Não fazer abusos (muitas requisições em pouco tempo)
- Implementar cache local
- Respeitar intervalos entre requisições

---

## Base URL

```
https://jurisdf.tjdft.jus.br/api/v1
```

### URL Completa do Endpoint

```
https://jurisdf.tjdft.jus.br/api/v1/pesquisa
```

---

## Endpoints

### Pesquisa de Jurisprudência

Pesquisa decisões no banco de dados do TJDFT.

```
POST /pesquisa
```

#### Parâmetros do Body (JSON)

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `query` | string | ✅ Sim | Termo principal da pesquisa |
| `pagina` | int | ✅ Sim | Número da página (começa em 0) |
| `tamanho` | int | ✅ Sim | Resultados por página (máx: 100) |
| `termosAcessorios` | array | ❌ Não | Lista de filtros adicionais |

#### Estrutura de `termosAcessorios`

```json
{
  "termosAcessorios": [
    {
      "campo": "nomeRelator",
      "valor": "CARMEN BITTENCOURT"
    }
  ]
}
```

### Filtros Disponíveis

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `base` | string | Base de dados | `"acordaos"`, `"decisoes"` |
| `subbase` | string | Subbase de dados | `"decisoes-monocraticas"` |
| `origem` | string | Origem da decisão | `"TJDFT"` |
| `uuid` | string | Identificador único | `"29df78c5-af48-..."` |
| `identificador` | string | ID numérico | `"70016492"` |
| `processo` | string | Número do processo | `"0710649-40.2025.8.07.0000"` |
| `nomeRelator` | string | Nome do relator | `"CARMEN BITTENCOURT"` |
| `nomeRevisor` | string | Nome do revisor | `"JOÃO EGMONT"` |
| `nomeRelatorDesignado` | string | Relator designado | `"LEONARDO ALVES"` |
| `descricaoOrgaoJulgador` | string | Órgão julgador | `"8ª Turma Cível"` |
| `dataJulgamento` | string | Data do julgamento | `"2025-03-25"` |
| `dataPublicacao` | string | Data da publicação | `"2025-03-25"` |
| `descricaoClasseCnj` | string | Classe CNJ | `"Procedimento Comum Cível"` |

---

## Formatos de Dados

### Requisição

#### Headers

```
Content-Type: application/json
Accept: application/json
User-Agent: SeuCliente/1.0
```

#### Body - Pesquisa Simples

```json
{
  "query": "dano moral",
  "pagina": 0,
  "tamanho": 20
}
```

#### Body - Pesquisa com Filtros

```json
{
  "query": "tutela de urgência",
  "pagina": 0,
  "tamanho": 10,
  "termosAcessorios": [
    {
      "campo": "nomeRelator",
      "valor": "CARMEN BITTENCOURT"
    },
    {
      "campo": "descricaoOrgaoJulgador",
      "valor": "8ª Turma Cível"
    }
  ]
}
```

### Resposta

#### Estrutura Principal

```json
{
  "hits": 1234,
  "pagina": 0,
  "registros": [...],
  "agregações": {...}
}
```

#### Campos da Resposta

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `hits` | int | Total de resultados encontrados |
| `pagina` | int | Página atual |
| `registros` | array | Array com as decisões |
| `agregações` | object | Agregações (facetas) para filtros |

#### Estrutura de `registros`

```json
{
  "uuid": "29df78c5-af48-48ee-b8f4-7db0bea4cff6",
  "identificador": "70016492",
  "sequencial": 1,
  "base": "decisoes",
  "subbase": "decisoes-monocraticas",
  "processo": "0710649-40.2025.8.07.0000",
  "nomeRelator": "CARMEN BITTENCOURT",
  "nomeRevisor": null,
  "descricaoOrgaoJulgador": "8ª Turma Cível",
  "dataPublicacao": "2025-03-25T03:00:00.000Z",
  "dataJulgamento": "2025-03-24T03:00:00.000Z",
  "ementa": "EMENTA: DIREITO DO CONSUMIDOR...",
  "inteiroTeor": "[Texto completo da decisão...]",
  "possuiInteiroTeor": true,
  "descricaoClasseCnj": "Procedimento Comum Cível",
  "codigoClasseCnj": 202
}
```

### Modelos

#### ResultadoBusca

```python
@dataclass
class ResultadoBusca:
    resultados: List[Dict[str, Any]]  # Lista de decisões
    total: int                        # Total encontrado
    pagina: int                       # Página atual
    por_pagina: int                   # Resultados por página
    agregacoes: Dict[str, Any]        # Facetas/agregações
    
    @property
    def total_paginas(self) -> int:
        """Retorna o total de páginas."""
        return (self.total + self.por_pagina - 1) // self.por_pagina
    
    @property
    def tem_proxima(self) -> bool:
        """Verifica se há próxima página."""
        return (self.pagina + 1) < self.total_paginas
```

#### Decisão

```python
@dataclass
class Decisao:
    uuid: str                    # ID único
    processo: str                # Número do processo
    ementa: str                  # Ementa da decisão
    inteiro_teor: str            # Texto completo (se disponível)
    nome_relator: str            # Nome do relator
    orgao_julgador: str          # Órgão julgador
    data_publicacao: str         # Data de publicação
    data_julgamento: str         # Data do julgamento
    classe_cnj: str              # Classe processual CNJ
    base: str                    # Base de dados
    possui_inteiro_teor: bool    # Se tem texto integral
```

---

## Exemplos de Uso

### Python

#### Instalação

```bash
pip install git+https://github.com/prof-ramos/tjdft-api-client.git
```

#### Uso Básico

```python
from tjdft import TJDFTClient

# Criar cliente
client = TJDFTClient()

# Pesquisa simples
resultados = client.pesquisar(query="dano moral", tamanho=10)

print(f"Total: {resultados.total}")
for r in resultados:
    print(f"Processo: {r['processo']}")
    print(f"Relator: {r['nome_relator']}")
    print(f"Ementa: {r['ementa'][:100]}...")
```

#### Pesquisa com Filtros

```python
from tjdft import TJDFTClient

client = TJDFTClient()

# Filtrar por relator e órgão
resultados = client.pesquisar(
    query="tutela de urgência",
    filtros={
        "nomeRelator": "CARMEN BITTENCOURT",
        "descricaoOrgaoJulgador": "8ª Turma Cível"
    },
    tamanho=20
)

print(f"Encontrados: {resultados.total}")
```

#### Paginação

```python
from tjdft import TJDFTClient

client = TJDFTClient()
todos_resultados = []

# Buscar todas as páginas
pagina = 0
while True:
    resultados = client.pesquisar(
        query="dano moral",
        pagina=pagina,
        tamanho=100
    )
    
    todos_resultados.extend(resultados.resultados)
    
    if not resultados.tem_proxima:
        break
    
    pagina += 1

print(f"Total coletado: {len(todos_resultados)}")
```

#### Usando Cliente Otimizado

```python
from tjdft import TJDFTClientOptimized

# Cliente com cache e rate limiting
client = TJDFTClientOptimized(
    cache_ttl=300,        # Cache por 5 minutos
    rate_limit=10.0,      # 10 req/s
    max_retries=3         # 3 tentativas
)

# Primeira chamada (cache miss)
r1 = client.pesquisar(query="dano moral")

# Segunda chamada (cache hit - instantâneo)
r2 = client.pesquisar(query="dano moral")

# Ver métricas
print(client.get_metrics())
# {'total_requests': 2, 'cache_hits': 1, 'avg_response_time_ms': 150.5}
```

#### Batch de Consultas

```python
from tjdft import TJDFTClientOptimized

client = TJDFTClientOptimized()

# Executar múltiplas consultas em paralelo
consultas = [
    {"query": "dano moral"},
    {"query": "habeas corpus"},
    {"query": "tutela de urgência"},
    {"query": "obrigação de fazer"},
]

resultados = client.pesquisar_lote(consultas, max_parallel=5)

for i, r in enumerate(resultados):
    print(f"{consultas[i]['query']}: {r.total} resultados")
```

### cURL

#### Pesquisa Simples

```bash
curl -X POST https://jurisdf.tjdft.jus.br/api/v1/pesquisa \
  -H "Content-Type: application/json" \
  -d '{
    "query": "dano moral",
    "pagina": 0,
    "tamanho": 10
  }'
```

#### Pesquisa com Filtros

```bash
curl -X POST https://jurisdf.tjdft.jus.br/api/v1/pesquisa \
  -H "Content-Type: application/json" \
  -d '{
    "query": "tutela de urgência",
    "pagina": 0,
    "tamanho": 20,
    "termosAcessorios": [
      {
        "campo": "nomeRelator",
        "valor": "CARMEN BITTENCOURT"
      },
      {
        "campo": "descricaoOrgaoJulgador",
        "valor": "8ª Turma Cível"
      }
    ]
  }'
```

#### Buscar por Número de Processo

```bash
curl -X POST https://jurisdf.tjdft.jus.br/api/v1/pesquisa \
  -H "Content-Type: application/json" \
  -d '{
    "query": "0710649-40.2025.8.07.0000",
    "pagina": 0,
    "tamanho": 1,
    "termosAcessorios": [
      {
        "campo": "processo",
        "valor": "0710649-40.2025.8.07.0000"
      }
    ]
  }'
```

### JavaScript

#### Fetch API

```javascript
// Pesquisa simples
async function pesquisar(query, pagina = 0, tamanho = 20) {
  const response = await fetch('https://jurisdf.tjdft.jus.br/api/v1/pesquisa', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      pagina: pagina,
      tamanho: tamanho
    })
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return response.json();
}

// Uso
pesquisar('dano moral', 0, 10)
  .then(data => {
    console.log(`Total: ${data.hits}`);
    data.registros.forEach(r => {
      console.log(`Processo: ${r.processo}`);
    });
  })
  .catch(console.error);
```

#### Com Filtros

```javascript
async function pesquisarComFiltros(query, filtros = {}) {
  const termosAcessorios = Object.entries(filtros).map(([campo, valor]) => ({
    campo,
    valor
  }));
  
  const response = await fetch('https://jurisdf.tjdft.jus.br/api/v1/pesquisa', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      pagina: 0,
      tamanho: 20,
      termosAcessorios
    })
  });
  
  return response.json();
}

// Uso
pesquisarComFiltros('tutela de urgência', {
  nomeRelator: 'CARMEN BITTENCOURT',
  descricaoOrgaoJulgador: '8ª Turma Cível'
}).then(console.log);
```

---

## Códigos de Status

### HTTP Status Codes

| Código | Descrição | Ação Recomendada |
|--------|-----------|------------------|
| `200` | Sucesso | Processar resposta normalmente |
| `400` | Bad Request | Verificar formato do JSON |
| `404` | Not Found | Verificar URL do endpoint |
| `429` | Too Many Requests | Implementar backoff e retry |
| `500` | Internal Server Error | Tentar novamente mais tarde |
| `502` | Bad Gateway | Servidor temporariamente indisponível |
| `503` | Service Unavailable | Aguardar e tentar novamente |
| `504` | Gateway Timeout | Reduzir tamanho da requisição |

### Tratamento de Erros em Python

```python
from tjdft import TJDFTClient
import requests

client = TJDFTClient()

try:
    resultados = client.pesquisar(query="dano moral")
except requests.exceptions.Timeout:
    print("Timeout: A API demorou muito para responder")
except requests.exceptions.ConnectionError:
    print("Erro de conexão: Verifique sua internet")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        print("Rate limit: Aguarde antes de fazer novas requisições")
    elif e.response.status_code >= 500:
        print(f"Erro no servidor: {e.response.status_code}")
    else:
        print(f"Erro HTTP: {e}")
except Exception as e:
    print(f"Erro inesperado: {e}")
```

---

## Limitações e Restrições

### Rate Limiting

⚠️ **A API não documenta oficialmente rate limits**, mas recomenda-se:

| Cenário | Recomendação |
|---------|--------------|
| Uso normal | Máximo 10 req/s |
| Coleta em massa | Máximo 5 req/s com pausas |
| Batch grande | Máximo 5 paralelo |

### Tamanho de Resposta

| Parâmetro | Limite |
|-----------|--------|
| `tamanho` | Máximo recomendado: 100 |
| Ementas | Sem limite documentado |
| Inteiro Teor | Alguns decisões têm, outras não |

### Disponibilidade

| Aspecto | Observação |
|---------|------------|
| Uptime | Alta disponibilidade (sem SLA oficial) |
| Horário | 24/7 (pode haver manutenções) |
| Histórico | Não todas decisões históricas disponíveis |

### Dados Ausentes

Alguns registros podem não ter:
- ❌ Inteiro teor (`possuiInteiroTeor: false`)
- ❌ Revisor (decisões monocráticas)
- ❌ Data de julgamento (apenas publicação)

### Busca Avançada

A API **não suporta** nativamente:
- ❌ Range de datas (apenas data específica)
- ❌ Operadores booleanos complexos (AND, OR, NOT)
- ❌ Busca por múltiplos processos
- ❌ Ordenação customizada

**Workaround**: Filtrar resultados no cliente após receber.

---

## Boas Práticas

### 1. Implemente Cache

```python
from tjdft import TJDFTClientOptimized

# Cache de 5 minutos
client = TJDFTClientOptimized(cache_ttl=300)

# Requisições repetidas usam cache
resultados = client.pesquisar(query="dano moral")  # API call
resultados = client.pesquisar(query="dano moral")  # Cache hit
```

### 2. Use Rate Limiting

```python
from tjdft import TJDFTClientOptimized

# Limitar a 5 requisições por segundo
client = TJDFTClientOptimized(rate_limit=5.0, rate_burst=10)
```

### 3. Trate Erros Gracefully

```python
from tjdft import TJDFTClientOptimized

client = TJDFTClientOptimized(max_retries=3)

try:
    resultados = client.pesquisar(query="termo")
except Exception as e:
    # Log do erro
    print(f"Erro: {e}")
    # Fallback ou retry manual
```

### 4. Paginação Eficiente

```python
from tjdft import TJDFTClient

client = TJDFTClient()

def buscar_todos(query, max_paginas=100):
    """Busca todas as páginas até limite."""
    todos = []
    
    for pagina in range(max_paginas):
        resultados = client.pesquisar(
            query=query,
            pagina=pagina,
            tamanho=100
        )
        
        todos.extend(resultados.resultados)
        
        if not resultados.tem_proxima:
            break
        
        # Pausa entre páginas
        time.sleep(0.5)
    
    return todos
```

### 5. Batch de Consultas

```python
from tjdft import TJDFTClientOptimized

client = TJDFTClientOptimized()

# Prefira batch em vez de loops sequenciais
consultas = [
    {"query": "dano moral"},
    {"query": "habeas corpus"},
]

resultados = client.pesquisar_lote(consultas, max_parallel=5)
```

### 6. Monitore Métricas

```python
client = TJDFTClientOptimized()

# ... fazer requisições ...

metrics = client.get_metrics()
print(f"Taxa de cache hits: {metrics['cache_hit_ratio']:.1%}")
print(f"Tempo médio: {metrics['avg_response_time_ms']:.1f}ms")
```

---

## FAQ

### Perguntas Frequentes

#### 1. A API é oficial?

✅ Sim, é a API oficial do TJDFT usada pelo site do tribunal para buscar jurisprudência.

#### 2. Preciso de autenticação?

❌ Não, a API é pública e não requer tokens ou credenciais.

#### 3. Qual o limite de requisições?

⚠️ Não há documentação oficial, mas recomenda-se máximo 10 req/s.

#### 4. Posso usar comercialmente?

⚖️ Os dados são públicos, mas verifique os termos de uso do TJDFT para uso comercial.

#### 5. Como buscar por período de datas?

A API não suporta range de datas nativamente. Use `dataPublicacao` com data específica ou filtre no cliente.

#### 6. Todas as decisões têm inteiro teor?

❌ Não. Verifique `possuiInteiroTeor` na resposta.

#### 7. Posso buscar processos de primeira instância?

✅ Sim, dependendo da `base` e `subbase` disponíveis.

#### 8. A API tem WebSocket/SSE?

❌ Não, apenas HTTP REST síncrono.

#### 9. Como contribuir com o cliente Python?

📦 Repo: https://github.com/prof-ramos/tjdft-api-client  
Abra uma issue ou pull request!

#### 10. A API retorna decisões de outros tribunais?

❌ Não, apenas do TJDFT. Para outros tribunais, use APIs específicas (DataJud, DadosJusBR).

---

## Recursos Adicionais

### Links Úteis

- 📚 [Repositório GitHub](https://github.com/prof-ramos/tjdft-api-client)
- 🌐 [Site Oficial TJDFT](https://www.tjdft.jus.br)
- 📖 [DataJud CNJ](https://datajud.cnj.jus.br)
- 📊 [DadosJusBR](https://dadosjusbr.org)

### Contato

Para dúvidas sobre a API oficial do TJDFT:
- Site: https://www.tjdft.jus.br
- Ouvidoria: Disponível no site oficial

Para questões sobre o cliente Python:
- GitHub Issues: https://github.com/prof-ramos/tjdft-api-client/issues

---

## Changelog

### v1.0.0 (2026-03-02)
- Documentação inicial
- Endpoint de pesquisa documentado
- Exemplos em Python, cURL, JavaScript
- Modelos de dados documentados
- Limitações e boas práticas

---

**Última atualização:** 2026-03-02  
**Versão da API:** v1  
**Versão do Documento:** 1.0.0
