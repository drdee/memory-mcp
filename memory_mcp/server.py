#!/usr/bin/env python3
"""
Memory Manager MCP Server

A Model Context Protocol server for storing and retrieving memories
using low-level Server implementation and SQLite storage.
"""

__version__ = "0.1.0"

import sqlite3
import datetime
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio


class DatabaseManager:
    """Manages SQLite database operations for the Memory Manager."""

    def __init__(self, db_path: str = "memories.db"):
        """Initialize the database manager with the given path."""
        self.db_path = Path(db_path)
        self.conn: Optional[sqlite3.Connection] = None
        self.initialize_db()

    def initialize_db(self) -> None:
        """Create the database and necessary tables if they don't exist."""
        self.conn = sqlite3.connect(self.db_path)
        if self.conn is None:
            raise RuntimeError("Failed to connect to database")

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL
            )
        """
        )
        self.conn.commit()

    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def add_memory(self, title: str, content: str) -> int:
        """Add a new memory to the database."""
        if not self.conn:
            self.initialize_db()

        if self.conn is None:
            raise RuntimeError("Database connection not available")

        current_time = datetime.datetime.now().isoformat()
        cursor = self.conn.execute(
            """
            INSERT INTO memories (title, content, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (title, content, current_time, current_time),
        )
        self.conn.commit()
        return cursor.lastrowid or 0

    def get_memory_by_id(self, memory_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a memory by its ID."""
        if not self.conn:
            self.initialize_db()

        if self.conn is None:
            raise RuntimeError("Database connection not available")

        cursor = self.conn.execute(
            "SELECT id, title, content, created_at, updated_at FROM memories WHERE id = ?",
            (memory_id,),
        )
        row = cursor.fetchone()

        if row:
            return {
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "created_at": row[3],
                "updated_at": row[4],
            }
        return None

    def get_memory_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """Retrieve a memory by its title."""
        if not self.conn:
            self.initialize_db()

        if self.conn is None:
            raise RuntimeError("Database connection not available")

        cursor = self.conn.execute(
            "SELECT id, title, content, created_at, updated_at FROM memories WHERE title = ?",
            (title,),
        )
        row = cursor.fetchone()

        if row:
            return {
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "created_at": row[3],
                "updated_at": row[4],
            }
        return None

    def list_memories(self) -> List[Dict[str, Any]]:
        """Get a list of all memories with basic information."""
        if not self.conn:
            self.initialize_db()

        if self.conn is None:
            raise RuntimeError("Database connection not available")

        cursor = self.conn.execute("SELECT id, title FROM memories")
        return [{"id": row[0], "title": row[1]} for row in cursor.fetchall()]

    def update_memory(
        self, memory_id: int, title: Optional[str] = None, content: Optional[str] = None
    ) -> bool:
        """Update an existing memory's title or content."""
        if not self.conn:
            self.initialize_db()

        if self.conn is None:
            raise RuntimeError("Database connection not available")

        # First check if the memory exists
        existing_memory = self.get_memory_by_id(memory_id)
        if not existing_memory:
            return False

        # Build update query
        update_items = []
        params: List[Any] = []

        if title is not None:
            update_items.append("title = ?")
            params.append(title)

        if content is not None:
            update_items.append("content = ?")
            params.append(content)

        if not update_items:
            return True  # Nothing to update

        # Add updated_at timestamp
        update_items.append("updated_at = ?")
        params.append(datetime.datetime.now().isoformat())

        # Add memory_id to params
        params.append(memory_id)

        # Execute update
        self.conn.execute(
            f"UPDATE memories SET {', '.join(update_items)} WHERE id = ?", params
        )
        self.conn.commit()
        return True

    def delete_memory(self, memory_id: int) -> bool:
        """Delete a memory by its ID."""
        if not self.conn:
            self.initialize_db()

        if self.conn is None:
            raise RuntimeError("Database connection not available")

        # Check if memory exists
        if not self.get_memory_by_id(memory_id):
            return False

        self.conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        self.conn.commit()
        return True


# Initialize the database manager
db = DatabaseManager()


# Core memory functions
def remember(title: str, content: str) -> str:
    """
    Store a new memory.

    Args:
        title: A concise title for the memory
        content: The full content of the memory to store

    Returns:
        A confirmation message with the ID of the stored memory
    """
    try:
        memory_id = db.add_memory(title, content)
        return f"Memory stored successfully with ID: {memory_id}."
    except Exception as e:
        return f"Error storing memory: {str(e)}"


def get_memory(memory_id: Optional[int] = None, title: Optional[str] = None) -> str:
    """
    Retrieve a specific memory by ID or title.

    Args:
        memory_id: The ID of the memory to retrieve
        title: The title of the memory to retrieve

    Returns:
        The memory content or an error message
    """
    try:
        if memory_id is not None:
            memory = db.get_memory_by_id(int(memory_id))
        elif title is not None:
            memory = db.get_memory_by_title(title)
        else:
            return "Error: Please provide either a memory_id or title."

        if memory:
            return f"Title: {memory['title']}\n\nContent: {memory['content']}"
        return "Memory not found."
    except Exception as e:
        return f"Error retrieving memory: {str(e)}"


def list_memories() -> str:
    """
    List all stored memories.

    Returns:
        A formatted list of all memories with ID and title
    """
    try:
        memories = db.list_memories()
        if not memories:
            return "No memories stored yet."

        result = "Stored Memories:\n\n"
        for memory in memories:
            result += f"ID: {memory['id']} - {memory['title']}\n"
        return result
    except Exception as e:
        return f"Error listing memories: {str(e)}"


def update_memory(
    memory_id: int, title: Optional[str] = None, content: Optional[str] = None
) -> str:
    """
    Update an existing memory.

    Args:
        memory_id: The ID of the memory to update
        title: Optional new title for the memory
        content: Optional new content for the memory

    Returns:
        A confirmation message
    """
    try:
        if title is None and content is None:
            return (
                "Error: Please provide at least one field to update (title or content)."
            )

        success = db.update_memory(memory_id, title, content)
        if success:
            return f"Memory {memory_id} updated successfully."
        return f"Memory with ID {memory_id} not found."
    except Exception as e:
        return f"Error updating memory: {str(e)}"


def delete_memory(memory_id: int) -> str:
    """
    Delete a memory.

    Args:
        memory_id: The ID of the memory to delete

    Returns:
        A confirmation message
    """
    try:
        success = db.delete_memory(memory_id)
        if success:
            return f"Memory {memory_id} deleted successfully."
        return f"Memory with ID {memory_id} not found."
    except Exception as e:
        return f"Error deleting memory: {str(e)}"


async def serve() -> Server:
    """Create and configure the memory server."""
    server: Server = Server("Memory Manager")

    @asynccontextmanager
    async def lifespan(_: Any) -> AsyncIterator[None]:
        """Manage the database connection lifecycle."""
        try:
            yield
        finally:
            db.close()

    # Set the lifespan handler
    server.lifespan = lifespan

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """Return list of available tools."""
        return [
            types.Tool(
                name="remember",
                description="Store a new memory.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "A concise title for the memory",
                        },
                        "content": {
                            "type": "string",
                            "description": "The full content of the memory to store",
                        },
                    },
                    "required": ["title", "content"],
                    "title": "rememberArguments",
                },
            ),
            types.Tool(
                name="get_memory",
                description="Retrieve a specific memory by ID or title.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "memory_id": {
                            "type": "integer",
                            "description": "The ID of the memory to retrieve",
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the memory to retrieve",
                        },
                    },
                    "title": "getMemoryArguments",
                },
            ),
            types.Tool(
                name="list_memories",
                description="List all stored memories.",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "title": "listMemoriesArguments",
                },
            ),
            types.Tool(
                name="update_memory",
                description="Update an existing memory.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "memory_id": {
                            "type": "integer",
                            "description": "The ID of the memory to update",
                        },
                        "title": {
                            "type": "string",
                            "description": "Optional new title for the memory",
                        },
                        "content": {
                            "type": "string",
                            "description": "Optional new content for the memory",
                        },
                    },
                    "required": ["memory_id"],
                    "title": "updateMemoryArguments",
                },
            ),
            types.Tool(
                name="delete_memory",
                description="Delete a memory.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "memory_id": {
                            "type": "integer",
                            "description": "The ID of the memory to delete",
                        },
                    },
                    "required": ["memory_id"],
                    "title": "deleteMemoryArguments",
                },
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool calls."""
        if name == "remember":
            if not arguments or "title" not in arguments or "content" not in arguments:
                raise ValueError("Missing title or content arguments")
            result = remember(arguments["title"], arguments["content"])
            return [types.TextContent(type="text", text=result)]

        elif name == "get_memory":
            if not arguments:
                raise ValueError("Missing arguments")
            memory_id = arguments.get("memory_id")
            title = arguments.get("title")
            result = get_memory(memory_id, title)
            return [types.TextContent(type="text", text=result)]

        elif name == "list_memories":
            result = list_memories()
            return [types.TextContent(type="text", text=result)]

        elif name == "update_memory":
            if not arguments or "memory_id" not in arguments:
                raise ValueError("Missing memory_id argument")
            memory_id = int(arguments["memory_id"])
            title = arguments.get("title")
            content = arguments.get("content")
            result = update_memory(memory_id, title, content)
            return [types.TextContent(type="text", text=result)]

        elif name == "delete_memory":
            if not arguments or "memory_id" not in arguments:
                raise ValueError("Missing memory_id argument")
            memory_id = int(arguments["memory_id"])
            result = delete_memory(memory_id)
            return [types.TextContent(type="text", text=result)]

        else:
            raise ValueError(f"Unknown tool: {name}")

    return server


def run_server() -> None:
    """CLI entry point to run the MCP server."""
    print("Starting Memory Manager MCP Server...")
    print("This server allows you to store and retrieve memories and ideas.")

    async def _run() -> None:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            mcp_server = await serve()
            await mcp_server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="Memory Manager",
                    server_version=__version__,
                    capabilities=mcp_server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        print("\nServer stopped.")
        exit(0)


async def main() -> None:
    """Main entry point for the package when run as a module."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        mcp_server = await serve()
        await mcp_server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="Memory Manager",
                server_version=__version__,
                capabilities=mcp_server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
