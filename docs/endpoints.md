# Endpoints da API TJDFT

> Documentação em construção. Endpoints sendo descobertos via engenharia reversa.

## Base URL

```
https://www.tjdft.jus.br
```

## Endpoints Conhecidos

### 1. Consulta de Jurisprudência

```
GET /jurisprudencia/busca
```

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `termo` | string | Termo de busca |
| `tipo` | string | Tipo de decisão (acordao, decisao, sentença) |
| `data_inicial` | date | Data inicial (DD/MM/YYYY) |
| `data_final` | date | Data final (DD/MM/YYYY) |
| `orgao` | string | Órgão julgador |
| `relator` | string | Nome do relator |

### 2. Consulta de Acórdãos

```
GET /jurisprudencia/acordaos
```

### 3. Consulta de Decisões

```
GET /jurisprudencia/decisoes
```

### 4. Diário da Justiça Eletrônico

```
GET /diario-da-justica-eletronico
```

## Formato de Resposta

```json
{
  "resultados": [
    {
      "numero": "2024XXX123456",
      "classe": "Habeas Corpus",
      "assunto": "Direito Penal",
      "relator": "Des. Fulano de Tal",
      "orgao_julgador": "2ª Turma Criminal",
      "data_julgamento": "2024-01-15",
      "data_publicacao": "2024-01-20",
      "ementa": "Ementa da decisão...",
      "inteiro_teor_url": "/jurisprudencia/2024XXX123456/inteiro-teor"
    }
  ],
  "total": 100,
  "pagina": 1,
  "por_pagina": 20
}
```

## Observações

1. A API pode requerer rate limiting
2. Alguns endpoints podem requerer autenticação
3. Formato de datas pode variar
4. Respostas podem ser paginadas

## Descoberta de Endpoints

Para descobrir novos endpoints, usar:

```bash
# Verificar headers
curl -I https://www.tjdft.jus.br/jurisprudencia

# Testar endpoints comuns
curl https://www.tjdft.jus.br/api/v1/jurisprudencia
curl https://www.tjdft.jus.br/api/jurisprudencia
curl https://www.tjdft.jus.br/api/acordaos
```

## Próximos Passos

- [ ] Confirmar endpoints funcionais
- [ ] Documentar autenticação (se necessária)
- [ ] Mapear todos os parâmetros
- [ ] Criar testes automatizados
