package mcpserver

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"
	"jsonmcptool/internal/operations"
)

// NewJSONMcpServer creates a new MCP server for JSON operations
func NewJSONMcpServer() *server.MCPServer {
	s := server.NewMCPServer(
		"jsonmcptool",
		"1.0.0",
	)

	// Add all JSON operation tools
	addGetKeyTool(s)
	addAddKeyTool(s)
	addUpdateKeyTool(s)
	addRenameKeyTool(s)
	addRemoveKeyTool(s)
	addListKeysTool(s)
	addKeyExistsTool(s)
	addValidateJSONTool(s)

	return s
}

// addGetKeyTool adds the get_key tool
func addGetKeyTool(s *server.MCPServer) {
	getTool := mcp.NewTool("get_key",
		mcp.WithDescription("Get value from JSON file by dot-notation key path"),
		mcp.WithString("file_path",
			mcp.Required(),
			mcp.Description("Path to the JSON file"),
		),
		mcp.WithString("key_path",
			mcp.Required(),
			mcp.Description("Dot-notation path to the key (e.g., 'dashboard.title')"),
		),
	)

	s.AddTool(getTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		filePath := mcp.ParseString(request, "file_path", "")
		if filePath == "" {
			return mcp.NewToolResultError("Missing file_path"), nil
		}

		keyPath := mcp.ParseString(request, "key_path", "")
		if keyPath == "" {
			return mcp.NewToolResultError("Missing key_path"), nil
		}

		result, err := operations.GetKey(filePath, keyPath)
		if err != nil {
			return mcp.NewToolResultError(fmt.Sprintf("❌ Error: %s", err.Error())), nil
		}

		jsonResult, err := json.MarshalIndent(result, "", "  ")
		if err != nil {
			return mcp.NewToolResultError(fmt.Sprintf("❌ Error serializing result: %v", err)), nil
		}

		return mcp.NewToolResultText(string(jsonResult)), nil
	})
}

// addAddKeyTool adds the add_key tool
func addAddKeyTool(s *server.MCPServer) {
	addTool := mcp.NewTool("add_key",
		mcp.WithDescription("Add new key-value pair to JSON file"),
		mcp.WithString("file_path",
			mcp.Required(),
			mcp.Description("Path to the JSON file"),
		),
		mcp.WithString("key_path",
			mcp.Required(),
			mcp.Description("Dot-notation path for the new key"),
		),
		mcp.WithObject("value",
			mcp.Required(),
			mcp.Description("Value to add (can be string, object, array, etc.)"),
		),
	)

	s.AddTool(addTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		filePath := mcp.ParseString(request, "file_path", "")
		if filePath == "" {
			return mcp.NewToolResultError("Missing file_path"), nil
		}

		keyPath := mcp.ParseString(request, "key_path", "")
		if keyPath == "" {
			return mcp.NewToolResultError("Missing key_path"), nil
		}

		value := mcp.ParseArgument(request, "value", nil)
		if value == nil {
			return mcp.NewToolResultError("Missing value"), nil
		}

		err := operations.AddKey(filePath, keyPath, value)
		if err != nil {
			return mcp.NewToolResultError(fmt.Sprintf("❌ Error: %s", err.Error())), nil
		}

		return mcp.NewToolResultText(fmt.Sprintf("✅ Added key '%s' to %s", keyPath, filePath)), nil
	})
}

