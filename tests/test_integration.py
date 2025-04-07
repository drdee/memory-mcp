"""Integration tests for the memory-mcp package."""

import os
import tempfile
from memory_mcp.server import (
    remember,
    get_memory,
    list_memories,
    update_memory,
    delete_memory,
    DatabaseManager,
)


class TestIntegration:
    """Integration tests for the memory-mcp system."""

    @classmethod
    def setup_class(cls):
        """Set up the test environment once for all tests."""
        # Create a temporary database
        cls.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        cls.db_path = cls.temp_file.name
        cls.temp_file.close()

        # Initialize the database manager with the temporary file
        from memory_mcp.server import db

        # Replace the global db with our test instance
        cls.original_db = db

        # Create a new instance and replace the global one
        test_db = DatabaseManager(cls.db_path)
        from memory_mcp.server import db as server_db

        # Copy attributes from test_db to server_db
        server_db.db_path = test_db.db_path
        server_db.conn = test_db.conn

    @classmethod
    def teardown_class(cls):
        """Clean up after all tests are done."""
        # Close the database connection
        from memory_mcp.server import db

        db.close()

        # Remove the temporary file
        if os.path.exists(cls.db_path):
            os.unlink(cls.db_path)

    def test_integration_workflow(self):
        """Test a complete workflow of memory operations."""
        # Step 1: List memories (should be empty)
        result = list_memories()
        assert "No memories stored yet" in result

        # Step 2: Store a memory
        result = remember("Integration Test", "This is an integration test memory")
        assert "Memory stored successfully" in result
        memory_id = int(result.split("ID: ")[1].split(".")[0])

        # Step 3: List memories (should have our memory)
        result = list_memories()
        assert "Integration Test" in result
        assert str(memory_id) in result

        # Step 4: Retrieve the memory by ID
        result = get_memory(memory_id=memory_id)
        assert "Title: Integration Test" in result
        assert "Content: This is an integration test memory" in result

        # Step 5: Store another memory
        result = remember("Second Memory", "This is a second test memory")
        assert "Memory stored successfully" in result
        second_id = int(result.split("ID: ")[1].split(".")[0])

        # Step 6: Retrieve the memory by title
        result = get_memory(title="Second Memory")
        assert "Title: Second Memory" in result
        assert "Content: This is a second test memory" in result

        # Step 7: Update the first memory
        result = update_memory(
            memory_id, title="Updated Integration Test", content="Updated content"
        )
        assert f"Memory {memory_id} updated successfully" in result

        # Step 8: Verify the update
        result = get_memory(memory_id=memory_id)
        assert "Title: Updated Integration Test" in result
        assert "Content: Updated content" in result

        # Step 9: Delete the second memory
        result = delete_memory(second_id)
        assert f"Memory {second_id} deleted successfully" in result

        # Step 10: Verify the deletion
        result = get_memory(memory_id=second_id)
        assert "Memory not found" in result

        # Step 11: List memories (should only have the first memory)
        result = list_memories()
        assert "Updated Integration Test" in result
        assert "Second Memory" not in result

        # Step 12: Attempt operations with invalid data
        result = get_memory(memory_id=999)
        assert "Memory not found" in result

        result = update_memory(999, title="Nonexistent")
        assert "Memory with ID 999 not found" in result

        result = delete_memory(999)
        assert "Memory with ID 999 not found" in result
