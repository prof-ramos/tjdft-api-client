# TJDFT API Client
"""
Cliente Python para a API de Jurisprudência do TJDFT.

Uso:
    from tjdft import TJDFTClient, AnaliseMagistrados
    
    client = TJDFTClient()
    resultados = client.pesquisar(query="dano moral")
    
    # Analisar padrões de decisão por magistrado
    analise = AnaliseMagistrados()
    perfis = analise.analisar_por_tema("tutela de urgência")
    
    for p in perfis[:5]:
        print(f"{p.nome}: {p.percentual_deferimento:.0f}% deferimento")
"""

__version__ = "0.3.0"
__author__ = "Prof. Gabriel Ramos"

from .client import TJDFTClient
from .models import Acordao, Decisao, ResultadoBusca
from .agent import JurisprudenciaAgent, AnaliseJurisprudencial
from .analise import AnaliseMagistrados, PerfilMagistrado

__all__ = [
    "TJDFTClient", 
    "Acordao", 
    "Decisao", 
    "ResultadoBusca",
    "JurisprudenciaAgent",
    "AnaliseJurisprudencial",
    "AnaliseMagistrados",
    "PerfilMagistrado",
]
