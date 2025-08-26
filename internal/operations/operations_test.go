package operations

import (
	"encoding/json"
	"os"
	"testing"
)

// Test data similar to original Python fixtures
var sampleI18nData = map[string]interface{}{
	"dashboard": map[string]interface{}{
		"title":   "Dashboard",
		"welcome": "Welcome back, {{name}}!",
		"stats": map[string]interface{}{
			"users":   "Total Users",
			"revenue": "Monthly Revenue",
		},
	},
	"forms": map[string]interface{}{
		"validation": map[string]interface{}{
			"required":  "This field is required",
			"email":     "Please enter a valid email",
			"minLength": "Minimum {{count}} characters required",
		},
		"buttons": map[string]interface{}{
			"submit": "Submit",
			"cancel": "Cancel",
			"reset":  "Reset Form",
		},
	},
	"alerts": map[string]interface{}{
		"success": "Operation completed successfully",
		"error":   "Something went wrong",
		"warning": "Please check your input",
	},
	"navigation": map[string]interface{}{
		"home":    "Home",
		"about":   "About",
		"contact": "Contact Us",
	},
	"auth": map[string]interface{}{
		"login": map[string]interface{}{
			"title":    "Sign In",
			"email":    "Email Address",
			"password": "Password",
			"remember": "Remember me",
		},
		"register": map[string]interface{}{
			"title":     "Create Account",
			"firstName": "First Name",
			"lastName":  "Last Name",
		},
	},
}

var simpleTestData = map[string]interface{}{
	"simple": "value",
	"nested": map[string]interface{}{
		"key": "nested value",
	},
	"array": []interface{}{
		"item1",
		"item2",
		map[string]interface{}{
			"arrayObject": "value",
		},
	},
	"key.with.dots": "dotted key value",
	"emptyObject":   map[string]interface{}{},
	"emptyArray":    []interface{}{},
	"nullValue":     nil,
	"booleanTrue":   true,
	"booleanFalse":  false,
	"number":        float64(42),
	"float":         3.14,
}

func TestGetKey(t *testing.T) {
	tempFile := createTempJSONFile(t, sampleI18nData)
	defer os.Remove(tempFile)

	tests := []struct {
		name    string
		path    string
		want    interface{}
		wantErr bool
	}{
		{
			name: "simple nested key",
			path: "dashboard.title",
			want: "Dashboard",
		},
		{
			name: "deeply nested key",
			path: "auth.login.title",
			want: "Sign In",
		},
		{
			name: "nested object",
			path: "forms.validation",
			want: map[string]interface{}{
				"required":  "This field is required",
				"email":     "Please enter a valid email",
				"minLength": "Minimum {{count}} characters required",
			},
		},
		{
			name:    "nonexistent key",
			path:    "nonexistent.key",
			wantErr: true,
		},
		{
			name:    "empty path",
			path:    "",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, err := GetKey(tempFile, tt.path)
			if (err != nil) != tt.wantErr {
				t.Errorf("GetKey() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !tt.wantErr {
				if !deepEqual(result, tt.want) {
					t.Errorf("GetKey() = %v, want %v", result, tt.want)
				}
			}
		})
	}
}

func TestGetKeyWithDottedKeys(t *testing.T) {
	tempFile := createTempJSONFile(t, simpleTestData)
	defer os.Remove(tempFile)

	// Test key that contains dots in its name
	result, err := GetKey(tempFile, "key.with.dots")
	if err != nil {
		t.Errorf("GetKey() error = %v", err)
		return
	}
	if result != "dotted key value" {
		t.Errorf("GetKey() = %v, want 'dotted key value'", result)
	}
}

