# Exemplos de Uso

## Instalação

```bash
pip install tjdft-api-client
```

## Uso Básico

### 1. Busca Simples

```python
from tjdft import TJDFTClient

with TJDFTClient() as client:
    resultados = client.buscar_jurisprudencia(
        termo="habeas corpus"
    )
    
    for r in resultados:
        print(f"{r.numero}: {r.ementa[:100]}")
```

### 2. Busca com Filtros

```python
from tjdft import TJDFTClient
from datetime import date

with TJDFTClient() as client:
    resultados = client.buscar_jurisprudencia(
        termo="tráfico de drogas",
        tipo="acordao",
        data_inicial=date(2024, 1, 1),
        data_final=date(2024, 12, 31),
        orgao="1ª Turma Criminal"
    )
```

### 3. Busca por Número

```python
from tjdft import TJDFTClient

client = TJDFTClient()

# Buscar acórdão
acordao = client.buscar_acordao("2024HC123456")
if acordao:
    print(acordao.ementa)

# Buscar decisão
decisao = client.buscar_decisao("2024HC123456")
if decisao:
    print(decisao.ementa)
```

### 4. Paginação

```python
from tjdft import TJDFTClient

client = TJDFTClient()

# Primeira página
pagina1 = client.buscar_jurisprudencia(termo="direito penal", por_pagina=10)

print(f"Total: {pagina1.total}")
print(f"Páginas: {pagina1.total_paginas}")

# Próxima página
if pagina1.tem_proxima:
    pagina2 = client.buscar_jurisprudencia(
        termo="direito penal", 
        pagina=2,
        por_pagina=10
    )
```

### 5. Listar Órgãos Julgadores

```python
from tjdft import TJDFTClient

client = TJDFTClient()
orgaos = client.listar_orgaos_julgadores()

for orgao in orgaos:
    print(orgao)
```

## Integração com Outros Sistemas

### Com Streamlit

```python
import streamlit as st
from tjdft import TJDFTClient

st.title("Busca de Jurisprudência TJDFT")

termo = st.text_input("Termo de busca")

if st.button("Buscar") and termo:
    with st.spinner("Buscando..."):
        client = TJDFTClient()
        resultados = client.buscar_jurisprudencia(termo=termo)
        
        st.write(f"Total encontrado: {resultados.total}")
        
        for r in resultados:
            st.markdown(f"### {r.numero}")
            st.write(f"**Classe:** {r.classe}")
            st.write(f"**Relator:** {r.relator}")
            st.write(f"**Ementa:** {r.ementa}")
            st.divider()
```

### Com Discord Bot

```python
import discord
from discord.ext import commands
from tjdft import TJDFTClient

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

@bot.command()
async def jurisprudencia(ctx, *, termo: str):
    """Busca jurisprudência no TJDFT."""
    async with ctx.typing():
        client = TJDFTClient()
        resultados = client.buscar_jurisprudencia(termo=termo, por_pagina=5)
        
        if not resultados:
            await ctx.send("Nenhum resultado encontrado.")
            return
        
        for r in resultados[:3]:
            embed = discord.Embed(
                title=r.numero,
                description=r.ementa[:500],
                color=discord.Color.blue()
            )
            embed.add_field(name="Classe", value=r.classe)
            embed.add_field(name="Relator", value=r.relator)
            await ctx.send(embed=embed)

bot.run("YOUR_TOKEN")
```

## Tratamento de Erros

```python
from tjdft import TJDFTClient
import requests

client = TJDFTClient()

try:
    resultados = client.buscar_jurisprudencia(termo="teste")
except requests.HTTPError as e:
    print(f"Erro HTTP: {e}")
except requests.Timeout:
    print("Timeout na requisição")
except requests.ConnectionError:
    print("Erro de conexão")
except Exception as e:
    print(f"Erro inesperado: {e}")
```
