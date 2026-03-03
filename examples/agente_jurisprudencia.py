#!/usr/bin/env python3
"""
Exemplo de uso do Agente de Jurisprudência com IA.

Este script demonstra como usar o JurisprudenciaAgent para
analisar casos jurídicos com busca no TJDFT e análise via Gemini.
"""

import os
import sys
sys.path.insert(0, "../src")

from tjdft import JurisprudenciaAgent


def exemplo_analise_caso():
    """Exemplo de análise de caso."""
    print("=" * 70)
    print("EXEMPLO: Análise de Caso com IA")
    print("=" * 70)
    
    # Verifica se a chave da API está disponível
    if not os.environ.get("OPENAI_API_KEY"):
        print("\n❌ Erro: OPENAI_API_KEY não definida")
        print("Exporte a variável: export OPENAI_API_KEY='sua-chave'")
        return
    
    # Cria o agente
    agent = JurisprudenciaAgent()
    
    # Descreve o caso
    caso = """
    Cliente solicitou renovação de CNH junto ao DETRAN/DF.
    Pagou todas as taxas (R$ 265,00) e realizou exames médicos.
    Passados 30 dias, a CNH não foi emitida.
    Sistema do DETRAN mostra "sem observações" no prontuário.
    Cliente está impedido de dirigir desde a expiração da autorização provisória.
    """
    
    # Termos de busca
    termos = [
        "DETRAN CNH renovação obrigação fazer",
        "tutela urgência CNH",
        "multa diária administração pública"
    ]
    
    print("\n🔍 Analisando caso...")
    print(f"Termos de busca: {termos}")
    
    # Analisa o caso
    resultado = agent.analisar_caso(
        descricao=caso,
        termos_busca=termos
    )
    
    # Exibe resultados
    print(f"\n📊 Jurisprudências encontradas: {resultado.jurisprudencias_encontradas}")
    
    print("\n" + "=" * 70)
    print("📝 ANÁLISE DA IA")
    print("=" * 70)
    print(resultado.analise_ia)
    
    if resultado.jurisprudencias_relevantes:
        print("\n" + "=" * 70)
        print("📚 JURISPRUDÊNCIAS RELEVANTES")
        print("=" * 70)
        for j in resultado.jurisprudencias_relevantes[:3]:
            print(f"\n• {j.get('processo', 'N/A')}")
            print(f"  Relator: {j.get('relator', 'N/A')}")
            print(f"  Trecho: {j.get('trecho', 'N/A')[:150]}...")
    
    if resultado.sugestoes:
        print("\n" + "=" * 70)
        print("💡 SUGESTÕES")
        print("=" * 70)
        for i, sugestao in enumerate(resultado.sugestoes, 1):
            print(f"{i}. {sugestao}")
    
    if resultado.precedentes:
        print("\n" + "=" * 70)
        print("⚖️ PRECEDENTES")
        print("=" * 70)
        for p in resultado.precedentes:
            print(f"  • {p}")


def exemplo_resumo_jurisprudencia():
    """Exemplo de resumo de jurisprudência específica."""
    print("\n" + "=" * 70)
    print("EXEMPLO: Resumo de Jurisprudência Específica")
    print("=" * 70)
    
    if not os.environ.get("OPENAI_API_KEY"):
        print("\n❌ OPENAI_API_KEY não definida")
        return
    
    agent = JurisprudenciaAgent()
    
    # Número do processo
    processo = "0723221-62.2024.8.07.0000"
    
    print(f"\n🔍 Buscando processo: {processo}")
    
    resumo = agent.resumir_jurisprudencia(processo)
    
    print("\n" + "=" * 70)
    print("📄 RESUMO")
    print("=" * 70)
    print(resumo)


def exemplo_busca_simples():
    """Exemplo de busca simples sem IA."""
    print("\n" + "=" * 70)
    print("EXEMPLO: Busca Simples (sem IA)")
    print("=" * 70)
    
    from tjdft import TJDFTClient
    
    client = TJDFTClient()
    
    # Busca sem IA
    resultados = client.pesquisar(
        query="DETRAN CNH renovação",
        tamanho=5
    )
    
    print(f"\nTotal encontrado: {resultados.total}")
    
    for i, dec in enumerate(resultados, 1):
        print(f"\n{i}. {dec.get('processo', 'N/A')}")
        print(f"   Relator: {dec.get('nome_relator', 'N/A')}")
        print(f"   Órgão: {dec.get('orgao_julgador', 'N/A')}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TJDFT API CLIENT - AGENTE DE JURISPRUDÊNCIA COM IA")
    print("=" * 70)
    
    print("\nEscolha uma opção:")
    print("1. Análise de caso com IA")
    print("2. Resumo de jurisprudência específica")
    print("3. Busca simples (sem IA)")
    
    escolha = input("\nOpção: ").strip()
    
    if escolha == "1":
        exemplo_analise_caso()
    elif escolha == "2":
        exemplo_resumo_jurisprudencia()
    elif escolha == "3":
        exemplo_busca_simples()
    else:
        print("\nOpção inválida. Executando busca simples...")
        exemplo_busca_simples()
