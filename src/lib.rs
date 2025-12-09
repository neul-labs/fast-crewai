// Allow non_local_definitions for pyo3 macros (older pyo3 version compatibility)
#![allow(non_local_definitions)]

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyTuple};
use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};
use std::collections::HashMap;

// Add a new struct to store memory items with metadata
#[derive(Debug, Clone)]
#[allow(dead_code)]
struct MemoryItem {
    id: u64,
    content: String,
    // Store word frequencies for TF-IDF computation
    word_frequencies: HashMap<String, f64>,
}

/// A high-performance memory storage system
#[pyclass]
pub struct RustMemoryStorage {
    data: Arc<Mutex<Vec<MemoryItem>>>,
    next_id: Arc<Mutex<u64>>,
}

impl RustMemoryStorage {
    // Helper function to compute word frequencies for TF-IDF (private, not exposed to Python)
    fn compute_word_frequencies(&self, text: &str) -> HashMap<String, f64> {
        let mut frequencies = HashMap::new();
        
        // Tokenize and convert to lowercase
        let lower_text = text.to_lowercase();
        let tokens: Vec<String> = lower_text
            .split(|c: char| c.is_whitespace() || c == '.' || c == ',' || c == '!' || c == '?' || c == ';' || c == ':' || c == '(' || c == ')')
            .filter(|s| !s.is_empty())
            .map(|s| s.to_string())
            .collect();
        
        for token in tokens {
            *frequencies.entry(token).or_insert(0.0) += 1.0;
        }
        
        frequencies
    }
    
    // Helper function to calculate cosine similarity between two word frequency maps (private, not exposed to Python)
    fn calculate_cosine_similarity(&self, query_freq: &HashMap<String, f64>, item_freq: &HashMap<String, f64>) -> f64 {
        // Get all unique terms from both documents
        let mut all_terms = std::collections::HashSet::new();
        for term in query_freq.keys() {
            all_terms.insert(term);
        }
        for term in item_freq.keys() {
            all_terms.insert(term);
        }
        
        // Calculate cosine similarity
        let mut dot_product = 0.0;
        let mut query_norm = 0.0;
        let mut item_norm = 0.0;
        
        for term in &all_terms {
            let query_tf = *query_freq.get(*term).unwrap_or(&0.0);
            let item_tf = *item_freq.get(*term).unwrap_or(&0.0);
            
            dot_product += query_tf * item_tf;
            query_norm += query_tf * query_tf;
            item_norm += item_tf * item_tf;
        }
        
        if query_norm == 0.0 || item_norm == 0.0 {
            return 0.0; // No similarity if one vector is zero
        }
        
        dot_product / (query_norm.sqrt() * item_norm.sqrt())
    }
}

#[pymethods]
impl RustMemoryStorage {
    #[new]
    pub fn new() -> Self {
        RustMemoryStorage {
            data: Arc::new(Mutex::new(Vec::new())),
            next_id: Arc::new(Mutex::new(0)),
        }
    }

    pub fn save(&self, value: &str) -> PyResult<()> {
        let mut data = self.data.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to acquire lock: {}",
                e
            ))
        })?;
        
        let mut next_id = self.next_id.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to acquire id lock: {}",
                e
            ))
        })?;
        
        // Create word frequency map for TF-IDF
        let word_frequencies = self.compute_word_frequencies(value);
        
        let item = MemoryItem {
            id: *next_id,
            content: value.to_string(),
            word_frequencies,
        };
        
        data.push(item);
        *next_id += 1;
        
        Ok(())
    }

    pub fn get_all(&self) -> PyResult<Vec<String>> {
        let data = self.data.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to acquire lock: {}",
                e
            ))
        })?;
        Ok(data.iter().map(|item| item.content.clone()).collect())
    }

    pub fn search(&self, query: &str, limit: usize) -> PyResult<Vec<String>> {
        let data = self.data.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to acquire lock: {}",
                e
            ))
        })?;
        
        // Compute query word frequencies
        let query_frequencies = self.compute_word_frequencies(query);
        
        // Calculate similarity scores for each item
        let mut scored_results: Vec<(String, f64)> = Vec::new();
        
        for item in &*data {
            let similarity = self.calculate_cosine_similarity(&query_frequencies, &item.word_frequencies);
            scored_results.push((item.content.clone(), similarity));
        }
        
        // Sort by similarity score (descending)
        scored_results.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        
        // Take top results up to limit
        let results: Vec<String> = scored_results
            .into_iter()
            .take(limit)
            .map(|(content, _)| content)
            .collect();
            
        Ok(results)
    }
}

/// A stack-safe tool execution engine
#[pyclass]
pub struct RustToolExecutor {
    max_recursion_depth: usize,
    execution_count: Arc<Mutex<usize>>,
}

#[pymethods]
impl RustToolExecutor {
    #[new]
    pub fn new(max_recursion_depth: usize) -> Self {
        RustToolExecutor {
            max_recursion_depth,
            execution_count: Arc::new(Mutex::new(0)),
        }
    }

    pub fn execute_tool(&self, tool_name: &str, args: &str) -> PyResult<String> {
        // Check recursion depth
        let mut count = self.execution_count.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to acquire lock: {}",
                e
            ))
        })?;
        
        if *count >= self.max_recursion_depth {
            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                "Maximum recursion depth exceeded".to_string(),
            ));
        }
        
        *count += 1;
        let _current_count = *count;
        drop(count); // Release the lock
        
        // Simulate tool execution
        let result = format!("Executed {} with args: {}", tool_name, args);
        
        // Decrement count after execution
        let mut count = self.execution_count.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to acquire lock: {}",
                e
            ))
        })?;
        *count -= 1;
        
        Ok(result)
    }
}

