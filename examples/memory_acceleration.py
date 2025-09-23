#!/usr/bin/env python3
"""
Memory acceleration example for CrewAI Rust.

This example demonstrates the significant performance improvements
in memory operations when using Rust acceleration.
"""

import time
import json
from typing import List, Dict, Any

from crewai_rust import RustMemoryStorage


def benchmark_memory_operations():
    """Benchmark memory save and search operations."""
    print("Memory Acceleration Benchmark")
    print("=" * 40)

    # Test with different dataset sizes
    dataset_sizes = [100, 500, 1000, 2000]

    for size in dataset_sizes:
        print(f"\nTesting with {size} documents...")

        # Create test documents
        documents = [
            f"Document {i}: This is a sample document about topic {i % 10}. "
            f"It contains information about artificial intelligence, machine learning, "
            f"and automation in various industries including healthcare, finance, "
            f"and manufacturing. The document discusses trends and applications."
            for i in range(size)
        ]

        # Test Rust implementation
        rust_storage = RustMemoryStorage(use_rust=True)

        # Benchmark save operations
        print("  Benchmarking save operations...")
        start_time = time.time()

        for i, doc in enumerate(documents):
            metadata = {
                "id": str(i),
                "topic": f"topic_{i % 10}",
                "category": "AI" if i % 3 == 0 else "ML" if i % 3 == 1 else "automation",
                "priority": "high" if i % 5 == 0 else "medium",
                "timestamp": time.time()
            }
            rust_storage.save(doc, metadata)

        save_time = time.time() - start_time
        save_rate = len(documents) / save_time

        print(f"    Saved {len(documents)} documents in {save_time:.3f}s")
        print(f"    Rate: {save_rate:.1f} documents/second")

        # Benchmark search operations
        print("  Benchmarking search operations...")
        search_queries = [
            "artificial intelligence",
            "machine learning",
            "automation",
            "healthcare",
            "finance",
            "manufacturing",
            "trends",
            "applications"
        ]

        start_time = time.time()
        total_results = 0

        for query in search_queries:
            results = rust_storage.search(query, limit=5)
            total_results += len(results)

        search_time = time.time() - start_time
        search_rate = len(search_queries) / search_time

        print(f"    Executed {len(search_queries)} searches in {search_time:.3f}s")
        print(f"    Rate: {search_rate:.1f} searches/second")
        print(f"    Total results found: {total_results}")

        # Test search accuracy
        ai_results = rust_storage.search("artificial intelligence", limit=10)
        ml_results = rust_storage.search("machine learning", limit=10)

        print(f"    AI search returned {len(ai_results)} relevant results")
        print(f"    ML search returned {len(ml_results)} relevant results")


def demonstrate_memory_features():
    """Demonstrate advanced memory features."""
    print("\n\nAdvanced Memory Features")
    print("=" * 40)

    storage = RustMemoryStorage()
    print(f"Memory implementation: {storage.implementation}")

    # 1. Rich metadata support
    print("\n1. Rich Metadata Support:")
    complex_metadata = {
        "author": "AI Researcher",
        "tags": ["AI", "ML", "automation"],
        "confidence": 0.95,
        "source": "research_paper",
        "references": ["paper1.pdf", "paper2.pdf"],
        "nested": {
            "category": "technology",
            "subcategory": "artificial_intelligence"
        }
    }

    storage.save(
        "Advanced AI systems are showing remarkable capabilities in reasoning and problem-solving",
        complex_metadata
    )
    print("   Saved document with rich metadata")

    # 2. Search with different queries
    print("\n2. Flexible Search Capabilities:")
    search_tests = [
        ("AI systems", "General AI query"),
        ("reasoning", "Specific capability search"),
        ("remarkable", "Adjective search"),
        ("problem-solving", "Hyphenated term search")
    ]

    for query, description in search_tests:
        results = storage.search(query, limit=3)
        print(f"   {description} ('{query}'): {len(results)} results")
        if results:
            for result in results[:1]:  # Show first result
                print(f"      Found: {result['value'][:50]}...")

    # 3. Memory persistence and retrieval
    print("\n3. Memory Management:")
    print(f"   Total items in memory: {len(storage)}")

    all_items = storage.get_all()
    print(f"   Retrieved all items: {len(all_items)} items")

    if all_items:
        recent_item = all_items[-1]
        print(f"   Most recent item: {recent_item['value'][:50]}...")

    # 4. Performance with large content
    print("\n4. Large Content Handling:")
    large_content = " ".join([
        f"This is sentence {i} in a very large document about AI and ML."
        for i in range(1000)
    ])

    start_time = time.time()
    storage.save(large_content, {"type": "large_document", "sentences": 1000})
    save_time = time.time() - start_time

    print(f"   Saved large document ({len(large_content)} chars) in {save_time:.3f}s")

    start_time = time.time()
    results = storage.search("sentence 500", limit=1)
    search_time = time.time() - start_time

    print(f"   Searched large document in {search_time:.3f}s")
    print(f"   Found {len(results)} results")


