#!/usr/bin/env python3
"""
Testes de performance comparando cliente original vs otimizado.

Executa benchmarks para medir:
- Response time
- Throughput (requests/sec)
- Cache hit ratio
- Rate limiting effectiveness
"""

import time
import sys
sys.path.insert(0, "src")

from tjdft.client import TJDFTClient
from tjdft.client_optimized import TJDFTClientOptimized
import statistics


def benchmark_client(client, queries: list, iterations: int = 3):
    """Benchmark a client with multiple queries."""
    results = []
    
    for i in range(iterations):
        for query in queries:
            start = time.time()
            
            try:
                result = client.pesquisar(query=query, tamanho=10)
                elapsed = (time.time() - start) * 1000  # ms
                
                results.append({
                    "query": query,
                    "iteration": i,
                    "time_ms": elapsed,
                    "total_results": result.total,
                    "success": True
                })
            except Exception as e:
                elapsed = (time.time() - start) * 1000
                results.append({
                    "query": query,
                    "iteration": i,
                    "time_ms": elapsed,
                    "error": str(e),
                    "success": False
                })
    
    return results


def print_stats(results, name):
    """Print statistics from benchmark results."""
    times = [r["time_ms"] for r in results if r["success"]]
    
    if not times:
        print(f"\n{name}: Nenhum resultado bem-sucedido")
        return
    
    total = len(results)
    success = len(times)
    
    print(f"\n{'='*60}")
    print(f" {name}")
    print(f"{'='*60}")
    print(f"  Total requests: {total}")
    print(f"  Successful: {success} ({success/total*100:.1f}%)")
    print(f"\n  Response Time (ms):")
    print(f"    Min:    {min(times):.1f}")
    print(f"    Max:    {max(times):.1f}")
    print(f"    Avg:    {statistics.mean(times):.1f}")
    print(f"    Median: {statistics.median(times):.1f}")
    print(f"    P95:    {sorted(times)[int(len(times)*0.95)]:.1f}")
    print(f"\n  Throughput:")
    print(f"    {len(times)/sum(times)*1000:.1f} requests/sec")


def test_cache_effectiveness():
    """Test cache hit ratio."""
    print("\n" + "="*60)
    print(" TESTE: Cache Effectiveness")
    print("="*60)
    
    client = TJDFTClientOptimized(cache_ttl=60)
    
    query = "dano moral"
    
    # First request (cache miss)
    start = time.time()
    result1 = client.pesquisar(query=query, tamanho=20)
    time1 = (time.time() - start) * 1000
    
    print(f"\n  1st request (cache miss): {time1:.1f}ms")
    
    # Second request (cache hit)
    start = time.time()
    result2 = client.pesquisar(query=query, tamanho=20)
    time2 = (time.time() - start) * 1000
    
    print(f"  2nd request (cache hit):  {time2:.1f}ms")
    
    # Speedup
    speedup = time1 / time2 if time2 > 0 else 0
    print(f"\n  🚀 Cache speedup: {speedup:.1f}x faster")
    
    # Metrics
    metrics = client.get_metrics()
    print(f"\n  Metrics:")
    print(f"    Cache hits: {metrics['cache_hits']}")
    print(f"    Cache misses: {metrics['cache_misses']}")
    print(f"    Hit ratio: {metrics['cache_hit_ratio']:.1%}")


def test_parallel_requests():
    """Test parallel batch requests."""
    print("\n" + "="*60)
    print(" TESTE: Parallel Batch Requests")
    print("="*60)
    
    client = TJDFTClientOptimized(rate_limit=5, rate_burst=10)
    
    queries = [
        {"query": "dano moral"},
        {"query": "habeas corpus"},
        {"query": "obrigação de fazer"},
        {"query": "tutela de urgência"},
        {"query": "contrato"},
    ]
    
    # Sequential
    start = time.time()
    for q in queries:
        client.pesquisar(**q, use_cache=False)
    sequential_time = (time.time() - start) * 1000
    
    # Clear cache for fair comparison
    client.clear_cache()
    
    # Parallel
    start = time.time()
    results = client.pesquisar_lote(queries, max_parallel=5)
    parallel_time = (time.time() - start) * 1000
    
    print(f"\n  Queries: {len(queries)}")
    print(f"\n  Sequential: {sequential_time:.1f}ms")
    print(f"  Parallel:   {parallel_time:.1f}ms")
    
    speedup = sequential_time / parallel_time if parallel_time > 0 else 0
    print(f"\n  🚀 Parallel speedup: {speedup:.1f}x faster")
    
    # Results
    print(f"\n  Results per query:")
    for i, r in enumerate(results):
        print(f"    {i+1}. {r.total} results")


def test_rate_limiting():
    """Test rate limiting."""
    print("\n" + "="*60)
    print(" TESTE: Rate Limiting")
    print("="*60)
    
    client = TJDFTClientOptimized(rate_limit=5, rate_burst=5)
    
    print("\n  Rate limit: 5 req/s")
    print("  Burst: 5")
    print("\n  Making 10 rapid requests...")
    
    start = time.time()
    for i in range(10):
        client.pesquisar(query=f"teste {i}", tamanho=1, use_cache=False)
    total_time = time.time() - start
    
    print(f"\n  Total time: {total_time:.1f}s")
    print(f"  Actual rate: {10/total_time:.1f} req/s")
    
    metrics = client.get_metrics()
    print(f"\n  Metrics:")
    print(f"    Requests: {metrics['total_requests']}")
    print(f"    Successful: {metrics['successful_requests']}")


def main():
    print("="*60)
    print(" TJDFT API CLIENT - PERFORMANCE TESTS")
    print("="*60)
    
    queries = [
        "dano moral",
        "habeas corpus",
        "obrigação de fazer"
    ]
    
    # Test original client
    print("\n\n📊 BENCHMARK: Cliente Original")
    original_client = TJDFTClient()
    original_results = benchmark_client(original_client, queries, iterations=2)
    print_stats(original_results, "Cliente Original")
    
    # Test optimized client (cold cache)
    print("\n\n📊 BENCHMARK: Cliente Otimizado (cold cache)")
    optimized_client = TJDFTClientOptimized()
    optimized_results = benchmark_client(optimized_client, queries, iterations=2)
    print_stats(optimized_results, "Cliente Otimizado (cold)")
    
    # Test optimized client (warm cache)
    print("\n\n📊 BENCHMARK: Cliente Otimizado (warm cache)")
    optimized_results_warm = benchmark_client(optimized_client, queries, iterations=2)
    print_stats(optimized_results_warm, "Cliente Otimizado (warm)")
    
    # Additional tests
    test_cache_effectiveness()
    test_parallel_requests()
    test_rate_limiting()
    
    # Final metrics
    print("\n" + "="*60)
    print(" 📊 MÉTRICAS FINAIS - CLIENTE OTIMIZADO")
    print("="*60)
    metrics = optimized_client.get_metrics()
    for k, v in metrics.items():
        print(f"  {k}: {v}")
    
    print("\n" + "="*60)
    print(" ✅ TESTES CONCLUÍDOS")
    print("="*60)


if __name__ == "__main__":
    main()