func TestGetKeyDifferentDataTypes(t *testing.T) {
	tempFile := createTempJSONFile(t, simpleTestData)
	defer os.Remove(tempFile)

	tests := []struct {
		name string
		path string
		want interface{}
	}{
		{"null value", "nullValue", nil},
		{"boolean true", "booleanTrue", true},
		{"boolean false", "booleanFalse", false},
		{"number", "number", float64(42)},
		{"float", "float", 3.14},
		{"array", "array", []interface{}{"item1", "item2", map[string]interface{}{"arrayObject": "value"}}},
		{"empty object", "emptyObject", map[string]interface{}{}},
		{"empty array", "emptyArray", []interface{}{}},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, err := GetKey(tempFile, tt.path)
			if err != nil {
				t.Errorf("GetKey() error = %v", err)
				return
			}
			if !deepEqual(result, tt.want) {
				t.Errorf("GetKey() = %v, want %v", result, tt.want)
			}
		})
	}
}

func TestAddKey(t *testing.T) {
	// Start with sample data
	tempFile := createTempJSONFile(t, sampleI18nData)
	defer os.Remove(tempFile)

	tests := []struct {
		name    string
		path    string
		value   interface{}
		wantErr bool
	}{
		{
			name:  "add new simple key",
			path:  "newSection.title",
			value: "New Section Title",
		},
		{
			name: "add new nested object",
			path: "modals.confirm",
			value: map[string]interface{}{
				"title":  "Confirm Action",
				"cancel": "Cancel",
			},
		},
		{
			name:    "add existing key should fail",
			path:    "dashboard.title",
			value:   "Should Fail",
			wantErr: true,
		},
		{
			name:    "empty path should fail",
			path:    "",
			value:   "value",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := AddKey(tempFile, tt.path, tt.value)
			if (err != nil) != tt.wantErr {
				t.Errorf("AddKey() error = %v, wantErr %v", err, tt.wantErr)
			}

			// Verify key was added if no error expected
			if !tt.wantErr {
				result, err := GetKey(tempFile, tt.path)
				if err != nil {
					t.Errorf("Failed to verify added key: %v", err)
					return
				}
				if !deepEqual(result, tt.value) {
					t.Errorf("Added key value = %v, want %v", result, tt.value)
				}
			}
		})
	}
}

func TestUpdateKey(t *testing.T) {
	tempFile := createTempJSONFile(t, sampleI18nData)
	defer os.Remove(tempFile)

	tests := []struct {
		name    string
		path    string
		value   interface{}
		wantErr bool
	}{
		{
			name:  "update existing key",
			path:  "dashboard.title",
			value: "Updated Dashboard",
		},
		{
			name: "update with object",
			path: "forms.validation",
			value: map[string]interface{}{
				"required": "New required message",
			},
		},
		{
			name:    "update nonexistent key should fail",
			path:    "nonexistent.key",
			value:   "Should Fail",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := UpdateKey(tempFile, tt.path, tt.value)
			if (err != nil) != tt.wantErr {
				t.Errorf("UpdateKey() error = %v, wantErr %v", err, tt.wantErr)
			}

			// Verify key was updated if no error expected
			if !tt.wantErr {
				result, err := GetKey(tempFile, tt.path)
				if err != nil {
					t.Errorf("Failed to verify updated key: %v", err)
					return
				}
				if !deepEqual(result, tt.value) {
					t.Errorf("Updated key value = %v, want %v", result, tt.value)
				}
			}
		})
	}
}

