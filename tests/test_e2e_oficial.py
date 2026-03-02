#!/usr/bin/env python3
"""
Testes e2e para a API Oficial do TJDFT.

Este script testa o endpoint oficial da API de Jurisprudência do TJDFT.
API: https://jurisdf.tjdft.jus.br/api/v1/pesquisa
"""

import sys
sys.path.insert(0, "../src")

import requests
import json
from datetime import datetime


API_URL = "https://jurisdf.tjdft.jus.br/api/v1/pesquisa"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "TJDFT-API-Client/0.2.0 (e2e-test)",
}


def test_api_basica():
    """Testa requisição básica à API."""
    print("\n" + "=" * 70)
    print("TESTE: Requisição básica")
    print("=" * 70)
    
    payload = {
        "query": "dano moral",
        "pagina": 0,
        "tamanho": 5
    }
    
    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers=HEADERS,
            timeout=30
        )
        
        print(f"URL: {API_URL}")
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ Sucesso!")
            print(f"Hits (total): {data.get('hits', 0)}")
            print(f"Registros retornados: {len(data.get('registros', []))}")
            
            # Mostra estrutura do primeiro registro
            registros = data.get('registros', [])
            if registros:
                print("\nEstrutura do primeiro registro:")
                primeiro = registros[0]
                for key in list(primeiro.keys())[:10]:
                    valor = str(primeiro[key])[:50]
                    print(f"  {key}: {valor}...")
            
            return True
        else:
            print(f"\n❌ Falha: Status {response.status_code}")
            print(f"Resposta: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return False


def test_api_com_filtro():
    """Testa requisição com filtro por relator."""
    print("\n" + "=" * 70)
    print("TESTE: Filtro por relator")
    print("=" * 70)
    
    payload = {
        "query": "habeas corpus",
        "pagina": 0,
        "tamanho": 5,
        "termosAcessorios": [
            {
                "campo": "nomeRelator",
                "valor": "CARMEN BITTENCOURT"
            }
        ]
    }
    
    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers=HEADERS,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ Sucesso!")
            print(f"Hits: {data.get('hits', 0)}")
            
            registros = data.get('registros', [])
            if registros:
                print("\nPrimeiros resultados:")
                for i, r in enumerate(registros[:3], 1):
                    print(f"{i}. {r.get('processo', 'N/A')}")
                    print(f"   Relator: {r.get('nomeRelator', 'N/A')}")
                    print(f"   Órgão: {r.get('descricaoOrgaoJulgador', 'N/A')}")
            
            return True
        else:
            print(f"\n❌ Falha: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return False


def test_api_paginacao():
    """Testa paginação."""
    print("\n" + "=" * 70)
    print("TESTE: Paginação")
    print("=" * 70)
    
    # Página 0
    payload_pag0 = {
        "query": "tráfico",
        "pagina": 0,
        "tamanho": 3
    }
    
    # Página 1
    payload_pag1 = {
        "query": "tráfico",
        "pagina": 1,
        "tamanho": 3
    }
    
    try:
        r0 = requests.post(API_URL, json=payload_pag0, headers=HEADERS, timeout=30)
        r1 = requests.post(API_URL, json=payload_pag1, headers=HEADERS, timeout=30)
        
        if r0.status_code == 200 and r1.status_code == 200:
            data0 = r0.json()
            data1 = r1.json()
            
            print(f"\n✅ Paginação funcionando!")
            print(f"Total de hits: {data0.get('hits', 0)}")
            
            ids_pag0 = [r.get('uuid') for r in data0.get('registros', [])]
            ids_pag1 = [r.get('uuid') for r in data1.get('registros', [])]
            
            print(f"UUIDs página 0: {ids_pag0[:2]}...")
            print(f"UUIDs página 1: {ids_pag1[:2]}...")
            
            # Verifica se são diferentes
            if set(ids_pag0) != set(ids_pag1):
                print("✅ Páginas retornam resultados diferentes (correto)")
                return True
            else:
                print("⚠️ Páginas retornam mesmos resultados (inesperado)")
                return False
        else:
            print(f"❌ Falha na paginação")
            return False
            
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return False


def test_cliente_python():
    """Testa o cliente Python."""
    print("\n" + "=" * 70)
    print("TESTE: Cliente Python")
    print("=" * 70)
    
    try:
        from tjdft import TJDFTClient
        
        client = TJDFTClient()
        
        # Teste básico
        resultados = client.pesquisar(query="habeas corpus", tamanho=3)
        
        print(f"\n✅ Cliente funcionando!")
        print(f"Total: {resultados.total}")
        print(f"Registros: {len(resultados)}")
        
        if resultados:
            print("\nPrimeiro resultado:")
            r = resultados[0]
            print(f"  Processo: {r.get('processo', 'N/A')}")
            print(f"  Relator: {r.get('nome_relator', 'N/A')}")
            print(f"  Órgão: {r.get('orgao_julgador', 'N/A')}")
        
        # Teste com filtro
        print("\nTestando filtro por relator...")
        resultados_filtro = client.pesquisar_por_relator(
            query="dano moral",
            relator="CARMEN BITTENCOURT",
            tamanho=3
        )
        print(f"Resultados com filtro: {resultados_filtro.total}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro no cliente: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_campos_disponiveis():
    """Lista campos disponíveis na resposta."""
    print("\n" + "=" * 70)
    print("TESTE: Campos disponíveis")
    print("=" * 70)
    
    payload = {
        "query": "teste",
        "pagina": 0,
        "tamanho": 1
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            registros = data.get('registros', [])
            
            if registros:
                campos = list(registros[0].keys())
                print(f"\nCampos disponíveis ({len(campos)}):")
                for campo in sorted(campos):
                    print(f"  - {campo}")
                return True
        
        return False
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return False


def main():
    print("=" * 70)
    print("TESTES E2E - API OFICIAL TJDFT")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Endpoint: {API_URL}")
    print("=" * 70)
    
    results = {
        "api_basica": test_api_basica(),
        "api_com_filtro": test_api_com_filtro(),
        "paginacao": test_api_paginacao(),
        "campos_disponiveis": test_campos_disponiveis(),
        "cliente_python": test_cliente_python(),
    }
    
    print("\n" + "=" * 70)
    print("RESUMO DOS TESTES")
    print("=" * 70)
    
    for name, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{name:25} → {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nTotal: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 Todos os testes passaram! API oficial funcionando!")


if __name__ == "__main__":
    main()
