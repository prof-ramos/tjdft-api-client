#!/usr/bin/env python3
"""
Script para descobrir endpoints da API do TJDFT.

Este script tenta descobrir endpoints válidos através de:
1. Análise do portal web
2. Teste de endpoints comuns
3. Engenharia reversa de requisições
"""

import requests
from urllib.parse import urljoin
import json
import re


BASE_URL = "https://www.tjdft.jus.br"

# Endpoints comuns de API
ENDPOINTS_COMUNS = [
    "/api/v1/jurisprudencia",
    "/api/v1/acordaos",
    "/api/v1/decisoes",
    "/api/v1/orgaos",
    "/api/jurisprudencia",
    "/api/acordaos",
    "/api/decisoes",
    "/jurisprudencia/api",
    "/jurisprudencia/api/v1",
    "/jurisprudencia/busca",
    "/jurisprudencia/pesquisa",
    "/jurisprudencia/consulta",
    "/ws/jurisprudencia",
    "/ws/acordaos",
    "/services/jurisprudencia",
    "/rest/jurisprudencia",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Accept": "application/json, text/html",
    "Accept-Language": "pt-BR,pt;q=0.9",
}


def testar_endpoint(endpoint: str) -> dict:
    """Testa um endpoint e retorna informações."""
    url = urljoin(BASE_URL, endpoint)
    
    try:
        # Testa GET
        r_get = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        
        # Testa OPTIONS
        try:
            r_options = requests.options(url, headers=HEADERS, timeout=10)
            allow = r_options.headers.get("Allow", "")
        except:
            allow = ""
        
        content_type = r_get.headers.get("Content-Type", "")
        
        return {
            "endpoint": endpoint,
            "url_final": r_get.url,
            "status": r_get.status_code,
            "content_type": content_type,
            "allow": allow,
            "tamanho": len(r_get.content),
            "json_valido": is_json(r_get.text) if r_get.status_code == 200 else False,
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "erro": str(e),
        }


def is_json(text: str) -> bool:
    """Verifica se o texto é JSON válido."""
    try:
        json.loads(text)
        return True
    except:
        return False


def analisar_portal():
    """Analisa o portal para encontrar links de API."""
    print("Analisando portal TJDFT...")
    
    try:
        r = requests.get(f"{BASE_URL}/jurisprudencia", headers=HEADERS, timeout=15)
        
        # Procura por URLs de API
        api_urls = re.findall(r'["\']([^"\']*(?:api|ws|rest)[^"\']*)["\']', r.text)
        
        # Procura por endpoints de fetch/axios
        fetch_urls = re.findall(r'fetch\(["\']([^"\']+)["\']', r.text)
        axios_urls = re.findall(r'axios\.[a-z]+\(["\']([^"\']+)["\']', r.text)
        
        return list(set(api_urls + fetch_urls + axios_urls))
    except Exception as e:
        print(f"Erro ao analisar portal: {e}")
        return []


def main():
    print("=" * 70)
    print("DESCOBERTA DE ENDPOINTS - API TJDFT")
    print("=" * 70)
    
    # Testa endpoints comuns
    print("\n1. Testando endpoints comuns...")
    print("-" * 70)
    
    resultados = []
    for endpoint in ENDPOINTS_COMUNS:
        print(f"Testando: {endpoint}...", end=" ")
        result = testar_endpoint(endpoint)
        resultados.append(result)
        
        if result.get("status"):
            print(f"Status: {result['status']} | CT: {result['content_type'][:30]}")
        else:
            print(f"Erro: {result.get('erro', 'desconhecido')[:30]}")
    
    # Analisa portal
    print("\n2. Analisando portal...")
    print("-" * 70)
    
    urls = analisar_portal()
    for url in urls[:20]:  # Limita a 20 URLs
        print(f"  Encontrado: {url}")
    
    # Resumo
    print("\n3. Resumo de endpoints promissores...")
    print("-" * 70)
    
    promissores = [
        r for r in resultados
        if r.get("status") == 200 and (
            r.get("json_valido") or 
            "json" in r.get("content_type", "").lower()
        )
    ]
    
    if promissores:
        for p in promissores:
            print(f"  ✅ {p['endpoint']} - {p['content_type']}")
    else:
        print("  Nenhum endpoint JSON encontrado ainda.")
    
    print("\n4. Próximos passos...")
    print("-" * 70)
    print("  1. Acessar https://www.tjdft.jus.br/jurisprudencia")
    print("  2. Abrir DevTools (F12) → Network tab")
    print("  3. Fazer uma busca")
    print("  4. Identificar endpoints nas requisições")
    print("  5. Documentar em docs/endpoints.md")


if __name__ == "__main__":
    main()
