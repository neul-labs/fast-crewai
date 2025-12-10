"""Root pytest configuration - ignore test_compatibility directory."""

# Tell pytest to ignore the test_compatibility directory
# This directory contains CrewAI's tests cloned for compatibility testing
# and has different dependencies
collect_ignore_glob = ["test_compatibility/*", "crewai_comparison_test/*"]