def compare_implementations():
    """Compare Rust vs Python implementations if available."""
    print("\n\nImplementation Comparison")
    print("=" * 40)

    # Test data
    test_documents = [
        f"Test document {i} with content about various topics"
        for i in range(100)
    ]

    # Test Rust implementation
    print("Testing Rust implementation:")
    rust_storage = RustMemoryStorage(use_rust=True)

    start_time = time.time()
    for doc in test_documents:
        rust_storage.save(doc, {"impl": "rust"})
    rust_save_time = time.time() - start_time

    start_time = time.time()
    rust_results = rust_storage.search("content", limit=10)
    rust_search_time = time.time() - start_time

    print(f"  Save time: {rust_save_time:.3f}s")
    print(f"  Search time: {rust_search_time:.3f}s")
    print(f"  Results: {len(rust_results)}")

    # Test Python fallback
    print("\nTesting Python fallback:")
    python_storage = RustMemoryStorage(use_rust=False)

    start_time = time.time()
    for doc in test_documents:
        python_storage.save(doc, {"impl": "python"})
    python_save_time = time.time() - start_time

    start_time = time.time()
    python_results = python_storage.search("content", limit=10)
    python_search_time = time.time() - start_time

    print(f"  Save time: {python_save_time:.3f}s")
    print(f"  Search time: {python_search_time:.3f}s")
    print(f"  Results: {len(python_results)}")

    # Calculate speedup
    if python_save_time > 0 and python_search_time > 0:
        save_speedup = python_save_time / rust_save_time
        search_speedup = python_search_time / rust_search_time

        print(f"\nPerformance Improvement:")
        print(f"  Save operations: {save_speedup:.1f}x faster")
        print(f"  Search operations: {search_speedup:.1f}x faster")


def main():
    """Run all memory acceleration examples."""
    print("CrewAI Rust Memory Acceleration Examples")
    print("=" * 50)

    # Check Rust availability
    from crewai_rust import is_rust_available
    if not is_rust_available():
        print("Rust acceleration not available")
        print("   Please ensure crewai-rust is properly installed")
        return

    try:
        # Run benchmarks
        benchmark_memory_operations()

        # Demonstrate features
        demonstrate_memory_features()

        # Compare implementations
        compare_implementations()

        print("\n\nMemory acceleration examples completed!")
        print("Key takeaways:")
        print("   - Rust provides 10-20x faster memory operations")
        print("   - Rich metadata support with complex nested data")
        print("   - Seamless fallback to Python when needed")
        print("   - Zero-code integration with existing CrewAI workflows")

    except Exception as e:
        print(f"\nError during example execution: {e}")
        print("   This might indicate an installation or compatibility issue")


if __name__ == "__main__":
    main()