func TestRenameKey(t *testing.T) {
	tempFile := createTempJSONFile(t, sampleI18nData)
	defer os.Remove(tempFile)

	tests := []struct {
		name     string
		oldPath  string
		newPath  string
		wantErr  bool
		expected interface{}
	}{
		{
			name:     "rename simple key",
			oldPath:  "dashboard.title",
			newPath:  "dashboard.heading",
			expected: "Dashboard",
		},
		{
			name:     "rename nested section",
			oldPath:  "forms.validation",
			newPath:  "common.validation",
			expected: sampleI18nData["forms"].(map[string]interface{})["validation"],
		},
		{
			name:    "rename nonexistent key should fail",
			oldPath: "nonexistent.key",
			newPath: "new.key",
			wantErr: true,
		},
		{
			name:    "rename to existing key should fail",
			oldPath: "alerts.success",
			newPath: "alerts.error",
			wantErr: true,
		},
		{
			name:    "same old and new path should fail",
			oldPath: "dashboard.title",
			newPath: "dashboard.title",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := RenameKey(tempFile, tt.oldPath, tt.newPath)
			if (err != nil) != tt.wantErr {
				t.Errorf("RenameKey() error = %v, wantErr %v", err, tt.wantErr)
			}

			if !tt.wantErr {
				// Verify old key no longer exists
				exists, _ := KeyExists(tempFile, tt.oldPath)
				if exists {
					t.Errorf("Old key '%s' should not exist after rename", tt.oldPath)
				}

				// Verify new key exists and has correct value
				result, err := GetKey(tempFile, tt.newPath)
				if err != nil {
					t.Errorf("Failed to get renamed key: %v", err)
					return
				}
				if !deepEqual(result, tt.expected) {
					t.Errorf("Renamed key value = %v, want %v", result, tt.expected)
				}
			}
		})
	}
}

func TestRemoveKey(t *testing.T) {
	tempFile := createTempJSONFile(t, sampleI18nData)
	defer os.Remove(tempFile)

	tests := []struct {
		name     string
		path     string
		wantErr  bool
		expected interface{}
	}{
		{
			name:     "remove simple key",
			path:     "dashboard.title",
			expected: "Dashboard",
		},
		{
			name:     "remove nested object",
			path:     "forms.validation",
			expected: sampleI18nData["forms"].(map[string]interface{})["validation"],
		},
		{
			name:    "remove nonexistent key should fail",
			path:    "nonexistent.key",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, err := RemoveKey(tempFile, tt.path)
			if (err != nil) != tt.wantErr {
				t.Errorf("RemoveKey() error = %v, wantErr %v", err, tt.wantErr)
			}

			if !tt.wantErr {
				// Verify returned value is correct
				if !deepEqual(result, tt.expected) {
					t.Errorf("RemoveKey() returned = %v, want %v", result, tt.expected)
				}

				// Verify key no longer exists
				exists, _ := KeyExists(tempFile, tt.path)
				if exists {
					t.Errorf("Key '%s' should not exist after removal", tt.path)
				}
			}
		})
	}
}

func TestListKeys(t *testing.T) {
	tempFile := createTempJSONFile(t, sampleI18nData)
	defer os.Remove(tempFile)

	tests := []struct {
		name     string
		path     *string
		expected []string
		wantErr  bool
	}{
		{
			name:     "list root keys",
			path:     nil,
			expected: []string{"dashboard", "forms", "alerts", "navigation", "auth"},
		},
		{
			name:     "list nested keys",
			path:     stringPtr("dashboard"),
			expected: []string{"title", "welcome", "stats"},
		},
		{
			name:     "list deeply nested keys",
			path:     stringPtr("forms.validation"),
			expected: []string{"required", "email", "minLength"},
		},
		{
			name:    "list from nonexistent path",
			path:    stringPtr("nonexistent"),
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, err := ListKeys(tempFile, tt.path)
			if (err != nil) != tt.wantErr {
				t.Errorf("ListKeys() error = %v, wantErr %v", err, tt.wantErr)
				return
			}

			if !tt.wantErr {
				if !sliceContainsSameElements(result, tt.expected) {
					t.Errorf("ListKeys() = %v, want %v", result, tt.expected)
				}
			}
		})
	}
}

func TestKeyExists(t *testing.T) {
	tempFile := createTempJSONFile(t, sampleI18nData)
	defer os.Remove(tempFile)

	tests := []struct {
		name string
		path string
		want bool
	}{
		{"existing simple key", "dashboard.title", true},
		{"existing nested key", "auth.login.email", true},
		{"nonexistent key", "nonexistent.key", false},
		{"nonexistent nested", "dashboard.nonexistent", false},
		{"partial path exists", "dashboard", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, err := KeyExists(tempFile, tt.path)
			if err != nil {
				t.Errorf("KeyExists() error = %v", err)
				return
			}
			if result != tt.want {
				t.Errorf("KeyExists() = %v, want %v", result, tt.want)
			}
		})
	}
}

