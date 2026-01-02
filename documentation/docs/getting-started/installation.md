# Installation

Fast-CrewAI can be installed using pip or uv. The package includes pre-built wheels for common platforms, so you don't need a Rust toolchain for basic usage.

## Quick Install

=== "uv (Recommended)"

    ```bash
    uv add fast-crewai
    ```

=== "pip"

    ```bash
    pip install fast-crewai
    ```

## Verify Installation

After installation, verify that Fast-CrewAI is working correctly:

```python
from fast_crewai import is_acceleration_available, get_acceleration_status

print(f"Rust acceleration available: {is_acceleration_available()}")
print(f"Status: {get_acceleration_status()}")
```

Expected output:

```
Rust acceleration available: True
Status: {'rust_available': True, 'components': {...}}
```

## Development Installation

If you want to contribute or build from source:

### Prerequisites

1. **Python 3.10+**
2. **Rust toolchain** (for building the Rust extension)

    ```bash
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    source ~/.cargo/env
    ```

3. **uv** (recommended package manager)

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

### Build from Source

```bash
# Clone the repository
git clone https://github.com/neul-labs/fast-crewai.git
cd fast-crewai

# Install dependencies
uv sync --dev

# Build the Rust extension
uv run maturin develop

# For optimized release build
uv run maturin develop --release
```

### Verify Development Build

```bash
# Run the test suite
uv run pytest

# Run quick tests only
./scripts/run_tests.sh fast
```

## Platform-Specific Notes

### Windows

If you encounter build errors on Windows, you may need to install Visual C++ Build Tools:

1. Download from [Visual Studio Downloads](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Install "Desktop development with C++"
3. Restart your terminal and try again

### macOS

If you see build errors on macOS, install Xcode command line tools:

```bash
xcode-select --install
```

### Linux

Install build dependencies:

```bash
# Debian/Ubuntu
sudo apt update
sudo apt install build-essential python3-dev

# Fedora
sudo dnf install gcc python3-devel

# Arch Linux
sudo pacman -S base-devel python
```

## Troubleshooting

### Rust Components Not Available

If `is_acceleration_available()` returns `False`:

1. **Rebuild from source:**
    ```bash
    uv sync --dev
    uv run maturin develop
    ```

2. **Check Rust installation:**
    ```bash
    rustc --version
    cargo --version
    ```

3. **Check for build errors** in the maturin output

### ImportError

If you see `ImportError: No module named '_core'`:

- The Rust extension wasn't built or installed correctly
- Try rebuilding with `uv run maturin develop`

See the [Troubleshooting Guide](../contributing/troubleshooting.md) for more solutions.

## Next Steps

- [Quick Start](quickstart.md) - Get your first accelerated workflow running
- [How It Works](how-it-works.md) - Understand the acceleration system
