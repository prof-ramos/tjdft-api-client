#!/usr/bin/env python3
"""
Testes e2e para a API do TJDFT.

Este script testa os endpoints descobertos da API do TJDFT.
"""

import requests
import json
from datetime import datetime


BASE_URL = "https://www.tjdft.jus.br"

# Headers para simular navegador
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


def test_ajax_search():
    """Testa endpoint de busca ajax."""
    print("\n" + "=" * 70)
    print("TESTE: @@ajax-search")
    print("=" * 70)
    
    url = f"{BASE_URL}/@@ajax-search"
    params = {"SearchableText": "habeas corpus"}
    
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=30)
        
        print(f"URL: {response.url}")
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Sucesso!")
            print(f"Total de resultados: {data.get('total', 0)}")
            
            items = data.get("items", [])
            print(f"Items retornados: {len(items)}")
            
            if items:
                print("\nPrimeiros 3 resultados:")
                for i, item in enumerate(items[:3], 1):
                    print(f"\n{i}. {item.get('title', 'N/A')}")
                    print(f"   URL: {item.get('url', 'N/A')}")
            
            return True
        else:
            print(f"\n❌ Falha: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return False


def test_site_search():
    """Testa endpoint de busca do site."""
    print("\n" + "=" * 70)
    print("TESTE: @@search")
    print("=" * 70)
    
    url = f"{BASE_URL}/@@search"
    params = {"SearchableText": "tráfico de drogas"}
    
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=30, allow_redirects=True)
        
        print(f"URL final: {response.url}")
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            # Verifica se é HTML ou JSON
            content_type = response.headers.get('Content-Type', '')
            
            if 'json' in content_type.lower():
                data = response.json()
                print(f"\n✅ Resposta JSON!")
                print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
            else:
                print(f"\n⚠️ Resposta HTML (não é JSON)")
                # Procura por resultados na página
                if 'resultado' in response.text.lower():
                    print("Página contém resultados")
            
            return True
        else:
            print(f"\n❌ Falha: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return False


def test_jurisprudencia_page():
    """Testa página de jurisprudência."""
    print("\n" + "=" * 70)
    print("TESTE: Página de Jurisprudência")
    print("=" * 70)
    
    url = f"{BASE_URL}/consultas/jurisprudencia/jurisprudencia"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        print(f"URL: {response.url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            # Procura por links de API
            api_links = []
            if '@@' in response.text:
                api_links = [l for l in response.text.split('"') if '@@' in l]
            
            print(f"\n✅ Página acessível")
            print(f"Links com '@@' encontrados: {len(api_links)}")
            
            if api_links:
                print("Exemplos:")
                for link in api_links[:5]:
                    print(f"  - {link}")
            
            return True
        else:
            print(f"\n❌ Falha: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return False


def test_common_api_endpoints():
    """Testa endpoints comuns de API."""
    print("\n" + "=" * 70)
    print("TESTE: Endpoints comuns de API")
    print("=" * 70)
    
    endpoints = [
        "/api/v1/jurisprudencia",
        "/api/jurisprudencia",
        "/api/acordaos",
        "/ws/jurisprudencia",
        "/rest/jurisprudencia",
        "/jurisprudencia/api",
    ]
    
    results = []
    
    for endpoint in endpoints:
        url = f"{BASE_URL}{endpoint}"
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            status = response.status_code
            content_type = response.headers.get('Content-Type', 'N/A')
            
            is_json = 'json' in content_type.lower()
            
            results.append({
                "endpoint": endpoint,
                "status": status,
                "content_type": content_type[:30],
                "is_json": is_json
            })
            
            print(f"{endpoint:30} → {status} {'✅ JSON' if is_json else ''}")
            
        except Exception as e:
            results.append({
                "endpoint": endpoint,
                "error": str(e)
            })
            print(f"{endpoint:30} → ERRO: {str(e)[:30]}")
    
    json_endpoints = [r for r in results if r.get('is_json')]
    
    print(f"\nResumo:")
    print(f"  Endpoints testados: {len(endpoints)}")
    print(f"  Endpoints JSON: {len(json_endpoints)}")
    
    return len(json_endpoints) > 0


def main():
    print("=" * 70)
    print("TESTES E2E - API TJDFT")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    results = {
        "ajax_search": test_ajax_search(),
        "site_search": test_site_search(),
        "jurisprudencia_page": test_jurisprudencia_page(),
        "common_endpoints": test_common_api_endpoints(),
    }
    
    print("\n" + "=" * 70)
    print("RESUMO DOS TESTES")
    print("=" * 70)
    
    for name, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{name:20} → {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nTotal: {passed}/{total} testes passaram")
    
    print("\n" + "=" * 70)
    print("DESCOBERTAS")
    print("=" * 70)
    print("""
1. @@ajax-search funciona e retorna JSON
   - URL: https://www.tjdft.jus.br/@@ajax-search?SearchableText=termo
   - Retorna: {"total": N, "items": [...]}

2. Site usa Plone CMS
   - Busca padrão Plone: @@search
   - API ajax: @@ajax-search

3. Não há API REST documentada
   - Endpoints comuns não funcionam
   - Necessário análise via DevTools

4. Próximos passos:
   - Usar browser para interceptar requisições
   - Documentar endpoints internos
   - Contatar TJDFT para documentação oficial
""")


if __name__ == "__main__":
    main()
