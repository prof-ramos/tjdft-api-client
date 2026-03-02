# Endpoints da API TJDFT

> **API Oficial descoberta!** Atualizado em: 2026-03-02

## Base URL

```
https://jurisdf.tjdft.jus.br/api/v1
```

## Endpoint Principal

### Pesquisa de Jurisprudência

```
POST /pesquisa
```

**URL completa:** `https://jurisdf.tjdft.jus.br/api/v1/pesquisa`

**Formato:** JSON (body)

**Parâmetros obrigatórios:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `query` | string | Termo principal da pesquisa |
| `pagina` | int | Número da página (começa em 0) |
| `tamanho` | int | Resultados por página |

**Parâmetro opcional:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `termosAcessorios` | array | Lista de filtros adicionais |

### Filtros Disponíveis (termosAcessorios)

| Campo | Descrição |
|-------|-----------|
| `base` | Base de dados da decisão |
| `subbase` | Subbase de dados |
| `origem` | Origem da decisão |
| `uuid` | Identificador UUID da decisão |
| `identificador` | Identificador da decisão |
| `processo` | Número do processo |
| `nomeRelator` | Nome do relator |
| `nomeRevisor` | Nome do revisor |
| `nomeRelatorDesignado` | Nome do relator designado |
| `descricaoOrgaoJulgador` | Nome do órgão julgador |
| `dataJulgamento` | Data do julgamento (YYYY-MM-DD) |
| `dataPublicacao` | Data da publicação (YYYY-MM-DD) |
| `descricaoClasseCnj` | Classe processual CNJ |

## Exemplo de Requisição

```bash
curl -X POST https://jurisdf.tjdft.jus.br/api/v1/pesquisa \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Dano moral",
    "termosAcessorios": [
      {
        "campo": "nomeRelator",
        "valor": "CARMEN BITTENCOURT"
      }
    ],
    "pagina": 0,
    "tamanho": 10
  }'
```

## Exemplo de Resposta

```json
{
  "hits": 1234,
  "agregações": {},
  "paginação": {},
  "registros": [
    {
      "sequencial": 1,
      "base": "decisoes",
      "subbase": "decisoes-monocraticas",
      "uuid": "29df78c5-af48-48ee-b8f4-7db0bea4cff6",
      "identificador": "70016492",
      "dataPublicacao": "2025-03-25T03:00:00.000Z",
      "ementa": "[texto da ementa]",
      "processo": "0710649-40.2025.8.07.0000",
      "nomeRelator": "CARMEN BITTENCOURT",
      "descricaoOrgaoJulgador": "8ª Turma Cível",
      "codigoClasseCnj": 202,
      "inteiroTeor": "[texto integral]",
      "possuiInteiroTeor": false
    }
  ]
}
```

## Campos da Resposta

| Campo | Descrição |
|-------|-----------|
| `hits` | Total de decisões encontradas |
| `agregações` | Lista de relatores, revisores e órgãos |
| `registros` | Array com as decisões |
| `ementa` | Ementa da decisão |
| `inteiroTeor` | Texto integral (se disponível) |
| `processo` | Número do processo |
| `nomeRelator` | Nome do relator |
| `descricaoOrgaoJulgador` | Órgão julgador |

---

## Endpoints Legados (Plone CMS)

### Busca Ajax

```
GET /@@ajax-search?SearchableText=termo
```

**Nota:** Este é o endpoint de busca geral do site, não específico para jurisprudência.

---

## Testes E2E

```
Teste                    Status
─────────────────────────────────
ajax_search              ✅ PASSOU
site_search              ✅ PASSOU
jurisprudencia_page      ✅ PASSOU
common_endpoints         ❌ FALHOU

Total: 3/4 testes passaram
```
