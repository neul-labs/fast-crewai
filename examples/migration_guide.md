# Migration Guide: Integrating Rust Components into Existing CrewAI Codebase

This guide explains how to gradually integrate Rust components into the existing CrewAI codebase while maintaining backward compatibility.

## Phase 1: Setting Up the Rust Infrastructure

### 1. Install Rust Toolchain
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```

### 2. Install Required Tools
```bash
pip install maturin
```

### 3. Verify Installation
```bash
rustc --version
cargo --version
maturin --version
```

## Phase 2: Building and Testing Rust Components

### 1. Build the Rust Components
```bash
cd /path/to/crewai
maturin develop
```

### 2. Run Tests
```bash
python rust_examples/test_rust_integration.py
```

### 3. Run Performance Benchmarks
```bash
python rust_examples/performance_benchmark.py
```

## Phase 3: Gradual Integration Strategy

### Option A: Feature Flag Approach
Modify existing Python classes to conditionally use Rust implementations:

```python
import os
from crewai_rust import RustMemoryStorage

class ShortTermMemory:
    def __init__(self, *args, **kwargs):
        # Check if Rust implementation is enabled
        self.use_rust = os.getenv('CREWAI_USE_RUST_MEMORY', 'false').lower() == 'true'
        
        if self.use_rust:
            try:
                self._rust_storage = RustMemoryStorage()
            except ImportError:
                print("Rust memory storage not available, falling back to Python implementation")
                self.use_rust = False
        
        # Initialize Python implementation as fallback
        if not self.use_rust:
            # Existing Python implementation
            pass
    
    def save(self, value, metadata=None):
        if self.use_rust:
            try:
                # Use Rust implementation
                import json
                data = {'value': value, 'metadata': metadata}
                serialized = json.dumps(data)
                self._rust_storage.save(serialized)
                return
            except Exception as e:
                print(f"Rust implementation failed, falling back to Python: {e}")
                self.use_rust = False
        
        # Fallback to Python implementation
        # Existing Python code here
        pass
    
    def search(self, query, limit=3, score_threshold=0.35):
        if self.use_rust:
            try:
                # Use Rust implementation
                results = self._rust_storage.search(query)
                # Convert results back to expected format
                import json
                converted_results = []
                for result in results[:limit]:
                    try:
                        data = json.loads(result)
                        converted_results.append(data)
                    except:
                        converted_results.append({'value': result, 'metadata': {}})
                return converted_results
            except Exception as e:
                print(f"Rust implementation failed, falling back to Python: {e}")
                self.use_rust = False
        
        # Fallback to Python implementation
        # Existing Python code here
        pass
```

### Option B: Subclass Approach
Create Rust-enhanced subclasses that inherit from existing classes:

```python
from crewai.memory.short_term.short_term_memory import ShortTermMemory
from crewai_rust import RustMemoryStorage

class RustEnhancedShortTermMemory(ShortTermMemory):
    """
    A Rust-enhanced version of ShortTermMemory that provides better performance
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self._rust_storage = RustMemoryStorage()
            self._rust_available = True
        except ImportError:
            self._rust_available = False
            print("Rust memory storage not available, using standard implementation")
    
    def save(self, value, metadata=None):
        if self._rust_available:
            try:
                # Use high-performance Rust implementation
                import json
                data = {'value': value, 'metadata': metadata}
                serialized = json.dumps(data)
                self._rust_storage.save(serialized)
                return
            except Exception as e:
                print(f"Rust implementation failed: {e}")
        
        # Fallback to parent implementation
        super().save(value, metadata)
    
    def search(self, query, limit=3, score_threshold=0.35):
        if self._rust_available:
            try:
                # Use high-performance Rust implementation
                results = self._rust_storage.search(query)
                # Convert results back to expected format
                import json
                converted_results = []
                for result in results[:limit]:
                    try:
                        data = json.loads(result)
                        converted_results.append(data)
                    except:
                        converted_results.append({'value': result, 'metadata': {}})
                return converted_results
            except Exception as e:
                print(f"Rust implementation failed: {e}")
        
        # Fallback to parent implementation
        return super().search(query, limit, score_threshold)

# Usage in Crew configuration:
# memory = RustEnhancedShortTermMemory(crew=crew, embedder_config=embedder_config)
```

## Phase 4: Performance Monitoring and Optimization

### 1. Add Performance Metrics
```python
import time

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
    
    def record_operation(self, operation_name, duration, implementation):
        if operation_name not in self.metrics:
            self.metrics[operation_name] = {'rust': [], 'python': []}
        
        self.metrics[operation_name][implementation].append(duration)
    
    def get_performance_comparison(self, operation_name):
        if operation_name not in self.metrics:
            return None
        
        rust_times = self.metrics[operation_name]['rust']
        python_times = self.metrics[operation_name]['python']
        
        if not rust_times or not python_times:
            return None
        
        avg_rust = sum(rust_times) / len(rust_times)
        avg_python = sum(python_times) / len(python_times)
        
        return {
            'rust_average': avg_rust,
            'python_average': avg_python,
            'improvement_ratio': avg_python / avg_rust if avg_rust > 0 else float('inf')
        }
```

### 2. Integration with Existing Monitoring
```python
# Example of integrating performance monitoring with existing CrewAI code
class MonitoredShortTermMemory(ShortTermMemory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.monitor = PerformanceMonitor()
        self.use_rust = os.getenv('CREWAI_USE_RUST_MEMORY', 'false').lower() == 'true'
        if self.use_rust:
            try:
                self._rust_storage = RustMemoryStorage()
            except ImportError:
                self.use_rust = False
    
    def save(self, value, metadata=None):
        start_time = time.time()
        
        if self.use_rust:
            try:
                # Rust implementation
                import json
                data = {'value': value, 'metadata': metadata}
                serialized = json.dumps(data)
                self._rust_storage.save(serialized)
                duration = time.time() - start_time
                self.monitor.record_operation('save', duration, 'rust')
                return
            except Exception as e:
                print(f"Rust implementation failed: {e}")
        
        # Python implementation
        super().save(value, metadata)
        duration = time.time() - start_time
        self.monitor.record_operation('save', duration, 'python')
```

## Phase 5: Gradual Rollout Plan

### 1. Development Environment
- Enable Rust components by default in development
- Run comprehensive tests to ensure compatibility
- Monitor performance improvements

### 2. Staging Environment
- Deploy with feature flags to enable selective use
- Run A/B tests comparing performance
- Gather feedback from internal users

### 3. Production Rollout
- Start with low-impact components (memory storage)
- Gradually enable more critical components (tool execution)
- Monitor system performance and stability
- Provide rollback capability if issues arise

## Phase 6: Documentation and Training

### 1. Developer Documentation
- Update API documentation with Rust implementation details
- Provide migration guides for existing users
- Create troubleshooting guides for common issues

### 2. User Documentation
- Explain performance benefits to end users
- Provide configuration examples
- Document any changes in behavior or limitations

## Next Steps

1. **Set up CI/CD** - Configure automated builds and testing for Rust components
2. **Implement feature flags** - Add configuration options to enable/disable Rust components
3. **Create comprehensive tests** - Ensure full test coverage for both implementations
4. **Run performance benchmarks** - Establish baseline performance metrics
5. **Begin gradual rollout** - Start with non-critical components in development

This phased approach ensures a smooth transition to Rust-enhanced components while maintaining backward compatibility and minimizing risk.