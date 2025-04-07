"""Pytest fixtures for the memory-mcp package."""

import os
import pytest
import tempfile
from memory_mcp.server import DatabaseManager


@pytest.fixture
def temp_db_path():
    """Create a temporary database file path."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name

    yield db_path

    # Clean up the temporary file after the test
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def db_manager(temp_db_path):
    """Create a database manager with a temporary database."""
    manager = DatabaseManager(db_path=temp_db_path)
    yield manager
    manager.close()


@pytest.fixture
def sample_memories(db_manager):
    """Create sample memories in the database."""
    memory_ids = []

    # Add some test memories
    memory_ids.append(
        db_manager.add_memory("Test Memory 1", "This is the content of test memory 1")
    )
    memory_ids.append(
        db_manager.add_memory("Test Memory 2", "This is the content of test memory 2")
    )
    memory_ids.append(
        db_manager.add_memory("Another Memory", "This is another test memory")
    )

    return memory_ids
