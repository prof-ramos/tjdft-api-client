"""
Cliente otimizado para API de Jurisprudência do TJDFT.

Esta version includes:
- Connection pooling with retries
- Multi-level caching (memory + TTL)
- Rate limiting
- Response compression
- Async support
- Parallel batch requests
- Performance metrics

API Oficial: https://jurisdf.tjdft.jus.br/api/v1/pesquisa
"""

import time
import asyncio
from typing import Optional, List, Dict, Any, Callable, TypeVar, Union
from datetime import date
from dataclasses import dataclass, field
from functools import wraps
import gzip
import json
from cachetools import TTLCache, LRUCache
import requests
from requests.adapters import HTTPAdapter

from .models import ResultadoBusca


# Type variables
T = TypeVar('T')


# ============================================================================
# PERFORMANCE METRICS
# ============================================================================

@dataclass
class PerformanceMetrics:
    """Tracks API performance metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_time_ms: float = 0.0
    avg_response_time_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    retries: int = 0
    
    def record_request(self, response_time_ms: float, success: bool, cached: bool = False):
        """Record a request for metrics."""
        self.total_requests += 1
        self.total_time_ms += response_time_ms
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        if cached:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
        
        # Update average
        if self.total_requests > 0:
            self.avg_response_time_ms = self.total_time_ms / self.total_requests
    
    def to_dict(self) -> Dict[str, Any]:
        """Export metrics as dict."""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "avg_response_time_ms": round(self.avg_response_time_ms, 2),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_ratio": self.cache_hits / max(self.cache_misses, 1) if self.cache_misses > 0 else 0,
            "retries": self.retries
        }


# ============================================================================
# RATE LIMITER
# ============================================================================

class RateLimiter:
    """Simple rate limiter using token bucket algorithm."""
    
    def __init__(self, requests_per_second: float = 10, burst: int = 20):
        self.requests_per_second = requests_per_second
        self.burst = burst
        self.tokens = burst
        self.last_update = time.time()
    
    def acquire(self) -> bool:
        """Try to acquire a token. Returns True if allowed."""
        now = time.time()
        elapsed = now - self.last_update
        
        # Add tokens based on elapsed time
        self.tokens = min(
            self.burst,
            self.tokens + elapsed * self.requests_per_second
        )
        self.last_update = now
        
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
    
    def wait_time(self) -> float:
        """Time to wait for next token."""
        if self.tokens >= 1:
            return 0
        return (1 - self.tokens) / self.requests_per_second


# ============================================================================
# RETRY HANDLER
# ============================================================================

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    retryable_exceptions: tuple = (requests.RequestException,)
):
    """Decorator for retry with exponential backoff."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = min(
                            base_delay * (exponential_base ** attempt),
                            max_delay
                        )
                        time.sleep(delay)
                    else:
                        raise
            raise last_exception
        return wrapper
    return decorator


# ============================================================================
# OPTIMIZED CLIENT
# ============================================================================

