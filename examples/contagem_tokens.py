#!/usr/bin/env python3
"""
Exemplo de contagem de tokens para análise de jurisprudência.

Demonstra como:
- Contar tokens de ementas
- Estimar custos de API OpenAI
- Truncar textos para limite de contexto
- Dividir textos longos em chunks
"""

import sys
sys.path.insert(0, "../src")

from tjdft import TJDFTClient, TokenCounter, estimate_openai_cost


def exemplo_contagem_basica():
    """Exemplo básico de contagem de tokens."""
    print("=" * 70)
    print("EXEMPLO: Contagem Básica de Tokens")
    print("=" * 70)
    
    counter = TokenCounter(model="gpt-4o-mini")
    
    textos = [
        "Olá, mundo!",
        "A tutela de urgência é um instituto processual que visa garantir a efetividade do processo.",
        "O Superior Tribunal de Justiça firmou entendimento no sentido de que o dano moral decorrente de atraso de voo é passível de indenização.",
    ]
    
    print("\nModelo: gpt-4o-mini")
    print(f"Encoding: {counter.encoding_name}\n")
    
    for texto in textos:
        count = counter.count(texto)
        print(f"'{texto[:50]}...'")
        print(f"  Tokens: {count.tokens}")
        print(f"  Chars: {count.chars}")
        print(f"  Chars/token: {count.chars_per_token:.1f}\n")


def exemplo_jurisprudencia():
    """Exemplo com jurisprudência real."""
    print("=" * 70)
    print("EXEMPLO: Tokens em Jurisprudência")
    print("=" * 70)
    
    client = TJDFTClient()
    counter = TokenCounter(model="gpt-4o-mini")
    
    # Buscar jurisprudência
    print("\n🔍 Buscando jurisprudência...")
    resultados = client.pesquisar(query="dano moral", tamanho=5)
    
    print(f"\n{len(resultados)} resultados encontrados\n")
    
    total_tokens = 0
    
    for i, r in enumerate(resultados, 1):
        ementa = r.get("ementa", "")
        if ementa:
            count = counter.count(ementa)
            total_tokens += count.tokens
            
            print(f"{i}. Processo: {r.get('processo', 'N/A')}")
            print(f"   Tokens: {count.tokens}")
            print(f"   Ementa: {ementa[:80]}...\n")
    
    print(f"📊 Total tokens: {total_tokens}")
    print(f"   Média por ementa: {total_tokens/len(resultados):.1f}")


def exemplo_estimativa_custo():
    """Exemplo de estimativa de custo OpenAI."""
    print("=" * 70)
    print("EXEMPLO: Estimativa de Custo OpenAI")
    print("=" * 70)
    
    counter = TokenCounter(model="gpt-4o-mini")
    
    # Prompt típico de análise jurídica
    prompt = """
Você é um assistente jurídico especialista em direito do consumidor.

Analise a seguinte ementa e identifique:
1. Teses principais
2. Fundamentos jurídicos
3. Relator e órgão julgador
4. Decisão final

Ementa:
TRIBUTÁRIO. ICMS. BASE DE CÁLCULO. VALOR DA OPERAÇÃO. DECRETO-LEI 406/68. 
COMPREENSÃO DO PREÇO FINAL AO CONSUMIDOR. FRETE E SEGURO. 
INCLUSÃO NA BASE DE CÁLCULO DO ICMS. RECURSO IMPROVIDO.

1. O ICMS incide sobre o valor da operação, que corresponde ao preço final 
pago pelo consumidor, incluindo todos os custos incidentes até a entrega 
do produto ao destinatário.
"""
    
    # Contar tokens do prompt
    prompt_count = counter.count(prompt)
    
    print(f"\nPrompt:")
    print(f"  Tokens: {prompt_count.tokens}")
    print(f"  Chars: {prompt_count.chars}")
    
    # Estimar custos para diferentes modelos
    print("\n💰 Estimativa de Custo (para 100 requisições):\n")
    
    modelos = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"]
    
    for modelo in modelos:
        # Estimar: prompt + 1000 tokens de resposta
        counter_model = TokenCounter(model=modelo)
        prompt_tokens = counter_model.count(prompt).tokens
        
        custo = counter_model.estimate_cost(
            input_tokens=prompt_tokens,
            output_tokens=1000  # Resposta estimada
        )
        
        custo_100 = custo["total_cost_usd"] * 100
        
        print(f"  {modelo}:")
        print(f"    Input: {custo['input_cost_usd']*100:.4f} USD")
        print(f"    Output: {custo['output_cost_usd']*100:.4f} USD")
        print(f"    Total (100 req): ${custo_100:.2f} USD\n")


