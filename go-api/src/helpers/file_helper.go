/*
* Copyright (C) Rodrigo Ferreira, All Rights Reserved
* Unauthorized copying of this file, via any medium is strictly prohibited
* Proprietary and confidential
 */

package helpers

import (
	"mime/multipart"
	"path/filepath"
	"regexp"
	"strings"
)

// GetContentType Determine the content type of a file
func GetContentType(file *multipart.FileHeader) string {
	// Try getting content type from the file header
	if file.Header != nil && len(file.Header["Content-Type"]) > 0 {
		return strings.ToLower(file.Header["Content-Type"][0])
	}

	// If the content type is not available, determine by extension
	extension := strings.ToLower(filepath.Ext(file.Filename))

	switch extension {
	case ".jpg", ".jpeg":
		return "image/jpeg"
	case ".png":
		return "image/png"
	case ".gif":
		return "image/gif"
	case ".bmp":
		return "image/bmp"
	case ".webp":
		return "image/webp"
	default:
		return "application/octet-stream" // Binário padrão
	}
}

// IsValidImageFile Verify if the file is a valid image file
func IsValidImageFile(file *multipart.FileHeader) bool {
	if file == nil || file.Size == 0 {
		return false
	}

	contentType := GetContentType(file)

	allowedImageTypes := []string{
		"image/jpeg",
		"image/png",
		"image/gif",
		"image/bmp",
		"image/webp",
	}

	for _, allowedType := range allowedImageTypes {
		if contentType == allowedType {
			return true
		}
	}

	return false
}

// HasValidFileName verifica se o nome do arquivo é válido
func HasValidFileName(fileName string) bool {
	if fileName == "" {
		return false
	}

	// Verificar nome de arquivo válido (evitar path traversal e caracteres inválidos)
	regex := regexp.MustCompile(`^[a-zA-Z0-9_\-\. ]+$`)
	return regex.MatchString(fileName)
}

// SanitizeFileName sanitiza o nome do arquivo
func SanitizeFileName(fileName string) string {
	// Remover caracteres inválidos
	regex := regexp.MustCompile(`[^\w\-\. ]`)
	return regex.ReplaceAllString(fileName, "_")
}
