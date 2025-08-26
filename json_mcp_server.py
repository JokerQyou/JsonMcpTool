#!/usr/bin/env python3
"""
JsonMcpTool - MCP Server for JSON Operations

A complete MCP (Model Context Protocol) server for efficient JSON file processing,
specifically designed for I18Next translation files and other large JSON documents.

This server provides JSON operations via the Model Context Protocol so users can
interact with their translation files through Claude Code.
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from operations import (
        get_key, add_key, update_key, rename_key, 
        remove_key, list_keys, key_exists, validate_json
    )
except ImportError as e:
    print(f"Error importing operations: {e}", file=sys.stderr)
    print("Make sure the 'src' directory exists with the required modules", file=sys.stderr)
    sys.exit(1)

class JsonMcpServer:
    """MCP Server for JSON operations"""
    
    def __init__(self):
        self.tools = [
            {
                "name": "get_key",
                "description": "Get value from JSON file by dot-notation key path",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the JSON file"
                        },
                        "key_path": {
                            "type": "string", 
                            "description": "Dot-notation path to the key (e.g., 'dashboard.title')"
                        }
                    },
                    "required": ["file_path", "key_path"]
                }
            },
            {
                "name": "add_key",
                "description": "Add new key-value pair to JSON file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the JSON file"
                        },
                        "key_path": {
                            "type": "string",
                            "description": "Dot-notation path for the new key"
                        },
                        "value": {
                            "description": "Value to add (can be string, object, array, etc.)"
                        }
                    },
                    "required": ["file_path", "key_path", "value"]
                }
            },
            {
                "name": "update_key", 
                "description": "Update existing key in JSON file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the JSON file"
                        },
                        "key_path": {
                            "type": "string",
                            "description": "Dot-notation path to the key to update"
                        },
                        "value": {
                            "description": "New value (can be string, object, array, etc.)"
                        }
                    },
                    "required": ["file_path", "key_path", "value"]
                }
            },
            {
                "name": "rename_key",
                "description": "Rename/move existing key in JSON file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the JSON file"
                        },
                        "old_path": {
                            "type": "string",
                            "description": "Current dot-notation path of the key"
                        },
                        "new_path": {
                            "type": "string", 
                            "description": "New dot-notation path for the key"
                        }
                    },
                    "required": ["file_path", "old_path", "new_path"]
                }
            },
            {
                "name": "remove_key",
                "description": "Remove key from JSON file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the JSON file"
                        },
                        "key_path": {
                            "type": "string",
                            "description": "Dot-notation path to the key to remove"
                        }
                    },
                    "required": ["file_path", "key_path"]
                }
            },
            {
                "name": "list_keys",
                "description": "List all keys at specified path in JSON file", 
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the JSON file"
                        },
                        "key_path": {
                            "type": "string",
                            "description": "Dot-notation path to list keys from (optional, defaults to root)"
                        }
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "key_exists",
                "description": "Check if key exists in JSON file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the JSON file"
                        },
                        "key_path": {
                            "type": "string",
                            "description": "Dot-notation path to check"
                        }
                    },
                    "required": ["file_path", "key_path"]
                }
            },
            {
                "name": "validate_json",
                "description": "Validate JSON file syntax and structure",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the JSON file to validate"
                        }
                    },
                    "required": ["file_path"]
                }
            }
        ]

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tool calls"""
        try:
            if tool_name == "get_key":
                result = get_key(arguments["file_path"], arguments["key_path"])
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2, ensure_ascii=False)
                        }
                    ]
                }
                
            elif tool_name == "add_key":
                add_key(arguments["file_path"], arguments["key_path"], arguments["value"])
                return {
                    "content": [
                        {
                            "type": "text", 
                            "text": f"✅ Added key '{arguments['key_path']}' to {arguments['file_path']}"
                        }
                    ]
                }
                
            elif tool_name == "update_key":
                update_key(arguments["file_path"], arguments["key_path"], arguments["value"])
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"✅ Updated key '{arguments['key_path']}' in {arguments['file_path']}"
                        }
                    ]
                }
                
            elif tool_name == "rename_key":
                rename_key(arguments["file_path"], arguments["old_path"], arguments["new_path"])
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"✅ Renamed '{arguments['old_path']}' → '{arguments['new_path']}' in {arguments['file_path']}"
                        }
                    ]
                }
                
            elif tool_name == "remove_key":
                removed_value = remove_key(arguments["file_path"], arguments["key_path"])
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"✅ Removed key '{arguments['key_path']}' from {arguments['file_path']}\nRemoved value: {json.dumps(removed_value, indent=2, ensure_ascii=False)}"
                        }
                    ]
                }
                
            elif tool_name == "list_keys":
                key_path = arguments.get("key_path")
                keys = list_keys(arguments["file_path"], key_path)
                path_desc = f"at '{key_path}'" if key_path else "at root level"
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Keys {path_desc} in {arguments['file_path']}:\n" + "\n".join(f"• {key}" for key in keys)
                        }
                    ]
                }
                
            elif tool_name == "key_exists":
                exists = key_exists(arguments["file_path"], arguments["key_path"])
                status = "✅ exists" if exists else "❌ does not exist"
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Key '{arguments['key_path']}' {status} in {arguments['file_path']}"
                        }
                    ]
                }
                
            elif tool_name == "validate_json":
                result = validate_json(arguments["file_path"])
                if result["valid"]:
                    perf = result.get("performance", {})
                    file_size = perf.get("file_size", 0)
                    parse_time = perf.get("parse_time", 0)
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"✅ {arguments['file_path']} is valid JSON\nFile size: {file_size} bytes\nParse time: {parse_time:.3f}s"
                            }
                        ]
                    }
                else:
                    error = result.get("error", {})
                    error_msg = error.get("message", "Unknown error")
                    line = error.get("line", 0)
                    return {
                        "content": [
                            {
                                "type": "text", 
                                "text": f"❌ {arguments['file_path']} contains invalid JSON\nError: {error_msg}\nLine: {line}"
                            }
                        ]
                    }
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Unknown tool: {tool_name}"
                        }
                    ],
                    "isError": True
                }
                
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"❌ Error: {str(e)}"
                    }
                ],
                "isError": True
            }

    async def run(self):
        """Run the MCP server"""
        print("JsonMcpTool MCP Server starting...", file=sys.stderr)
        
        # Send server info
        server_info = {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "jsonmcptool",
                    "version": "1.0.0"
                }
            }
        }
        
        try:
            while True:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                    
                try:
                    request = json.loads(line.strip())
                    method = request.get("method")
                    
                    if method == "initialize":
                        response = {
                            "jsonrpc": "2.0", 
                            "id": request.get("id"),
                            "result": {
                                "protocolVersion": "2024-11-05",
                                "capabilities": {
                                    "tools": {}
                                },
                                "serverInfo": {
                                    "name": "jsonmcptool", 
                                    "version": "1.0.0"
                                }
                            }
                        }
                        
                    elif method == "tools/list":
                        response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {
                                "tools": self.tools
                            }
                        }
                        
                    elif method == "tools/call":
                        params = request.get("params", {})
                        tool_name = params.get("name")
                        arguments = params.get("arguments", {})
                        
                        result = self.handle_tool_call(tool_name, arguments)
                        response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"), 
                            "result": result
                        }
                        
                    else:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "error": {
                                "code": -32601,
                                "message": f"Method not found: {method}"
                            }
                        }
                    
                    print(json.dumps(response), flush=True)
                    
                except json.JSONDecodeError as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": f"Parse error: {str(e)}"
                        }
                    }
                    print(json.dumps(error_response), flush=True)
                    
                except Exception as e:
                    error_response = {
                        "jsonrpc": "2.0", 
                        "id": request.get("id") if 'request' in locals() else None,
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    }
                    print(json.dumps(error_response), flush=True)
                    
        except KeyboardInterrupt:
            print("JsonMcpTool MCP Server stopped", file=sys.stderr)

def main():
    """Main entry point"""
    server = JsonMcpServer()
    try:
        asyncio.run(server.run())
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()