func TestValidateJSON(t *testing.T) {
	// Valid JSON file
	validFile := createTempJSONFile(t, sampleI18nData)
	defer os.Remove(validFile)

	result, err := ValidateJSON(validFile)
	if err != nil {
		t.Errorf("ValidateJSON() error = %v", err)
		return
	}
	if !result.Valid {
		t.Error("ValidateJSON() should return valid=true for valid JSON")
	}
	if result.Performance == nil {
		t.Error("ValidateJSON() should include performance metrics for valid JSON")
	}

	// Invalid JSON file
	invalidFile, err := os.CreateTemp("", "invalid_*.json")
	if err != nil {
		t.Fatal(err)
	}
	defer os.Remove(invalidFile.Name())

	_, err = invalidFile.WriteString("{invalid json")
	if err != nil {
		t.Fatal(err)
	}
	invalidFile.Close()

	result, err = ValidateJSON(invalidFile.Name())
	if err != nil {
		t.Errorf("ValidateJSON() should not return error for invalid JSON: %v", err)
		return
	}
	if result.Valid {
		t.Error("ValidateJSON() should return valid=false for invalid JSON")
	}
	if result.Error == nil {
		t.Error("ValidateJSON() should include error details for invalid JSON")
	}
}

func TestFileNotFoundErrors(t *testing.T) {
	nonexistentFile := "nonexistent.json"

	// Test all operations with nonexistent file
	_, err := GetKey(nonexistentFile, "any.key")
	if err == nil {
		t.Error("GetKey() should fail for nonexistent file")
	}

	err = AddKey(nonexistentFile, "any.key", "value")
	if err == nil {
		t.Error("AddKey() should fail for nonexistent file")
	}

	err = UpdateKey(nonexistentFile, "any.key", "value")
	if err == nil {
		t.Error("UpdateKey() should fail for nonexistent file")
	}

	err = RenameKey(nonexistentFile, "old.key", "new.key")
	if err == nil {
		t.Error("RenameKey() should fail for nonexistent file")
	}

	_, err = RemoveKey(nonexistentFile, "any.key")
	if err == nil {
		t.Error("RemoveKey() should fail for nonexistent file")
	}

	_, err = ListKeys(nonexistentFile, nil)
	if err == nil {
		t.Error("ListKeys() should fail for nonexistent file")
	}

	_, err = KeyExists(nonexistentFile, "any.key")
	if err == nil {
		t.Error("KeyExists() should fail for nonexistent file")
	}
}

// Helper functions

func createTempJSONFile(t *testing.T, data map[string]interface{}) string {
	tempFile, err := os.CreateTemp("", "test_*.json")
	if err != nil {
		t.Fatal(err)
	}

	jsonData, err := json.MarshalIndent(data, "", "  ")
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

func stringPtr(s string) *string {
	return &s
}

func deepEqual(a, b interface{}) bool {
	aJSON, err1 := json.Marshal(a)
	bJSON, err2 := json.Marshal(b)
	if err1 != nil || err2 != nil {
		return false
	}
	return string(aJSON) == string(bJSON)
}

func sliceContainsSameElements(a, b []string) bool {
	if len(a) != len(b) {
		return false
	}

	aMap := make(map[string]bool)
	bMap := make(map[string]bool)

	for _, v := range a {
		aMap[v] = true
	}
	for _, v := range b {
		bMap[v] = true
	}

	for k := range aMap {
		if !bMap[k] {
			return false
		}
	}
	for k := range bMap {
		if !aMap[k] {
			return false
		}
	}

	return true
}