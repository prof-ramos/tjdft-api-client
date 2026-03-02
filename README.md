# TJDFT API Client

Cliente Python para a API de Jurisprudência do Tribunal de Justiça do Distrito Federal e dos Territórios.

## Status

✅ **API Oficial Funcionando!**

## Sobre

A API do TJDFT permite consulta pública a:
- Acórdãos
- Decisões monocráticas
- Ementas
- Inteiro teor

**Endpoint Oficial:** `https://jurisdf.tjdft.jus.br/api/v1/pesquisa`

## Instalação

```bash
pip install tjdft-api-client
```

Ou desenvolvimento:

```bash
git clone https://github.com/prof-ramos/tjdft-api-client.git
cd tjdft-api-client
pip install -e ".[dev]"
```

## Uso Rápido

```python
from tjdft import TJDFTClient

client = TJDFTClient()

# Busca simples
resultados = client.pesquisar(query="dano moral")
print(f"Total: {resultados.total}")

for r in resultados:
    print(f"{r['processo']} - {r['nome_relator']}")

# Com filtros
resultados = client.pesquisar(
    query="habeas corpus",
    filtros={"nomeRelator": "CARMEN BITTENCOURT"}
)
```

## Filtros Disponíveis

| Campo | Descrição |
|-------|-----------|
| `nomeRelator` | Nome do relator |
| `descricaoOrgaoJulgador` | Órgão julgador |
| `dataPublicacao` | Data da publicação (YYYY-MM-DD) |
| `dataJulgamento` | Data do julgamento (YYYY-MM-DD) |
| `processo` | Número do processo |
| `descricaoClasseCnj` | Classe processual CNJ |

## Documentação

- [Endpoints da API](docs/endpoints.md)
- [Exemplos de uso](docs/examples.md)

## Testes

```bash
# Unit tests
pytest tests/

# E2E tests (requer conexão)
python tests/test_e2e_oficial.py
```

## Resultados dos Testes E2E

```
Teste                    Status
─────────────────────────────────
api_basica                ✅ PASSOU
api_com_filtro            ✅ PASSOU
paginacao                 ✅ PASSOU
campos_disponiveis        ✅ PASSOU
cliente_python            ✅ PASSOU

Total: 5/5 testes passaram
```

## Fontes Oficiais

- Portal TJDFT: https://www.tjdft.jus.br/
- Jurisprudência: https://www.tjdft.jus.br/consultas/jurisprudencia/jurisprudencia
- API: https://jurisdf.tjdft.jus.br/api/v1/pesquisa

## Licença

MIT License

## Contribuindo

Contribuições são bem-vindas! Especialmente:
- Casos de uso adicionais
- Melhorias na documentação
- Exemplos de integração
- Testes adicionais
