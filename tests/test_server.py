"""Tests for the server module functionality."""

import pytest
from unittest.mock import patch, MagicMock
from memory_mcp.server import run_server, serve
import mcp.types as types


@patch("memory_mcp.server.asyncio.run")
@patch("builtins.print")
def test_run_server(mock_print, mock_run):
    """Test the run_server function."""
    # Setup a proper mock for _run coroutine
    async def mock_coro():
        return None
    
    # Make the mock return the coroutine function
    mock_run.return_value = None
    
    # Call the function
    run_server()

    # Assert the prints were called correctly
    assert mock_print.call_count >= 2
    mock_print.assert_any_call("Starting Memory Manager MCP Server...")

    # Assert asyncio.run was called
    mock_run.assert_called_once()


@pytest.mark.asyncio
async def test_lifespan():
    """Test the lifespan context manager."""
    # Create a mock context
    mock_context = MagicMock()

    # Mock db.close to track it's called
    with patch("memory_mcp.server.db") as mock_db:
        # Use the lifespan context manager
        server = await serve()
        async with server.lifespan(mock_context):
            # The db should not be closed yet
            mock_db.close.assert_not_called()

        # After exiting the context, db.close should be called
        mock_db.close.assert_called_once()


@pytest.mark.asyncio
async def test_server_tools():
    """Test that the Server instance is created with the right tools."""
    # Create the server instance
    server = await serve()
    
    # Assert that server is initialized with the right name
    assert server is not None
    assert server.name == "Memory Manager"
    
    # Test the registered request handlers
    assert types.ListToolsRequest in server.request_handlers
    assert types.CallToolRequest in server.request_handlers
    
    # Create a mock ListToolsRequest
    mock_request = MagicMock()
    
    # Call the handler directly
    response = await server.request_handlers[types.ListToolsRequest](mock_request)
    
    # Verify the response
    assert response is not None
    assert isinstance(response, types.ServerResult)
    assert isinstance(response.root, types.ListToolsResult)
    
    # Check tool names
    tool_names = [tool.name for tool in response.root.tools]
    assert "remember" in tool_names
    assert "get_memory" in tool_names
    assert "list_memories" in tool_names
    assert "update_memory" in tool_names
    assert "delete_memory" in tool_names


@pytest.mark.asyncio
async def test_handle_call_tool():
    """Test the call_tool handler."""
    server = await serve()
    
    with patch("memory_mcp.server.remember") as mock_remember:
        mock_remember.return_value = "Memory stored successfully with ID: 1."
        
        # Create a CallToolRequest
        request = types.CallToolRequest(
            method="tools/call",
            params=types.CallToolRequestParams(
                name="remember",
                arguments={"title": "Test Title", "content": "Test Content"}
            )
        )
        
        # Call the handler directly
        response = await server.request_handlers[types.CallToolRequest](request)
        
        # Assert mock was called with correct parameters
        mock_remember.assert_called_once_with("Test Title", "Test Content")
        
        # Assert the result is as expected
        assert isinstance(response, types.ServerResult)
        assert isinstance(response.root, types.CallToolResult)
        assert response.root.isError is False
        assert len(response.root.content) == 1
        assert response.root.content[0].type == "text"
        assert response.root.content[0].text == "Memory stored successfully with ID: 1."


@pytest.mark.asyncio
async def test_handle_call_tool_get_memory():
    """Test the call_tool handler for get_memory."""
    server = await serve()
    
    with patch("memory_mcp.server.get_memory") as mock_get_memory:
        mock_get_memory.return_value = "Title: Test Memory\n\nContent: Test content."
        
        # Call with memory_id
        request = types.CallToolRequest(
            method="tools/call",
            params=types.CallToolRequestParams(
                name="get_memory",
                arguments={"memory_id": 1}
            )
        )
        
        response = await server.request_handlers[types.CallToolRequest](request)
        
        # Assert mock was called with correct parameters
        mock_get_memory.assert_called_once_with(1, None)
        
        # Assert the result is as expected
        assert response.root.content[0].text == "Title: Test Memory\n\nContent: Test content."
        
        # Reset mock for next test
        mock_get_memory.reset_mock()
        
        # Call with title
        request = types.CallToolRequest(
            method="tools/call",
            params=types.CallToolRequestParams(
                name="get_memory",
                arguments={"title": "Test Memory"}
            )
        )
        
        response = await server.request_handlers[types.CallToolRequest](request)
        
        # Assert mock was called with correct parameters
        mock_get_memory.assert_called_once_with(None, "Test Memory")


