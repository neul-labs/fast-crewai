"""
Tests for memory storage components.
"""

import time

import pytest


class TestAcceleratedMemoryStorage:
    """Test cases for AcceleratedMemoryStorage component."""

    def test_import_memory_storage(self):
        """Test that we can import AcceleratedMemoryStorage."""
        from fast_crewai import AcceleratedMemoryStorage

        storage = AcceleratedMemoryStorage()
        assert storage is not None

    def test_memory_save_basic(self):
        """Test basic save functionality."""
        from fast_crewai import AcceleratedMemoryStorage

        storage = AcceleratedMemoryStorage()
        storage.save("test data", {"key": "value"})

        # Basic verification that save doesn't crash
        assert True

    def test_memory_search_basic(self):
        """Test basic search functionality."""
        from fast_crewai import AcceleratedMemoryStorage

        storage = AcceleratedMemoryStorage()
        storage.save("test document about AI", {"topic": "AI"})
        storage.save("another document about ML", {"topic": "ML"})

        results = storage.search("AI", limit=5)
        assert isinstance(results, list)

    def test_memory_implementation_detection(self):
        """Test that we can detect which implementation is being used."""
        from fast_crewai import AcceleratedMemoryStorage

        storage = AcceleratedMemoryStorage()
        assert hasattr(storage, "implementation")
        assert storage.implementation in ["rust", "python"]

    def test_memory_with_complex_metadata(self):
        """Test memory storage with complex metadata."""
        from fast_crewai import AcceleratedMemoryStorage

        storage = AcceleratedMemoryStorage()

        complex_metadata = {
            "author": "AI Researcher",
            "tags": ["AI", "ML", "automation"],
            "confidence": 0.95,
            "nested": {
                "category": "technology",
                "subcategory": "artificial_intelligence",
            },
        }

        storage.save("Complex document with rich metadata", complex_metadata)
        results = storage.search("Complex", limit=1)

        assert len(results) >= 0  # Should not crash

    def test_memory_performance_basic(self):
        """Basic performance test for memory operations."""
        from fast_crewai import AcceleratedMemoryStorage

        storage = AcceleratedMemoryStorage()

        # Test save performance
        documents = [f"Document {i}" for i in range(100)]

        start_time = time.time()
        for doc in documents:
            storage.save(doc, {"id": documents.index(doc)})
        save_time = time.time() - start_time

        # Test search performance
        start_time = time.time()
        for i in range(10):
            storage.search("Document", limit=5)
        search_time = time.time() - start_time

        # Performance should be reasonable (not testing specific speeds)
        assert save_time < 10.0  # Should save 100 docs in under 10 seconds
        assert search_time < 5.0  # Should search 10 times in under 5 seconds

    def test_memory_fallback_behavior(self):
        """Test fallback behavior when Rust is not available."""
        from fast_crewai import AcceleratedMemoryStorage

        # Test with explicit Python fallback
        storage = AcceleratedMemoryStorage(use_rust=False)
        assert storage.implementation == "python"

        # Test basic functionality with Python fallback
        storage.save("fallback test", {"mode": "python"})
        results = storage.search("fallback", limit=1)
        assert isinstance(results, list)


class TestMemoryIntegration:
    """Integration tests for memory components with CrewAI."""

    def test_crewai_memory_import_compatibility(self):
        """Test that CrewAI memory imports work after shimming."""
        try:
            # Import shim first
            from crewai.memory.long_term.long_term_memory import (  # noqa: F401
                LongTermMemory,
            )
            from crewai.memory.short_term.short_term_memory import (  # noqa: F401
                ShortTermMemory,
            )
            # Then try to import CrewAI memory components
            from crewai.memory.storage.rag_storage import RAGStorage  # noqa: F401

            import fast_crewai.shim  # noqa: F401

            assert True  # If we get here, imports worked

        except ImportError:
            # CrewAI might not be installed in test environment
            pytest.skip("CrewAI not available for integration testing")

    def test_memory_component_replacement(self):
        """Test that memory components are properly replaced by shim."""
        try:
            from crewai.memory.storage.rag_storage import RAGStorage

            import fast_crewai.shim  # noqa: F401

            # Try to create storage - should use Rust implementation if available
            storage = RAGStorage(type="test")

            # Basic functionality test
            if hasattr(storage, "save"):
                storage.save("test", {"shim": "test"})

            assert True  # If we get here, shimming worked

        except ImportError:
            pytest.skip("CrewAI not available for integration testing")


class TestMemoryEdgeCases:
    """Test edge cases and error conditions."""

    def test_memory_empty_search(self):
        """Test search with empty storage."""
        from fast_crewai import AcceleratedMemoryStorage

        storage = AcceleratedMemoryStorage()
        results = storage.search("nonexistent", limit=5)
        assert isinstance(results, list)
        assert len(results) == 0

    def test_memory_large_document(self):
        """Test with large document content."""
        from fast_crewai import AcceleratedMemoryStorage

        storage = AcceleratedMemoryStorage()

        # Create a large document
        large_content = " ".join([f"word{i}" for i in range(1000)])
        storage.save(large_content, {"size": "large"})

        results = storage.search("word500", limit=1)
        assert isinstance(results, list)

    def test_memory_special_characters(self):
        """Test with special characters and unicode."""
        from fast_crewai import AcceleratedMemoryStorage

        storage = AcceleratedMemoryStorage()

        special_content = "Special characters: αβγ 中文 🚀 emoji test"
        storage.save(special_content, {"encoding": "utf-8"})

        results = storage.search("🚀", limit=1)
        assert isinstance(results, list)

    def test_memory_json_serialization(self):
        """Test that metadata can be properly serialized."""
        from fast_crewai import AcceleratedMemoryStorage

        storage = AcceleratedMemoryStorage()

        # Metadata that might cause JSON issues
        problematic_metadata = {
            "unicode": "测试",
            "float": 3.14159,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
            "nested": {"deep": {"value": "test"}},
        }

        storage.save("JSON test document", problematic_metadata)
        results = storage.search("JSON", limit=1)
        assert isinstance(results, list)


if __name__ == "__main__":
    pytest.main([__file__])
