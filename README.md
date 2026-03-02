# TJDFT API Client

Cliente Python para a API de Jurisprudência do Tribunal de Justiça do Distrito Federal e dos Territórios.

## Status

> ⚠️ **Em desenvolvimento** - Este projeto está em fase de pesquisa e documentação dos endpoints.

## Sobre

A API do TJDFT permite consulta pública a:
- Acórdãos
- Decisões monocráticas
- Ementas
- Jurisprudência consolidada

## Estrutura

```
tjdft-api-client/
├── README.md           # Este arquivo
├── docs/               # Documentação da API
│   ├── endpoints.md    # Endpoints descobertos
│   └── examples.md     # Exemplos de uso
├── src/                # Código fonte
│   ├── client.py       # Cliente Python
│   └── models.py       # Modelos de dados
├── examples/           # Exemplos práticos
│   └── busca_jurisprudencia.py
└── tests/              # Testes
```

## Instalação

```bash
pip install tjdft-api-client
```

Ou desenvolvimento:

```bash
git clone https://github.com/prof-ramos/tjdft-api-client.git
cd tjdft-api-client
pip install -e .
```

## Uso Rápido

```python
from tjdft import TJDFTClient

client = TJDFTClient()

# Buscar jurisprudência
resultados = client.buscar_jurisprudencia(
    termo="habeas corpus",
    limite=10
)

for r in resultados:
    print(f"{r.numero} - {r.ementa[:100]}...")
```

## Documentação

- [Endpoints descobertos](docs/endpoints.md)
- [Exemplos de uso](docs/examples.md)

## Fontes Oficiais

- Portal TJDFT: https://www.tjdft.jus.br/
- Jurisprudência: https://www.tjdft.jus.br/jurisprudencia
- Diário da Justiça Eletrônico: https://www.tjdft.jus.br/diario-da-justica-eletronico

## Licença

MIT License

## Contribuindo

Contribuições são bem-vindas! Especialmente:
- Descoberta de novos endpoints
- Correções de documentação
- Exemplos de uso
- Testes
