package operations

import (
	"errors"
	"fmt"
	"time"

	"jsonmcptool/internal/jsonhandler"
	"jsonmcptool/internal/pathresolver"
)

var (
	ErrKeyNotFound   = errors.New("KEY_NOT_FOUND")
	ErrKeyExists     = errors.New("KEY_EXISTS")
	ErrInvalidPath   = errors.New("INVALID_PATH")
	ErrInvalidJSON   = errors.New("INVALID_JSON")
	ErrFileNotFound  = errors.New("FILE_NOT_FOUND")
	ErrAddKeyError   = errors.New("ADD_KEY_ERROR")
	ErrUpdateKeyError = errors.New("UPDATE_KEY_ERROR")
	ErrRemoveKeyError = errors.New("REMOVE_KEY_ERROR")
	ErrRenameKeyError = errors.New("RENAME_KEY_ERROR")
	ErrSameKey       = errors.New("SAME_KEY")
)

// GetKey retrieves value by dot-notation key path
func GetKey(filePath, keyPath string) (interface{}, error) {
	handler := jsonhandler.NewJSONHandler(filePath)
	data, err := handler.LoadJSON(true)
	if err != nil {
		return nil, err
	}

	value, err := pathresolver.NavigateToKey(data, keyPath)
	if err != nil {
		if errors.Is(err, pathresolver.ErrKeyNotFound) {
			return nil, fmt.Errorf("%w: Key '%s' not found in %s", ErrKeyNotFound, keyPath, filePath)
		}
		if errors.Is(err, pathresolver.ErrInvalidPath) {
			return nil, fmt.Errorf("%w: %v", ErrInvalidPath, err)
		}
		return nil, fmt.Errorf("PATH_ERROR: %v", err)
	}

	return value, nil
}

// AddKey adds new key-value pair
func AddKey(filePath, keyPath string, value interface{}) error {
	handler := jsonhandler.NewJSONHandler(filePath)
	data, err := handler.LoadJSON(true)
	if err != nil {
		return err
	}

	// Check if key already exists
	if pathresolver.KeyExists(data, keyPath) {
		return fmt.Errorf("%w: Key '%s' already exists in %s", ErrKeyExists, keyPath, filePath)
	}

	// Create the nested path and set the value
	err = pathresolver.SetValueAtPath(data, keyPath, value, true)
	if err != nil {
		if errors.Is(err, pathresolver.ErrPathConflict) {
			return fmt.Errorf("PATH_CONFLICT: %v", err)
		}
		return fmt.Errorf("%w: Failed to add key '%s': %v", ErrAddKeyError, keyPath, err)
	}

	// Save the updated data
	if err := handler.SaveJSON(data, 2); err != nil {
		return fmt.Errorf("%w: Failed to save file: %v", ErrAddKeyError, err)
	}

	return nil
}

// UpdateKey updates existing key with new value
func UpdateKey(filePath, keyPath string, value interface{}) error {
	handler := jsonhandler.NewJSONHandler(filePath)
	data, err := handler.LoadJSON(true)
	if err != nil {
		return err
	}

	// Validate path first
	if err := pathresolver.ValidatePath(keyPath); err != nil {
		return fmt.Errorf("%w: %v", ErrInvalidPath, err)
	}

	// Check if key exists
	if !pathresolver.KeyExists(data, keyPath) {
		return fmt.Errorf("%w: Key '%s' not found in %s", ErrKeyNotFound, keyPath, filePath)
	}

	// Update the value
	err = pathresolver.SetValueAtPath(data, keyPath, value, false)
	if err != nil {
		if errors.Is(err, pathresolver.ErrKeyNotFound) {
			return fmt.Errorf("%w: Key '%s' not found in %s", ErrKeyNotFound, keyPath, filePath)
		}
		return fmt.Errorf("%w: Failed to update key '%s': %v", ErrUpdateKeyError, keyPath, err)
	}

	// Save the updated data
	if err := handler.SaveJSON(data, 2); err != nil {
		return fmt.Errorf("%w: Failed to save file: %v", ErrUpdateKeyError, err)
	}

	return nil
}

