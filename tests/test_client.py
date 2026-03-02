"""Testes para o cliente TJDFT."""

import pytest
from datetime import date
from unittest.mock import Mock, patch

from tjdft import TJDFTClient
from tjdft.models import Acordao, Decisao, ResultadoBusca


class TestTJDFTClient:
    """Testes para o cliente TJDFT."""
    
    def test_init(self):
        """Testa inicialização do cliente."""
        client = TJDFTClient(timeout=60, retries=5)
        assert client.timeout == 60
        assert client.retries == 5
    
    def test_listar_orgaos_julgadores(self):
        """Testa listagem de órgãos julgadores."""
        client = TJDFTClient()
        orgaos = client.listar_orgaos_julgadores()
        
        assert len(orgaos) > 0
        assert "1ª Turma Criminal" in orgaos
    
    @patch("tjdft.client.requests.Session.get")
    def test_buscar_jurisprudencia_mock(self, mock_get):
        """Testa busca de jurisprudência com mock."""
        # Configura mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "resultados": [
                {
                    "numero": "2024HC123456",
                    "classe": "Habeas Corpus",
                    "assunto": "Direito Penal",
                    "relator": "Des. Fulano",
                    "orgao_julgador": "1ª Turma Criminal",
                    "ementa": "Ementa de teste..."
                }
            ],
            "total": 1,
            "pagina": 1,
            "por_pagina": 20
        }
        mock_get.return_value = mock_response
        
        # Executa teste
        client = TJDFTClient()
        resultados = client.buscar_jurisprudencia(termo="habeas corpus")
        
        assert len(resultados) == 1
        assert resultados.total == 1


class TestModels:
    """Testes para os modelos de dados."""
    
    def test_acordao_from_dict(self):
        """Testa criação de Acordao a partir de dicionário."""
        data = {
            "numero": "2024HC123456",
            "classe": "Habeas Corpus",
            "assunto": "Direito Penal",
            "relator": "Des. Fulano",
            "orgao_julgador": "1ª Turma Criminal",
            "ementa": "Ementa de teste...",
            "turma": "1ª Turma Criminal",
            "unanimidade": True
        }
        
        acordao = Acordao.from_dict(data)
        
        assert acordao.numero == "2024HC123456"
        assert acordao.classe == "Habeas Corpus"
        assert acordao.unanimidade is True
    
    def test_decisao_from_dict(self):
        """Testa criação de Decisao a partir de dicionário."""
        data = {
            "numero": "2024DEC123456",
            "classe": "Decisão Monocrática",
            "assunto": "Direito Civil",
            "relator": "Juiz Ciclano",
            "orgao_julgador": "1ª Vara Cível",
            "ementa": "Ementa de decisão..."
        }
        
        decisao = Decisao.from_dict(data)
        
        assert decisao.numero == "2024DEC123456"
        assert decisao.tipo == "decisao"
    
    def test_resultado_busca(self):
        """Testa resultado de busca."""
        resultado = ResultadoBusca(
            resultados=[],
            total=100,
            pagina=1,
            por_pagina=20
        )
        
        assert resultado.total_paginas == 5
        assert resultado.tem_proxima is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
