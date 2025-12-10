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

/// Tool execution result for caching
#[derive(Debug, Clone)]
struct CachedResult {
    result: String,
    timestamp: std::time::Instant,
}

/// A high-performance tool execution engine with caching and validation
#[pyclass]
pub struct RustToolExecutor {
    max_recursion_depth: usize,
    execution_count: Arc<Mutex<usize>>,
    /// Cache for tool results (tool_name + args_hash -> result)
    result_cache: Arc<Mutex<HashMap<String, CachedResult>>>,
    /// Cache TTL in seconds
    cache_ttl_secs: u64,
    /// Execution statistics
    stats: Arc<Mutex<ExecutionStats>>,
}

#[derive(Debug, Clone, Default)]
struct ExecutionStats {
    total_executions: usize,
    cache_hits: usize,
    cache_misses: usize,
    validation_failures: usize,
}

#[pymethods]
impl RustToolExecutor {
    #[new]
    #[pyo3(signature = (max_recursion_depth, cache_ttl_secs=300))]
    pub fn new(max_recursion_depth: usize, cache_ttl_secs: u64) -> Self {
        RustToolExecutor {
            max_recursion_depth,
            execution_count: Arc::new(Mutex::new(0)),
            result_cache: Arc::new(Mutex::new(HashMap::new())),
            cache_ttl_secs,
            stats: Arc::new(Mutex::new(ExecutionStats::default())),
        }
    }

