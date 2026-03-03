# Exemplos Práticos - API TJDFT

> Casos de uso comuns para advogados, juristas e desenvolvedores

---

## 📋 Sumário

1. [Busca de Precedentes](#1-busca-de-precedentes)
2. [Análise de Magistrados](#2-análise-de-magistrados)
3. [Monitoramento de Processos](#3-monitoramento-de-processos)
4. [Pesquisa por Matéria](#4-pesquisa-por-matéria)
5. [Exportação de Dados](#5-exportação-de-dados)
6. [Integração com IA](#6-integração-com-ia)

---

## 1. Busca de Precedentes

### Cenário: Encontrar precedentes sobre dano moral em atraso de voo

```python
from tjdft import TJDFTClientOptimized

client = TJDFTClientOptimized(cache_ttl=600)

# Buscar precedentes
resultados = client.pesquisar(
    query="dano moral atraso voo",
    tamanho=20
)

print(f"Total de precedentes: {resultados.total}\n")

# Filtrar apenas decisões favoráveis
favoraveis = []
for r in resultados:
    ementa = r.get("ementa", "").lower()
    
    # Verificar se é deferimento
    if any(p in ementa for p in ["deferido", "procedente", "condeno", "indenização"]):
        favoraveis.append({
            "processo": r["processo"],
            "relator": r["nome_relator"],
            "orgao": r["orgao_julgador"],
            "ementa": r["ementa"][:200] + "...",
            "data": r["data_publicacao"]
        })

print(f"Decisões favoráveis: {len(favoraveis)}\n")

for i, d in enumerate(favoraveis[:5], 1):
    print(f"{i}. {d['processo']}")
    print(f"   Relator: {d['relator']}")
    print(f"   Data: {d['data']}")
    print(f"   Ementa: {d['ementa']}\n")
```

### Saída Esperada

```
Total de precedentes: 234

Decisões favoráveis: 156

1. 0701234-56.2024.8.07.0000
   Relator: CARMEN BITTENCOURT
   Data: 2024-06-15
   Ementa: EMENTA: DIREITO DO CONSUMIDOR. DANO MORAL. ATRASO DE VOO. 
   RESPONSABILIDADE OBJETIVA DA COMPANHIA AÉREA. DEVER DE INDENIZAR...

2. 0712345-67.2024.8.07.0001
   Relator: JOÃO EGMONT
   Data: 2024-07-20
   Ementa: EMENTA: INDENIZAÇÃO POR DANOS MORAIS. ATRASO DE VOO INTERNACIONAL...
```

---

## 2. Análise de Magistrados

### Cenário: Analisar perfil decisório de um desembargador

```python
from tjdft import TJDFTClientOptimized
from tjdft.analise import AnaliseMagistrados

client = TJDFTClientOptimized()
analise = AnaliseMagistrados()

# Buscar decisões do magistrado
resultados = client.pesquisar_por_relator(
    query="dano moral",  # ou query vazia para todas
    relator="CARMEN BITTENCOURT",
    tamanho=100
)

# Analisar perfil
perfil = analise.analisar(resultados.resultados)

print(f"Análise do(a) Desembargador(a): {perfil.nome}")
print(f"Total de decisões analisadas: {perfil.total_decisoes}")
print(f"\nDeferimentos: {perfil.deferimentos} ({perfil.percentual_deferimento:.1%})")
print(f"Indeferimentos: {perfil.indeferimentos} ({perfil.percentual_indeferimento:.1%})")
print(f"\nPrincipais matérias:")
for materia, qtd in perfil.materias_frequentes[:5]:
    print(f"  - {materia}: {qtd}")

print(f"\nValor médio de indenização: R$ {perfil.valor_medio_indenizacao:,.2f}")
```

### Saída Esperada

```
Análise do(a) Desembargador(a): CARMEN BITTENCOURT
Total de decisões analisadas: 87

Deferimentos: 52 (59.8%)
Indeferimentos: 35 (40.2%)

Principais matérias:
  - Direito do Consumidor: 34
  - Responsabilidade Civil: 28
  - Contratos: 15
  - Direito Bancário: 10

Valor médio de indenização: R$ 8.500,00
```

---

## 3. Monitoramento de Processos

### Cenário: Monitorar movimentações de uma lista de processos

```python
from tjdft import TJDFTClientOptimized
import json
from datetime import datetime

client = TJDFTClientOptimized()

# Lista de processos para monitorar
processos_interesse = [
    "0710649-40.2025.8.07.0000",
    "0712345-67.2024.8.07.0001",
    "0723456-78.2024.8.07.0002",
]

def monitorar_processos(processos):
    """Verifica processos e retorna novidades."""
    novidades = []
    
    for processo in processos:
        # Buscar processo
        decisao = client.buscar_por_processo(processo)
        
        if decisao:
            novidades.append({
                "processo": processo,
                "encontrado": True,
                "data_publicacao": decisao.get("data_publicacao"),
                "ementa": decisao.get("ementa", "")[:100],
            })
        else:
            novidades.append({
                "processo": processo,
                "encontrado": False,
            })
    
    return novidades

# Executar monitoramento
resultado = monitorar_processos(processos_interesse)

# Gerar relatório
print(f"Monitoramento - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
print("="*60)

for r in resultado:
    if r["encontrado"]:
        print(f"✅ {r['processo']}")
        print(f"   Publicado: {r['data_publicacao']}")
        print(f"   Ementa: {r['ementa']}...\n")
    else:
        print(f"❌ {r['processo']} - Não encontrado\n")

# Salvar em arquivo
with open("monitoramento.json", "w") as f:
    json.dump(resultado, f, indent=2, ensure_ascii=False)

print("\n✅ Relatório salvo em monitoramento.json")
```

### Saída Esperada

```
Monitoramento - 02/03/2026 21:45

============================================================
✅ 0710649-40.2025.8.07.0000
   Publicado: 2025-03-25
   Ementa: EMENTA: DIREITO ADMINISTRATIVO. MANDADO DE SEGURANÇA. 
   RENOVAÇÃO DE CNH. ATRASO INJUSTIFICADO DO DETRAN...

✅ 0712345-67.2024.8.07.0001
   Publicado: 2024-12-10
   Ementa: EMENTA: APELAÇÃO CÍVEL. INDENIZAÇÃO POR DANOS MORAIS...

❌ 0723456-78.2024.8.07.0002 - Não encontrado

✅ Relatório salvo em monitoramento.json
```

---

## 4. Pesquisa por Matéria

### Cenário: Pesquisar todas as decisões sobre um tema específico

```python
from tjdft import TJDFTClientOptimized
import time

client = TJDFTClientOptimized(rate_limit=5.0)

def buscar_tema(tema, max_resultados=500):
    """Busca todas as decisões sobre um tema."""
    todos = []
    pagina = 0
    tamanho = 100
    
    while len(todos) < max_resultados:
        print(f"Buscando página {pagina}...")
        
        resultados = client.pesquisar(
            query=tema,
            pagina=pagina,
            tamanho=tamanho
        )
        
        if not resultados.resultados:
            break
        
        todos.extend(resultados.resultados)
        
        print(f"  Encontrados: {len(resultados.resultados)}")
        print(f"  Total acumulado: {len(todos)}/{resultados.total}")
        
        if not resultados.tem_proxima:
            break
        
        pagina += 1
        time.sleep(0.5)  # Pausa entre páginas
    
    return todos[:max_resultados]

# Buscar decisões sobre "tutela de urgência"
decisoes = buscar_tema("tutela de urgência CNH", max_resultados=200)

print(f"\n{'='*60}")
print(f"Total coletado: {len(decisoes)} decisões")

# Estatísticas
orgaos = {}
relatores = {}

for d in decisoes:
    orgao = d.get("orgao_julgador", "N/A")
    relator = d.get("nome_relator", "N/A")
    
    orgaos[orgao] = orgaos.get(orgao, 0) + 1
    relatores[relator] = relatores.get(relator, 0) + 1

print(f"\nTop 5 Órgãos Julgadores:")
for orgao, qtd in sorted(orgaos.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {orgao}: {qtd}")

print(f"\nTop 5 Relatores:")
for relator, qtd in sorted(relatores.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {relator}: {qtd}")
```

### Saída Esperada

```
Buscando página 0...
  Encontrados: 100
  Total acumulado: 100/1451
Buscando página 1...
  Encontrados: 100
  Total acumulado: 200/1451

============================================================
Total coletado: 200 decisões

Top 5 Órgãos Julgadores:
  8ª Turma Cível: 45
  5ª Turma Cível: 38
  3ª Turma Cível: 32
  1ª Turma Cível: 28
  6ª Turma Cível: 22

Top 5 Relatores:
  CARMEN BITTENCOURT: 34
  JOÃO EGMONT: 28
  LEONARDO ALVES: 25
  MARIA SOUZA: 22
  PEDRO SILVA: 19
```

---

## 5. Exportação de Dados

### Cenário: Exportar decisões para CSV e JSON

```python
from tjdft import TJDFTClientOptimized
import csv
import json
from datetime import datetime

client = TJDFTClientOptimized()

# Buscar decisões
resultados = client.pesquisar(query="dano moral banco", tamanho=50)

# Preparar dados
dados = []
for r in resultados:
    dados.append({
        "processo": r.get("processo", ""),
        "relator": r.get("nome_relator", ""),
        "orgao": r.get("orgao_julgador", ""),
        "data_publicacao": r.get("data_publicacao", ""),
        "classe": r.get("classe_cnj", ""),
        "ementa": r.get("ementa", "").replace("\n", " ")[:500],
        "tem_inteiro_teor": r.get("possui_inteiro_teor", False),
    })

# Exportar para CSV
csv_file = "jurisprudencias.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    if dados:
        writer = csv.DictWriter(f, fieldnames=dados[0].keys())
        writer.writeheader()
        writer.writerows(dados)

print(f"✅ CSV exportado: {csv_file}")

# Exportar para JSON
json_file = "jurisprudencias.json"
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(dados, f, indent=2, ensure_ascii=False)

print(f"✅ JSON exportado: {json_file}")

# Exportar para Markdown
md_file = "jurisprudencias.md"
with open(md_file, "w", encoding="utf-8") as f:
    f.write(f"# Jurisprudências - Dano Moral (Banco)\n\n")
    f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
    f.write(f"Total: {len(dados)} decisões\n\n")
    f.write("---\n\n")
    
    for i, d in enumerate(dados, 1):
        f.write(f"## {i}. {d['processo']}\n\n")
        f.write(f"- **Relator:** {d['relator']}\n")
        f.write(f"- **Órgão:** {d['orgao']}\n")
        f.write(f"- **Data:** {d['data_publicacao']}\n")
        f.write(f"- **Classe:** {d['classe']}\n\n")
        f.write(f"**Ementa:**\n\n{d['ementa']}\n\n")
        f.write("---\n\n")

print(f"✅ Markdown exportado: {md_file}")
```

### Saída Esperada

```
✅ CSV exportado: jurisprudencias.csv
✅ JSON exportado: jurisprudencias.json
✅ Markdown exportado: jurisprudencias.md
```

---

## 6. Integração com IA

### Cenário: Usar GPT para analisar jurisprudência

```python
from tjdft import TJDFTClientOptimized, TokenCounter
import os
from openai import OpenAI

# Configurar
client_tjdft = TJDFTClientOptimized()
client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
counter = TokenCounter(model="gpt-4o-mini")

# Buscar jurisprudência
resultados = client_tjdft.pesquisar(query="dano moral atraso voo", tamanho=5)

# Preparar contexto
contexto = "ANALISE AS SEGUINTES DECISÕES:\n\n"
for i, r in enumerate(resultados, 1):
    ementa = r.get("ementa", "")
    contexto += f"DECISÃO {i}:\n{ementa}\n\n{'='*60}\n\n"

# Contar tokens
token_count = counter.count(contexto)
print(f"Contexto: {token_count.tokens} tokens")

# Estimar custo
cost = counter.estimate_cost(
    input_tokens=token_count.tokens,
    output_tokens=1000,
    model="gpt-4o-mini"
)
print(f"Custo estimado: ${cost['total_cost_usd']:.4f}")

# Truncar se necessário
if token_count.tokens > 100000:
    contexto = counter.truncate_to_tokens(contexto, 100000)
    print("Contexto truncado para 100k tokens")

# Analisar com GPT
prompt = f"""
Você é um especialista em direito do consumidor e jurisprudência.

{contexto}

Por favor, responda:

1. Qual é a tese principal dessas decisões?
2. Quais argumentos são mais recorrentes?
3. Qual o valor médio de indenização deferido?
4. Há alguma tendência ou padrão identificável?
5. Quais são os requisitos para deferimento?

Responda de forma estruturada e objetiva.
"""

response = client_openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Você é um especialista jurídico."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    max_tokens=1500
)

analise = response.choices[0].message.content

print("\n" + "="*60)
print("ANÁLISE DA IA:")
print("="*60)
print(analise)

# Salvar análise
with open("analise_ia.md", "w", encoding="utf-8") as f:
    f.write(f"# Análise de Jurisprudência\n\n")
    f.write(f"**Tema:** Dano moral - Atraso de voo\n\n")
    f.write(f"**Data:** {datetime.now().strftime('%d/%m/%Y')}\n\n")
    f.write(f"## Análise\n\n{analise}\n")

print("\n✅ Análise salva em analise_ia.md")
```

### Saída Esperada

```
Contexto: 2847 tokens
Custo estimado: $0.0023

============================================================
ANÁLISE DA IA:
============================================================

## 1. Tese Principal

As decisões analisadas estabelecem que as companhias aéreas têm 
responsabilidade objetiva pelos danos morais causados por atrasos 
de voo, conforme o art. 14 do CDC...

## 2. Argumentos Recorrentes

- Violação do dever de informação
- Ausência de assistência material
- Dano in re ipsa (não precisa provar prejuízo)
...

✅ Análise salva em analise_ia.md
```

---

## Exemplos Avançados

### Análise Comparativa de Turmas

```python
from tjdft import TJDFTClientOptimized

client = TJDFTClientOptimized()

turmas = [
    "3ª Turma Cível",
    "5ª Turma Cível",
    "8ª Turma Cível"
]

estatisticas = {}

for turma in turmas:
    resultados = client.pesquisar_por_orgao(
        query="dano moral",
        orgao=turma,
        tamanho=100
    )
    
    deferimentos = 0
    for r in resultados:
        ementa = r.get("ementa", "").lower()
        if any(p in ementa for p in ["deferido", "procedente", "condeno"]):
            deferimentos += 1
    
    estatisticas[turma] = {
        "total": len(resultados),
        "deferimentos": deferimentos,
        "taxa": deferimentos / len(resultados) if resultados else 0
    }

print("COMPARATIVO DE TURMAS - DANO MORAL\n")
print(f"{'Turma':<20} {'Total':>10} {'Deferiu':>10} {'Taxa':>10}")
print("-" * 50)

for turma, stats in estatisticas.items():
    print(f"{turma:<20} {stats['total']:>10} {stats['deferimentos']:>10} {stats['taxa']:>10.1%}")
```

### Monitoramento Contínuo com Cron

```python
# Script para executar diariamente via cron

from tjdft import TJDFTClientOptimized
import json
from datetime import datetime, timedelta

def verificar_novas_decisoes():
    """Verifica decisões dos últimos 7 dias."""
    client = TJDFTClientOptimized()
    
    # Carregar estado anterior
    try:
        with open("estado.json", "r") as f:
            estado = json.load(f)
    except FileNotFoundError:
        estado = {"processos_conhecidos": []}
    
    # Buscar decisões recentes
    resultados = client.pesquisar(
        query="dano moral",
        tamanho=50
    )
    
    novos = []
    for r in resultados:
        processo = r.get("processo")
        if processo not in estado["processos_conhecidos"]:
            novos.append(r)
            estado["processos_conhecidos"].append(processo)
    
    # Salvar estado
    with open("estado.json", "w") as f:
        json.dump(estado, f)
    
    # Notificar se houver novos
    if novos:
        print(f"🔔 {len(novos)} novas decisões encontradas!")
        for n in novos[:5]:
            print(f"  - {n['processo']}: {n['data_publicacao']}")
    else:
        print("Nenhuma decisão nova.")
    
    return novos

if __name__ == "__main__":
    verificar_novas_decisoes()
```

---

## Scripts de Linha de Comando

### CLI para Busca Rápida

```python
#!/usr/bin/env python3
"""
CLI para buscar jurisprudência rapidamente.

Uso:
    python buscar.py "dano moral" --relator "CARMEN" --tamanho 10
"""

import argparse
from tjdft import TJDFTClientOptimized

def main():
    parser = argparse.ArgumentParser(description="Buscar jurisprudência TJDFT")
    parser.add_argument("query", help="Termo de busca")
    parser.add_argument("--relator", help="Filtrar por relator")
    parser.add_argument("--orgao", help="Filtrar por órgão julgador")
    parser.add_argument("--tamanho", type=int, default=10, help="Resultados por página")
    
    args = parser.parse_args()
    
    client = TJDFTClientOptimized()
    
    filtros = {}
    if args.relator:
        filtros["nomeRelator"] = args.relator
    if args.orgao:
        filtros["descricaoOrgaoJulgador"] = args.orgao
    
    resultados = client.pesquisar(
        query=args.query,
        filtros=filtros if filtros else None,
        tamanho=args.tamanho
    )
    
    print(f"\nTotal: {resultados.total} resultados\n")
    
    for i, r in enumerate(resultados, 1):
        print(f"{i}. {r['processo']}")
        print(f"   Relator: {r['nome_relator']}")
        print(f"   Órgão: {r['orgao_julgador']}")
        print(f"   Data: {r['data_publicacao']}")
        print(f"   Ementa: {r['ementa'][:100]}...\n")

if __name__ == "__main__":
    main()
```

---

**Dica:** Salve estes exemplos em arquivos `.py` e execute conforme necessário!