// RenameKey renames existing key (move value from old path to new path)
func RenameKey(filePath, oldPath, newPath string) error {
	if oldPath == newPath {
		return fmt.Errorf("%w: Old and new key paths cannot be the same", ErrSameKey)
	}

	// Validate paths first
	if err := pathresolver.ValidatePath(oldPath); err != nil {
		return fmt.Errorf("%w: %v", ErrInvalidPath, err)
	}
	if err := pathresolver.ValidatePath(newPath); err != nil {
		return fmt.Errorf("%w: %v", ErrInvalidPath, err)
	}

	handler := jsonhandler.NewJSONHandler(filePath)
	data, err := handler.LoadJSON(true)
	if err != nil {
		return err
	}

	// Check if old key exists
	if !pathresolver.KeyExists(data, oldPath) {
		return fmt.Errorf("%w: Key '%s' not found in %s", ErrKeyNotFound, oldPath, filePath)
	}

	// Check if new key already exists
	if pathresolver.KeyExists(data, newPath) {
		return fmt.Errorf("%w: Key '%s' already exists in %s", ErrKeyExists, newPath, filePath)
	}

	// Get the value from old location
	value, err := pathresolver.NavigateToKey(data, oldPath)
	if err != nil {
		return fmt.Errorf("%w: Failed to get value at '%s': %v", ErrRenameKeyError, oldPath, err)
	}

	// Set value at new location (create path if needed)
	err = pathresolver.SetValueAtPath(data, newPath, value, true)
	if err != nil {
		return fmt.Errorf("%w: Failed to set value at '%s': %v", ErrRenameKeyError, newPath, err)
	}

	// Remove from old location
	_, err = pathresolver.RemoveKeyAtPath(data, oldPath)
	if err != nil {
		return fmt.Errorf("%w: Failed to remove old key '%s': %v", ErrRenameKeyError, oldPath, err)
	}

	// Save the updated data
	if err := handler.SaveJSON(data, 2); err != nil {
		return fmt.Errorf("%w: Failed to save file: %v", ErrRenameKeyError, err)
	}

	return nil
}

// RemoveKey removes key and returns its value
func RemoveKey(filePath, keyPath string) (interface{}, error) {
	handler := jsonhandler.NewJSONHandler(filePath)
	data, err := handler.LoadJSON(true)
	if err != nil {
		return nil, err
	}

	// Validate path first
	if err := pathresolver.ValidatePath(keyPath); err != nil {
		return nil, fmt.Errorf("%w: %v", ErrInvalidPath, err)
	}

	// Check if key exists
	if !pathresolver.KeyExists(data, keyPath) {
		return nil, fmt.Errorf("%w: Key '%s' not found in %s", ErrKeyNotFound, keyPath, filePath)
	}

	// Remove the key and get its value
	removedValue, err := pathresolver.RemoveKeyAtPath(data, keyPath)
	if err != nil {
		return nil, fmt.Errorf("%w: Failed to remove key '%s': %v", ErrRemoveKeyError, keyPath, err)
	}

	// Save the updated data
	if err := handler.SaveJSON(data, 2); err != nil {
		return nil, fmt.Errorf("%w: Failed to save file: %v", ErrRemoveKeyError, err)
	}

	return removedValue, nil
}

// ListKeys lists all immediate child keys at the specified path
func ListKeys(filePath string, keyPath *string) ([]string, error) {
	handler := jsonhandler.NewJSONHandler(filePath)
	data, err := handler.LoadJSON(true)
	if err != nil {
		return nil, err
	}

	keys, err := pathresolver.GetAllKeysAtPath(data, keyPath)
	if err != nil {
		if errors.Is(err, pathresolver.ErrKeyNotFound) {
			pathDesc := "root"
			if keyPath != nil {
				pathDesc = fmt.Sprintf("'%s'", *keyPath)
			}
			return nil, fmt.Errorf("%w: Key %s not found in %s", ErrKeyNotFound, pathDesc, filePath)
		}
		if errors.Is(err, pathresolver.ErrNotObject) {
			return nil, fmt.Errorf("NOT_OBJECT: %v", err)
		}
		return nil, err
	}

	return keys, nil
}

// KeyExists checks if a key exists at the specified path
func KeyExists(filePath, keyPath string) (bool, error) {
	handler := jsonhandler.NewJSONHandler(filePath)
	data, err := handler.LoadJSON(true)
	if err != nil {
		return false, err
	}

	return pathresolver.KeyExists(data, keyPath), nil
}

// ValidationResult represents the result of JSON validation
type ValidationResult struct {
	Valid       bool                                   `json:"valid"`
	File        string                                 `json:"file"`
	Error       *jsonhandler.ValidationError           `json:"error,omitempty"`
	ErrorType   string                                 `json:"error_type,omitempty"`
	Performance *jsonhandler.PerformanceMetrics        `json:"performance,omitempty"`
}

// ValidateJSON validates JSON file syntax and structure
func ValidateJSON(filePath string) (*ValidationResult, error) {
	startTime := time.Now()
	handler := jsonhandler.NewJSONHandler(filePath)

	// Get basic file info
	fileInfo := handler.GetFileInfo()
	
	result := handler.ValidateJSONSyntax()

	// Add performance metrics if valid
	if result.Valid && result.Performance != nil {
		result.Performance.ParseTime = time.Since(startTime).Seconds()
		if fileInfo.Exists {
			result.Performance.FileSize = fileInfo.SizeBytes
		}
	}

	// Convert to our result type
	validationResult := &ValidationResult{
		Valid:       result.Valid,
		File:        result.File,
		Error:       result.Error,
		ErrorType:   result.ErrorType,
		Performance: result.Performance,
	}

	return validationResult, nil
}