package main

import (
	"log"
	"os"

	"github.com/mark3labs/mcp-go/server"
	"jsonmcptool/internal/mcpserver"
)

func main() {
	// Create the JSON MCP server
	s := mcpserver.NewJSONMcpServer()

	// Add debug logging if requested
	if os.Getenv("DEBUG") != "" {
		log.Println("JsonMcpTool MCP Server starting...")
	}

	// Serve over stdio
	if err := server.ServeStdio(s); err != nil {
		log.Fatalf("Server error: %v", err)
	}
}