    /// Validate JSON arguments - returns parsed JSON or error message
    pub fn validate_args(&self, args_json: &str) -> PyResult<bool> {
        match serde_json::from_str::<serde_json::Value>(args_json) {
            Ok(_) => Ok(true),
            Err(e) => {
                let mut stats = self.stats.lock().map_err(|e| {
                    PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Lock error: {}", e))
                })?;
                stats.validation_failures += 1;
                Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                    "Invalid JSON arguments: {}",
                    e
                )))
            }
        }
    }

    /// Parse and normalize JSON arguments for consistent caching
    pub fn parse_args(&self, args_json: &str) -> PyResult<String> {
        let value: serde_json::Value = serde_json::from_str(args_json).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Invalid JSON: {}",
                e
            ))
        })?;

        // Re-serialize with sorted keys for consistent cache keys
        serde_json::to_string(&value).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to serialize: {}",
                e
            ))
        })
    }

    /// Check if we can execute (recursion depth check)
    pub fn can_execute(&self) -> PyResult<bool> {
        let count = self.execution_count.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to acquire lock: {}",
                e
            ))
        })?;
        Ok(*count < self.max_recursion_depth)
    }

    /// Begin execution - returns an execution ID for tracking
    pub fn begin_execution(&self, tool_name: &str, args: &str) -> PyResult<String> {
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

        // Update stats
        let mut stats = self.stats.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Lock error: {}", e))
        })?;
        stats.total_executions += 1;

        // Generate a unique execution ID
        Ok(format!("{}:{}", tool_name, args.len()))
    }

    /// End execution - call this after tool completes
    pub fn end_execution(&self) -> PyResult<()> {
        let mut count = self.execution_count.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to acquire lock: {}",
                e
            ))
        })?;

        if *count > 0 {
            *count -= 1;
        }
        Ok(())
    }

    /// Get cached result if available and not expired
    pub fn get_cached(&self, tool_name: &str, args: &str) -> PyResult<Option<String>> {
        let cache_key = format!("{}:{}", tool_name, args);

        let cache = self.result_cache.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to acquire cache lock: {}",
                e
            ))
        })?;

        if let Some(cached) = cache.get(&cache_key) {
            // Check if cache is still valid
            if cached.timestamp.elapsed().as_secs() < self.cache_ttl_secs {
                let mut stats = self.stats.lock().map_err(|e| {
                    PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Lock error: {}", e))
                })?;
                stats.cache_hits += 1;
                return Ok(Some(cached.result.clone()));
            }
        }

        let mut stats = self.stats.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Lock error: {}", e))
        })?;
        stats.cache_misses += 1;
        Ok(None)
    }

    /// Store result in cache
    pub fn cache_result(&self, tool_name: &str, args: &str, result: &str) -> PyResult<()> {
        let cache_key = format!("{}:{}", tool_name, args);

        let mut cache = self.result_cache.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to acquire cache lock: {}",
                e
            ))
        })?;

        cache.insert(
            cache_key,
            CachedResult {
                result: result.to_string(),
                timestamp: std::time::Instant::now(),
            },
        );

        Ok(())
    }

    /// Clear the result cache
    pub fn clear_cache(&self) -> PyResult<usize> {
        let mut cache = self.result_cache.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to acquire cache lock: {}",
                e
            ))
        })?;

        let count = cache.len();
        cache.clear();
        Ok(count)
    }

    /// Get execution statistics
    pub fn get_stats(&self) -> PyResult<HashMap<String, usize>> {
        let stats = self.stats.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Lock error: {}", e))
        })?;

        let mut result = HashMap::new();
        result.insert("total_executions".to_string(), stats.total_executions);
        result.insert("cache_hits".to_string(), stats.cache_hits);
        result.insert("cache_misses".to_string(), stats.cache_misses);
        result.insert("validation_failures".to_string(), stats.validation_failures);

        // Calculate cache hit rate
        let total_cache_lookups = stats.cache_hits + stats.cache_misses;
        if total_cache_lookups > 0 {
            result.insert(
                "cache_hit_rate_percent".to_string(),
                (stats.cache_hits * 100) / total_cache_lookups,
            );
        }

        Ok(result)
    }

    /// Batch validate multiple tool argument sets
    pub fn batch_validate(&self, args_list: Vec<String>) -> PyResult<Vec<bool>> {
        args_list
            .iter()
            .map(|args| {
                serde_json::from_str::<serde_json::Value>(args)
                    .map(|_| true)
                    .unwrap_or(false)
            })
            .map(Ok)
            .collect()
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

/// Task state for tracking execution
#[derive(Debug, Clone, PartialEq)]
enum TaskState {
    Pending,
    Running,
    Completed,
    Failed,
}

/// A task with dependencies and state tracking
#[derive(Debug, Clone)]
struct TaskInfo {
    dependencies: Vec<String>,
    state: TaskState,
    result: Option<String>,
    error: Option<String>,
}

/// A concurrent task executor with dependency tracking
#[pyclass]
pub struct RustTaskExecutor {
    runtime: Arc<tokio::runtime::Runtime>,
    tasks: Arc<Mutex<HashMap<String, TaskInfo>>>,
    stats: Arc<Mutex<TaskExecutionStats>>,
}

#[derive(Debug, Clone, Default)]
struct TaskExecutionStats {
    tasks_scheduled: usize,
    tasks_completed: usize,
    tasks_failed: usize,
    total_execution_time_ms: u64,
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
            tasks: Arc::new(Mutex::new(HashMap::new())),
            stats: Arc::new(Mutex::new(TaskExecutionStats::default())),
        })
    }

    /// Register a task with optional dependencies
    pub fn register_task(&self, task_id: &str, dependencies: Vec<String>) -> PyResult<()> {
        let mut tasks = self.tasks.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Lock error: {}", e))
        })?;

        tasks.insert(
            task_id.to_string(),
            TaskInfo {
                dependencies,
                state: TaskState::Pending,
                result: None,
                error: None,
            },
        );

        let mut stats = self.stats.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Lock error: {}", e))
        })?;
        stats.tasks_scheduled += 1;

        Ok(())
    }

    /// Check if a task's dependencies are all completed
    pub fn can_execute(&self, task_id: &str) -> PyResult<bool> {
        let tasks = self.tasks.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Lock error: {}", e))
        })?;

        if let Some(task) = tasks.get(task_id) {
            for dep_id in &task.dependencies {
                if let Some(dep_task) = tasks.get(dep_id) {
                    if dep_task.state != TaskState::Completed {
                        return Ok(false);
                    }
                } else {
                    return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                        "Dependency task '{}' not found",
                        dep_id
                    )));
                }
            }
            Ok(true)
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Task '{}' not found",
                task_id
            )))
        }
    }

    /// Get all tasks that are ready to execute (dependencies satisfied)
    pub fn get_ready_tasks(&self) -> PyResult<Vec<String>> {
        let tasks = self.tasks.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Lock error: {}", e))
        })?;

        let mut ready = Vec::new();

        for (task_id, task) in tasks.iter() {
            if task.state != TaskState::Pending {
                continue;
            }

            let mut deps_satisfied = true;
            for dep_id in &task.dependencies {
                if let Some(dep_task) = tasks.get(dep_id) {
                    if dep_task.state != TaskState::Completed {
                        deps_satisfied = false;
                        break;
                    }
                } else {
                    deps_satisfied = false;
                    break;
                }
            }

            if deps_satisfied {
                ready.push(task_id.clone());
            }
        }

        Ok(ready)
    }

    /// Mark a task as started
    pub fn mark_started(&self, task_id: &str) -> PyResult<()> {
        let mut tasks = self.tasks.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Lock error: {}", e))
        })?;

        if let Some(task) = tasks.get_mut(task_id) {
            task.state = TaskState::Running;
            Ok(())
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Task '{}' not found",
                task_id
            )))
        }
    }

    /// Mark a task as completed with a result
    pub fn mark_completed(&self, task_id: &str, result: &str) -> PyResult<()> {
        let mut tasks = self.tasks.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Lock error: {}", e))
        })?;

        if let Some(task) = tasks.get_mut(task_id) {
            task.state = TaskState::Completed;
            task.result = Some(result.to_string());

            let mut stats = self.stats.lock().map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Lock error: {}", e))
            })?;
            stats.tasks_completed += 1;

            Ok(())
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Task '{}' not found",
                task_id
            )))
        }
    }

    /// Mark a task as failed with an error message
    pub fn mark_failed(&self, task_id: &str, error: &str) -> PyResult<()> {
        let mut tasks = self.tasks.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Lock error: {}", e))
        })?;

        if let Some(task) = tasks.get_mut(task_id) {
            task.state = TaskState::Failed;
            task.error = Some(error.to_string());

            let mut stats = self.stats.lock().map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Lock error: {}", e))
            })?;
            stats.tasks_failed += 1;

            Ok(())
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Task '{}' not found",
                task_id
            )))
        }
    }

    /// Get the result of a completed task
    pub fn get_result(&self, task_id: &str) -> PyResult<Option<String>> {
        let tasks = self.tasks.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Lock error: {}", e))
        })?;

        if let Some(task) = tasks.get(task_id) {
            Ok(task.result.clone())
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Task '{}' not found",
                task_id
            )))
        }
    }

    /// Get topological sort order for task execution
    pub fn get_execution_order(&self) -> PyResult<Vec<String>> {
        let tasks = self.tasks.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Lock error: {}", e))
        })?;

        // Kahn's algorithm for topological sort
        let mut in_degree: HashMap<String, usize> = HashMap::new();
        let mut adj_list: HashMap<String, Vec<String>> = HashMap::new();

        // Initialize
        for (task_id, task) in tasks.iter() {
            in_degree.entry(task_id.clone()).or_insert(0);
            adj_list.entry(task_id.clone()).or_insert_with(Vec::new);

            for dep_id in &task.dependencies {
                *in_degree.entry(task_id.clone()).or_insert(0) += 1;
                adj_list
                    .entry(dep_id.clone())
                    .or_insert_with(Vec::new)
                    .push(task_id.clone());
            }
        }

        // Find all nodes with no incoming edges
        let mut queue: Vec<String> = in_degree
            .iter()
            .filter(|(_, &deg)| deg == 0)
            .map(|(id, _)| id.clone())
            .collect();

        let mut result = Vec::new();

        while let Some(node) = queue.pop() {
            result.push(node.clone());

            if let Some(neighbors) = adj_list.get(&node) {
                for neighbor in neighbors {
                    if let Some(deg) = in_degree.get_mut(neighbor) {
                        *deg -= 1;
                        if *deg == 0 {
                            queue.push(neighbor.clone());
                        }
                    }
                }
            }
        }

        // Check for cycles
        if result.len() != tasks.len() {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Circular dependency detected in tasks",
            ));
        }

        Ok(result)
    }

    /// Execute multiple independent tasks concurrently and aggregate results
    pub fn execute_concurrent_tasks(&self, tasks: Vec<String>) -> PyResult<Vec<String>> {
        let runtime = self.runtime.clone();
        let start_time = std::time::Instant::now();

        let results: Result<Vec<String>, PyErr> = Python::with_gil(|py| {
            py.allow_threads(|| {
                runtime.block_on(async {
                    let mut handles = Vec::new();

                    for task in tasks {
                        let task_str = task.clone();
                        let handle = tokio::spawn(async move {
                            // Return the task ID - actual execution happens in Python
                            task_str
                        });
                        handles.push(handle);
                    }

                    let mut results = Vec::new();
                    for handle in handles {
                        match handle.await {
                            Ok(result) => results.push(result),
                            Err(e) => {
                                return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                                    format!("Task execution failed: {}", e),
                                ))
                            }
                        }
                    }

                    Ok(results)
                })
            })
        });

        // Update stats
        let elapsed_ms = start_time.elapsed().as_millis() as u64;
        if let Ok(mut stats) = self.stats.lock() {
            stats.total_execution_time_ms += elapsed_ms;
        }

        results
    }

    /// Get execution statistics
    pub fn get_stats(&self) -> PyResult<HashMap<String, usize>> {
        let stats = self.stats.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Lock error: {}", e))
        })?;

        let mut result = HashMap::new();
        result.insert("tasks_scheduled".to_string(), stats.tasks_scheduled);
        result.insert("tasks_completed".to_string(), stats.tasks_completed);
        result.insert("tasks_failed".to_string(), stats.tasks_failed);
        result.insert(
            "total_execution_time_ms".to_string(),
            stats.total_execution_time_ms as usize,
        );

        Ok(result)
    }

    /// Clear all tasks
    pub fn clear(&self) -> PyResult<()> {
        let mut tasks = self.tasks.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Lock error: {}", e))
        })?;

        tasks.clear();
        Ok(())
    }
}

