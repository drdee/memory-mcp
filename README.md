# Memory MCP

A Model Context Protocol server for storing and retrieving memories using low-level Server implementation and SQLite storage.

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management instead of pip. uv is a fast, reliable Python package installer and resolver.

Install using uv:

```bash
uv pip install memory-mcp
```

Or install directly from source:

```bash
uv pip install .
```

For development:

```bash
uv pip install -e ".[dev]"
```

If you don't have uv installed, you can install it following the [official instructions](https://github.com/astral-sh/uv#installation).

## Usage

### Running the server

```bash
memory-mcp
```

This will start the MCP server that allows you to store and retrieve memories.

### Available Tools

The Memory MCP provides the following tools:

- `remember`: Store a new memory with a title and content
- `get_memory`: Retrieve a specific memory by ID or title
- `list_memories`: List all stored memories
- `update_memory`: Update an existing memory
- `delete_memory`: Delete a memory

## Debugging with MCP Inspect

MCP provides a handy command-line tool called `mcp inspect` that allows you to debug and interact with your MCP server directly.

### Setup

1. First, make sure the MCP CLI tools are installed:

```bash
uv pip install mcp[cli]
```

2. Start the Memory MCP server in one terminal:

```bash
memory-mcp
```

3. In another terminal, connect to the running server using `mcp inspect`:

```bash
mcp inspect
```

### Using MCP Inspect

Once connected, you can:

#### List available tools

```
> tools
```

This will display all the tools provided by the Memory MCP server.

#### Call a tool

To call a tool, use the `call` command followed by the tool name and any required arguments:

```
> call remember title="Meeting Notes" content="Discussed project timeline and milestones."
```

```
> call list_memories
```

```
> call get_memory memory_id=1
```

```
> call update_memory memory_id=1 title="Updated Title" content="Updated content."
```

```
> call delete_memory memory_id=1
```

#### Debug Mode

You can enable debug mode to see detailed request and response information:

```
> debug on
```

This helps you understand exactly what data is being sent to and received from the server.

#### Exploring Tool Schemas

To view the schema for a specific tool:

```
> tool remember
```

This shows the input schema, required parameters, and description for the tool.

### Troubleshooting

If you encounter issues:

1. Check the server logs in the terminal where your server is running for any error messages.
2. In the MCP inspect terminal, enable debug mode with `debug on` to see raw requests and responses.
3. Ensure the tool parameters match the expected schema (check with the `tool` command).
4. If the server crashes, check for any uncaught exceptions in the server terminal.

## Development

To contribute to the project, install the development dependencies:

```bash
uv pip install -e ".[dev]"
```

### Managing Dependencies

This project uses `uv.lock` file to lock dependencies. To update dependencies:

```bash
uv pip compile pyproject.toml -o uv.lock
```

### Running tests

```bash
python -m pytest
```

### Code formatting

```bash
black memory_mcp tests
```

### Linting

```bash
ruff check memory_mcp tests
```

### Type checking

```bash
mypy memory_mcp
``` 