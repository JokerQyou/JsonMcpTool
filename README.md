# JsonMcpTool

A complete MCP (Model Context Protocol) tool for efficient JSON file processing, specifically designed for I18Next translation files and other large JSON documents.

## What This Tool Does

JsonMcpTool allows you to interact with JSON translation files through **Claude Code** using natural language. Instead of manually editing large translation files, you can ask Claude to:

- "Get the dashboard title from my translations.json"
- "Add a new success message to the alerts section" 
- "Update the login form validation text"
- "Rename the old_section to new_section"
- "Remove the deprecated translations"
- "List all the keys in the dashboard section"

## Key Features

- **🎯 I18Next Optimized**: Perfect for translation files with interpolation (`{{name}}`)
- **🚀 Memory Efficient**: Handles large JSON files without loading everything into memory
- **🔍 Smart Path Resolution**: Works with both `"key.with.dots"` and `section.subsection.key`
- **💾 Safe Operations**: Atomic file writes prevent corruption
- **⚡ Fast**: Optimized for files up to 100MB+
- **🛡️ Error Handling**: Clear error messages for debugging

## Installation & Setup

### 1. Prerequisites

You need the `uv` command-line tool installed:

```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
# OR on macOS with Homebrew:
brew install uv
# OR with pip:
pip install uv
```

### 2. Download JsonMcpTool
```bash
# Clone or download this repository to your preferred location
git clone <repository-url> /path/to/JsonMcpTool
# OR download and extract the ZIP file
```

### 3. Configure Claude Code

Add JsonMcpTool to your Claude Code MCP configuration using the recommended command:

```bash
claude mcp add jsonmcptool -- uv --directory /PATH/TO/REPO run json_mcp_server.py
```

**⚠️ Important**: Replace `/PATH/TO/REPO` with the actual absolute path where you saved JsonMcpTool.

**Alternative manual configuration:**
If you prefer to configure manually, add this to your Claude Code settings:

```json
{
  "mcpServers": {
    "jsonmcptool": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "/PATH/TO/REPO",
        "run", 
        "json_mcp_server.py"
      ]
    }
  }
}
```

### 4. Restart Claude Code

Restart Claude Code to load the new MCP tool.

### 5. Test It Works

Create a simple JSON file and ask Claude:
```
"I have a translations.json file at /path/to/translations.json with this content:
{
  "dashboard": {
    "title": "Dashboard"  
  }
}

Can you get the dashboard title for me?"
```

Claude should respond with the value "Dashboard".

## How to Use

Once configured, you can ask Claude Code to perform JSON operations using natural language:

### Getting Values
- *"Get the dashboard.title from my translations.json"*
- *"What's the value of forms.validation.email in the translation file?"*
- *"Show me the entire alerts section"*

### Adding New Translations  
- *"Add a new key success_message with value 'Success!' to the alerts section"*
- *"Create a new modal.confirm section with title 'Confirm Action' and cancel 'Cancel'"*

### Updating Existing Translations
- *"Change the dashboard title to 'Control Panel'"*
- *"Update the login form email validation message"*

### Managing Structure
- *"Rename dashboard.old_title to dashboard.title"*
- *"Move forms.validation to common.validation"*
- *"Remove the deprecated section from the file"*

### Exploring Files
- *"List all the top-level sections in my translations.json"*
- *"What keys are available in the dashboard section?"*
- *"Check if alerts.success exists"*

## Example Translation File

JsonMcpTool works perfectly with I18Next translation files:

```json
{
  "dashboard": {
    "title": "Dashboard",
    "welcome": "Welcome back, {{username}}!",
    "stats": {
      "users": "Total Users: {{count}}",
      "revenue": "Monthly Revenue"
    }
  },
  "forms": {
    "validation": {
      "required": "This field is required",
      "email": "Please enter a valid email",
      "minLength": "Minimum {{min}} characters required"
    },
    "buttons": {
      "submit": "Submit",
      "cancel": "Cancel"
    }
  },
  "alerts": {
    "success": "Operation completed successfully",
    "error": "Something went wrong",
    "warning": "Please check your input"
  }
}
```

## Advanced Features

### Smart Key Handling
- **Literal keys with dots**: `"api.key.v1": "value"` 
- **Nested paths**: `api.endpoints.users`
- **Mixed usage**: Both work automatically

### I18Next Features
- **Interpolation**: `"Hello {{name}}!"` 
- **Pluralization**: `"item"` / `"item_plural"`
- **Namespaces**: Full support for namespace:key syntax

### Performance
- **Large files**: Optimized for translation files up to 100MB+
- **Memory efficient**: Stream-based processing
- **Atomic writes**: Safe concurrent access

## Available Operations

| Operation | Description | Example Usage |
|-----------|-------------|---------------|
| **get_key** | Retrieve value by path | *"Get dashboard.title"* |
| **add_key** | Add new key-value pair | *"Add alerts.info with message"* |
| **update_key** | Update existing key | *"Change dashboard.title to 'New Title'"* |
| **rename_key** | Rename/move key | *"Rename old_key to new_key"* |
| **remove_key** | Delete key | *"Remove the deprecated section"* |
| **list_keys** | List keys at path | *"List all dashboard keys"* |
| **key_exists** | Check if key exists | *"Does alerts.success exist?"* |
| **validate_json** | Validate file syntax | *"Check if my JSON file is valid"* |

## Troubleshooting

### Common Issues

**"Tool not found"**: 
- Restart Claude Code after adding the MCP configuration
- Check that the path to `json_mcp_server.py` is absolute and correct

**"Permission denied"**:
- Make sure `json_mcp_server.py` is executable: `chmod +x json_mcp_server.py`
- On Windows, ensure Python is in your PATH

**"Module not found errors"**:
- Ensure the `src` directory exists in the JsonMcpTool folder
- Don't move or rename the internal files

**File path issues**:
- Always use absolute paths when referring to JSON files
- Use forward slashes even on Windows: `/path/to/file.json`

### Getting Help

If you encounter issues:

1. **Test the tool directly**:
   ```bash
   python /path/to/JsonMcpTool/json_mcp_server.py
   ```

2. **Check the files exist**:
   ```bash
   ls -la /path/to/JsonMcpTool/
   # Should show: json_mcp_server.py, src/, tests/, etc.
   ```

3. **Verify JSON file syntax**:
   Use any online JSON validator to check your translation files

## What Makes This Special

Unlike generic text-editing tools, JsonMcpTool:

✅ **Understands JSON structure** - No risk of breaking syntax  
✅ **Handles large files efficiently** - Works with 100MB+ translation files  
✅ **Supports I18Next patterns** - Built for translation workflows  
✅ **Safe operations** - Atomic writes prevent file corruption  
✅ **Natural language interface** - Just ask Claude what you want to do  

Perfect for managing translation files, configuration files, or any JSON data through Claude Code!

## Project Structure

```
JsonMcpTool/
├── json_mcp_server.py        # ← Main MCP server (ready to use!)
├── src/
│   ├── operations.py         # Core JSON operations
│   ├── json_handler.py       # File I/O with caching
│   ├── path_resolver.py      # Smart path handling
│   └── __init__.py           # Package initialization
├── tests/                    # Comprehensive test suite
│   ├── unit/                 # 187+ unit tests
│   ├── integration/          # Integration tests
│   ├── performance/          # Performance tests
│   └── fixtures/             # Test JSON files
├── PLAN.md                   # Implementation details
└── README.md                 # This file
```

## License

MIT License - Use freely in your projects!