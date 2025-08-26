# JsonMcpTool - MCP Tool for JSON Processing

## Project Overview
JsonMcpTool is an MCP (Model Context Protocol) server designed specifically for processing large JSON files, with a focus on I18Next translation files. It provides efficient operations without loading entire files into LLM context, addressing the limitations of generic tools like Grep/Update when working with complex JSON structures.

## Core Features

### Primary Operations
1. **get_key(path)** - Retrieve value by dot-notation key path
   - Returns: value (string), object (for sections), or error if not found
   - Example: `get_key('dashboard.title')` → `"Dashboard"`
   - Example: `get_key('forms.validation')` → `{"required": "Required field", "email": "Invalid email"}`

2. **add_key(path, value)** - Add new key-value pair
   - Supports string values and nested objects
   - Returns error if key already exists
   - Example: `add_key('alerts.success', 'Operation completed')`
   - Example: `add_key('modals.confirm', {'title': 'Confirm', 'cancel': 'Cancel'})`

3. **update_key(path, value)** - Update existing key
   - Returns error if key doesn't exist
   - Supports both string and object values

4. **rename_key(old_path, new_path)** - Rename existing key
   - Preserves value and nested structure
   - Returns error if old key doesn't exist or new key exists

5. **remove_key(path)** - Delete key and its value
   - Returns error if key doesn't exist
   - Handles nested cleanup (removes empty parent objects)

### Supporting Operations
6. **list_keys(path?)** - List all keys at given path (or root)
   - Returns flat list of available keys
   - Useful for exploration and validation

7. **key_exists(path)** - Check if key exists
   - Returns boolean
   - Faster than get_key for existence checks

8. **validate_json(file_path)** - Validate JSON syntax
   - Returns validation status and error details

## Technical Architecture

### Core Components
1. **JSON Parser Module** - Stream-based JSON parsing for large files
2. **Path Resolution Engine** - Handle dot-notation key paths
3. **Operation Engine** - Execute CRUD operations efficiently
4. **MCP Server Interface** - Handle protocol communication
5. **Error Handling System** - Comprehensive error reporting

### Key Design Principles
- **Memory Efficient**: Stream processing, avoid loading entire files
- **Path-based Operations**: Support nested key access via dot notation
- **Atomic Operations**: Ensure file consistency during modifications
- **Error-first Design**: Clear error messages for debugging
- **I18Next Optimized**: Handle common translation file patterns

### File Handling Strategy
- Use streaming JSON parser for reading
- Implement incremental updates for modifications
- Maintain file locks during operations
- Backup mechanism for critical operations
- Support for multiple JSON file formats

### Path Resolution
- Support dot notation: `section.subsection.key`
- Handle array indices: `items[0].name`
- Escape sequences for keys with dots: `"key.with.dots"`
- Root-level operations: direct key access

## Error Handling

### Error Types
- `KEY_NOT_FOUND` - Specified key doesn't exist
- `KEY_EXISTS` - Key already exists (for add operations)
- `INVALID_PATH` - Malformed key path
- `INVALID_JSON` - File contains invalid JSON
- `FILE_NOT_FOUND` - Target file doesn't exist
- `PERMISSION_DENIED` - Insufficient file permissions
- `PARSE_ERROR` - JSON parsing failed

### Error Response Format
```json
{
  "error": "KEY_NOT_FOUND",
  "message": "Key 'dashboard.nonexistent' not found",
  "path": "dashboard.nonexistent",
  "file": "/path/to/file.json"
}
```

## Performance Considerations
- Implement caching for frequently accessed paths
- Use efficient JSON libraries (ijson for Python, stream-json for Node.js)
- Minimize file I/O operations
- Batch operations where possible
- Index commonly used key patterns

## Development Phases

### Phase 1: Core Functionality
- Basic JSON parsing and path resolution
- Implement get_key, add_key, remove_key operations
- Basic MCP server setup
- Error handling framework

### Phase 2: Advanced Operations
- rename_key and update_key operations
- list_keys and key_exists utilities
- File validation and backup systems
- Performance optimizations

### Phase 3: I18Next Optimization
- I18Next-specific features (pluralization, interpolation)
- Namespace handling
- Multi-file project support
- Translation validation tools

### Phase 4: Enhanced Features
- Batch operations support
- Watch mode for file changes
- Configuration management
- Advanced caching strategies

## Testing Strategy
- Unit tests for each operation type
- Integration tests with various JSON file sizes
- Performance benchmarks with large translation files
- Error scenario testing
- I18Next compatibility validation

## Security Considerations
- File path validation to prevent directory traversal
- Permission checks before file operations
- Input sanitization for all parameters
- Atomic file operations to prevent corruption
- Audit logging for sensitive operations