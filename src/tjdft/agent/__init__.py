"""
Agente de análise de jurisprudência com IA.

Este módulo fornece um agente que combina a API do TJDFT com
modelos de linguagem para análise inteligente de jurisprudência.

Uso:
    from tjdft.agent import JurisprudenciaAgent
    
    agent = JurisprudenciaAgent(api_key="sua-chave-openai")
    analise = agent.analisar_caso(
        descricao="Cliente não recebeu CNH renovada após 30 dias",
        termos_busca=["DETRAN CNH renovação"]
    )
"""

import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from ..client import TJDFTClient
from ..models import ResultadoBusca


@dataclass
class AnaliseJurisprudencial:
    """Resultado da análise de jurisprudência."""
    caso: str
    jurisprudencias_encontradas: int
    analise_ia: str
    jurisprudencias_relevantes: List[Dict[str, Any]]
    sugestoes: List[str]
    precedentes: List[str]


class JurisprudenciaAgent:
    """
    Agente de análise de jurisprudência do TJDFT.
    
    Combina busca na API do TJDFT com análise via IA (OpenAI).
    
    Example:
        >>> agent = JurisprudenciaAgent()
        >>> resultado = agent.analisar_caso(
        ...     descricao="Ação contra DETRAN por não emissão de CNH",
        ...     termos_busca=["DETRAN CNH", "obrigação fazer"]
        ... )
        >>> print(resultado.analise_ia)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        tjdft_client: Optional[TJDFTClient] = None
    ):
        """
        Inicializa o agente.
        
        Args:
            api_key: Chave da API da OpenAI (ou via OPENAI_API_KEY)
            model: Modelo da OpenAI a ser usado (default: gpt-4o-mini)
            tjdft_client: Cliente TJDFT customizado (opcional)
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Chave da API da OpenAI não fornecida. "
                "Defina OPENAI_API_KEY ou passe api_key."
            )
        
        self.model = model
        self.client = tjdft_client or TJDFTClient()
        self._openai_client = None
    
    @property
    def openai_client(self):
        """Lazy loading do cliente OpenAI."""
        if self._openai_client is None:
            try:
                from openai import OpenAI
                self._openai_client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "Biblioteca openai não instalada. "
                    "Instale com: pip install openai"
                )
        return self._openai_client
    
    def buscar_jurisprudencia(
        self,
        termos: List[str],
        filtros: Optional[Dict[str, str]] = None,
        por_termo: int = 10
    ) -> Dict[str, ResultadoBusca]:
        """
        Busca jurisprudência para múltiplos termos.
        
        Args:
            termos: Lista de termos de busca
            filtros: Filtros opcionais
            por_termo: Resultados por termo
            
        Returns:
            Dicionário com resultados por termo
        """
        resultados = {}
        
        for termo in termos:
            resultado = self.client.pesquisar(
                query=termo,
                filtros=filtros,
                tamanho=por_termo
            )
            resultados[termo] = resultado
        
        return resultados
    
    def analisar_caso(
        self,
        descricao: str,
        termos_busca: List[str],
        filtros: Optional[Dict[str, str]] = None,
        contexto_adicional: Optional[str] = None
    ) -> AnaliseJurisprudencial:
        """
        Analisa um caso jurídico buscando jurisprudência relevante.
        
        Args:
            descricao: Descrição do caso
            termos_busca: Termos para busca no TJDFT
            filtros: Filtros opcionais para a busca
            contexto_adicional: Contexto extra para análise
            
        Returns:
            AnaliseJurisprudencial com resultados e análise
        """
        # 1. Buscar jurisprudência
        resultados = self.buscar_jurisprudencia(
            termos=termos_busca,
            filtros=filtros,
            por_termo=5
        )
        
        # 2. Consolidar resultados
        todas_jurisprudencias = []
        for termo, resultado in resultados.items():
            for dec in resultado:
                dec["_termo_busca"] = termo
                todas_jurisprudencias.append(dec)
        
        # 3. Preparar contexto para IA
        contexto = self._preparar_contexto(
            descricao=descricao,
            jurisprudencias=todas_jurisprudencias[:20],  # Limita a 20
            contexto_adicional=contexto_adicional
        )
        
        # 4. Analisar com OpenAI
        analise = self._analisar_com_ia(contexto)
        
        # 5. Retornar resultado estruturado
        return AnaliseJurisprudencial(
            caso=descricao,
            jurisprudencias_encontradas=sum(r.total.get("value", 0) for r in resultados.values()),
            analise_ia=analise.get("analise", ""),
            jurisprudencias_relevantes=analise.get("relevantes", []),
            sugestoes=analise.get("sugestoes", []),
            precedentes=analise.get("precedentes", [])
        )
    
    def _preparar_contexto(
        self,
        descricao: str,
        jurisprudencias: List[Dict[str, Any]],
        contexto_adicional: Optional[str] = None
    ) -> str:
        """Prepara contexto para envio à IA."""
        contexto = f"""
## CASO A ANALISAR

{descricao}

"""

        if contexto_adicional:
            contexto += f"""
## CONTEXTO ADICIONAL

{contexto_adicional}

"""
        
        contexto += "## JURISPRUDÊNCIAS ENCONTRADAS NO TJDFT\n\n"
        
        for i, j in enumerate(jurisprudencias, 1):
            contexto += f"""
### Jurisprudência {i}
- **Processo:** {j.get('processo', 'N/A')}
- **Relator:** {j.get('nome_relator', 'N/A')}
- **Órgão:** {j.get('orgao_julgador', 'N/A')}
- **Data:** {j.get('data_publicacao', 'N/A')}
- **Ementa:** {j.get('ementa', 'N/A')[:500]}...

"""
        
        return contexto
    
    def _analisar_com_ia(self, contexto: str) -> Dict[str, Any]:
        """Envia contexto para análise pela OpenAI."""
        prompt = f"""
Você é um assistente jurídico especialista em direito administrativo e processual civil do TJDFT.

Analise o caso e as jurisprudências fornecidas abaixo. Retorne uma análise estruturada.

{contexto}

---

Por favor, forneça:

1. **ANÁLISE DO CASO:** Avaliação jurídica do caso com base nas jurisprudências encontradas

2. **JURISPRUDÊNCIAS RELEVANTES:** Liste as 3-5 jurisprudências mais relevantes com:
   - Número do processo
   - Relator
   - Trecho relevante da ementa

3. **SUGESTÕES:** Sugestões práticas para a ação judicial

4. **PRECEDENTES:** Cite os números de processo que podem ser usados como precedentes

Retorne em formato JSON:
{{
  "analise": "string com a análise completa",
  "relevantes": [
    {{"processo": "...", "relator": "...", "trecho": "..."}}
  ],
  "sugestoes": ["sugestão 1", "sugestão 2"],
  "precedentes": ["processo 1", "processo 2"]
}}
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um assistente jurídico especialista em direito administrativo brasileiro. Sempre retorne respostas em JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Parsear resposta JSON
            import json
            
            texto = response.choices[0].message.content
            
            try:
                return json.loads(texto)
            except json.JSONDecodeError:
                return {
                    "analise": texto,
                    "relevantes": [],
                    "sugestoes": [],
                    "precedentes": []
                }
            
        except Exception as e:
            return {
                "analise": f"Erro na análise: {str(e)}",
                "relevantes": [],
                "sugestoes": ["Verifique a conexão com a API da OpenAI"],
                "precedentes": []
            }
    
    def resumir_jurisprudencia(self, processo: str) -> str:
        """
        Resume uma jurisprudência específica.
        
        Args:
            processo: Número do processo
            
        Returns:
            Resumo da jurisprudência
        """
        resultados = self.client.pesquisar(
            query=processo,
            filtros={"processo": processo},
            tamanho=1
        )
        
        if not resultados:
            return "Jurisprudência não encontrada."
        
        dec = resultados[0]
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Você é um assistente jurídico. Resuma jurisprudências de forma clara e objetiva."},
                {"role": "user", "content": f"""
