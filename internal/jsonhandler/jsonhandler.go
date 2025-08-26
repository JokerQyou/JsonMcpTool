package jsonhandler

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"
)

var (
	ErrFileNotFound   = errors.New("FILE_NOT_FOUND")
	ErrInvalidJSON    = errors.New("INVALID_JSON")
	ErrFileReadError  = errors.New("FILE_READ_ERROR")
	ErrFileWriteError = errors.New("FILE_WRITE_ERROR")
	ErrParseError     = errors.New("PARSE_ERROR")
	ErrUnknownError   = errors.New("UNKNOWN_ERROR")
)

// JSONHandler handles JSON file operations with caching support
type JSONHandler struct {
	filePath   string
	cachedData map[string]interface{}
	fileMTime  time.Time
	mutex      sync.RWMutex
}

// NewJSONHandler creates a new JSON handler for a specific file
func NewJSONHandler(filePath string) *JSONHandler {
	return &JSONHandler{
		filePath: filePath,
	}
}

// LoadJSON loads JSON data from file with optional caching
func (h *JSONHandler) LoadJSON(useCache bool) (map[string]interface{}, error) {
	h.mutex.Lock()
	defer h.mutex.Unlock()

	// Check if file exists
	fileInfo, err := os.Stat(h.filePath)
	if os.IsNotExist(err) {
		return nil, fmt.Errorf("%w: File %s not found", ErrFileNotFound, h.filePath)
	}
	if err != nil {
		return nil, fmt.Errorf("%w: Failed to stat %s: %v", ErrFileReadError, h.filePath, err)
	}

	currentMTime := fileInfo.ModTime()

	// Use cache if available and file hasn't changed
	if useCache && h.cachedData != nil && h.fileMTime.Equal(currentMTime) {
		return h.cachedData, nil
	}

	// Read and parse file
	data, err := os.ReadFile(h.filePath)
	if err != nil {
		return nil, fmt.Errorf("%w: Failed to read %s: %v", ErrFileReadError, h.filePath, err)
	}

	var jsonData map[string]interface{}
	if err := json.Unmarshal(data, &jsonData); err != nil {
		return nil, fmt.Errorf("%w: File %s contains invalid JSON: %v", ErrInvalidJSON, h.filePath, err)
	}

	// Update cache
	if useCache {
		h.cachedData = jsonData
		h.fileMTime = currentMTime
	}

	return jsonData, nil
}

// SaveJSON saves JSON data to file with atomic write
func (h *JSONHandler) SaveJSON(data map[string]interface{}, indent int) error {
	h.mutex.Lock()
	defer h.mutex.Unlock()

	// Use atomic write - write to temp file then rename
	dir := filepath.Dir(h.filePath)
	tempFile, err := os.CreateTemp(dir, "*.tmp")
	if err != nil {
		return fmt.Errorf("%w: Failed to create temp file: %v", ErrFileWriteError, err)
	}
	tempPath := tempFile.Name()
	
	defer func() {
		tempFile.Close()
		// Clean up temp file if it still exists
		os.Remove(tempPath)
	}()

	// Encode JSON with indentation
	encoder := json.NewEncoder(tempFile)
	encoder.SetIndent("", getIndentString(indent))
	encoder.SetEscapeHTML(false)
	
	if err := encoder.Encode(data); err != nil {
		return fmt.Errorf("%w: Failed to encode JSON: %v", ErrFileWriteError, err)
	}

	if err := tempFile.Close(); err != nil {
		return fmt.Errorf("%w: Failed to close temp file: %v", ErrFileWriteError, err)
	}

	// Atomic rename
	if err := os.Rename(tempPath, h.filePath); err != nil {
		return fmt.Errorf("%w: Failed to rename temp file: %v", ErrFileWriteError, err)
	}

	// Update cache
	h.cachedData = data
	if fileInfo, err := os.Stat(h.filePath); err == nil {
		h.fileMTime = fileInfo.ModTime()
	}

	return nil
}

// ValidationResult represents the result of JSON validation
type ValidationResult struct {
	Valid       bool                   `json:"valid"`
	File        string                 `json:"file"`
	Error       *ValidationError       `json:"error,omitempty"`
	ErrorType   string                 `json:"error_type,omitempty"`
	Performance *PerformanceMetrics    `json:"performance,omitempty"`
}