/// A high-performance SQLite wrapper with FTS5 support
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

        // Initialize database schema with FTS5 for full-text search
        {
            let conn = pool.get().map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                    "Failed to get connection: {}",
                    e
                ))
            })?;

            // Main table for long-term memories
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

            // FTS5 virtual table for full-text search
            conn.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS long_term_memories_fts USING fts5(
                    task_description,
                    metadata,
                    content='long_term_memories',
                    content_rowid='id'
                )",
                [],
            ).map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                    "Failed to create FTS5 table: {}",
                    e
                ))
            })?;

            // Create triggers to keep FTS5 in sync
            conn.execute_batch(
                "CREATE TRIGGER IF NOT EXISTS long_term_memories_ai AFTER INSERT ON long_term_memories BEGIN
                    INSERT INTO long_term_memories_fts(rowid, task_description, metadata)
                    VALUES (new.id, new.task_description, new.metadata);
                END;
                CREATE TRIGGER IF NOT EXISTS long_term_memories_ad AFTER DELETE ON long_term_memories BEGIN
                    INSERT INTO long_term_memories_fts(long_term_memories_fts, rowid, task_description, metadata)
                    VALUES('delete', old.id, old.task_description, old.metadata);
                END;
                CREATE TRIGGER IF NOT EXISTS long_term_memories_au AFTER UPDATE ON long_term_memories BEGIN
                    INSERT INTO long_term_memories_fts(long_term_memories_fts, rowid, task_description, metadata)
                    VALUES('delete', old.id, old.task_description, old.metadata);
                    INSERT INTO long_term_memories_fts(rowid, task_description, metadata)
                    VALUES (new.id, new.task_description, new.metadata);
                END;"
            ).map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                    "Failed to create FTS5 triggers: {}",
                    e
                ))
            })?;
        }

        Ok(RustSQLiteWrapper {
            connection_pool: Arc::new(Mutex::new(pool)),
        })
    }

    /// Insert a memory into the database
    pub fn insert_memory(&self, task_description: &str, metadata: &str, datetime: &str, score: f64) -> PyResult<i64> {
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

        conn.execute(
            "INSERT INTO long_term_memories (task_description, metadata, datetime, score) VALUES (?1, ?2, ?3, ?4)",
            rusqlite::params![task_description, metadata, datetime, score],
        ).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to insert memory: {}",
                e
            ))
        })?;

        Ok(conn.last_insert_rowid())
    }

    /// Full-text search using FTS5 - returns memories matching the query
    pub fn search_memories(&self, query: &str, limit: usize) -> PyResult<Vec<HashMap<String, String>>> {
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

        // Use FTS5 MATCH for full-text search with BM25 ranking
        let mut stmt = conn.prepare(
            "SELECT m.id, m.task_description, m.metadata, m.datetime, m.score,
                    bm25(long_term_memories_fts) as rank
             FROM long_term_memories m
             JOIN long_term_memories_fts fts ON m.id = fts.rowid
             WHERE long_term_memories_fts MATCH ?1
             ORDER BY rank
             LIMIT ?2"
        ).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to prepare query: {}",
                e
            ))
        })?;

        let rows = stmt.query_map(rusqlite::params![query, limit as i64], |row| {
            let mut map = HashMap::new();
            map.insert("id".to_string(), row.get::<_, i64>(0)?.to_string());
            map.insert("task_description".to_string(), row.get::<_, String>(1)?);
            map.insert("metadata".to_string(), row.get::<_, String>(2)?);
            map.insert("datetime".to_string(), row.get::<_, String>(3)?);
            map.insert("score".to_string(), row.get::<_, f64>(4)?.to_string());
            map.insert("rank".to_string(), row.get::<_, f64>(5)?.to_string());
            Ok(map)
        }).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to execute query: {}",
                e
            ))
        })?;

        let mut results = Vec::new();
        for row in rows {
            results.push(row.map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                    "Failed to read row: {}",
                    e
                ))
            })?);
        }

        Ok(results)
    }

    /// Execute a raw SELECT query and return results
    pub fn execute_query(&self, query: &str, params: Bound<'_, PyDict>) -> PyResult<Vec<HashMap<String, String>>> {
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

        // Convert PyDict to named parameters
        let mut param_values: Vec<(String, String)> = Vec::new();
        for (key, value) in params.iter() {
            let key_str: String = key.extract()?;
            let value_str: String = value.extract()?;
            param_values.push((key_str, value_str));
        }

        let mut stmt = conn.prepare(query).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to prepare query: {}",
                e
            ))
        })?;

        // Get column names
        let column_names: Vec<String> = stmt.column_names().iter().map(|s| s.to_string()).collect();

        // Build params slice for binding
        let params_slice: Vec<(&str, &dyn rusqlite::ToSql)> = param_values
            .iter()
            .map(|(k, v)| (k.as_str(), v as &dyn rusqlite::ToSql))
            .collect();

        let rows = stmt.query_map(params_slice.as_slice(), |row| {
            let mut map = HashMap::new();
            for (i, col_name) in column_names.iter().enumerate() {
                // Try to extract as string, fallback to debug format for other types
                let value: String = match row.get::<_, rusqlite::types::Value>(i) {
                    Ok(rusqlite::types::Value::Null) => "null".to_string(),
                    Ok(rusqlite::types::Value::Integer(i)) => i.to_string(),
                    Ok(rusqlite::types::Value::Real(f)) => f.to_string(),
                    Ok(rusqlite::types::Value::Text(s)) => s,
                    Ok(rusqlite::types::Value::Blob(b)) => format!("{:?}", b),
                    Err(_) => "error".to_string(),
                };
                map.insert(col_name.clone(), value);
            }
            Ok(map)
        }).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to execute query: {}",
                e
            ))
        })?;

        let mut results = Vec::new();
        for row in rows {
            results.push(row.map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                    "Failed to read row: {}",
                    e
                ))
            })?);
        }

        Ok(results)
    }

    /// Execute an INSERT/UPDATE/DELETE query
    pub fn execute_update(&self, query: &str, params: Bound<'_, PyDict>) -> PyResult<usize> {
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

        // Convert PyDict to named parameters
        let mut param_values: Vec<(String, String)> = Vec::new();
        for (key, value) in params.iter() {
            let key_str: String = key.extract()?;
            let value_str: String = value.extract()?;
            param_values.push((key_str, value_str));
        }

        let params_slice: Vec<(&str, &dyn rusqlite::ToSql)> = param_values
            .iter()
            .map(|(k, v)| (k.as_str(), v as &dyn rusqlite::ToSql))
            .collect();

        let affected = conn.execute(query, params_slice.as_slice()).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to execute update: {}",
                e
            ))
        })?;

        Ok(affected)
    }

    /// Execute multiple queries in a batch within a transaction
    pub fn execute_batch(&self, queries: Bound<'_, PyList>) -> PyResult<Vec<usize>> {
        let pool = self.connection_pool.lock().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to acquire pool lock: {}",
                e
            ))
        })?;

        let mut conn = pool.get().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to get connection: {}",
                e
            ))
        })?;

        // Use a transaction for batch operations
        let tx = conn.transaction().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to start transaction: {}",
                e
            ))
        })?;

        let mut results = Vec::new();

        for item in queries.iter() {
            // Each item should be a tuple of (query, params_dict)
            if let Ok(tuple) = item.downcast::<PyTuple>() {
                if tuple.len() == 2 {
                    let query: String = tuple.get_item(0)?.extract()?;
                    let params: Bound<'_, PyDict> = tuple.get_item(1)?.downcast()?.clone();

                    // Convert params
                    let mut param_values: Vec<(String, String)> = Vec::new();
                    for (key, value) in params.iter() {
                        let key_str: String = key.extract()?;
                        let value_str: String = value.extract()?;
                        param_values.push((key_str, value_str));
                    }

                    let params_slice: Vec<(&str, &dyn rusqlite::ToSql)> = param_values
                        .iter()
                        .map(|(k, v)| (k.as_str(), v as &dyn rusqlite::ToSql))
                        .collect();

                    let affected = tx.execute(&query, params_slice.as_slice()).map_err(|e| {
                        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                            "Failed to execute batch query: {}",
                            e
                        ))
                    })?;

                    results.push(affected);
                }
            }
        }

        tx.commit().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to commit transaction: {}",
                e
            ))
        })?;

        Ok(results)
    }

    /// Get all memories ordered by datetime (most recent first)
    pub fn get_all_memories(&self, limit: usize) -> PyResult<Vec<HashMap<String, String>>> {
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

        let mut stmt = conn.prepare(
            "SELECT id, task_description, metadata, datetime, score
             FROM long_term_memories
             ORDER BY datetime DESC
             LIMIT ?1"
        ).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to prepare query: {}",
                e
            ))
        })?;

        let rows = stmt.query_map([limit as i64], |row| {
            let mut map = HashMap::new();
            map.insert("id".to_string(), row.get::<_, i64>(0)?.to_string());
            map.insert("task_description".to_string(), row.get::<_, String>(1)?);
            map.insert("metadata".to_string(), row.get::<_, String>(2)?);
            map.insert("datetime".to_string(), row.get::<_, String>(3)?);
            map.insert("score".to_string(), row.get::<_, f64>(4)?.to_string());
            Ok(map)
        }).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to execute query: {}",
                e
            ))
        })?;

        let mut results = Vec::new();
        for row in rows {
            results.push(row.map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                    "Failed to read row: {}",
                    e
                ))
            })?);
        }

        Ok(results)
    }
}

/// Python module declaration
#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<RustMemoryStorage>()?;
    m.add_class::<RustToolExecutor>()?;
    m.add_class::<AgentMessage>()?;
    m.add_class::<RustTaskExecutor>()?;
    m.add_class::<RustSQLiteWrapper>()?;
    Ok(())
}
