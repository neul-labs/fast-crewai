use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyTuple};
use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};
use std::collections::HashMap;

/// A high-performance memory storage system
#[pyclass]
pub struct RustMemoryStorage {
    data: Arc<Mutex<Vec<String>>>,
}

#[pymethods]
impl RustMemoryStorage {
    #[new]
    pub fn new() -> Self {
        RustMemoryStorage {
            data: Arc::new(Mutex::new(Vec::new())),
        }
    }

    pub fn save(&self, value: &str) -> PyResult<()> {
        let mut data = self.data.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to acquire lock: {}",
                e
            ))
        })?;
        data.push(value.to_string());
        Ok(())
    }

    pub fn get_all(&self) -> PyResult<Vec<String>> {
        let data = self.data.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to acquire lock: {}",
                e
            ))
        })?;
        Ok(data.clone())
    }

    pub fn search(&self, query: &str) -> PyResult<Vec<String>> {
        let data = self.data.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to acquire lock: {}",
                e
            ))
        })?;
        let results: Vec<String> = data
            .iter()
            .filter(|item| item.contains(query))
            .cloned()
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
        let current_count = *count;
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

    pub fn execute_query(&self, query: &str, params: &PyDict) -> PyResult<Vec<HashMap<String, String>>> {
        let pool = self.connection_pool.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to acquire pool lock: {}",
                e
            ))
        })?;
        
        let conn = pool.get().map_err(|e| {
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

    pub fn execute_update(&self, query: &str, params: &PyDict) -> PyResult<usize> {
        let pool = self.connection_pool.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to acquire pool lock: {}",
                e
            ))
        })?;
        
        let conn = pool.get().map_err(|e| {
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