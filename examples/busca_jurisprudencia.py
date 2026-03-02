#!/usr/bin/env python3
"""
Exemplo de uso do cliente TJDFT.

Este script demonstra como buscar jurisprudência no TJDFT.
"""

import sys
sys.path.insert(0, "../src")

from tjdft import TJDFTClient
from datetime import date


def exemplo_busca_simples():
    """Exemplo de busca simples."""
    print("=" * 60)
    print("Busca simples por jurisprudência")
    print("=" * 60)
    
    with TJDFTClient() as client:
        # Busca por termo
        resultados = client.buscar_jurisprudencia(
            termo="habeas corpus",
            por_pagina=5
        )
        
        print(f"\nTotal encontrado: {resultados.total}")
        print(f"Página: {resultados.pagina}/{resultados.total_paginas}")
        
        for i, r in enumerate(resultados, 1):
            print(f"\n{i}. {r.numero}")
            print(f"   Classe: {r.classe}")
            print(f"   Relator: {r.relator}")
            print(f"   Ementa: {r.ementa[:100]}...")


def exemplo_busca_avancada():
    """Exemplo de busca avançada."""
    print("\n" + "=" * 60)
    print("Busca avançada com filtros")
    print("=" * 60)
    
    with TJDFTClient() as client:
        resultados = client.buscar_jurisprudencia(
            termo="tráfico de drogas",
            tipo="acordao",
            data_inicial=date(2024, 1, 1),
            data_final=date(2024, 12, 31),
            orgao="1ª Turma Criminal",
            por_pagina=10
        )
        
        print(f"\nTotal: {resultados.total}")
        
        # Filtra por relator
        for r in resultados:
            print(f"\n{r.numero} - {r.classe}")
            print(f"  Relator: {r.relator}")
            print(f"  Julgado em: {r.data_julgamento}")


def exemplo_listar_orgaos():
    """Exemplo listando órgãos julgadores."""
    print("\n" + "=" * 60)
    print("Órgãos julgadores disponíveis")
    print("=" * 60)
    
    with TJDFTClient() as client:
        orgaos = client.listar_orgaos_julgadores()
        
        for i, orgao in enumerate(orgaos, 1):
            print(f"{i:2}. {orgao}")


def exemplo_buscar_por_numero():
    """Exemplo buscando decisão por número."""
    print("\n" + "=" * 60)
    print("Busca por número de processo")
    print("=" * 60)
    
    with TJDFTClient() as client:
        # Substitua por um número real
        numero = "2024HC123456"
        
        acordao = client.buscar_acordao(numero)
        
        if acordao:
            print(f"\nEncontrado: {acordao.numero}")
            print(f"Classe: {acordao.classe}")
            print(f"Ementa: {acordao.ementa}")
        else:
            print(f"\nAcórdão {numero} não encontrado.")


if __name__ == "__main__":
    print("TJDFT API Client - Exemplos de Uso\n")
    
    try:
        exemplo_busca_simples()
        exemplo_busca_avancada()
        exemplo_listar_orgaos()
        # exemplo_buscar_por_numero()  # Descomente para testar
        
    except Exception as e:
        print(f"\nErro: {e}")
        print("\nNota: A API pode não estar disponível ou os endpoints")
        print("ainda precisam ser descobertos/documented.")
