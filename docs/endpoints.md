# Endpoints da API TJDFT

> Documentação baseada em engenharia reversa. Última atualização: 2026-03-02

## Base URL

```
https://www.tjdft.jus.br
```

## Status da API

⚠️ **O TJDFT não possui uma API REST documentada para jurisprudência.**

O site utiliza **Plone CMS** e os endpoints descobertos são do sistema de busca padrão do Plone, não uma API estruturada de jurisprudência.

## Endpoints Descobertos

### 1. Busca Ajax (Plone)

```
GET /@@ajax-search
```

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `SearchableText` | string | Termo de busca |

**Exemplo:**
```bash
curl "https://www.tjdft.jus.br/@@ajax-search?SearchableText=habeas%20corpus"
```

**Resposta:**
```json
{
  "total": 2603,
  "items": [
    {
      "id": "3ad148d4c54944df80f7d51936085d93",
      "title": "Habeas data",
      "description": "",
      "url": "https://www.tjdft.jus.br/consultas/jurisprudencia/...",
      "state": "published"
    }
  ]
}
```

**Limitações:**
- Retorna páginas do site, não especificamente acórdãos
- Não há filtros por tipo de decisão
- Não há dados estruturados (ementa, relator, etc)

### 2. Busca do Site (Plone)

```
GET /@@search
```

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `SearchableText` | string | Termo de busca |
| `path` | string | Caminho para limitar busca |

**Resposta:** HTML (não JSON)

## Endpoints Testados (não funcionais)

| Endpoint | Status |
|----------|--------|
| `/api/v1/jurisprudencia` | 404 |
| `/api/jurisprudencia` | 404 |
| `/api/acordaos` | 404 |
| `/ws/jurisprudencia` | 404 |
| `/rest/jurisprudencia` | 404 |

## Sistema do TJDFT

O site do TJDFT é construído sobre **Plone CMS**:

- Busca padrão: `@@search`
- API ajax: `@@ajax-search`
- Não há API REST nativa para jurisprudência

## Alternativas

### 1. Web Scraping
- Página de jurisprudência: `https://www.tjdft.jus.br/consultas/jurisprudencia/jurisprudencia`
- Requer parsing de HTML
- Risco de mudanças no layout

### 2. Contato Oficial
- Solicitar documentação via ouvidoria
- URL: https://www.tjdft.jus.br/ouvidoria

### 3. DadosJusBR
- API alternativa com dados do judiciário
- URL: https://api.dadosjusbr.org/v1/orgao/tjdft
- Dados de remuneração, não jurisprudência

## Próximos Passos

1. **Análise com DevTools** - Interceptar requisições ao fazer busca
2. **Contato oficial** - Solicitar API documentada
3. **Web scraping** - Como alternativa temporária

## Resultados dos Testes E2E

```
Teste                    Status
─────────────────────────────────
ajax_search              ✅ PASSOU
site_search              ✅ PASSOU
jurisprudencia_page      ✅ PASSOU
common_endpoints         ❌ FALHOU

Total: 3/4 testes passaram
```
