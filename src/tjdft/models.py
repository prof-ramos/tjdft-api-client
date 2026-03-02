"""
Modelos de dados para a API do TJDFT.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List, Dict, Any


@dataclass
class ResultadoBusca:
    """Resultado de uma busca na API."""
    resultados: List[Dict[str, Any]] = field(default_factory=list)
    total: int = 0
    pagina: int = 0
    por_pagina: int = 20
    agregacoes: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def total_paginas(self) -> int:
        """Retorna o total de páginas."""
        if self.por_pagina <= 0:
            return 0
        return (self.total + self.por_pagina - 1) // self.por_pagina
    
    @property
    def tem_proxima(self) -> bool:
        """Verifica se há próxima página."""
        return (self.pagina + 1) < self.total_paginas
    
    def __len__(self) -> int:
        return len(self.resultados)
    
    def __iter__(self):
        return iter(self.resultados)
    
    def __getitem__(self, index):
        return self.resultados[index]


@dataclass
class DecisaoBase:
    """Classe base para decisões (mantida para compatibilidade)."""
    numero: str
    classe: str
    assunto: str
    relator: str
    orgao_julgador: str
    data_julgamento: Optional[date] = None
    data_publicacao: Optional[date] = None
    ementa: str = ""
    inteiro_teor_url: str = ""
    
    @classmethod
    def from_dict(cls, data: dict) -> "DecisaoBase":
        """Cria instância a partir de dicionário."""
        return cls(
            numero=data.get("numero", data.get("processo", "")),
            classe=data.get("classe", data.get("descricaoClasseCnj", "")),
            assunto=data.get("assunto", ""),
            relator=data.get("relator", data.get("nomeRelator", "")),
            orgao_julgador=data.get("orgao_julgador", data.get("descricaoOrgaoJulgador", "")),
            data_julgamento=_parse_date(data.get("data_julgamento", data.get("dataJulgamento"))),
            data_publicacao=_parse_date(data.get("data_publicacao", data.get("dataPublicacao"))),
            ementa=data.get("ementa", ""),
            inteiro_teor_url=data.get("inteiro_teor_url", data.get("inteiroTeor", "")),
        )


@dataclass
class Acordao(DecisaoBase):
    """
    Representa um acórdão do TJDFT.
    
    Um acórdão é uma decisão colegiada proferida por uma turma ou câmara.
    """
    tipo: str = "acordao"
    turma: str = ""
    unanimidade: Optional[bool] = None
    votacao: str = ""
    
    @classmethod
    def from_dict(cls, data: dict) -> "Acordao":
        """Cria instância a partir de dicionário."""
        base = super().from_dict(data)
        return cls(
            numero=base.numero,
            classe=base.classe,
            assunto=base.assunto,
            relator=base.relator,
            orgao_julgador=base.orgao_julgador,
            data_julgamento=base.data_julgamento,
            data_publicacao=base.data_publicacao,
            ementa=base.ementa,
            inteiro_teor_url=base.inteiro_teor_url,
            tipo="acordao",
            turma=data.get("turma", data.get("descricaoOrgaoJulgador", "")),
            unanimidade=data.get("unanimidade"),
            votacao=data.get("votacao", ""),
        )


@dataclass
class Decisao(DecisaoBase):
    """
    Representa uma decisão monocrática do TJDFT.
    
    Uma decisão monocrática é proferida por um único juiz/desembargador.
    """
    tipo: str = "decisao"
    juiz: str = ""
    
    @classmethod
    def from_dict(cls, data: dict) -> "Decisao":
        """Cria instância a partir de dicionário."""
        base = super().from_dict(data)
        return cls(
            numero=base.numero,
            classe=base.classe,
            assunto=base.assunto,
            relator=base.relator,
            orgao_julgador=base.orgao_julgador,
            data_julgamento=base.data_julgamento,
            data_publicacao=base.data_publicacao,
            ementa=base.ementa,
            inteiro_teor_url=base.inteiro_teor_url,
            tipo="decisao",
            juiz=data.get("juiz", data.get("nomeRelator", "")),
        )


def _parse_date(value: Optional[str]) -> Optional[date]:
    """Parseia string de data."""
    if not value:
        return None
    
    # Remove timezone se presente
    if "T" in value:
        value = value.split("T")[0]
    
    formatos = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]
    
    for fmt in formatos:
        try:
            return date.strptime(value, fmt)
        except ValueError:
            continue
    
    return None
