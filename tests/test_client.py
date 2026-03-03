"""
Testes para o cliente da API TJDFT.
"""

import pytest
from unittest.mock import Mock, patch
from tjdft import TJDFTClient
from tjdft.models import ResultadoBusca


class TestTJDFTClient:
    """Testes do cliente TJDFT."""

    def test_init(self):
        """Testa inicialização do cliente."""
        client = TJDFTClient(timeout=60)
        assert client.timeout == 60
        assert client.session is not None

    def test_pesquisar_mock(self):
        """Testa pesquisa de jurisprudência com mock."""
        with patch.object(TJDFTClient, 'pesquisar') as mock_pesquisar:
            # Configurar mock
            mock_result = ResultadoBusca(
                resultados=[{
                    "processo": "0710649-40.2025.8.07.0000",
                    "ementa": "Teste de ementa",
                    "nome_relator": "Des. Teste"
                }],
                total=1,
                pagina=0,
                por_pagina=20
            )
            mock_pesquisar.return_value = mock_result

            # Executar
            client = TJDFTClient()
            resultados = client.pesquisar(query="dano moral", tamanho=10)

            # Verificar
            assert resultados.total == 1
            assert len(resultados) == 1
            assert resultados[0]["processo"] == "0710649-40.2025.8.07.0000"

    def test_pesquisar_por_relator(self):
        """Testa pesquisa por relator."""
        with patch.object(TJDFTClient, 'pesquisar') as mock_pesquisar:
            mock_pesquisar.return_value = ResultadoBusca(resultados=[], total=0)
            
            client = TJDFTClient()
            client.pesquisar_por_relator(query="teste", relator="NOME")
            
            # Verificar se chamou pesquisar com filtro correto
            mock_pesquisar.assert_called_once()
            call_args = mock_pesquisar.call_args
            assert call_args[1]["filtros"]["nomeRelator"] == "NOME"


class TestModels:
    """Testes dos modelos de dados."""

    def test_resultado_busca(self):
        """Testa modelo ResultadoBusca."""
        resultado = ResultadoBusca(
            resultados=[{"teste": "valor"}],
            total=100,
            pagina=0,
            por_pagina=20
        )

        assert resultado.total == 100
        assert len(resultado) == 1
        assert resultado.total_paginas == 5
        assert resultado.tem_proxima is True

    def test_resultado_busca_vazio(self):
        """Testa ResultadoBusca vazio."""
        resultado = ResultadoBusca()

        assert resultado.total == 0
        assert len(resultado) == 0
        assert resultado.total_paginas == 0
        assert resultado.tem_proxima is False

    def test_resultado_busca_iteracao(self):
        """Testa iteração sobre ResultadoBusca."""
        dados = [{"id": 1}, {"id": 2}, {"id": 3}]
        resultado = ResultadoBusca(resultados=dados, total=3)

        ids = [r["id"] for r in resultado]
        assert ids == [1, 2, 3]

    def test_resultado_busca_indexing(self):
        """Testa indexação de ResultadoBusca."""
        dados = [{"id": 1}, {"id": 2}]
        resultado = ResultadoBusca(resultados=dados, total=2)

        assert resultado[0] == {"id": 1}
        assert resultado[1] == {"id": 2}