class TJDFTClientOptimized:
    """
    Optimized client for TJDFT Jurisprudence API.
    
    Features:
    - Connection pooling with retries
    - Multi-level caching (memory + TTL)
    - Rate limiting
    - Response compression
    - Async support
    - Parallel batch requests
    - Performance metrics
    
    Example:
        >>> client = TJDFTClientOptimized()
        >>> resultados = client.pesquisar(query="dano moral")
        >>> print(client.metrics.to_dict())
    """
    
    API_URL = "https://jurisdf.tjdft.jus.br/api/v1/pesquisa"
    
    CAMPOS_FILTRO = [
        "base", "subbase", "origem", "uuid", "identificador",
        "processo", "nomeRelator", "nomeRevisor", "nomeRelatorDesignado",
        "descricaoOrgaoJulgador", "dataJulgamento", "dataPublicacao",
        "descricaoClasseCnj",
    ]
    
    def __init__(
        self,
        timeout: int = 30,
        user_agent: str = "TJDFT-API-Client/0.3.0",
        cache_ttl: int = 300,  # 5 minutes
        cache_maxsize: int = 1000,
        rate_limit: float = 10.0,  # requests per second
        rate_burst: int = 20,
        max_retries: int = 3,
        enable_compression: bool = True,
        pool_connections: int = 10,
        pool_maxsize: int = 100,
    ):
        """Initialize optimized client."""
        self.timeout = timeout
        self.user_agent = user_agent
        self.enable_compression = enable_compression
        
        # Performance metrics
        self.metrics = PerformanceMetrics()
        
        # Rate limiter
        self.rate_limiter = RateLimiter(
            requests_per_second=rate_limit,
            burst=rate_burst
        )
        
        # Multi-level caching
        # L1: Small hot cache (LRU)
        self._hot_cache = LRUCache(maxsize=100)
        # L2: Main cache with TTL
        self._cache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)
        
        # Configure session with connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate" if enable_compression else None,
        })
        
        # Connection pooling
        adapter = HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=3
        )
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # Retry configuration
        self.max_retries = max_retries
    
    def _cache_key(self, query: str, pagina: int, tamanho: int, filtros: Optional[Dict] = None) -> str:
        """Generate cache key for request."""
        filtros_str = json.dumps(filtros, sort_keys=True) if filtros else ""
        return f"{query}|{pagina}|{tamanho}|{filtros_str}"
    
    def _wait_for_rate_limit(self) -> None:
        """Wait if rate limited."""
        while not self.rate_limiter.acquire():
            wait = self.rate_limiter.wait_time()
            time.sleep(wait)
    
    @retry_with_backoff(max_retries=3)
    def pesquisar(
        self,
        query: str,
        pagina: int = 0,
        tamanho: int = 20,
        filtros: Optional[Dict[str, str]] = None,
        use_cache: bool = True,
    ) -> ResultadoBusca:
        """
        Search jurisprudence with optimizations.
        
        Args:
            query: Search term
            pagina: Page number (starts at 0)
            tamanho: Results per page
            filtros: Filters dict
            use_cache: Whether to use cache
            
        Returns:
            ResultadoBusca with results
        """
        # Check cache first
        cache_key = self._cache_key(query, pagina, tamanho, filtros)
        
        if use_cache:
            # Check L1 hot cache
            if cache_key in self._hot_cache:
                self.metrics.record_request(0.1, success=True, cached=True)
                return self._hot_cache[cache_key]
            
            # Check L2 cache
            if cache_key in self._cache:
                result = self._cache[cache_key]
                self.metrics.record_request(0.5, success=True, cached=True)
                # Promote to hot cache
                self._hot_cache[cache_key] = result
                return result
        
        # Rate limiting
        self._wait_for_rate_limit()
        
        # Build payload
        payload = {
            "query": query,
            "pagina": pagina,
            "tamanho": tamanho,
        }
        
        if filtros:
            termos_acessorios = []
            for campo, valor in filtros.items():
                if campo in self.CAMPOS_FILTRO:
                    termos_acessorios.append({"campo": campo, "valor": valor})
            if termos_acessorios:
                payload["termosAcessorios"] = termos_acessorios
        
        # Execute request
        start_time = time.time()
        
        response = self.session.post(
            self.API_URL,
            json=payload,
            timeout=self.timeout
        )
        
        response_time = (time.time() - start_time) * 1000
        
        response.raise_for_status()
        
        # Parse response
        result = self._parse_resposta(response.json())
        
        # Record metrics
        self.metrics.record_request(response_time, success=True, cached=False)
        
        # Cache result
        if use_cache:
            self._cache[cache_key] = result
        
        return result
    
    def pesquisar_lote(
        self,
        consultas: List[Dict[str, Any]],
        max_parallel: int = 5,
    ) -> List[ResultadoBusca]:
        """
        Execute multiple searches in parallel.
        
        Args:
            consultas: List of search params dicts
            max_parallel: Max parallel requests
            
        Returns:
            List of ResultadoBusca
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = [None] * len(consultas)
        
        with ThreadPoolExecutor(max_workers=max_parallel) as executor:
            futures = {
                executor.submit(
                    self.pesquisar,
                    **consulta
                ): i
                for i, consulta in enumerate(consultas)
            }
            
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    # Record failed request
                    self.metrics.record_request(0, success=False, cached=False)
                    results[idx] = ResultadoBusca(resultados=[], total=0)
        
        return results
    
    async def pesquisar_async(
        self,
        query: str,
        pagina: int = 0,
        tamanho: int = 20,
        filtros: Optional[Dict[str, str]] = None,
    ) -> ResultadoBusca:
        """
        Async search using aiohttp.
        
        Args:
            query: Search term
            pagina: Page number
            tamanho: Results per page
            filtros: Filters dict
            
        Returns:
            ResultadoBusca with results
        """
        try:
            import aiohttp
        except ImportError:
            raise ImportError("aiohttp required for async. Install with: pip install aiohttp")
        
        cache_key = self._cache_key(query, pagina, tamanho, filtros)
        
        # Check cache
        if cache_key in self._cache:
            self.metrics.record_request(0.5, success=True, cached=True)
            return self._cache[cache_key]
        
        # Build payload
        payload = {
            "query": query,
            "pagina": pagina,
            "tamanho": tamanho,
        }
        
        if filtros:
            termos_acessorios = []
            for campo, valor in filtros.items():
                if campo in self.CAMPOS_FILTRO:
                    termos_acessorios.append({"campo": campo, "valor": valor})
            if termos_acessorios:
                payload["termosAcessorios"] = termos_acessorios
        
        headers = {
            "User-Agent": self.user_agent,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        start_time = time.time()
        
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(
                self.API_URL,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                data = await response.json()
        
        response_time = (time.time() - start_time) * 1000
        
        result = self._parse_resposta(data)
        
        self.metrics.record_request(response_time, success=True, cached=False)
        self._cache[cache_key] = result
        
        return result
    
    def _parse_resposta(self, data: Dict[str, Any]) -> ResultadoBusca:
        """Parse API response."""
        resultados = []
        
        for registro in data.get("registros", []):
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
                "base": registro.get("base", "").lower(),
                "subbase": registro.get("subbase", ""),
                "possui_inteiro_teor": registro.get("possuiInteiroTeor", False),
            }
            resultados.append(resultado)
        
        return ResultadoBusca(
            resultados=resultados,
            total=data.get("hits", 0),
            pagina=data.get("pagina", 0),
            por_pagina=len(resultados),
            agregacoes=data.get("agregações", {})
        )
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        self._hot_cache.clear()
        self._cache.clear()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return self.metrics.to_dict()
    
    def reset_metrics(self) -> None:
        """Reset performance metrics."""
        self.metrics = PerformanceMetrics()
    
    # Convenience methods (same as original client)
    
    def pesquisar_por_relator(self, query: str, relator: str, tamanho: int = 20) -> ResultadoBusca:
        """Search by relator."""
        return self.pesquisar(query=query, filtros={"nomeRelator": relator}, tamanho=tamanho)
    
    def pesquisar_por_orgao(self, query: str, orgao: str, tamanho: int = 20) -> ResultadoBusca:
        """Search by orgao."""
        return self.pesquisar(query=query, filtros={"descricaoOrgaoJulgador": orgao}, tamanho=tamanho)
    
    def buscar_por_processo(self, numero_processo: str) -> Optional[Dict[str, Any]]:
        """Search by process number."""
        resultados = self.pesquisar(
            query=numero_processo,
            filtros={"processo": numero_processo},
            tamanho=1
        )
        return resultados[0] if resultados else None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