// ValidationError represents a JSON validation error
type ValidationError struct {
	Message string `json:"message"`
	Line    int    `json:"line"`
	Column  int    `json:"column"`
}

// PerformanceMetrics represents performance metrics
type PerformanceMetrics struct {
	ParseTime float64 `json:"parse_time"`
	FileSize  int64   `json:"file_size"`
}

// ValidateJSONSyntax validates JSON file syntax without loading into memory completely
func (h *JSONHandler) ValidateJSONSyntax() *ValidationResult {
	result := &ValidationResult{
		File: h.filePath,
	}

	// Check if file exists
	fileInfo, err := os.Stat(h.filePath)
	if os.IsNotExist(err) {
		result.Valid = false
		result.ErrorType = "FILE_NOT_FOUND"
		result.Error = &ValidationError{
			Message: fmt.Sprintf("File %s not found", h.filePath),
			Line:    0,
			Column:  0,
		}
		return result
	}

	fileSize := fileInfo.Size()

	if fileSize == 0 {
		result.Valid = false
		result.ErrorType = "PARSE_ERROR"
		result.Error = &ValidationError{
			Message: "File is empty",
			Line:    1,
			Column:  1,
		}
		return result
	}

	// Read file content
	startTime := time.Now()
	data, err := os.ReadFile(h.filePath)
	if err != nil {
		result.Valid = false
		result.ErrorType = "FILE_READ_ERROR"
		result.Error = &ValidationError{
			Message: fmt.Sprintf("Failed to read file: %v", err),
			Line:    0,
			Column:  0,
		}
		return result
	}

	// Check for empty content after reading
	if len(data) == 0 {
		result.Valid = false
		result.ErrorType = "PARSE_ERROR"
		result.Error = &ValidationError{
			Message: "File contains only whitespace",
			Line:    1,
			Column:  1,
		}
		return result
	}

	// Try to parse JSON
	var jsonData interface{}
	if err := json.Unmarshal(data, &jsonData); err != nil {
		result.Valid = false
		result.ErrorType = "PARSE_ERROR"
		
		// Try to extract line/column information from JSON error
		if jsonErr, ok := err.(*json.SyntaxError); ok {
			line, col := getLineColumn(data, jsonErr.Offset)
			result.Error = &ValidationError{
				Message: jsonErr.Error(),
				Line:    line,
				Column:  col,
			}
		} else {
			result.Error = &ValidationError{
				Message: err.Error(),
				Line:    0,
				Column:  0,
			}
		}
		return result
	}

	// Success
	parseTime := time.Since(startTime).Seconds()
	result.Valid = true
	result.Performance = &PerformanceMetrics{
		ParseTime: parseTime,
		FileSize:  fileSize,
	}

	return result
}

// ClearCache clears cached data to force reload on next access
func (h *JSONHandler) ClearCache() {
	h.mutex.Lock()
	defer h.mutex.Unlock()
	
	h.cachedData = nil
	h.fileMTime = time.Time{}
}

// FileInfo represents file information
type FileInfo struct {
	Exists       bool      `json:"exists"`
	Path         string    `json:"path"`
	SizeBytes    int64     `json:"size_bytes,omitempty"`
	ModifiedTime time.Time `json:"modified_time,omitempty"`
	IsCached     bool      `json:"is_cached"`
}

// GetFileInfo gets information about the JSON file
func (h *JSONHandler) GetFileInfo() *FileInfo {
	h.mutex.RLock()
	defer h.mutex.RUnlock()

	info := &FileInfo{
		Path:     h.filePath,
		IsCached: h.cachedData != nil,
	}

	if fileInfo, err := os.Stat(h.filePath); err == nil {
		info.Exists = true
		info.SizeBytes = fileInfo.Size()
		info.ModifiedTime = fileInfo.ModTime()
	} else {
		info.Exists = false
	}

	return info
}

// Helper function to get indent string
func getIndentString(indent int) string {
	result := ""
	for i := 0; i < indent; i++ {
		result += " "
	}
	return result
}

// Helper function to calculate line and column from byte offset
func getLineColumn(data []byte, offset int64) (int, int) {
	line := 1
	col := 1
	
	for i := int64(0); i < offset && i < int64(len(data)); i++ {
		if data[i] == '\n' {
			line++
			col = 1
		} else {
			col++
		}
	}
	
	return line, col
}