# Fast-CrewAI Testing Guide

This guide explains how to test Fast-CrewAI's acceleration patches with CrewAI.

## Quick Start

```bash
cd /home/dipankar/Code/fast-crewai

# 1. Validate patches load correctly
python3 test_all_patches.py

# 2. Run practical integration test
python3 test_integration.py

# 3. Run CrewAI's full test suite (requires setup)
./scripts/test_crewai_compatibility.sh
```

## Test Levels

### Level 1: Patch Validation ⚡️ (Fast - 5 seconds)

**Purpose:** Verify all Fast-CrewAI patches load without errors.

```bash
python3 test_all_patches.py
```

**What it tests:**
- ✅ Shim imports successfully
- ✅ Acceleration status reports correctly
- ✅ Tool patching uses dynamic inheritance
- ✅ Task patching uses dynamic inheritance
- ✅ Memory components load
- ✅ Database components load
- ✅ Serialization components load
- ✅ CrewAI classes are actually patched (if installed)

**Expected Output:**
```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    Fast-CrewAI Patch Validation                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

TEST 1: Shim Loading
✅ Shim imported successfully

TEST 2: Acceleration Status
✅ Acceleration status retrieved successfully

...

TEST SUMMARY
✅ PASS     | Shim Loading
✅ PASS     | Acceleration Status
✅ PASS     | Tool Patching
✅ PASS     | Task Patching
✅ PASS     | Memory Components
✅ PASS     | Database Components
✅ PASS     | Serialization Components
✅ PASS     | CrewAI Patching

Results: 8/8 tests passed

🎉 All tests passed! Fast-CrewAI patches are working correctly.
```

---

### Level 2: Integration Test ⚡️⚡️ (Medium - 10 seconds)

**Purpose:** Test real CrewAI workflow with Fast-CrewAI acceleration.

```bash
python3 test_integration.py
```

**What it tests:**
- ✅ Shim activation before CrewAI import
- ✅ Creating and executing tools
- ✅ Creating agents with tools
- ✅ Creating tasks with agents
- ✅ Creating crews with agents and tasks
- ✅ Memory storage functionality
- ✅ Message serialization/deserialization
- ✅ All components work together

**Expected Output:**
```
Fast-CrewAI Integration Test

Step 1: Activating Fast-CrewAI shim...
✅ Shim activated successfully

Step 2: Checking acceleration status...
   Available: True
   Components: {...}
✅ Acceleration status retrieved

Step 3: Importing CrewAI...
✅ CrewAI imported successfully

Step 4: Verifying class patching...
   BaseTool class: AcceleratedBaseTool
   Task class: AcceleratedTask
   Crew class: AcceleratedCrew
✅ Classes are using accelerated versions

...

INTEGRATION TEST SUMMARY
✅ Shim activation: SUCCESS
✅ CrewAI import: SUCCESS
✅ Tool creation: SUCCESS
✅ Tool execution: SUCCESS
✅ Agent creation: SUCCESS
✅ Task creation: SUCCESS
✅ Crew creation: SUCCESS
✅ Memory components: SUCCESS
✅ Serialization: SUCCESS

🎉 All integration tests passed!
```

---

### Level 3: CrewAI Compatibility Test ⚡️⚡️⚡️ (Full - 5+ minutes)

**Purpose:** Run CrewAI's entire test suite with Fast-CrewAI acceleration enabled.

#### First Time Setup:

```bash
# Run the setup script (clones CrewAI, creates venv, installs everything)
./scripts/test_crewai_compatibility.sh
```

This will:
1. Clone CrewAI repository to `test_compatibility/crewai/`
2. Create Python virtual environment in `test_compatibility/venv/`
3. Install CrewAI and all dependencies
4. Install Fast-CrewAI
5. Run CrewAI's test suite with acceleration enabled

#### Subsequent Runs:

```bash
# Skip clone and install (much faster)
./scripts/test_crewai_compatibility.sh --skip-clone --skip-install
```

#### Run Specific Tests:

```bash
# Test only agent-related tests
./scripts/test_crewai_compatibility.sh --skip-clone --skip-install --filter "test_agent"

# Test only tool-related tests
./scripts/test_crewai_compatibility.sh --skip-clone --skip-install --filter "test_tool"

# Test only memory-related tests
./scripts/test_crewai_compatibility.sh --skip-clone --skip-install --filter "test_memory"
```

#### Keep Test Environment:

```bash
# Keep the test environment after completion for inspection
./scripts/test_crewai_compatibility.sh --skip-clone --skip-install --keep-env
```

**What it tests:**
- ✅ Full CrewAI test suite (100+ tests)
- ✅ All CrewAI agents, tasks, crews work with acceleration
- ✅ Tool execution compatibility
- ✅ Memory operations compatibility
- ✅ Database operations compatibility
- ✅ No API breaking changes

