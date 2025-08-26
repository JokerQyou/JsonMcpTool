package jsonhandler

import (
	"encoding/json"
	"os"
	"testing"
	"time"
)

func TestNewJSONHandler(t *testing.T) {
	handler := NewJSONHandler("test.json")
	if handler.filePath != "test.json" {
		t.Errorf("NewJSONHandler() filePath = %s, want test.json", handler.filePath)
	}
}

func TestLoadJSON(t *testing.T) {
	// Create temp file with test data
	testData := map[string]interface{}{
		"key": "value",
		"nested": map[string]interface{}{
			"inner": "data",
		},
	}

	tempFile := createTempJSONFile(t, testData)
	defer os.Remove(tempFile)

	handler := NewJSONHandler(tempFile)

	// Test loading without cache
	result, err := handler.LoadJSON(false)
	if err != nil {
		t.Errorf("LoadJSON() error = %v", err)
		return
	}

	if result["key"] != "value" {
		t.Errorf("LoadJSON() key = %v, want value", result["key"])
	}

	// Test loading with cache
	result2, err := handler.LoadJSON(true)
	if err != nil {
		t.Errorf("LoadJSON() with cache error = %v", err)
		return
	}

	if result2["key"] != "value" {
		t.Errorf("LoadJSON() cached key = %v, want value", result2["key"])
	}
}

func TestLoadJSONFileNotFound(t *testing.T) {
	handler := NewJSONHandler("nonexistent.json")
	
	_, err := handler.LoadJSON(false)
	if err == nil {
		t.Error("LoadJSON() should fail for nonexistent file")
	}
	if err != nil && err.Error() == "" {
		t.Error("LoadJSON() error message should not be empty")
	}
}

func TestLoadJSONInvalidJSON(t *testing.T) {
	// Create temp file with invalid JSON
	tempFile, err := os.CreateTemp("", "invalid_*.json")
	if err != nil {
		t.Fatal(err)
	}
	defer os.Remove(tempFile.Name())

	_, err = tempFile.WriteString("{invalid json")
	if err != nil {
		t.Fatal(err)
	}
	tempFile.Close()

	handler := NewJSONHandler(tempFile.Name())
	
	_, err = handler.LoadJSON(false)
	if err == nil {
		t.Error("LoadJSON() should fail for invalid JSON")
	}
}

func TestSaveJSON(t *testing.T) {
	tempFile, err := os.CreateTemp("", "save_test_*.json")
	if err != nil {
		t.Fatal(err)
	}
	tempFile.Close()
	defer os.Remove(tempFile.Name())

	handler := NewJSONHandler(tempFile.Name())

	testData := map[string]interface{}{
		"key":    "value",
		"number": 42,
		"nested": map[string]interface{}{
			"inner": "data",
		},
	}

	err = handler.SaveJSON(testData, 2)
	if err != nil {
		t.Errorf("SaveJSON() error = %v", err)
		return
	}

	// Verify file was written correctly
	data, err := os.ReadFile(tempFile.Name())
	if err != nil {
		t.Fatal(err)
	}

	var result map[string]interface{}
	if err := json.Unmarshal(data, &result); err != nil {
		t.Errorf("SaveJSON() wrote invalid JSON: %v", err)
		return
	}

	if result["key"] != "value" {
		t.Errorf("SaveJSON() saved key = %v, want value", result["key"])
	}
	if result["number"].(float64) != 42 {
		t.Errorf("SaveJSON() saved number = %v, want 42", result["number"])
	}
}

func TestValidateJSONSyntax(t *testing.T) {
	tests := []struct {
		name        string
		content     string
		wantValid   bool
		wantErrType string
	}{
		{
			name:      "valid JSON",
			content:   `{"key": "value"}`,
			wantValid: true,
		},
		{
			name:        "invalid JSON",
			content:     `{invalid json`,
			wantValid:   false,
			wantErrType: "PARSE_ERROR",
		},
		{
			name:        "empty file",
			content:     "",
			wantValid:   false,
			wantErrType: "PARSE_ERROR",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Create temp file with content
			tempFile, err := os.CreateTemp("", "validate_*.json")
			if err != nil {
				t.Fatal(err)
			}
			defer os.Remove(tempFile.Name())

			if tt.content != "" {
				_, err = tempFile.WriteString(tt.content)
				if err != nil {
					t.Fatal(err)
				}
			}
			tempFile.Close()

			handler := NewJSONHandler(tempFile.Name())
			result := handler.ValidateJSONSyntax()

			if result.Valid != tt.wantValid {
				t.Errorf("ValidateJSONSyntax() Valid = %v, want %v", result.Valid, tt.wantValid)
			}

			if !tt.wantValid && result.ErrorType != tt.wantErrType {
				t.Errorf("ValidateJSONSyntax() ErrorType = %v, want %v", result.ErrorType, tt.wantErrType)
			}

			if result.File != tempFile.Name() {
				t.Errorf("ValidateJSONSyntax() File = %v, want %v", result.File, tempFile.Name())
			}
		})
	}
}

