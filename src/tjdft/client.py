"""
Cliente para a API de Jurisprudência do TJDFT.

API Oficial: https://jurisdf.tjdft.jus.br/api/v1/pesquisa

Uso:
    from tjdft import TJDFTClient
    
    client = TJDFTClient()
    resultados = client.pesquisar(query="habeas corpus")
"""

import requests
from typing import Optional, List, Dict, Any
from datetime import date
from dataclasses import dataclass

from .models import Acordao, Decisao, ResultadoBusca


class TJDFTClient:
    """
    Cliente para a API de Jurisprudência do TJDFT.
    
    API Oficial: https://jurisdf.tjdft.jus.br/api/v1/pesquisa
    
    Exemplo:
        >>> client = TJDFTClient()
        >>> resultados = client.pesquisar(query="dano moral")
        >>> for r in resultados:
        ...     print(r.processo, r.nome_relator)
    """
    
    API_URL = "https://jurisdf.tjdft.jus.br/api/v1/pesquisa"
    
    # Campos disponíveis para filtros
    CAMPOS_FILTRO = [
        "base",
        "subbase", 
        "origem",
        "uuid",
        "identificador",
        "processo",
        "nomeRelator",
        "nomeRevisor",
        "nomeRelatorDesignado",
        "descricaoOrgaoJulgador",
        "dataJulgamento",
        "dataPublicacao",
        "descricaoClasseCnj",
    ]
    
    def __init__(
        self,
        timeout: int = 30,
        user_agent: str = "TJDFT-API-Client/0.2.0"
    ):
        """
        Inicializa o cliente.
        
        Args:
            timeout: Tempo máximo de espera em segundos
            user_agent: User-Agent para as requisições
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
    
    def pesquisar(
        self,
        query: str,
        pagina: int = 0,
        tamanho: int = 20,
        filtros: Optional[Dict[str, str]] = None
    ) -> ResultadoBusca:
        """
        Pesquisa jurisprudência no TJDFT.
        
        Args:
            query: Termo de busca
            pagina: Número da página (começa em 0)
            tamanho: Resultados por página
            filtros: Dicionário com filtros (campo: valor)
            
        Returns:
            ResultadoBusca com os resultados encontrados
            
        Example:
            >>> resultados = client.pesquisar(
            ...     query="habeas corpus",
            ...     filtros={"nomeRelator": "CARMEN BITTENCOURT"}
            ... )
        """
        payload = {
            "query": query,
            "pagina": pagina,
            "tamanho": tamanho,
        }
        
        if filtros:
            termos_acessorios = []
            for campo, valor in filtros.items():
                if campo in self.CAMPOS_FILTRO:
                    termos_acessorios.append({
                        "campo": campo,
                        "valor": valor
                    })
            if termos_acessorios:
                payload["termosAcessorios"] = termos_acessorios
        
        response = self.session.post(
            self.API_URL,
            json=payload,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        
        return self._parse_resposta(response.json())
    
    def pesquisar_por_relator(
        self,
        query: str,
        relator: str,
        tamanho: int = 20
    ) -> ResultadoBusca:
        """
        Pesquisa por termo filtrando por relator.
        
        Args:
            query: Termo de busca
            relator: Nome do relator
            tamanho: Resultados por página
            
        Returns:
            ResultadoBusca com os resultados
        """
        return self.pesquisar(
            query=query,
            filtros={"nomeRelator": relator},
            tamanho=tamanho
        )
    
    def pesquisar_por_orgao(
        self,
        query: str,
        orgao: str,
        tamanho: int = 20
    ) -> ResultadoBusca:
        """
        Pesquisa por termo filtrando por órgão julgador.
        
        Args:
            query: Termo de busca
            orgao: Nome do órgão julgador
            tamanho: Resultados por página
            
        Returns:
            ResultadoBusca com os resultados
        """
        return self.pesquisar(
            query=query,
            filtros={"descricaoOrgaoJulgador": orgao},
            tamanho=tamanho
        )
    
    def pesquisar_por_periodo(
        self,
        query: str,
        data_inicial: date,
        data_final: date,
        tamanho: int = 20
    ) -> ResultadoBusca:
        """
        Pesquisa por termo filtrando por período de publicação.
        
        Args:
            query: Termo de busca
            data_inicial: Data inicial
            data_final: Data final
            tamanho: Resultados por página
            
        Returns:
            ResultadoBusca com os resultados
        """
        # Nota: A API pode não suportar range de datas diretamente
        # Este método usa dataPublicacao como filtro único
        return self.pesquisar(
            query=query,
            filtros={
                "dataPublicacao": data_inicial.strftime("%Y-%m-%d")
            },
            tamanho=tamanho
        )
    
    def buscar_por_processo(self, numero_processo: str) -> Optional[Dict[str, Any]]:
        """
        Busca decisão por número do processo.
        
        Args:
            numero_processo: Número do processo
            
        Returns:
            Dicionário com dados da decisão ou None
        """
        resultados = self.pesquisar(
            query=numero_processo,
            filtros={"processo": numero_processo},
            tamanho=1
        )
        
        if resultados:
            return resultados[0]
        return None
    
    def _parse_resposta(self, data: Dict[str, Any]) -> ResultadoBusca:
        """Parseia resposta da API."""
        resultados = []
        
        for registro in data.get("registros", []):
            # Determina se é acórdão ou decisão baseado na base
            base = registro.get("base", "").lower()
            
            resultado = {
                "uuid": registro.get("uuid", ""),
                "identificador": registro.get("identificador", ""),
                "processo": registro.get("processo", ""),
                "ementa": registro.get("ementa", ""),
                "inteiro_teor": registro.get("inteiroTeor", ""),
                "nome_relator": registro.get("nomeRelator", ""),
                "nome_revisor": registro.get("nomeRevisor", ""),
                "orgao_julgador": registro.get("descricaoOrgaoJulgador", ""),
                "data_publicacao": registro.get("dataPublicacao", ""),
                "data_julgamento": registro.get("dataJulgamento", ""),
                "classe_cnj": registro.get("descricaoClasseCnj", ""),
                "codigo_classe_cnj": registro.get("codigoClasseCnj", ""),
                "base": base,
                "subbase": registro.get("subbase", ""),
                "possui_inteiro_teor": registro.get("possuiInteiroTeor", False),
            }
            resultados.append(resultado)

        # Extract total from hits (can be dict with 'value' or int)
        hits = data.get("hits", {})
        if isinstance(hits, dict):
            total = hits.get("value", 0)
        else:
            total = hits

        return ResultadoBusca(
            resultados=resultados,
            total=total,
            pagina=data.get("pagina", 0),
            por_pagina=len(resultados),
            agregacoes=data.get("agregações", {})
        )
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
