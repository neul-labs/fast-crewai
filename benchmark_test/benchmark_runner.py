
#!/usr/bin/env python3
"""
Benchmark runner for Fast-CrewAI performance testing.
"""
import os
import sys
import json
from datetime import datetime
from pathlib import Path

def run_benchmarks():
    """Run the Fast-CrewAI benchmark suite."""
    try:
        # Import benchmark module
        from fast_crewai.benchmark import PerformanceBenchmark

        print("="*80)
        print("Fast-CrewAI Performance Benchmark")
        print("="*80)
        print(f"Benchmark started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Iterations: {os.environ.get('ITERATIONS', '300')}")
        print()

        # Print rust availability
        from fast_crewai import is_acceleration_available
        print(f"Rust acceleration available: {is_acceleration_available()}")
        print()

        # Configure benchmark with specified iterations
        iterations = int(os.environ.get('ITERATIONS', '300'))
        benchmark = PerformanceBenchmark(iterations=iterations)

        # Run all benchmarks
        results = benchmark.run_all_benchmarks()

        # Print detailed summary
        benchmark.print_summary()

        # Generate BENCHMARK.md report if requested
        report_output = os.environ.get('BENCHMARK_REPORT_OUTPUT')
        if report_output:
            print()
            print("Generating BENCHMARK.md report...")
            benchmark.generate_benchmark_report(Path(report_output))

        # Print raw results
        print()
        print("Raw Results:")
        print(json.dumps(results, indent=2))

        return results
    except ImportError as e:
        print(f"Error importing benchmark module: {e}")
        print("Make sure Fast-CrewAI is properly installed.")
        return None
    except Exception as e:
        print(f"Error running benchmarks: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    results = run_benchmarks()
    if results is None:
        sys.exit(1)
    else:
        sys.exit(0)