/// A message structure for serialization
#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct AgentMessage {
    #[pyo3(get, set)]
    pub id: String,
    #[pyo3(get, set)]
    pub sender: String,
    #[pyo3(get, set)]
    pub recipient: String,
    #[pyo3(get, set)]
    pub content: String,
    #[pyo3(get, set)]
    pub timestamp: u64,
}

#[pymethods]
impl AgentMessage {
    #[new]
    pub fn new(id: &str, sender: &str, recipient: &str, content: &str, timestamp: u64) -> Self {
        AgentMessage {
            id: id.to_string(),
            sender: sender.to_string(),
            recipient: recipient.to_string(),
            content: content.to_string(),
            timestamp,
        }
    }

    pub fn to_json(&self) -> PyResult<String> {
        serde_json::to_string(self).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to serialize to JSON: {}",
                e
            ))
        })
    }

    #[staticmethod]
    pub fn from_json(json_str: &str) -> PyResult<AgentMessage> {
        serde_json::from_str(json_str).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to deserialize from JSON: {}",
                e
            ))
        })
    }
}

/// A concurrent task executor
#[pyclass]
pub struct RustTaskExecutor {
    runtime: Arc<tokio::runtime::Runtime>,
}

#[pymethods]
impl RustTaskExecutor {
    #[new]
    pub fn new() -> PyResult<Self> {
        let runtime = tokio::runtime::Builder::new_multi_thread()
            .enable_all()
            .build()
            .map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                    "Failed to create Tokio runtime: {}",
                    e
                ))
            })?;
            
        Ok(RustTaskExecutor {
            runtime: Arc::new(runtime),
        })
    }

    pub fn execute_concurrent_tasks(&self, tasks: Vec<&str>) -> PyResult<Vec<String>> {
        let runtime = self.runtime.clone();
        
        let results: Result<Vec<String>, PyErr> = Python::with_gil(|py| {
            py.allow_threads(|| {
                runtime.block_on(async {
                    let mut handles = Vec::new();
                    
                    for task in tasks {
                        let task_str = task.to_string();
                        let handle = tokio::spawn(async move {
                            // Simulate some async work
                            tokio::time::sleep(std::time::Duration::from_millis(10)).await;
                            format!("Completed: {}", task_str)
                        });
                        handles.push(handle);
                    }
                    
                    let mut results = Vec::new();
                    for handle in handles {
                        match handle.await {
                            Ok(result) => results.push(result),
                            Err(e) => return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                                format!("Task execution failed: {}", e)
                            )),
                        }
                    }
                    
                    Ok(results)
                })
            })
        });
        
        results
    }
}

/// A high-performance SQLite wrapper
#[pyclass]
pub struct RustSQLiteWrapper {
    connection_pool: Arc<Mutex<r2d2::Pool<r2d2_sqlite::SqliteConnectionManager>>>,
}

#[pymethods]
impl RustSQLiteWrapper {
    #[new]
    pub fn new(db_path: &str, pool_size: u32) -> PyResult<Self> {
        let manager = r2d2_sqlite::SqliteConnectionManager::file(db_path);
        let pool = r2d2::Pool::builder()
            .max_size(pool_size)
            .build(manager)
            .map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                    "Failed to create connection pool: {}",
                    e
                ))
            })?;
            
        // Initialize database schema
        {
            let conn = pool.get().map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                    "Failed to get connection: {}",
                    e
                ))
            })?;
            
            conn.execute(
                "CREATE TABLE IF NOT EXISTS long_term_memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_description TEXT,
                    metadata TEXT,
                    datetime TEXT,
                    score REAL
                )",
                [],
            ).map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                    "Failed to create table: {}",
                    e
                ))
            })?;
        }
            
        Ok(RustSQLiteWrapper {
            connection_pool: Arc::new(Mutex::new(pool)),
        })
    }

    pub fn execute_query(&self, _query: &str, params: &PyDict) -> PyResult<Vec<HashMap<String, String>>> {
        let pool = self.connection_pool.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to acquire pool lock: {}",
                e
            ))
        })?;

        let _conn = pool.get().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to get connection: {}",
                e
            ))
        })?;

        // Convert PyDict to Vec of parameters
        let mut param_vec = Vec::new();
        for (key, value) in params.iter() {
            let key_str: String = key.extract()?;
            let value_str: String = value.extract()?;
            param_vec.push((key_str, value_str));
        }

        // For now, we'll return a simplified result
        // In a full implementation, we'd execute the query and return actual results
        let mut results = Vec::new();
        let mut row = HashMap::new();
        row.insert("status".to_string(), "success".to_string());
        results.push(row);

        Ok(results)
    }

    pub fn execute_update(&self, _query: &str, _params: &PyDict) -> PyResult<usize> {
        let pool = self.connection_pool.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to acquire pool lock: {}",
                e
            ))
        })?;

        let _conn = pool.get().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to get connection: {}",
                e
            ))
        })?;

        // For now, we'll return a simplified result
        // In a full implementation, we'd execute the query and return actual results
        Ok(1)
    }

    pub fn execute_batch(&self, queries: &PyList) -> PyResult<Vec<usize>> {
        let mut results = Vec::new();
        
        for item in queries.iter() {
            // Each item should be a tuple of (query, params)
            if let Ok(tuple) = item.downcast::<PyTuple>() {
                if tuple.len() == 2 {
                    // In a full implementation, we'd execute each query
                    results.push(1);
                }
            }
        }
        
        Ok(results)
    }
}

/// Python module declaration
#[pymodule]
fn _core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<RustMemoryStorage>()?;
    m.add_class::<RustToolExecutor>()?;
    m.add_class::<AgentMessage>()?;
    m.add_class::<RustTaskExecutor>()?;
    m.add_class::<RustSQLiteWrapper>()?;
    Ok(())
}