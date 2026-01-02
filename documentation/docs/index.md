# Fast-CrewAI

**Drop-in performance acceleration for CrewAI** - Get up to **34x faster serialization**, **17x faster tool execution**, and **11x faster database search** with zero code changes to your existing CrewAI projects.

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Quick Start**

    ---

    Get your CrewAI code running faster in seconds with a single import.

    [:octicons-arrow-right-24: Getting started](getting-started/quickstart.md)

-   :material-speedometer:{ .lg .middle } **Performance**

    ---

    Up to 34x faster serialization, 17x faster tools, 11x faster search.

    [:octicons-arrow-right-24: Benchmarks](user-guide/performance.md)

-   :material-cog:{ .lg .middle } **Configuration**

    ---

    Fine-tune acceleration with environment variables and API options.

    [:octicons-arrow-right-24: Configuration](user-guide/configuration.md)

-   :material-api:{ .lg .middle } **API Reference**

    ---

    Complete documentation for all accelerated components.

    [:octicons-arrow-right-24: API Reference](api/index.md)

</div>

## What Gets Faster

| Component | Performance Boost | What This Means |
|-----------|-------------------|-----------------|
| **Serialization** | :rocket: **34x faster** | Agent message serialization using serde |
| **Tool Execution** | :rocket: **17x faster** | Result caching and JSON validation |
| **Database Search** | :rocket: **11x faster** | FTS5 full-text search with BM25 ranking |
| **Memory Storage** | :white_check_mark: **TF-IDF search** | Semantic search using cosine similarity |
| **Task Execution** | :white_check_mark: **Dependency tracking** | Topological sort and parallel scheduling |

## Zero-Code Integration

Fast-CrewAI uses smart monkey patching to seamlessly accelerate your existing CrewAI code:

```python
# Add this single line before your CrewAI imports
import fast_crewai.shim

# Your existing code remains unchanged!
from crewai import Agent, Task, Crew

agent = Agent(role="Analyst", goal="Analyze data", backstory="Expert analyst")
task = Task(description="Analyze the data", expected_output="Report", agent=agent)
crew = Crew(agents=[agent], tasks=[task], memory=True)

result = crew.kickoff()  # Now accelerated with Rust!
```

## Memory Usage Savings

| Component | Python | Rust | Savings |
|-----------|--------|------|---------|
| Tool Execution | 1.2 MB | 0.0 MB | **99% less** |
| Serialization | 8.0 MB | 3.4 MB | **58% less** |
| Database | 0.1 MB | 0.1 MB | **31% less** |

## Platform Support

| Platform | Status |
|----------|--------|
| Linux (x86_64) | :white_check_mark: Fully supported |
| macOS (x86_64) | :white_check_mark: Fully supported |
| macOS (ARM64/M1) | :white_check_mark: Fully supported |
| Windows (x86_64) | :white_check_mark: Supported |

## Python Version Support

| Python Version | Status |
|----------------|--------|
| Python 3.10 | :white_check_mark: Fully tested |
| Python 3.11 | :white_check_mark: Fully tested |
| Python 3.12 | :white_check_mark: Fully tested |
| Python 3.13 | :white_check_mark: Fully tested |

## Next Steps

- [Installation](getting-started/installation.md) - Install Fast-CrewAI
- [Quick Start](getting-started/quickstart.md) - Get up and running in seconds
- [How It Works](getting-started/how-it-works.md) - Understand the acceleration system
