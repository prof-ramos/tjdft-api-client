"""
Análise de padrões de decisão por magistrado.

Este módulo permite analisar como cada magistrado do TJDFT
costuma decidir sobre determinados temas.

Uso:
    from tjdft.analise import AnaliseMagistrados
    
    analise = AnaliseMagistrados()
    relatores = analise.analisar_por_tema("tutela de urgência")
    
    for r in relatores[:5]:
        print(f"{r.nome}: {r.percentual_deferimento}%")
"""

import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from collections import Counter, defaultdict


@dataclass
class PerfilMagistrado:
    """Perfil de decisão de um magistrado."""
    nome: str
    total_decisoes: int
    deferimentos: int
    indeferimentos: int
    parciais: int = 0
    orgaos: List[str] = field(default_factory=list)
    temas_comuns: List[str] = field(default_factory=list)
    
    @property
    def percentual_deferimento(self) -> float:
        """Percentual de deferimentos."""
        if self.total_decisoes == 0:
            return 0.0
        return (self.deferimentos / self.total_decisoes) * 100
    
    @property
    def percentual_indeferimento(self) -> float:
        """Percentual de indeferimentos."""
        if self.total_decisoes == 0:
            return 0.0
        return (self.indeferimentos / self.total_decisoes) * 100


class AnaliseMagistrados:
    """
    Analisa padrões de decisão dos magistrados do TJDFT.
    
    Example:
        >>> analise = AnaliseMagistrados()
        >>> perfil = analise.perfil_magistrado("CARMEN BITTENCOURT")
        >>> print(perfil.percentual_deferimento)
        75.5
    """
    
    API_URL = "https://jurisdf.tjdft.jus.br/api/v1/pesquisa"
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
    def buscar(self, query: str, tamanho: int = 100) -> List[Dict[str, Any]]:
        """Busca decisões na API."""
        payload = {
            "query": query,
            "pagina": 0,
            "tamanho": tamanho
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "TJDFT-API-Client/0.2.0"
        }
        
        try:
            response = requests.post(
                self.API_URL,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            return data.get('registros', [])
            
        except Exception:
            return []
    
    def analisar_por_tema(
        self,
        tema: str,
        tamanho: int = 100
    ) -> List[PerfilMagistrado]:
        """
        Analisa decisões de todos os magistrados sobre um tema.
        
        Args:
            tema: Termo de busca
            tamanho: Quantidade de decisões a analisar
            
        Returns:
            Lista de PerfilMagistrado ordenada por volume
        """
        registros = self.buscar(tema, tamanho)
        
        # Agrupar por relator
        ementas_por_relator = defaultdict(list)
        orgaos_por_relator = defaultdict(set)
        
        for r in registros:
            relator = r.get('nomeRelator', r.get('nome_relator', 'N/A'))
            if relator and relator != 'N/A':
                ementas_por_relator[relator].append(r.get('ementa', '').lower())
                orgaos_por_relator[relator].add(r.get('descricaoOrgaoJulgador', r.get('orgao_julgador', 'N/A')))
        
        # Criar perfis
        perfis = []
        
        for nome, ementas in ementas_por_relator.items():
            total = len(ementas)
            
            deferimentos = sum(
                1 for e in ementas 
                if any(p in e for p in ['provimento', 'deferido', 'acolhido', 'provido', 'deferir'])
            )
            
            indeferimentos = sum(
                1 for e in ementas 
                if any(p in e for p in ['improvimento', 'indeferido', 'não provido', 'desprovido', 'indeferir'])
            )
            
            parciais = sum(
                1 for e in ementas 
                if 'parcial' in e
            )
            
            # Identificar temas comuns
            temas = Counter()
            palavras_chave = [
                'dano moral', 'tutela', 'urgência', 'obrigação', 
                'fazenda pública', 'contrato', 'consumidor',
                'defesa do consumidor', 'administrativo', 'civil',
                'penal', 'trabalhista', 'tributário'
            ]
            
            for e in ementas:
                for p in palavras_chave:
                    if p in e:
                        temas[p] += 1
            
            temas_comuns = [
                t for t, c in temas.most_common(5)
                if c > total * 0.2
            ]
            
            perfis.append(PerfilMagistrado(
                nome=nome,
                total_decisoes=total,
                deferimentos=deferimentos,
                indeferimentos=indeferimentos,
                parciais=parciais,
                orgaos=list(orgaos_por_relator[nome])[:3],
                temas_comuns=temas_comuns
            ))
        
        # Ordenar por volume
        perfis.sort(key=lambda p: p.total_decisoes, reverse=True)
        
        return perfis
    
    def perfil_magistrado(
        self,
        nome: str,
        tema: Optional[str] = None,
        tamanho: int = 100
    ) -> Optional[PerfilMagistrado]:
        """
        Obtém perfil de um magistrado específico.
        
        Args:
            nome: Nome do magistrado
            tema: Tema para filtrar (opcional)
            tamanho: Quantidade de decisões
            
        Returns:
            PerfilMagistrado ou None se não encontrado
        """
        query = f'nomeRelator:"{nome}"'
        if tema:
            query = f'{tema} {query}'
        
        registros = self.buscar(query, tamanho)
        
        if not registros:
            return None
        
        ementas = [r.get('ementa', '').lower() for r in registros]
        orgaos = set(r.get('descricaoOrgaoJulgador', r.get('orgao_julgador', 'N/A')) for r in registros)
        
        deferimentos = sum(
            1 for e in ementas 
            if any(p in e for p in ['provimento', 'deferido', 'acolhido', 'provido'])
        )
        
        indeferimentos = sum(
            1 for e in ementas 
            if any(p in e for p in ['improvimento', 'indeferido', 'não provido', 'desprovido'])
        )
        
        parciais = sum(1 for e in ementas if 'parcial' in e)
        
        return PerfilMagistrado(
            nome=nome,
            total_decisoes=len(ementas),
            deferimentos=deferimentos,
            indeferimentos=indeferimentos,
            parciais=parciais,
            orgaos=list(orgaos)[:3]
        )
    
    def comparar_magistrados(
        self,
        nomes: List[str],
        tema: str,
        tamanho: int = 50
    ) -> Dict[str, PerfilMagistrado]:
        """
        Compara perfis de múltiplos magistrados.
        
        Args:
            nomes: Lista de nomes de magistrados
            tema: Tema para comparar
            tamanho: Decisões por magistrado
            
        Returns:
            Dicionário nome -> PerfilMagistrado
        """
        resultados = {}
        
        for nome in nomes:
            perfil = self.perfil_magistrado(nome, tema, tamanho)
            if perfil:
                resultados[nome] = perfil
        
        return resultados
    
    def magistrados_por_deferimento(
        self,
        tema: str,
        tamanho: int = 100,
        min_decisoes: int = 5
    ) -> List[PerfilMagistrado]:
        """
        Retorna magistrados ordenados por taxa de deferimento.
        
        Args:
            tema: Termo de busca
            tamanho: Quantidade de decisões
            min_decisoes: Mínimo de decisões para incluir
            
        Returns:
            Lista ordenada por percentual de deferimento
        """
        perfis = self.analisar_por_tema(tema, tamanho)
        
        # Filtrar por mínimo de decisões
        perfis = [p for p in perfis if p.total_decisoes >= min_decisoes]
        
        # Ordenar por deferimento
        perfis.sort(key=lambda p: p.percentual_deferimento, reverse=True)
        
        return perfis