Resuma a seguinte jurisprudência do TJDFT de forma clara e objetiva:

**Processo:** {dec.get('processo', 'N/A')}
**Relator:** {dec.get('nome_relator', 'N/A')}
**Órgão:** {dec.get('orgao_julgador', 'N/A')}
**Ementa:** {dec.get('ementa', 'N/A')}

Forneça:
1. Teses principais
2. Decisão
3. Relevância para casos similares
"""}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    def comparar_casos(
        self,
        caso1: str,
        caso2: str,
        termos_busca: List[str]
    ) -> str:
        """
        Compara dois casos com base em jurisprudência.
        
        Args:
            caso1: Descrição do primeiro caso
            caso2: Descrição do segundo caso
            termos_busca: Termos para busca
            
        Returns:
            Análise comparativa
        """
        # Buscar jurisprudência
        resultados = self.buscar_jurisprudencia(termos=termos_busca, por_termo=5)
        
        # Consolidar
        todas = []
        for r in resultados.values():
            todas.extend(list(r))
        
        contexto = f"""
## CASO 1
{caso1}

## CASO 2
{caso2}

## JURISPRUDÊNCIAS RELACIONADAS
"""
        for j in todas[:10]:
            contexto += f"- {j.get('processo')}: {j.get('ementa', '')[:200]}...\n"
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Você é um assistente jurídico especialista em direito comparado."},
                {"role": "user", "content": f"""
{contexto}

Compare os dois casos com base nas jurisprudências encontradas.
Identifique:
1. Similaridades
2. Diferenças
3. Quais jurisprudências se aplicam a cada caso
4. Probabilidade de sucesso em cada caso
"""}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