// addUpdateKeyTool adds the update_key tool
func addUpdateKeyTool(s *server.MCPServer) {
	updateTool := mcp.NewTool("update_key",
		mcp.WithDescription("Update existing key in JSON file"),
		mcp.WithString("file_path",
			mcp.Required(),
			mcp.Description("Path to the JSON file"),
		),
		mcp.WithString("key_path",
			mcp.Required(),
			mcp.Description("Dot-notation path to the key to update"),
		),
		mcp.WithObject("value",
			mcp.Required(),
			mcp.Description("New value (can be string, object, array, etc.)"),
		),
	)

	s.AddTool(updateTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		filePath := mcp.ParseString(request, "file_path", "")
		if filePath == "" {
			return mcp.NewToolResultError("Missing file_path"), nil
		}

		keyPath := mcp.ParseString(request, "key_path", "")
		if keyPath == "" {
			return mcp.NewToolResultError("Missing key_path"), nil
		}

		value := mcp.ParseArgument(request, "value", nil)
		if value == nil {
			return mcp.NewToolResultError("Missing value"), nil
		}

		err := operations.UpdateKey(filePath, keyPath, value)
		if err != nil {
			return mcp.NewToolResultError(fmt.Sprintf("❌ Error: %s", err.Error())), nil
		}

		return mcp.NewToolResultText(fmt.Sprintf("✅ Updated key '%s' in %s", keyPath, filePath)), nil
	})
}

// addRenameKeyTool adds the rename_key tool
func addRenameKeyTool(s *server.MCPServer) {
	renameTool := mcp.NewTool("rename_key",
		mcp.WithDescription("Rename/move existing key in JSON file"),
		mcp.WithString("file_path",
			mcp.Required(),
			mcp.Description("Path to the JSON file"),
		),
		mcp.WithString("old_path",
			mcp.Required(),
			mcp.Description("Current dot-notation path of the key"),
		),
		mcp.WithString("new_path",
			mcp.Required(),
			mcp.Description("New dot-notation path for the key"),
		),
	)

	s.AddTool(renameTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		filePath := mcp.ParseString(request, "file_path", "")
		if filePath == "" {
			return mcp.NewToolResultError("Missing file_path"), nil
		}

		oldPath := mcp.ParseString(request, "old_path", "")
		if oldPath == "" {
			return mcp.NewToolResultError("Missing old_path"), nil
		}

		newPath := mcp.ParseString(request, "new_path", "")
		if newPath == "" {
			return mcp.NewToolResultError("Missing new_path"), nil
		}

		err := operations.RenameKey(filePath, oldPath, newPath)
		if err != nil {
			return mcp.NewToolResultError(fmt.Sprintf("❌ Error: %s", err.Error())), nil
		}

		return mcp.NewToolResultText(fmt.Sprintf("✅ Renamed '%s' → '%s' in %s", oldPath, newPath, filePath)), nil
	})
}

// addRemoveKeyTool adds the remove_key tool
func addRemoveKeyTool(s *server.MCPServer) {
	removeTool := mcp.NewTool("remove_key",
		mcp.WithDescription("Remove key from JSON file"),
		mcp.WithString("file_path",
			mcp.Required(),
			mcp.Description("Path to the JSON file"),
		),
		mcp.WithString("key_path",
			mcp.Required(),
			mcp.Description("Dot-notation path to the key to remove"),
		),
	)

	s.AddTool(removeTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		filePath := mcp.ParseString(request, "file_path", "")
		if filePath == "" {
			return mcp.NewToolResultError("Missing file_path"), nil
		}

		keyPath := mcp.ParseString(request, "key_path", "")
		if keyPath == "" {
			return mcp.NewToolResultError("Missing key_path"), nil
		}

		removedValue, err := operations.RemoveKey(filePath, keyPath)
		if err != nil {
			return mcp.NewToolResultError(fmt.Sprintf("❌ Error: %s", err.Error())), nil
		}

		jsonValue, err := json.MarshalIndent(removedValue, "", "  ")
		if err != nil {
			return mcp.NewToolResultError(fmt.Sprintf("❌ Error serializing removed value: %v", err)), nil
		}

		return mcp.NewToolResultText(fmt.Sprintf("✅ Removed key '%s' from %s\nRemoved value: %s", keyPath, filePath, string(jsonValue))), nil
	})
}

