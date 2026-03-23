"""Performance benchmark module for Wealth platform."""

import os
import sys
import time
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

@dataclass
class BenchmarkResult:
    name: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    p50_time: float
    p95_time: float
    p99_time: float
    ops_per_second: float

class PerformanceBenchmark:
    def __init__(self):
        self.results: List[BenchmarkResult] = []

    def run_benchmark(self, name: str, func, iterations: int = 1000, **kwargs) -> BenchmarkResult:
        """Run a benchmark test on a function."""
        times = []

        for _ in range(iterations):
            start = time.perf_counter()
            func(**kwargs)
            end = time.perf_counter()
            times.append(end - start)

        times.sort()
        total_time = sum(times)

        result = BenchmarkResult(
            name=name,
            iterations=iterations,
            total_time=total_time,
            avg_time=total_time / iterations,
            min_time=times[0],
            max_time=times[-1],
            p50_time=times[int(iterations * 0.5)],
            p95_time=times[int(iterations * 0.95)],
            p99_time=times[int(iterations * 0.99)] if iterations >= 100 else times[-1],
            ops_per_second=iterations / total_time if total_time > 0 else 0
        )

        self.results.append(result)
        return result

    def generate_test_data(self, count: int = 100) -> List[Dict]:
        """Generate mock stock data for testing."""
        symbols = ["000001", "000002", "600000", "600036", "000858", "000333", "600519", "601318"]
        data = []

        for i in range(count):
            symbol = random.choice(symbols)
            base_price = random.uniform(10, 200)
            change = random.uniform(-0.1, 0.1)

            record = {
                "timestamp": (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat(),
                "symbol": symbol,
                "name": f"股票{symbol}",
                "open": round(base_price * (1 + random.uniform(-0.02, 0.02)), 2),
                "high": round(base_price * (1 + random.uniform(0, 0.05)), 2),
                "low": round(base_price * (1 - random.uniform(0, 0.05)), 2),
                "close": round(base_price * (1 + change), 2),
                "volume": random.randint(1_000_000, 100_000_000),
                "amount": round(random.uniform(10_000_000, 1_000_000_000), 2),
                "change_pct": round(change * 100, 2)
            }
            data.append(record)

        return data

    def benchmark_data_processing(self) -> Dict[str, BenchmarkResult]:
        """Benchmark data processing operations."""
        data = self.generate_test_data(1000)
        results = {}

        def filter_data():
            return [d for d in data if d["change_pct"] > 0]

        def sort_data():
            return sorted(data, key=lambda x: x["change_pct"], reverse=True)

        def calculate_stats():
            changes = [d["change_pct"] for d in data]
            return {
                "avg": sum(changes) / len(changes),
                "max": max(changes),
                "min": min(changes)
            }

        def group_by_symbol():
            groups = {}
            for d in data:
                symbol = d["symbol"]
                if symbol not in groups:
                    groups[symbol] = []
                groups[symbol].append(d)
            return groups

        results["filter_data"] = self.run_benchmark("filter_data (1000 records)", filter_data, iterations=500)
        results["sort_data"] = self.run_benchmark("sort_data (1000 records)", sort_data, iterations=500)
        results["calculate_stats"] = self.run_benchmark("calculate_stats (1000 records)", calculate_stats, iterations=500)
        results["group_by_symbol"] = self.run_benchmark("group_by_symbol (1000 records)", group_by_symbol, iterations=500)

        return results

    def benchmark_api_simulation(self) -> Dict[str, BenchmarkResult]:
        """Simulate API endpoint performance."""
        results = {}

        def health_check():
            return {"status": "healthy", "version": "0.3.0"}

        def stock_quote():
            return {
                "symbol": "000001",
                "name": "平安银行",
                "price": round(random.uniform(10, 20), 2),
                "change_pct": round(random.uniform(-5, 5), 2)
            }

        def kline_request():
            return [self.generate_test_data(100) for _ in range(5)]

        results["health_check"] = self.run_benchmark("GET /health", health_check, iterations=1000)
        results["stock_quote"] = self.run_benchmark("POST /stocks/quote", stock_quote, iterations=500)
        results["kline_request"] = self.run_benchmark("POST /stocks/kline", kline_request, iterations=100)

        return results

    def benchmark_caching(self) -> Dict[str, BenchmarkResult]:
        """Benchmark caching operations."""
        from wealth.utils.performance import RequestCache

        cache = RequestCache()
        test_data = self.generate_test_data(100)[0]

        results = {}

        def cache_set():
            key = cache.generate_key("test", random.randint(1, 100))
            cache.set_cached(key, test_data, ttl=60)

        def cache_get():
            key = cache.generate_key("test", random.randint(1, 100))
            return cache.get_cached(key)

        results["cache_set"] = self.run_benchmark("cache_set", cache_set, iterations=1000)
        results["cache_get"] = self.run_benchmark("cache_get", cache_get, iterations=1000)

        return results

    def benchmark_data_serialization(self) -> Dict[str, BenchmarkResult]:
        """Benchmark data serialization."""
        data = self.generate_test_data(1000)

        results = {}

        def serialize_json():
            return json.dumps(data)

        def deserialize_json():
            json_str = json.dumps(data)
            return json.loads(json_str)

        results["serialize_json"] = self.run_benchmark("serialize_json (1000 records)", serialize_json, iterations=100)
        results["deserialize_json"] = self.run_benchmark("deserialize_json (1000 records)", deserialize_json, iterations=100)

        return results

    def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all benchmark tests."""
        print("\n" + "=" * 70)
        print("WEALTH PLATFORM - PERFORMANCE BENCHMARK")
        print("=" * 70)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Python Version: 3.10+")

        all_results = {}

        print("\n[1/5] Data Processing Benchmarks")
        all_results["data_processing"] = self.benchmark_data_processing()

        print("\n[2/5] API Simulation Benchmarks")
        all_results["api_simulation"] = self.benchmark_api_simulation()

        print("\n[3/5] Caching Benchmarks")
        all_results["caching"] = self.benchmark_caching()

        print("\n[4/5] Serialization Benchmarks")
        all_results["serialization"] = self.benchmark_data_serialization()

        print("\n[5/5] Summary")
        self.print_summary(all_results)

        return all_results

    def print_summary(self, results: Dict[str, Any]) -> None:
        """Print benchmark summary."""
        print("\n" + "=" * 70)
        print("BENCHMARK RESULTS SUMMARY")
        print("=" * 70)

        for category, benchmarks in results.items():
            print(f"\n{category.upper().replace('_', ' ')}:")
            print("-" * 60)

            for name, result in benchmarks.items():
                print(f"\n  {result.name}:")
                print(f"    Operations/sec: {result.ops_per_second:,.2f}")
                print(f"    Avg time:      {result.avg_time * 1000:.4f} ms")
                print(f"    P95 time:      {result.p95_time * 1000:.4f} ms")
                print(f"    Min/Max:       {result.min_time * 1000:.4f} / {result.max_time * 1000:.4f} ms")

        print("\n" + "=" * 70)

    def export_results(self, filepath: str) -> None:
        """Export benchmark results to JSON file."""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "results": [
                {
                    "name": r.name,
                    "iterations": r.iterations,
                    "total_time": r.total_time,
                    "avg_time": r.avg_time,
                    "min_time": r.min_time,
                    "max_time": r.max_time,
                    "p50_time": r.p50_time,
                    "p95_time": r.p95_time,
                    "p99_time": r.p99_time,
                    "ops_per_second": r.ops_per_second
                }
                for r in self.results
            ]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        print(f"\nResults exported to: {filepath}")

def main():
    benchmark = PerformanceBenchmark()
    results = benchmark.run_all_benchmarks()
    benchmark.export_results("benchmark_results.json")

if __name__ == "__main__":
    main()
