"""
Cliente para a API de Jurisprudência do TJDFT.
"""

import requests
from typing import Optional, List, Dict, Any
from datetime import date
from dataclasses import dataclass

from .models import Acordao, Decisao, ResultadoBusca


class TJDFTClient:
    """
    Cliente para a API de Jurisprudência do TJDFT.
    
    Exemplo:
        >>> client = TJDFTClient()
        >>> resultados = client.buscar_jurisprudencia(termo="habeas corpus")
        >>> for r in resultados:
        ...     print(r.numero, r.ementa[:50])
    """
    
    BASE_URL = "https://www.tjdft.jus.br"
    
    def __init__(
        self,
        timeout: int = 30,
        retries: int = 3,
        user_agent: str = "TJDFT-API-Client/0.1.0"
    ):
        """
        Inicializa o cliente.
        
        Args:
            timeout: Tempo máximo de espera em segundos
            retries: Número de tentativas em caso de falha
            user_agent: User-Agent para as requisições
        """
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept": "application/json",
            "Accept-Language": "pt-BR,pt;q=0.9",
        })
    
    def buscar_jurisprudencia(
        self,
        termo: str,
        tipo: Optional[str] = None,
        data_inicial: Optional[date] = None,
        data_final: Optional[date] = None,
        orgao: Optional[str] = None,
        relator: Optional[str] = None,
        pagina: int = 1,
        por_pagina: int = 20
    ) -> ResultadoBusca:
        """
        Busca jurisprudência no TJDFT.
        
        Args:
            termo: Termo de busca
            tipo: Tipo de decisão (acordao, decisao, sentenca)
            data_inicial: Data inicial
            data_final: Data final
            orgao: Órgão julgador
            relator: Nome do relator
            pagina: Número da página
            por_pagina: Resultados por página
            
        Returns:
            ResultadoBusca com os resultados encontrados
        """
        params = {
            "termo": termo,
            "pagina": pagina,
            "por_pagina": por_pagina,
        }
        
        if tipo:
            params["tipo"] = tipo
        if data_inicial:
            params["data_inicial"] = data_inicial.strftime("%d/%m/%Y")
        if data_final:
            params["data_final"] = data_final.strftime("%d/%m/%Y")
        if orgao:
            params["orgao"] = orgao
        if relator:
            params["relator"] = relator
        
        # TODO: Implementar endpoint real quando descoberto
        response = self.session.get(
            f"{self.BASE_URL}/jurisprudencia/busca",
            params=params,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        
        return self._parse_resultado(response.json())
    
    def buscar_acordao(self, numero: str) -> Optional[Acordao]:
        """
        Busca um acórdão pelo número.
        
        Args:
            numero: Número do processo/acórdão
            
        Returns:
            Acordao encontrado ou None
        """
        response = self.session.get(
            f"{self.BASE_URL}/jurisprudencia/acordao/{numero}",
            timeout=self.timeout
        )
        
        if response.status_code == 404:
            return None
        
        response.raise_for_status()
        return Acordao.from_dict(response.json())
    
    def buscar_decisao(self, numero: str) -> Optional[Decisao]:
        """
        Busca uma decisão pelo número.
        
        Args:
            numero: Número do processo/decisão
            
        Returns:
            Decisao encontrada ou None
        """
        response = self.session.get(
            f"{self.BASE_URL}/jurisprudencia/decisao/{numero}",
            timeout=self.timeout
        )
        
        if response.status_code == 404:
            return None
        
        response.raise_for_status()
        return Decisao.from_dict(response.json())
    
    def listar_orgaos_julgadores(self) -> List[str]:
        """
        Lista os órgãos julgadores disponíveis.
        
        Returns:
            Lista de nomes dos órgãos julgadores
        """
        # TODO: Implementar endpoint real
        return [
            "1ª Turma Criminal",
            "2ª Turma Criminal",
            "1ª Turma Cível",
            "2ª Turma Cível",
            "3ª Turma Cível",
            "4ª Turma Cível",
            "5ª Turma Cível",
            "Câmara Criminal",
            "Turma Recursal dos Juizados Especiais",
            "Órgão Especial",
        ]
    
    def _parse_resultado(self, data: Dict[str, Any]) -> ResultadoBusca:
        """Parseia resposta da API."""
        resultados = []
        
        for item in data.get("resultados", []):
            tipo = item.get("tipo", "acordao")
            if tipo == "acordao":
                resultados.append(Acordao.from_dict(item))
            else:
                resultados.append(Decisao.from_dict(item))
        
        return ResultadoBusca(
            resultados=resultados,
            total=data.get("total", 0),
            pagina=data.get("pagina", 1),
            por_pagina=data.get("por_pagina", 20)
        )
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
