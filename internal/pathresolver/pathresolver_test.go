package pathresolver

import (
	"testing"
)

func TestValidatePath(t *testing.T) {
	tests := []struct {
		name    string
		path    string
		wantErr bool
	}{
		{"valid simple path", "key", false},
		{"valid nested path", "section.subsection.key", false},
		{"empty path", "", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := ValidatePath(tt.path)
			if (err != nil) != tt.wantErr {
				t.Errorf("ValidatePath() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func TestSplitPath(t *testing.T) {
	tests := []struct {
		name string
		path string
		want []string
	}{
		{"simple path", "key", []string{"key"}},
		{"nested path", "a.b.c", []string{"a", "b", "c"}},
		{"empty path", "", []string{}},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := SplitPath(tt.path)
			if len(result) != len(tt.want) {
				t.Errorf("SplitPath() = %v, want %v", result, tt.want)
				return
			}
			for i, v := range result {
				if v != tt.want[i] {
					t.Errorf("SplitPath()[%d] = %v, want %v", i, v, tt.want[i])
				}
			}
		})
	}
}

func TestNavigateToKey(t *testing.T) {
	testData := map[string]interface{}{
		"simple": "value",
		"nested": map[string]interface{}{
			"key": "nested value",
		},
		"key.with.dots": "dotted key value",
		"dashboard": map[string]interface{}{
			"title": "Dashboard",
			"stats": map[string]interface{}{
				"users": "Total Users",
			},
		},
	}

	tests := []struct {
		name    string
		data    interface{}
		path    string
		want    interface{}
		wantErr bool
	}{
		{"simple key", testData, "simple", "value", false},
		{"nested key", testData, "nested.key", "nested value", false},
		{"deeply nested", testData, "dashboard.stats.users", "Total Users", false},
		{"key with dots", testData, "key.with.dots", "dotted key value", false},
		{"nonexistent key", testData, "nonexistent", nil, true},
		{"nonexistent nested", testData, "dashboard.nonexistent", nil, true},
		{"empty path", testData, "", nil, true},
		{"navigate through non-object", testData, "simple.invalid", nil, true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, err := NavigateToKey(tt.data, tt.path)
			if (err != nil) != tt.wantErr {
				t.Errorf("NavigateToKey() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !tt.wantErr && result != tt.want {
				t.Errorf("NavigateToKey() = %v, want %v", result, tt.want)
			}
		})
	}
}

func TestKeyExists(t *testing.T) {
	testData := map[string]interface{}{
		"simple": "value",
		"nested": map[string]interface{}{
			"key": "nested value",
		},
		"key.with.dots": "dotted key value",
	}

	tests := []struct {
		name string
		data interface{}
		path string
		want bool
	}{
		{"existing simple key", testData, "simple", true},
		{"existing nested key", testData, "nested.key", true},
		{"existing key with dots", testData, "key.with.dots", true},
		{"nonexistent key", testData, "nonexistent", false},
		{"nonexistent nested", testData, "nested.nonexistent", false},
		{"empty path", testData, "", false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := KeyExists(tt.data, tt.path)
			if result != tt.want {
				t.Errorf("KeyExists() = %v, want %v", result, tt.want)
			}
		})
	}
}

func TestCreateNestedPath(t *testing.T) {
	tests := []struct {
		name    string
		path    string
		wantErr bool
	}{
		{"root level", "key", false},
		{"nested path", "section.subsection.key", false},
		{"deeply nested", "a.b.c.d.e", false},
		{"empty path", "", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			data := make(map[string]interface{})
			_, err := CreateNestedPath(data, tt.path)
			if (err != nil) != tt.wantErr {
				t.Errorf("CreateNestedPath() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func TestCreateNestedPathConflict(t *testing.T) {
	data := map[string]interface{}{
		"existing": "string value",
	}

	// Try to create path through existing string value
	_, err := CreateNestedPath(data, "existing.new.key")
	if err == nil {
		t.Error("CreateNestedPath() should fail when trying to create path through non-object")
	}
}

func TestGetAllKeysAtPath(t *testing.T) {
	testData := map[string]interface{}{
		"dashboard": map[string]interface{}{
			"title":   "Dashboard",
			"welcome": "Welcome",
		},
		"forms": map[string]interface{}{
			"buttons": map[string]interface{}{
				"submit": "Submit",
				"cancel": "Cancel",
			},
		},
	}

	tests := []struct {
		name    string
		data    interface{}
		path    *string
		want    []string
		wantErr bool
	}{
		{
			name: "root level keys",
			data: testData,
			path: nil,
			want: []string{"dashboard", "forms"},
		},
		{
			name: "nested keys",
			data: testData,
			path: stringPtr("dashboard"),
			want: []string{"title", "welcome"},
		},
		{
			name: "deeply nested keys",
			data: testData,
			path: stringPtr("forms.buttons"),
			want: []string{"submit", "cancel"},
		},
		{
			name:    "nonexistent path",
			data:    testData,
			path:    stringPtr("nonexistent"),
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, err := GetAllKeysAtPath(tt.data, tt.path)
			if (err != nil) != tt.wantErr {
				t.Errorf("GetAllKeysAtPath() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !tt.wantErr {
				if len(result) != len(tt.want) {
					t.Errorf("GetAllKeysAtPath() = %v, want %v", result, tt.want)
					return
				}
				// Convert to sets for comparison (order doesn't matter)
				resultSet := make(map[string]bool)
				wantSet := make(map[string]bool)
				for _, v := range result {
					resultSet[v] = true
				}
				for _, v := range tt.want {
					wantSet[v] = true
				}
				for k := range wantSet {
					if !resultSet[k] {
						t.Errorf("GetAllKeysAtPath() missing key %s", k)
					}
				}
				for k := range resultSet {
					if !wantSet[k] {
						t.Errorf("GetAllKeysAtPath() unexpected key %s", k)
					}
				}
			}
		})
	}
}

func TestRemoveKeyAtPath(t *testing.T) {
	tests := []struct {
		name    string
		path    string
		wantErr bool
	}{
		{"existing simple key", "simple", false},
		{"existing nested key", "nested.key", false},
		{"nonexistent key", "nonexistent", true},
		{"empty path", "", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			data := map[string]interface{}{
				"simple": "value",
				"nested": map[string]interface{}{
					"key": "nested value",
				},
			}

			_, err := RemoveKeyAtPath(data, tt.path)
			if (err != nil) != tt.wantErr {
				t.Errorf("RemoveKeyAtPath() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func TestSetValueAtPath(t *testing.T) {
	tests := []struct {
		name       string
		path       string
		value      interface{}
		createPath bool
		wantErr    bool
	}{
		{"set existing key", "existing", "new value", false, false},
		{"set with create path", "new.nested.key", "created value", true, false},
		{"set without create path", "nonexistent.key", "value", false, true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			data := map[string]interface{}{
				"existing": "old value",
			}

			err := SetValueAtPath(data, tt.path, tt.value, tt.createPath)
			if (err != nil) != tt.wantErr {
				t.Errorf("SetValueAtPath() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

// Helper function to create string pointer
func stringPtr(s string) *string {
	return &s
}