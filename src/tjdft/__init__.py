# TJDFT API Client

"""
Cliente Python para a API de Jurisprudência do TJDFT.

Uso:
    from tjdft import TJDFTClient
    
    client = TJDFTClient()
    resultados = client.pesquisar(query="dano moral")
"""

__version__ = "0.2.0"
__author__ = "Prof. Gabriel Ramos"

from .client import TJDFTClient
from .models import Acordao, Decisao, ResultadoBusca
from .agent import JurisprudenciaAgent, AnaliseJurisprudencial

__all__ = [
    "TJDFTClient", 
    "Acordao", 
    "Decisao", 
    "ResultadoBusca",
    "JurisprudenciaAgent",
    "AnaliseJurisprudencial"
]