@pytest.mark.asyncio
async def test_handle_call_tool_list_memories():
    """Test the call_tool handler for list_memories."""
    server = await serve()
    
    with patch("memory_mcp.server.list_memories") as mock_list_memories:
        mock_list_memories.return_value = "Stored Memories:\n\nID: 1 - Test Memory"
        
        # Create request
        request = types.CallToolRequest(
            method="tools/call",
            params=types.CallToolRequestParams(
                name="list_memories",
                arguments={}
            )
        )
        
        # Call the handler
        response = await server.request_handlers[types.CallToolRequest](request)
        
        # Assert mock was called
        mock_list_memories.assert_called_once()
        
        # Assert the result is as expected
        assert response.root.content[0].text == "Stored Memories:\n\nID: 1 - Test Memory"


@pytest.mark.asyncio
async def test_handle_call_tool_update_memory():
    """Test the call_tool handler for update_memory."""
    server = await serve()
    
    with patch("memory_mcp.server.update_memory") as mock_update_memory:
        mock_update_memory.return_value = "Memory 1 updated successfully."
        
        # Call with both title and content
        request = types.CallToolRequest(
            method="tools/call",
            params=types.CallToolRequestParams(
                name="update_memory",
                arguments={"memory_id": 1, "title": "New Title", "content": "New Content"}
            )
        )
        
        response = await server.request_handlers[types.CallToolRequest](request)
        
        # Assert mock was called with correct parameters
        mock_update_memory.assert_called_once_with(1, "New Title", "New Content")
        
        # Assert the result is as expected
        assert response.root.content[0].text == "Memory 1 updated successfully."
        
        # Reset mock for next test
        mock_update_memory.reset_mock()
        
        # Call with just title
        request = types.CallToolRequest(
            method="tools/call",
            params=types.CallToolRequestParams(
                name="update_memory",
                arguments={"memory_id": 1, "title": "New Title"}
            )
        )
        
        response = await server.request_handlers[types.CallToolRequest](request)
        
        # Assert mock was called with correct parameters
        mock_update_memory.assert_called_once_with(1, "New Title", None)


@pytest.mark.asyncio
async def test_handle_call_tool_delete_memory():
    """Test the call_tool handler for delete_memory."""
    server = await serve()
    
    with patch("memory_mcp.server.delete_memory") as mock_delete_memory:
        mock_delete_memory.return_value = "Memory 1 deleted successfully."
        
        # Create request
        request = types.CallToolRequest(
            method="tools/call",
            params=types.CallToolRequestParams(
                name="delete_memory",
                arguments={"memory_id": 1}
            )
        )
        
        # Call the handler
        response = await server.request_handlers[types.CallToolRequest](request)
        
        # Assert mock was called with correct parameters
        mock_delete_memory.assert_called_once_with(1)
        
        # Assert the result is as expected
        assert response.root.content[0].text == "Memory 1 deleted successfully."


@pytest.mark.asyncio
async def test_handle_call_tool_unknown_tool():
    """Test the call_tool handler with an unknown tool."""
    server = await serve()
    
    # Create request with unknown tool
    request = types.CallToolRequest(
        method="tools/call",
        params=types.CallToolRequestParams(
            name="unknown_tool",
            arguments={}
        )
    )
    
    # Call the handler
    response = await server.request_handlers[types.CallToolRequest](request)
    
    # Check that we got an error response
    assert response.root.isError is True
    assert "Unknown tool: unknown_tool" in response.root.content[0].text


