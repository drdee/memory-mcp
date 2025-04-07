"""Tests for the DatabaseManager class."""

from memory_mcp.server import DatabaseManager


def test_initialization(temp_db_path):
    """Test that the database manager initializes correctly."""
    manager = DatabaseManager(db_path=temp_db_path)
    assert manager.conn is not None
    manager.close()
    assert manager.conn is None


def test_add_memory(db_manager):
    """Test adding a memory to the database."""
    memory_id = db_manager.add_memory("Test Title", "Test Content")
    assert memory_id > 0

    memory = db_manager.get_memory_by_id(memory_id)
    assert memory is not None
    assert memory["title"] == "Test Title"
    assert memory["content"] == "Test Content"
    assert "created_at" in memory
    assert "updated_at" in memory


def test_get_memory_by_id(db_manager, sample_memories):
    """Test retrieving a memory by ID."""
    memory_id = sample_memories[0]
    memory = db_manager.get_memory_by_id(memory_id)

    assert memory is not None
    assert memory["id"] == memory_id
    assert memory["title"] == "Test Memory 1"
    assert memory["content"] == "This is the content of test memory 1"

    # Test non-existent memory
    non_existent = db_manager.get_memory_by_id(9999)
    assert non_existent is None


def test_get_memory_by_title(db_manager, sample_memories):
    """Test retrieving a memory by title."""
    memory = db_manager.get_memory_by_title("Test Memory 2")

    assert memory is not None
    assert memory["id"] == sample_memories[1]
    assert memory["title"] == "Test Memory 2"
    assert memory["content"] == "This is the content of test memory 2"

    # Test non-existent memory
    non_existent = db_manager.get_memory_by_title("Non-existent Memory")
    assert non_existent is None


def test_list_memories(db_manager, sample_memories):
    """Test listing all memories."""
    memories = db_manager.list_memories()

    assert len(memories) == 3
    assert {"id": sample_memories[0], "title": "Test Memory 1"} in memories
    assert {"id": sample_memories[1], "title": "Test Memory 2"} in memories
    assert {"id": sample_memories[2], "title": "Another Memory"} in memories


def test_update_memory(db_manager, sample_memories):
    """Test updating a memory."""
    memory_id = sample_memories[0]

    # Test updating title only
    assert db_manager.update_memory(memory_id, title="Updated Title") is True
    memory = db_manager.get_memory_by_id(memory_id)
    assert memory["title"] == "Updated Title"
    assert memory["content"] == "This is the content of test memory 1"

    # Test updating content only
    assert db_manager.update_memory(memory_id, content="Updated content") is True
    memory = db_manager.get_memory_by_id(memory_id)
    assert memory["title"] == "Updated Title"
    assert memory["content"] == "Updated content"

    # Test updating both title and content
    assert (
        db_manager.update_memory(
            memory_id, title="Final Title", content="Final content"
        )
        is True
    )
    memory = db_manager.get_memory_by_id(memory_id)
    assert memory["title"] == "Final Title"
    assert memory["content"] == "Final content"

    # Test updating non-existent memory
    assert db_manager.update_memory(9999, title="Non-existent") is False


def test_delete_memory(db_manager, sample_memories):
    """Test deleting a memory."""
    memory_id = sample_memories[0]

    # Verify the memory exists
    assert db_manager.get_memory_by_id(memory_id) is not None

    # Delete the memory
    assert db_manager.delete_memory(memory_id) is True

    # Verify it's gone
    assert db_manager.get_memory_by_id(memory_id) is None

    # Test deleting non-existent memory
    assert db_manager.delete_memory(9999) is False

    # Verify remaining memories
    memories = db_manager.list_memories()
    assert len(memories) == 2
    memory_ids = [m["id"] for m in memories]
    assert memory_id not in memory_ids
    assert sample_memories[1] in memory_ids
    assert sample_memories[2] in memory_ids
