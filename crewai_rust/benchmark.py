"""
Benchmarking utilities for CrewAI Rust integration.

This module provides comprehensive benchmarking tools to measure
performance improvements from Rust integration.
"""

import time
import json
import random
import string
from typing import Any, Dict, List
from .memory import RustMemoryStorage
from .tools import RustToolExecutor
from .tasks import RustTaskExecutor
from .serialization import AgentMessage, RustSerializer
from .database import RustSQLiteWrapper


class PerformanceBenchmark:
    """
    Comprehensive benchmarking suite for CrewAI Rust integration.
    """
    
    def __init__(self, iterations: int = 1000):
        """
        Initialize the benchmark suite.
        
        Args:
            iterations: Number of iterations for each benchmark
        """
        self.iterations = iterations
        self.results = {}
    
    def benchmark_memory_storage(self) -> Dict[str, Any]:
        """
        Benchmark memory storage performance.
        
        Returns:
            Dictionary with benchmark results
        """
        # Generate test data
        test_data = [
            {
                'value': f"Test item {i} " + ''.join(random.choices(string.ascii_letters, k=50)),
                'metadata': {
                    'id': i,
                    'category': random.choice(['A', 'B', 'C']),
                    'priority': random.randint(1, 10)
                }
            }
            for i in range(self.iterations)
        ]
        
        search_queries = [
            "Test item",
            "category A",
            "priority 5",
            "nonexistent",
            "random text"
        ]
        
        # Benchmark Python implementation
        python_results = self._benchmark_python_memory(test_data, search_queries)
        
        # Benchmark Rust implementation
        rust_results = self._benchmark_rust_memory(test_data, search_queries)
        
        # Calculate improvements
        improvements = {}
        for key in python_results:
            if key in rust_results and rust_results[key] > 0:
                improvements[key] = python_results[key] / rust_results[key]
            else:
                improvements[key] = float('inf')
        
        return {
            'python': python_results,
            'rust': rust_results,
            'improvements': improvements
        }
    
    def _benchmark_python_memory(self, test_data: List[Dict], search_queries: List[str]) -> Dict[str, float]:
        """Benchmark Python memory implementation."""
        # Simple list-based storage for comparison
        storage = []
        
        # Benchmark save operations
        start_time = time.time()
        for item in test_data:
            storage.append(item)
        save_time = time.time() - start_time
        
        # Benchmark search operations
        start_time = time.time()
        for query in search_queries:
            results = [item for item in storage if query in str(item)]
        search_time = time.time() - start_time
        
        return {
            'save_time': save_time,
            'search_time': search_time,
            'operations_per_second': {
                'save': len(test_data) / save_time if save_time > 0 else 0,
                'search': (len(search_queries) * len(test_data)) / search_time if search_time > 0 else 0
            }
        }
    
    def _benchmark_rust_memory(self, test_data: List[Dict], search_queries: List[str]) -> Dict[str, float]:
        """Benchmark Rust memory implementation."""
        try:
            # Initialize Rust memory storage
            rust_storage = RustMemoryStorage(use_rust=True)
            
            # Benchmark save operations
            start_time = time.time()
            for item in test_data:
                rust_storage.save(item['value'], item['metadata'])
            save_time = time.time() - start_time
            
            # Benchmark search operations
            start_time = time.time()
            for query in search_queries:
                results = rust_storage.search(query)
            search_time = time.time() - start_time
            
            return {
                'save_time': save_time,
                'search_time': search_time,
                'operations_per_second': {
                    'save': len(test_data) / save_time if save_time > 0 else 0,
                    'search': (len(search_queries) * len(test_data)) / search_time if search_time > 0 else 0
                }
            }
        except Exception as e:
            # Return zero performance if Rust implementation fails
            return {
                'save_time': 0,
                'search_time': 0,
                'operations_per_second': {
                    'save': 0,
                    'search': 0
                }
            }
    
    def benchmark_tool_execution(self) -> Dict[str, Any]:
        """
        Benchmark tool execution performance.
        
        Returns:
            Dictionary with benchmark results
        """
        # Generate test data
        test_tools = [
            (f"tool_{i}", {"param1": f"value{i}", "param2": random.randint(1, 100)})
            for i in range(self.iterations)
        ]
        
        # Benchmark Python implementation
        python_results = self._benchmark_python_tools(test_tools)
        
        # Benchmark Rust implementation
        rust_results = self._benchmark_rust_tools(test_tools)
        
        # Calculate improvements
        improvements = {}
        for key in python_results:
            if key in rust_results and rust_results[key] > 0:
                improvements[key] = python_results[key] / rust_results[key]
            else:
                improvements[key] = float('inf')
        
        return {
            'python': python_results,
            'rust': rust_results,
            'improvements': improvements
        }
    
    def _benchmark_python_tools(self, test_tools: List[tuple]) -> Dict[str, float]:
        """Benchmark Python tool execution."""
        # Simple function-based tool execution for comparison
        def execute_tool(tool_name: str, arguments: Dict) -> str:
            args_str = ", ".join([f"{k}={v}" for k, v in arguments.items()])
            return f"Executed {tool_name} with args: {args_str}"
        
        start_time = time.time()
        for tool_name, args in test_tools:
            result = execute_tool(tool_name, args)
        execution_time = time.time() - start_time
        
        return {
            'execution_time': execution_time,
            'operations_per_second': len(test_tools) / execution_time if execution_time > 0 else 0
        }
    
    def _benchmark_rust_tools(self, test_tools: List[tuple]) -> Dict[str, float]:
        """Benchmark Rust tool execution."""
        try:
            # Initialize Rust tool executor
            rust_executor = RustToolExecutor(use_rust=True, max_recursion_depth=self.iterations)
            
            start_time = time.time()
            for tool_name, args in test_tools:
                result = rust_executor.execute_tool(tool_name, args)
            execution_time = time.time() - start_time
            
            return {
                'execution_time': execution_time,
                'operations_per_second': len(test_tools) / execution_time if execution_time > 0 else 0
            }
        except Exception as e:
            # Return zero performance if Rust implementation fails
            return {
                'execution_time': 0,
                'operations_per_second': 0
            }
    
    def benchmark_serialization(self) -> Dict[str, Any]:
        """
        Benchmark serialization performance.
        
        Returns:
            Dictionary with benchmark results
        """
        # Generate test data
        test_messages = [
            {
                'id': f'{i}',
                'sender': f'agent_{i % 10}',
                'recipient': f'agent_{(i + 1) % 10}',
                'content': f'Test message content {i} with some realistic data ' + ''.join(random.choices(string.ascii_letters, k=100)),
                'timestamp': 1000000 + i
            }
            for i in range(self.iterations)
        ]
        
        # Benchmark Python implementation
        python_results = self._benchmark_python_serialization(test_messages)
        
        # Benchmark Rust implementation
        rust_results = self._benchmark_rust_serialization(test_messages)
        
        # Calculate improvements
        improvements = {}
        for key in python_results:
            if key in rust_results and rust_results[key] > 0:
                improvements[key] = python_results[key] / rust_results[key]
            else:
                improvements[key] = float('inf')
        
        return {
            'python': python_results,
            'rust': rust_results,
            'improvements': improvements
        }
    
    def _benchmark_python_serialization(self, test_messages: List[Dict]) -> Dict[str, float]:
        """Benchmark Python serialization."""
        # Serialization
        start_time = time.time()
        serialized = []
        for msg in test_messages:
            json_str = json.dumps(msg, separators=(',', ':'))
            serialized.append(json_str)
        serialize_time = time.time() - start_time
        
        # Deserialization
        start_time = time.time()
        deserialized = []
        for json_str in serialized:
            msg = json.loads(json_str)
            deserialized.append(msg)
        deserialize_time = time.time() - start_time
        
        return {
            'serialize_time': serialize_time,
            'deserialize_time': deserialize_time,
            'operations_per_second': {
                'serialize': len(test_messages) / serialize_time if serialize_time > 0 else 0,
                'deserialize': len(test_messages) / deserialize_time if deserialize_time > 0 else 0
            }
        }
    
    def _benchmark_rust_serialization(self, test_messages: List[Dict]) -> Dict[str, float]:
        """Benchmark Rust serialization."""
        try:
            # Serialization
            start_time = time.time()
            serialized = []
            for msg in test_messages:
                rust_msg = AgentMessage(
                    id=msg['id'],
                    sender=msg['sender'],
                    recipient=msg['recipient'],
                    content=msg['content'],
                    timestamp=msg['timestamp'],
                    use_rust=True
                )
                json_str = rust_msg.to_json()
                serialized.append(json_str)
            serialize_time = time.time() - start_time
            
            # Deserialization
            start_time = time.time()
            deserialized = []
            for json_str in serialized:
                rust_msg = AgentMessage.from_json(json_str, use_rust=True)
                msg = {
                    'id': rust_msg.id,
                    'sender': rust_msg.sender,
                    'recipient': rust_msg.recipient,
                    'content': rust_msg.content,
                    'timestamp': rust_msg.timestamp
                }
                deserialized.append(msg)
            deserialize_time = time.time() - start_time
            
            return {
                'serialize_time': serialize_time,
                'deserialize_time': deserialize_time,
                'operations_per_second': {
                    'serialize': len(test_messages) / serialize_time if serialize_time > 0 else 0,
                    'deserialize': len(test_messages) / deserialize_time if deserialize_time > 0 else 0
                }
            }
        except Exception as e:
            # Return zero performance if Rust implementation fails
            return {
                'serialize_time': 0,
                'deserialize_time': 0,
                'operations_per_second': {
                    'serialize': 0,
                    'deserialize': 0
                }
            }
    
    def benchmark_database(self) -> Dict[str, Any]:
        """
        Benchmark database performance.
        
        Returns:
            Dictionary with benchmark results
        """
        import tempfile
        import os
        
        # Create temporary database files
        python_db_path = tempfile.mktemp(suffix='.db')
        rust_db_path = tempfile.mktemp(suffix='.db')
        
        try:
            # Generate test data
            test_data = [
                {
                    'task_description': f"Task {i}",
                    'metadata': {"param1": f"value{i}", "param2": random.randint(1, 100)},
                    'datetime': f"2023-01-{i+1:02d} 12:00:00",
                    'score': random.uniform(0.0, 1.0)
                }
                for i in range(min(self.iterations, 1000))  # Limit for database tests
            ]
            
            # Benchmark Python implementation
            python_results = self._benchmark_python_database(python_db_path, test_data)
            
            # Benchmark Rust implementation
            rust_results = self._benchmark_rust_database(rust_db_path, test_data)
            
            # Calculate improvements
            improvements = {}
            for key in python_results:
                if key in rust_results and rust_results[key] > 0:
                    improvements[key] = python_results[key] / rust_results[key]
                else:
                    improvements[key] = float('inf')
            
            return {
                'python': python_results,
                'rust': rust_results,
                'improvements': improvements
            }
        finally:
            # Clean up temporary files
            try:
                os.unlink(python_db_path)
                os.unlink(rust_db_path)
            except:
                pass
    
    def _benchmark_python_database(self, db_path: str, test_data: List[Dict]) -> Dict[str, float]:
        """Benchmark Python database operations."""
        import sqlite3
        
        # Initialize database
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS long_term_memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_description TEXT,
                    metadata TEXT,
                    datetime TEXT,
                    score REAL
                )
            """)
            conn.commit()
        
        # Benchmark insert operations
        start_time = time.time()
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            for item in test_data:
                cursor.execute("""
                    INSERT INTO long_term_memories (task_description, metadata, datetime, score)
                    VALUES (?, ?, ?, ?)
                """, (
                    item['task_description'],
                    json.dumps(item['metadata']),
                    item['datetime'],
                    item['score']
                ))
            conn.commit()
        insert_time = time.time() - start_time
        
        # Benchmark query operations
        start_time = time.time()
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            for item in test_data[:100]:  # Limit query tests
                cursor.execute("""
                    SELECT * FROM long_term_memories 
                    WHERE task_description = ?
                """, (item['task_description'],))
                rows = cursor.fetchall()
        query_time = time.time() - start_time
        
        return {
            'insert_time': insert_time,
            'query_time': query_time,
            'operations_per_second': {
                'insert': len(test_data) / insert_time if insert_time > 0 else 0,
                'query': 100 / query_time if query_time > 0 else 0
            }
        }
    
    def _benchmark_rust_database(self, db_path: str, test_data: List[Dict]) -> Dict[str, float]:
        """Benchmark Rust database operations."""
        try:
            # Initialize Rust database wrapper
            rust_db = RustSQLiteWrapper(db_path, use_rust=True)
            
            # Benchmark insert operations
            start_time = time.time()
            queries = []
            for item in test_data:
                queries.append((
                    """
                    INSERT INTO long_term_memories (task_description, metadata, datetime, score)
                    VALUES (?, ?, ?, ?)
                    """,
                    {
                        'task_description': item['task_description'],
                        'metadata': json.dumps(item['metadata']),
                        'datetime': item['datetime'],
                        'score': item['score']
                    }
                ))
            rust_db.execute_batch(queries)
            insert_time = time.time() - start_time
            
            # Benchmark query operations
            start_time = time.time()
            for item in test_data[:100]:  # Limit query tests
                results = rust_db.execute_query("""
                    SELECT * FROM long_term_memories 
                    WHERE task_description = ?
                """, {'task_description': item['task_description']})
            query_time = time.time() - start_time
            
            return {
                'insert_time': insert_time,
                'query_time': query_time,
                'operations_per_second': {
                    'insert': len(test_data) / insert_time if insert_time > 0 else 0,
                    'query': 100 / query_time if query_time > 0 else 0
                }
            }
        except Exception as e:
            # Return zero performance if Rust implementation fails
            return {
                'insert_time': 0,
                'query_time': 0,
                'operations_per_second': {
                    'insert': 0,
                    'query': 0
                }
            }
    
    def run_all_benchmarks(self) -> Dict[str, Any]:
        """
        Run all benchmarks and return results.
        
        Returns:
            Dictionary with all benchmark results
        """
        print("Running CrewAI Rust Integration Benchmarks...")
        print("=" * 50)
        
        results = {}
        
        # Memory storage benchmark
        print("Benchmarking memory storage...")
        results['memory'] = self.benchmark_memory_storage()
        print(f"  Python: {results['memory']['python']['operations_per_second']['save']:.0f} saves/sec")
        if results['memory']['rust']['operations_per_second']['save'] > 0:
            print(f"  Rust: {results['memory']['rust']['operations_per_second']['save']:.0f} saves/sec")
            print(f"  Improvement: {results['memory']['improvements']['save_time']:.1f}x")
        
        # Tool execution benchmark
        print("\nBenchmarking tool execution...")
        results['tools'] = self.benchmark_tool_execution()
        print(f"  Python: {results['tools']['python']['operations_per_second']:.0f} ops/sec")
        if results['tools']['rust']['operations_per_second'] > 0:
            print(f"  Rust: {results['tools']['rust']['operations_per_second']:.0f} ops/sec")
            print(f"  Improvement: {results['tools']['improvements']['execution_time']:.1f}x")
        
        # Serialization benchmark
        print("\nBenchmarking serialization...")
        results['serialization'] = self.benchmark_serialization()
        print(f"  Python serialize: {results['serialization']['python']['operations_per_second']['serialize']:.0f} ops/sec")
        if results['serialization']['rust']['operations_per_second']['serialize'] > 0:
            print(f"  Rust serialize: {results['serialization']['rust']['operations_per_second']['serialize']:.0f} ops/sec")
            print(f"  Serialization improvement: {results['serialization']['improvements']['serialize_time']:.1f}x")
        
        # Database benchmark
        print("\nBenchmarking database operations...")
        results['database'] = self.benchmark_database()
        print(f"  Python insert: {results['database']['python']['operations_per_second']['insert']:.0f} ops/sec")
        if results['database']['rust']['operations_per_second']['insert'] > 0:
            print(f"  Rust insert: {results['database']['rust']['operations_per_second']['insert']:.0f} ops/sec")
            print(f"  Insert improvement: {results['database']['improvements']['insert_time']:.1f}x")
        
        print("\n" + "=" * 50)
        print("Benchmarking complete!")
        
        self.results = results
        return results
    
    def print_summary(self) -> None:
        """Print a summary of benchmark results."""
        if not self.results:
            print("No benchmark results available. Run benchmarks first.")
            return
        
        print("\nCrewAI Rust Integration Benchmark Summary")
        print("=" * 50)
        
        # Memory improvements
        if self.results.get('memory'):
            mem_improvement = self.results['memory']['improvements'].get('save_time', 0)
            if mem_improvement > 0:
                print(f"Memory Storage: {mem_improvement:.1f}x improvement")
        
        # Tool execution improvements
        if self.results.get('tools'):
            tool_improvement = self.results['tools']['improvements'].get('execution_time', 0)
            if tool_improvement > 0:
                print(f"Tool Execution: {tool_improvement:.1f}x improvement")
        
        # Serialization improvements
        if self.results.get('serialization'):
            ser_improvement = self.results['serialization']['improvements'].get('serialize_time', 0)
            if ser_improvement > 0:
                print(f"Serialization: {ser_improvement:.1f}x improvement")
        
        # Database improvements
        if self.results.get('database'):
            db_improvement = self.results['database']['improvements'].get('insert_time', 0)
            if db_improvement > 0:
                print(f"Database Operations: {db_improvement:.1f}x improvement")
        
        print("=" * 50)


def run_benchmarks():
    """
    Run the benchmark suite and print results.
    """
    benchmark = PerformanceBenchmark(iterations=1000)
    results = benchmark.run_all_benchmarks()
    benchmark.print_summary()
    return results


if __name__ == "__main__":
    run_benchmarks()