**Expected Output:**
```
[INFO] Starting Fast-CrewAI compatibility testing

[INFO] Step 1/6: Creating test directory
[SUCCESS] Test directory created: /path/to/test_compatibility

[INFO] Step 2/6: Skipping CrewAI clone (using existing)

[INFO] Step 3/6: Setting up Python virtual environment
[INFO] Using existing virtual environment

[INFO] Step 4/6: Skipping installation

[INFO] Step 5/6: Creating test runner with Fast-CrewAI shim
[SUCCESS] Test runner configuration created

[INFO] Step 6/6: Running CrewAI tests with Fast-CrewAI shim

================================================================================
Fast-CrewAI shim activated successfully!
================================================================================

Acceleration Status:
  available: True
  components: { ... }

✅ Acceleration bootstrap completed!
  - Memory patches applied: 4, failed: 0
  - Tool patches applied: 2, failed: 0
  - Task patches applied: 2, failed: 0
  - Database patches applied: 2, failed: 0
  - Total patches applied: 10

🚀 Performance improvements now active:
  - Memory Storage: 2-5x faster
  - Database Operations: 2-4x faster
  - Tool Execution: Acceleration hooks enabled
  - Task Execution: Acceleration hooks enabled

================================================================================

============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.1, pluggy-1.6.0
rootdir: /path/to/crewai
collected 127 items

lib/crewai/tests/test_agent.py ......                                    [  4%]
lib/crewai/tests/test_task.py ........                                   [ 10%]
lib/crewai/tests/test_crew.py ...............                            [ 22%]
...

============================= 127 passed in 45.2s ===============================

[SUCCESS] All tests passed! Fast-CrewAI is compatible with CrewAI.
```

---

## Troubleshooting

### Issue: "CrewAI not installed"

**Solution:** Install CrewAI in the test environment:
```bash
cd test_compatibility
source venv/bin/activate
pip install crewai
```

### Issue: "Module not found: mem0" or "qdrant_client"

**Solution:** These are optional CrewAI dependencies. Either:
1. Install them: `pip install mem0 qdrant_client crewai_tools`
2. Or skip those tests with `--filter` to avoid them

### Issue: Tests fail with API key errors

**Solution:** Some tests require LLM API keys. Either:
1. Set your API key: `export OPENAI_API_KEY=your_key`
2. Or skip LLM tests (most tests don't need API keys)

### Issue: "Rust extension not found"

**Solution:** This is fine! Fast-CrewAI works without Rust:
- Python fallback is automatic
- Patches still work
- Just won't get the Rust performance boost
- To build Rust extension: `pip install maturin && maturin develop`

---

## Testing Checklist

Before committing changes:

- [ ] Run `python3 test_all_patches.py` - should pass all 8 tests
- [ ] Run `python3 test_integration.py` - should complete all 13 steps
- [ ] Run compatibility tests: `./scripts/test_crewai_compatibility.sh --skip-clone --skip-install --filter "test_agent"`
- [ ] Verify no import errors or class mismatch issues

---

## Python Script Alternative

You can also use the Python version of the compatibility test:

```bash
python3 scripts/test_crewai_compatibility.py --skip-clone --skip-install
```

This works on all platforms (Windows, macOS, Linux).

---

## CI/CD Integration

The `.github/workflows/compatibility-tests.yml` workflow automatically runs:
- Patch validation tests
- Integration tests
- CrewAI compatibility tests

On every pull request and push to main/develop branches.

---

## Performance Testing

To benchmark performance improvements:

```bash
# Run with acceleration
python3 test_integration.py

# Run without acceleration
FAST_CREWAI_ACCELERATION=0 python3 test_integration.py

# Compare execution times
```

---

## Test Environment Details

- **Location:** `./test_compatibility/`
- **CrewAI Clone:** `./test_compatibility/crewai/`
- **Virtual Environment:** `./test_compatibility/venv/`
- **Test Results:** `./test_compatibility/test_results.log`
- **Conftest:** `./test_compatibility/conftest.py` (auto-generated)

---

## Summary

| Test Level | Speed | Requires CrewAI | Requires API Key | Command |
|------------|-------|-----------------|------------------|---------|
| Level 1: Patch Validation | ⚡️ Fast (5s) | No | No | `python3 test_all_patches.py` |
| Level 2: Integration | ⚡️⚡️ Medium (10s) | Yes | No | `python3 test_integration.py` |
| Level 3: Full Compatibility | ⚡️⚡️⚡️ Slow (5m+) | Yes | Some tests | `./scripts/test_crewai_compatibility.sh` |

Start with Level 1, move to Level 2, then Level 3 as needed.
