package pathresolver

import (
	"errors"
	"fmt"
	"strings"
)

var (
	ErrInvalidPath   = errors.New("INVALID_PATH")
	ErrKeyNotFound   = errors.New("KEY_NOT_FOUND")
	ErrPathError     = errors.New("PATH_ERROR")
	ErrPathConflict  = errors.New("PATH_CONFLICT")
	ErrNotObject     = errors.New("NOT_OBJECT")
)

// ValidatePath validates a key path
func ValidatePath(keyPath string) error {
	if keyPath == "" {
		return fmt.Errorf("%w: Key path cannot be empty", ErrInvalidPath)
	}
	return nil
}

// SplitPath splits a dot-notation path into individual keys
func SplitPath(keyPath string) []string {
	if keyPath == "" {
		return []string{}
	}
	return strings.Split(keyPath, ".")
}

// NavigateToKey navigates through nested structure to get value at key path
func NavigateToKey(data interface{}, keyPath string) (interface{}, error) {
	if err := ValidatePath(keyPath); err != nil {
		return nil, err
	}

	// Convert to map[string]interface{} if needed
	dataMap, ok := data.(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("%w: Root data is not an object", ErrPathError)
	}

	// First, try the whole path as a single key (handles keys with dots)
	if value, exists := dataMap[keyPath]; exists {
		return value, nil
	}

	// If that fails, try dot-separated navigation
	keys := SplitPath(keyPath)
	current := data

	for i, key := range keys {
		currentMap, ok := current.(map[string]interface{})
		if !ok {
			partialPath := strings.Join(keys[:i], ".")
			return nil, fmt.Errorf("%w: Cannot navigate through non-object value at '%s'", ErrPathError, partialPath)
		}

		value, exists := currentMap[key]
		if !exists {
			return nil, fmt.Errorf("%w: Key '%s' not found", ErrKeyNotFound, keyPath)
		}

		current = value
	}

	return current, nil
}

// NavigateToParent navigates to the parent of the target key
func NavigateToParent(data interface{}, keyPath string) (map[string]interface{}, string, error) {
	if err := ValidatePath(keyPath); err != nil {
		return nil, "", err
	}

	keys := SplitPath(keyPath)
	
	dataMap, ok := data.(map[string]interface{})
	if !ok {
		return nil, "", fmt.Errorf("%w: Root data is not an object", ErrPathError)
	}

	if len(keys) == 1 {
		// Key is at root level
		return dataMap, keys[0], nil
	}

	// Navigate to parent
	parentPath := strings.Join(keys[:len(keys)-1], ".")
	parent, err := NavigateToKey(data, parentPath)
	if err != nil {
		return nil, "", err
	}

	parentMap, ok := parent.(map[string]interface{})
	if !ok {
		return nil, "", fmt.Errorf("%w: Parent at '%s' is not an object", ErrPathError, parentPath)
	}

	return parentMap, keys[len(keys)-1], nil
}

// KeyExists checks if a key path exists in the data structure
func KeyExists(data interface{}, keyPath string) bool {
	if err := ValidatePath(keyPath); err != nil {
		return false
	}

	dataMap, ok := data.(map[string]interface{})
	if !ok {
		return false
	}

	// First, try the whole path as a single key (handles keys with dots)
	if _, exists := dataMap[keyPath]; exists {
		return true
	}

	// If that fails, try dot-separated navigation
	_, err := NavigateToKey(data, keyPath)
	return err == nil
}

// CreateNestedPath creates nested path structure, creating intermediate objects as needed
func CreateNestedPath(data map[string]interface{}, keyPath string) (map[string]interface{}, error) {
	if err := ValidatePath(keyPath); err != nil {
		return nil, err
	}

	keys := SplitPath(keyPath)
	
	if len(keys) == 1 {
		// Root level key
		return data, nil
	}

	current := data

	// Create intermediate objects
	for i, key := range keys[:len(keys)-1] {
		if value, exists := current[key]; exists {
			if valueMap, ok := value.(map[string]interface{}); ok {
				current = valueMap
			} else {
				partialPath := strings.Join(keys[:i+1], ".")
				return nil, fmt.Errorf("%w: Cannot create nested path through non-object value at '%s'", ErrPathConflict, partialPath)
			}
		} else {
			// Create new nested object
			newMap := make(map[string]interface{})
			current[key] = newMap
			current = newMap
		}
	}

	return current, nil
}

// GetAllKeysAtPath gets all immediate child keys at the specified path
func GetAllKeysAtPath(data interface{}, keyPath *string) ([]string, error) {
	var target interface{}
	var err error

	if keyPath == nil {
		target = data
	} else {
		target, err = NavigateToKey(data, *keyPath)
		if err != nil {
			return nil, err
		}
	}

	targetMap, ok := target.(map[string]interface{})
	if !ok {
		pathDesc := "root"
		if keyPath != nil {
			pathDesc = fmt.Sprintf("'%s'", *keyPath)
		}
		return nil, fmt.Errorf("%w: Value at %s is not an object, cannot list keys", ErrNotObject, pathDesc)
	}

	keys := make([]string, 0, len(targetMap))
	for key := range targetMap {
		keys = append(keys, key)
	}

	return keys, nil
}

// RemoveKeyAtPath removes a key at the specified path and returns its value
func RemoveKeyAtPath(data map[string]interface{}, keyPath string) (interface{}, error) {
	if err := ValidatePath(keyPath); err != nil {
		return nil, err
	}

	// First, try the whole path as a single key (handles keys with dots)
	if value, exists := data[keyPath]; exists {
		delete(data, keyPath)
		return value, nil
	}

	// If that fails, try dot-separated navigation
	parent, finalKey, err := NavigateToParent(data, keyPath)
	if err != nil {
		return nil, err
	}

	value, exists := parent[finalKey]
	if !exists {
		return nil, fmt.Errorf("%w: Key '%s' not found", ErrKeyNotFound, keyPath)
	}

	delete(parent, finalKey)
	return value, nil
}

// SetValueAtPath sets a value at the specified path
func SetValueAtPath(data map[string]interface{}, keyPath string, value interface{}, createPath bool) error {
	var parent map[string]interface{}
	var finalKey string
	var err error

	if createPath {
		parent, err = CreateNestedPath(data, keyPath)
		if err != nil {
			return err
		}
		finalKey = SplitPath(keyPath)[len(SplitPath(keyPath))-1]
	} else {
		parent, finalKey, err = NavigateToParent(data, keyPath)
		if err != nil {
			return err
		}
	}

	parent[finalKey] = value
	return nil
}