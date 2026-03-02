# TJDFT API Client

"""
Cliente Python para a API de Jurisprudência do TJDFT.

Uso:
    from tjdft import TJDFTClient
    
    client = TJDFTClient()
    resultados = client.buscar_jurisprudencia(termo="habeas corpus")
"""

__version__ = "0.1.0"
__author__ = "Prof. Gabriel Ramos"

from .client import TJDFTClient
from .models import Acordao, Decisao, ResultadoBusca

__all__ = ["TJDFTClient", "Acordao", "Decisao", "ResultadoBusca"]