@pytest.mark.asyncio
async def test_handle_call_tool_missing_arguments():
    """Test the call_tool handler with missing arguments."""
    server = await serve()
    
    # Test remember with missing arguments
    request = types.CallToolRequest(
        method="tools/call",
        params=types.CallToolRequestParams(
            name="remember",
            arguments={}
        )
    )
    
    response = await server.request_handlers[types.CallToolRequest](request)
    assert response.root.isError is True
    assert "Missing title or content arguments" in response.root.content[0].text
    
    # Test update_memory with missing memory_id
    request = types.CallToolRequest(
        method="tools/call",
        params=types.CallToolRequestParams(
            name="update_memory",
            arguments={}
        )
    )
    
    response = await server.request_handlers[types.CallToolRequest](request)
    assert response.root.isError is True
    assert "Missing memory_id argument" in response.root.content[0].text
    
    # Test delete_memory with missing memory_id
    request = types.CallToolRequest(
        method="tools/call",
        params=types.CallToolRequestParams(
            name="delete_memory",
            arguments={}
        )
    )
    
    response = await server.request_handlers[types.CallToolRequest](request)
    assert response.root.isError is True
    assert "Missing memory_id argument" in response.root.content[0].text


@pytest.mark.asyncio
@patch("mcp.server.stdio.stdio_server")
@patch("memory_mcp.server.serve")
async def test_main(mock_serve, mock_stdio_server):
    """Test the main function."""
    from memory_mcp.server import main
    
    # Set up mocks
    mock_server = MagicMock()
    mock_server.get_capabilities.return_value = {"capabilities": "test"}
    
    # Create a proper awaitable for the run method
    async def mock_run(*args, **kwargs):
        return None
    
    mock_server.run = mock_run
    mock_serve.return_value = mock_server
    
    # Mock the context manager for stdio_server
    mock_read_stream = MagicMock()
    mock_write_stream = MagicMock()
    mock_stdio_context = MagicMock()
    mock_stdio_context.__aenter__.return_value = (mock_read_stream, mock_write_stream)
    mock_stdio_server.return_value = mock_stdio_context
    
    # Call the function
    await main()
    
    # Assert mocks were called correctly
    mock_serve.assert_called_once()
    mock_stdio_server.assert_called_once()
    
    # Since we replaced the run method, we can't assert it was called directly
    # We'll verify that the server was initialized correctly in our other tests


@pytest.mark.asyncio
async def test_list_tools_schema():
    """Test that the list_tools handler returns tools with correct schemas."""
    server = await serve()
    
    # Call the handler directly
    mock_request = MagicMock()
    response = await server.request_handlers[types.ListToolsRequest](mock_request)
    
    # Extract tools from response
    tools = response.root.tools
    
    # Check the remember tool schema
    remember_tool = next(tool for tool in tools if tool.name == "remember")
    assert remember_tool.description == "Store a new memory."
    assert "title" in remember_tool.inputSchema["properties"]
    assert "content" in remember_tool.inputSchema["properties"]
    assert "required" in remember_tool.inputSchema
    assert "title" in remember_tool.inputSchema["required"]
    assert "content" in remember_tool.inputSchema["required"]
    
    # Check the get_memory tool schema
    get_memory_tool = next(tool for tool in tools if tool.name == "get_memory")
    assert get_memory_tool.description == "Retrieve a specific memory by ID or title."
    assert "memory_id" in get_memory_tool.inputSchema["properties"]
    assert "title" in get_memory_tool.inputSchema["properties"]
    
    # Check the list_memories tool schema
    list_memories_tool = next(tool for tool in tools if tool.name == "list_memories")
    assert list_memories_tool.description == "List all stored memories."
    
    # Check the update_memory tool schema
    update_memory_tool = next(tool for tool in tools if tool.name == "update_memory")
    assert update_memory_tool.description == "Update an existing memory."
    assert "memory_id" in update_memory_tool.inputSchema["properties"]
    assert "title" in update_memory_tool.inputSchema["properties"]
    assert "content" in update_memory_tool.inputSchema["properties"]
    assert "required" in update_memory_tool.inputSchema
    assert "memory_id" in update_memory_tool.inputSchema["required"]
    
    # Check the delete_memory tool schema
    delete_memory_tool = next(tool for tool in tools if tool.name == "delete_memory")
    assert delete_memory_tool.description == "Delete a memory."
    assert "memory_id" in delete_memory_tool.inputSchema["properties"]
    assert "required" in delete_memory_tool.inputSchema
    assert "memory_id" in delete_memory_tool.inputSchema["required"]