// addListKeysTool adds the list_keys tool
func addListKeysTool(s *server.MCPServer) {
	listTool := mcp.NewTool("list_keys",
		mcp.WithDescription("List all keys at specified path in JSON file"),
		mcp.WithString("file_path",
			mcp.Required(),
			mcp.Description("Path to the JSON file"),
		),
		mcp.WithString("key_path",
			mcp.Description("Dot-notation path to list keys from (optional, defaults to root)"),
		),
	)

	s.AddTool(listTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		filePath := mcp.ParseString(request, "file_path", "")
		if filePath == "" {
			return mcp.NewToolResultError("Missing file_path"), nil
		}

		var keyPath *string
		keyPathStr := mcp.ParseString(request, "key_path", "")
		if keyPathStr != "" {
			keyPath = &keyPathStr
		}

		keys, err := operations.ListKeys(filePath, keyPath)
		if err != nil {
			return mcp.NewToolResultError(fmt.Sprintf("❌ Error: %s", err.Error())), nil
		}

		pathDesc := "at root level"
		if keyPath != nil {
			pathDesc = fmt.Sprintf("at '%s'", *keyPath)
		}

		result := fmt.Sprintf("Keys %s in %s:\n", pathDesc, filePath)
		for _, key := range keys {
			result += fmt.Sprintf("• %s\n", key)
		}

		return mcp.NewToolResultText(result), nil
	})
}

// addKeyExistsTool adds the key_exists tool
func addKeyExistsTool(s *server.MCPServer) {
	existsTool := mcp.NewTool("key_exists",
		mcp.WithDescription("Check if key exists in JSON file"),
		mcp.WithString("file_path",
			mcp.Required(),
			mcp.Description("Path to the JSON file"),
		),
		mcp.WithString("key_path",
			mcp.Required(),
			mcp.Description("Dot-notation path to check"),
		),
	)

	s.AddTool(existsTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		filePath := mcp.ParseString(request, "file_path", "")
		if filePath == "" {
			return mcp.NewToolResultError("Missing file_path"), nil
		}

		keyPath := mcp.ParseString(request, "key_path", "")
		if keyPath == "" {
			return mcp.NewToolResultError("Missing key_path"), nil
		}

		exists, err := operations.KeyExists(filePath, keyPath)
		if err != nil {
			return mcp.NewToolResultError(fmt.Sprintf("❌ Error: %s", err.Error())), nil
		}

		status := "❌ does not exist"
		if exists {
			status = "✅ exists"
		}

		return mcp.NewToolResultText(fmt.Sprintf("Key '%s' %s in %s", keyPath, status, filePath)), nil
	})
}

// addValidateJSONTool adds the validate_json tool
func addValidateJSONTool(s *server.MCPServer) {
	validateTool := mcp.NewTool("validate_json",
		mcp.WithDescription("Validate JSON file syntax and structure"),
		mcp.WithString("file_path",
			mcp.Required(),
			mcp.Description("Path to the JSON file to validate"),
		),
	)

	s.AddTool(validateTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		filePath := mcp.ParseString(request, "file_path", "")
		if filePath == "" {
			return mcp.NewToolResultError("Missing file_path"), nil
		}

		result, err := operations.ValidateJSON(filePath)
		if err != nil {
			return mcp.NewToolResultError(fmt.Sprintf("❌ Error: %s", err.Error())), nil
		}

		if result.Valid {
			perf := ""
			if result.Performance != nil {
				perf = fmt.Sprintf("\nFile size: %d bytes\nParse time: %.3fs", result.Performance.FileSize, result.Performance.ParseTime)
			}
			return mcp.NewToolResultText(fmt.Sprintf("✅ %s is valid JSON%s", filePath, perf)), nil
		} else {
			errorMsg := "Unknown error"
			line := 0
			if result.Error != nil {
				errorMsg = result.Error.Message
				line = result.Error.Line
			}
			return mcp.NewToolResultText(fmt.Sprintf("❌ %s contains invalid JSON\nError: %s\nLine: %d", filePath, errorMsg, line)), nil
		}
	})
}