func TestValidateJSONSyntaxFileNotFound(t *testing.T) {
	handler := NewJSONHandler("nonexistent.json")
	result := handler.ValidateJSONSyntax()

	if result.Valid {
		t.Error("ValidateJSONSyntax() should return invalid for nonexistent file")
	}
	if result.ErrorType != "FILE_NOT_FOUND" {
		t.Errorf("ValidateJSONSyntax() ErrorType = %v, want FILE_NOT_FOUND", result.ErrorType)
	}
}

func TestClearCache(t *testing.T) {
	testData := map[string]interface{}{
		"key": "value",
	}

	tempFile := createTempJSONFile(t, testData)
	defer os.Remove(tempFile)

	handler := NewJSONHandler(tempFile)

	// Load with cache
	_, err := handler.LoadJSON(true)
	if err != nil {
		t.Fatal(err)
	}

	// Verify cache is set
	if handler.cachedData == nil {
		t.Error("Cache should be set after LoadJSON(true)")
	}

	// Clear cache
	handler.ClearCache()

	// Verify cache is cleared
	if handler.cachedData != nil {
		t.Error("Cache should be cleared after ClearCache()")
	}
}

func TestGetFileInfo(t *testing.T) {
	testData := map[string]interface{}{
		"key": "value",
	}

	tempFile := createTempJSONFile(t, testData)
	defer os.Remove(tempFile)

	handler := NewJSONHandler(tempFile)

	info := handler.GetFileInfo()

	if !info.Exists {
		t.Error("GetFileInfo() Exists should be true for existing file")
	}
	if info.Path != tempFile {
		t.Errorf("GetFileInfo() Path = %v, want %v", info.Path, tempFile)
	}
	if info.SizeBytes == 0 {
		t.Error("GetFileInfo() SizeBytes should be > 0")
	}
	if info.IsCached {
		t.Error("GetFileInfo() IsCached should be false initially")
	}

	// Load with cache and check again
	_, err := handler.LoadJSON(true)
	if err != nil {
		t.Fatal(err)
	}

	info2 := handler.GetFileInfo()
	if !info2.IsCached {
		t.Error("GetFileInfo() IsCached should be true after caching")
	}
}

func TestGetFileInfoNonexistent(t *testing.T) {
	handler := NewJSONHandler("nonexistent.json")
	info := handler.GetFileInfo()

	if info.Exists {
		t.Error("GetFileInfo() Exists should be false for nonexistent file")
	}
	if info.Path != "nonexistent.json" {
		t.Errorf("GetFileInfo() Path = %v, want nonexistent.json", info.Path)
	}
}

func TestCacheInvalidation(t *testing.T) {
	testData := map[string]interface{}{
		"key": "original",
	}

	tempFile := createTempJSONFile(t, testData)
	defer os.Remove(tempFile)

	handler := NewJSONHandler(tempFile)

	// Load with cache
	result1, err := handler.LoadJSON(true)
	if err != nil {
		t.Fatal(err)
	}
	if result1["key"] != "original" {
		t.Errorf("First load key = %v, want original", result1["key"])
	}

	// Modify file externally
	time.Sleep(10 * time.Millisecond) // Ensure different mtime
	newData := map[string]interface{}{
		"key": "modified",
	}
	data, _ := json.Marshal(newData)
	err = os.WriteFile(tempFile, data, 0644)
	if err != nil {
		t.Fatal(err)
	}

	// Load with cache again - should detect file change
	result2, err := handler.LoadJSON(true)
	if err != nil {
		t.Fatal(err)
	}
	if result2["key"] != "modified" {
		t.Errorf("Second load key = %v, want modified", result2["key"])
	}
}

// Helper function to create temporary JSON file
func createTempJSONFile(t *testing.T, data map[string]interface{}) string {
	tempFile, err := os.CreateTemp("", "test_*.json")
	if err != nil {
		t.Fatal(err)
	}

	jsonData, err := json.Marshal(data)
	if err != nil {
		t.Fatal(err)
	}

	_, err = tempFile.Write(jsonData)
	if err != nil {
		t.Fatal(err)
	}

	tempFile.Close()
	return tempFile.Name()
}

func TestGetLineColumn(t *testing.T) {
	data := []byte("{\n  \"key\": \"value\",\n  \"error\"")
	
	tests := []struct {
		offset   int64
		wantLine int
		wantCol  int
	}{
		{0, 1, 1},   // Start of file: '{'
		{1, 1, 2},   // After '{', at '\n'
		{2, 2, 1},   // After '\n', first space on line 2
		{4, 2, 3},   // At '"key"' 
		{21, 3, 2},  // Third line, second space
	}

	for _, tt := range tests {
		line, col := getLineColumn(data, tt.offset)
		if line != tt.wantLine || col != tt.wantCol {
			t.Errorf("getLineColumn(%d) = (%d, %d), want (%d, %d)", 
				tt.offset, line, col, tt.wantLine, tt.wantCol)
		}
	}
}