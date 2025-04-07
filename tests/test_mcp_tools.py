"""Tests for the tool functions."""

from unittest.mock import patch
from memory_mcp.server import (
    remember,
    get_memory,
    list_memories,
    update_memory,
    delete_memory,
)


@patch("memory_mcp.server.db")
def test_remember(mock_db):
    """Test the remember tool function."""
    # Set up the mock
    mock_db.add_memory.return_value = 42

    # Call the function
    result = remember("Test Title", "Test Content")

    # Assert the mock was called correctly
    mock_db.add_memory.assert_called_once_with("Test Title", "Test Content")

    # Assert the result
    assert "Memory stored successfully with ID: 42" in result


@patch("memory_mcp.server.db")
def test_remember_exception(mock_db):
    """Test the remember function with an exception."""
    # Set up the mock to raise an exception
    mock_db.add_memory.side_effect = Exception("Test error")

    # Call the function
    result = remember("Test Title", "Test Content")

    # Assert the result contains the error message
    assert "Error storing memory: Test error" in result


@patch("memory_mcp.server.db")
def test_get_memory_by_id(mock_db):
    """Test the get_memory function using an ID."""
    # Set up the mock
    mock_db.get_memory_by_id.return_value = {
        "id": 42,
        "title": "Test Title",
        "content": "Test Content",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00",
    }

    # Call the function
    result = get_memory(memory_id=42)

    # Assert the mock was called correctly
    mock_db.get_memory_by_id.assert_called_once_with(42)

    # Assert the result contains the expected content
    assert "Title: Test Title" in result
    assert "Content: Test Content" in result


@patch("memory_mcp.server.db")
def test_get_memory_by_title(mock_db):
    """Test the get_memory function using a title."""
    # Set up the mock
    mock_db.get_memory_by_title.return_value = {
        "id": 42,
        "title": "Test Title",
        "content": "Test Content",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00",
    }

    # Call the function
    result = get_memory(title="Test Title")

    # Assert the mock was called correctly
    mock_db.get_memory_by_title.assert_called_once_with("Test Title")

    # Assert the result contains the expected content
    assert "Title: Test Title" in result
    assert "Content: Test Content" in result


@patch("memory_mcp.server.db")
def test_get_memory_not_found(mock_db):
    """Test the get_memory function when the memory is not found."""
    # Set up the mock
    mock_db.get_memory_by_id.return_value = None

    # Call the function
    result = get_memory(memory_id=999)

    # Assert the mock was called correctly
    mock_db.get_memory_by_id.assert_called_once_with(999)

    # Assert the result
    assert "Memory not found" in result


@patch("memory_mcp.server.db")
def test_get_memory_missing_params(mock_db):
    """Test the get_memory function with missing parameters."""
    # Call the function without required parameters
    result = get_memory()

    # Assert the mocks were not called
    mock_db.get_memory_by_id.assert_not_called()
    mock_db.get_memory_by_title.assert_not_called()

    # Assert the result
    assert "Error: Please provide either a memory_id or title" in result


@patch("memory_mcp.server.db")
def test_get_memory_exception(mock_db):
    """Test the get_memory function with an exception."""
    # Set up the mock to raise an exception
    mock_db.get_memory_by_id.side_effect = Exception("Test error")

    # Call the function
    result = get_memory(memory_id=42)

    # Assert the result contains the error message
    assert "Error retrieving memory: Test error" in result


@patch("memory_mcp.server.db")
def test_list_memories(mock_db):
    """Test the list_memories function."""
    # Set up the mock
    mock_db.list_memories.return_value = [
        {"id": 1, "title": "Memory 1"},
        {"id": 2, "title": "Memory 2"},
        {"id": 3, "title": "Memory 3"},
    ]

    # Call the function
    result = list_memories()

    # Assert the mock was called correctly
    mock_db.list_memories.assert_called_once()

    # Assert the result contains the expected content
    assert "Stored Memories:" in result
    assert "ID: 1 - Memory 1" in result
    assert "ID: 2 - Memory 2" in result
    assert "ID: 3 - Memory 3" in result


@patch("memory_mcp.server.db")
def test_list_memories_empty(mock_db):
    """Test the list_memories function with an empty list."""
    # Set up the mock
    mock_db.list_memories.return_value = []

    # Call the function
    result = list_memories()

    # Assert the mock was called correctly
    mock_db.list_memories.assert_called_once()

    # Assert the result
    assert "No memories stored yet" in result


@patch("memory_mcp.server.db")
def test_list_memories_exception(mock_db):
    """Test the list_memories function with an exception."""
    # Set up the mock to raise an exception
    mock_db.list_memories.side_effect = Exception("Test error")

    # Call the function
    result = list_memories()

    # Assert the result contains the error message
    assert "Error listing memories: Test error" in result


@patch("memory_mcp.server.db")
def test_update_memory(mock_db):
    """Test the update_memory function."""
    # Set up the mock
    mock_db.update_memory.return_value = True

    # Call the function
    result = update_memory(42, title="New Title", content="New Content")

    # Assert the mock was called correctly
    mock_db.update_memory.assert_called_once_with(42, "New Title", "New Content")

    # Assert the result
    assert "Memory 42 updated successfully" in result


@patch("memory_mcp.server.db")
def test_update_memory_not_found(mock_db):
    """Test the update_memory function when the memory is not found."""
    # Set up the mock
    mock_db.update_memory.return_value = False

    # Call the function
    result = update_memory(999, title="New Title")

    # Assert the mock was called correctly
    mock_db.update_memory.assert_called_once_with(999, "New Title", None)

    # Assert the result
    assert "Memory with ID 999 not found" in result


@patch("memory_mcp.server.db")
def test_update_memory_missing_params(mock_db):
    """Test the update_memory function with missing parameters."""
    # Call the function without optional parameters
    result = update_memory(42)

    # Assert the mock was not called
    mock_db.update_memory.assert_not_called()

    # Assert the result
    assert "Error: Please provide at least one field to update" in result


@patch("memory_mcp.server.db")
def test_update_memory_exception(mock_db):
    """Test the update_memory function with an exception."""
    # Set up the mock to raise an exception
    mock_db.update_memory.side_effect = Exception("Test error")

    # Call the function
    result = update_memory(42, title="New Title")

    # Assert the result contains the error message
    assert "Error updating memory: Test error" in result


@patch("memory_mcp.server.db")
def test_delete_memory(mock_db):
    """Test the delete_memory function."""
    # Set up the mock
    mock_db.delete_memory.return_value = True

    # Call the function
    result = delete_memory(42)

    # Assert the mock was called correctly
    mock_db.delete_memory.assert_called_once_with(42)

    # Assert the result
    assert "Memory 42 deleted successfully" in result


@patch("memory_mcp.server.db")
def test_delete_memory_not_found(mock_db):
    """Test the delete_memory function when the memory is not found."""
    # Set up the mock
    mock_db.delete_memory.return_value = False

    # Call the function
    result = delete_memory(999)

    # Assert the mock was called correctly
    mock_db.delete_memory.assert_called_once_with(999)

    # Assert the result
    assert "Memory with ID 999 not found" in result


@patch("memory_mcp.server.db")
def test_delete_memory_exception(mock_db):
    """Test the delete_memory function with an exception."""
    # Set up the mock to raise an exception
    mock_db.delete_memory.side_effect = Exception("Test error")

    # Call the function
    result = delete_memory(42)

    # Assert the result contains the error message
    assert "Error deleting memory: Test error" in result
