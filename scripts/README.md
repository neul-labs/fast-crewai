# Scripts

Development and testing scripts for CrewAI Rust.

## Scripts

### `build_and_test.sh`
Basic build and test script that:
- Installs maturin if needed
- Builds the package in development mode
- Runs basic import tests

Usage:
```bash
./scripts/build_and_test.sh
```

### `run_tests.sh`
Comprehensive test runner with multiple options:
- `all` - Run all tests (default)
- `fast` - Run fast tests only (exclude slow/integration/performance)
- `unit` - Run unit tests only
- `integration` - Run integration tests
- `performance` - Run performance tests
- `coverage` - Run tests with coverage report
- `memory` - Run memory component tests
- `tools` - Run tool component tests
- `tasks` - Run task component tests
- `shim` - Run shim system tests

Usage:
```bash
./scripts/run_tests.sh [test_type]
./scripts/run_tests.sh fast
./scripts/run_tests.sh coverage
```

For help:
```bash
./scripts/run_tests.sh help
```