def exemplo_truncagem():
    """Exemplo de truncagem para limite de contexto."""
    print("=" * 70)
    print("EXEMPLO: Truncagem para Limite de Contexto")
    print("=" * 70)
    
    counter = TokenCounter()
    
    # Texto longo
    texto = """
EMENTA: APELAÇÃO CÍVEL. AÇÃO DE INDENIZAÇÃO POR DANOS MORAIS E MATERIAIS. 
ACIDENTE DE TRÂNSITO. COLISÃO TRASEIRA. PRELIMINAR DE ILEGITIMIDADE PASSIVA 
AD CAUSAM AFASTADA. PRESCRIÇÃO. MATÉRIA NÃO ARGUÍDA EM PRIMEIRO GRAU. 
PRECLUSÃO. MÉRITO. RESPONSABILIDADE CIVIL OBJETIVA. DEVER DE INDENIZAR 
CONFIGURADO. QUANTUM INDENIZATÓRIO. RAZOABILIDADE. RECURSO IMPROVIDO.

1. Preliminar de ilegitimidade passiva afastada, pois a demandada figura 
no polo passivo da ação como legitimada, uma vez que o veículo envolvido 
no acidente estava registrado em seu nome, sendo a responsabilidade do 
proprietário do veículo pelos danos causados por seus prepostos.

2. A matéria referente à prescrição não foi arguida em primeiro grau de 
jurisdição, sendo matéria de defesa de direito material, operando-se a 
preclusão, não podendo ser conhecida em sede de recurso de apelação.

3. No mérito, restou demonstrado nos autos que o acidente de trânsito 
ocorreu por culpa exclusiva do preposto da ré, que colidiu na traseira 
do veículo da autora, configurando a responsabilidade civil objetiva 
prevista no art. 927, parágrafo único, do Código Civil.

4. O quantum indenizatório foi fixado em R$ 5.000,00 (cinco mil reais), 
valor que se mostra razoável e proporcional ao dano sofrido, considerando 
a extensão do dano, a culpa do agente, a situação econômica das partes 
e os critérios da razoabilidade e proporcionalidade.

5. Recurso improvido.
"""
    
    print(f"\nTexto original: {len(texto)} chars")
    
    # Contar tokens originais
    original_count = counter.count(texto)
    print(f"Tokens originais: {original_count.tokens}")
    
    # Truncar para 200 tokens
    max_tokens = 200
    truncado = counter.truncate_to_tokens(texto, max_tokens)
    truncado_count = counter.count(truncado)
    
    print(f"\nTruncado para {max_tokens} tokens:")
    print(f"  Tokens resultantes: {truncado_count.tokens}")
    print(f"  Redução: {(1 - truncado_count.tokens/original_count.tokens)*100:.1f}%")
    print(f"\nTexto truncado:\n{truncado[:300]}...")


def exemplo_chunking():
    """Exemplo de divisão em chunks."""
    print("=" * 70)
    print("EXEMPLO: Divisão em Chunks")
    print("=" * 70)
    
    counter = TokenCounter()
    
    # Texto muito longo
    texto_longo = "EMENTA: " + ("Este é um exemplo de texto jurídico longo. " * 200)
    
    original = counter.count(texto_longo)
    print(f"\nTexto original: {original.tokens} tokens")
    
    # Dividir em chunks de 500 tokens
    chunks = counter.chunk_text(texto_longo, chunk_size=500, overlap=50)
    
    print(f"\nDividido em {len(chunks)} chunks de 500 tokens:")
    
    for i, chunk in enumerate(chunks, 1):
        count = counter.count(chunk)
        print(f"  Chunk {i}: {count.tokens} tokens")


def exemplo_analise_lote():
    """Exemplo de análise em lote."""
    print("=" * 70)
    print("EXEMPLO: Análise em Lote")
    print("=" * 70)
    
    client = TJDFTClient()
    counter = TokenCounter()
    
    # Buscar várias ementas
    resultados = client.pesquisar(query="tutela de urgência", tamanho=10)
    
    # Contar tokens de todas
    counts = []
    for r in resultados:
        ementa = r.get("ementa", "")
        if ementa:
            counts.append(counter.count(ementa))
    
    # Resumo
    summary = counter.summarize_token_usage(counts)
    
    print(f"\n📊 Resumo de {summary['total_texts']} ementas:\n")
    print(f"  Total tokens: {summary['total_tokens']}")
    print(f"  Média por ementa: {summary['avg_tokens_per_text']}")
    print(f"  Min: {summary['min_tokens']}")
    print(f"  Max: {summary['max_tokens']}")
    print(f"  Chars/token: {summary['avg_chars_per_token']}")
    
    # Estimar custo para processar todas com GPT-4o-mini
    cost = counter.estimate_cost(
        input_tokens=summary['total_tokens'],
        output_tokens=summary['total_texts'] * 500  # ~500 tokens resposta cada
    )
    
    print(f"\n💰 Custo estimado (gpt-4o-mini): ${cost['total_cost_usd']:.4f} USD")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print(" TJDFT API CLIENT - CONTAGEM DE TOKENS")
    print("=" * 70)
    
    exemplo_contagem_basica()
    exemplo_jurisprudencia()
    exemplo_estimativa_custo()
    exemplo_truncagem()
    exemplo_chunking()
    exemplo_analise_lote()
    
    print("\n" + "=" * 70)
    print(" ✅ EXEMPLOS CONCLUÍDOS")
    print("=" * 70)
