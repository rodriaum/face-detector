/*
* Copyright (C) Rodrigo Ferreira, All Rights Reserved
* Unauthorized copying of this file, via any medium is strictly prohibited
* Proprietary and confidential
 */

package controllers

import (
	"encoding/base64"
	"face-detector-api/src/helpers"
	"face-detector-api/src/services"
	"mime/multipart"
	"net/http"
	"path/filepath"
	"time"

	"github.com/gin-gonic/gin"
)

type ImagesController struct {
	mongoService *services.MongoService
}

func NewImagesController(mongoService *services.MongoService) *ImagesController {
	return &ImagesController{
		mongoService: mongoService,
	}
}

// UploadImage godoc
// @Summary Upload image
// @Description Upload a new image file
// @Tags Images
// @Accept multipart/form-data
// @Produce json
// @Param file formData file true "Image file (JPG, PNG, GIF, BMP, WebP)"
// @Param uploadedBy formData string false "Name of the uploader (defaults to 'anonymous' if not provided)"
// @Success 200 {object} models.FileUploadResponse "Image uploaded successfully"
// @Failure 400 {object} map[string]interface{} "Bad request (no file, invalid image format, or invalid filename)"
// @Failure 500 {object} map[string]interface{} "Internal server error"
// @Router /images/upload [post]
func (c *ImagesController) UploadImage(ctx *gin.Context) {
	file, err := ctx.FormFile("file")
	if err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "No files were uploaded"})
		return
	}

	if !helpers.IsValidImageFile(file) {
		ctx.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid image file. Only JPG, PNG, GIF, BMP and WebP formats are allowed",
		})
		return
	}

	originalFileName := filepath.Base(file.Filename)
	if !helpers.HasValidFileName(originalFileName) {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file name"})
		return
	}
	safeFileName := helpers.SanitizeFileName(originalFileName)

	// Get content type
	contentType := helpers.GetContentType(file)

	uploadedBy := ctx.DefaultPostForm("uploadedBy", "anonymous")

	metadata := map[string]interface{}{
		"contentType":      contentType,
		"originalFileName": originalFileName,
		"uploadedBy":       uploadedBy,
		"uploadDate":       time.Now().UTC(),
	}

	src, err := file.Open()
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Error opening file"})
		return
	}
	defer func(src multipart.File) {
		err := src.Close()
		if err != nil {
			ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Error closing file"})
			return
		}
	}(src)

	// Upload to GridFS
	response, err := c.mongoService.UploadFile(src, safeFileName, metadata)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Error uploading file: " + err.Error()})
		return
	}

	ctx.JSON(http.StatusOK, response)
}

// GetImages godoc
// @Summary Get all images
// @Description Retrieve a list of all uploaded images with base64 encoded data
// @Tags Images
// @Produce json
// @Success 200 {array} map[string]interface{} "A list of images"
// @Failure 404 {object} map[string]interface{} "No images found"
// @Failure 500 {object} map[string]interface{} "Internal server error"
// @Router /images/list [get]
func (c *ImagesController) GetImages(ctx *gin.Context) {
	filesData, err := c.mongoService.GetAllFiles()
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Error getting files"})
		return
	}

	if len(filesData) == 0 {
		ctx.JSON(http.StatusNotFound, gin.H{"error": "No files found"})
		return
	}

	var files []map[string]interface{}

	for id, bytes := range filesData {
		fileInfo, err := c.mongoService.GetFileInfoById(id)
		if err != nil {
			continue
		}

		contentType := fileInfo.ContentType
		fileName := fileInfo.FileName

		files = append(files, map[string]interface{}{
			"id":          id,
			"fileName":    fileName,
			"contentType": contentType,
			"base64":      base64.StdEncoding.EncodeToString(bytes),
		})
	}

	ctx.JSON(http.StatusOK, files)
}

// GetImage godoc
// @Summary Get image by ID
// @Description Retrieve a specific image by its ID
// @Tags Images
// @Produce image/*
// @Param id path string true "Image ID"
// @Success 200 "Image file returned as binary data"
// @Failure 404 {object} map[string]interface{} "Image not found"
// @Failure 500 {object} map[string]interface{} "Internal server error"
// @Router /images/view/{id} [get]
func (c *ImagesController) GetImage(ctx *gin.Context) {
	id := ctx.Param("id")

	fileData, err := c.mongoService.GetFileById(id)
	if err != nil {
		ctx.JSON(http.StatusNotFound, gin.H{"error": "File not found"})
		return
	}

	fileInfo, err := c.mongoService.GetFileInfoById(id)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Error getting file info"})
		return
	}

	contentType := fileInfo.ContentType
	ctx.Data(http.StatusOK, contentType, fileData)
}

// GetImageInfo godoc
// @Summary Get image metadata
// @Description Retrieve metadata about a specific image
// @Tags Images
// @Produce json
// @Param id path string true "Image ID"
// @Success 200 {object} models.FileUploadResponse "Image metadata retrieved successfully"
// @Failure 404 {object} map[string]interface{} "Image not found"
// @Router /images/metadata/{id} [get]
func (c *ImagesController) GetImageInfo(ctx *gin.Context) {
	id := ctx.Param("id")

	fileInfo, err := c.mongoService.GetFileInfoById(id)
	if err != nil {
		ctx.JSON(http.StatusNotFound, gin.H{"error": "File not found"})
		return
	}

	ctx.JSON(http.StatusOK, fileInfo)
}

// DeleteImage godoc
// @Summary Delete image by ID
// @Description Delete a specific image by its ID
// @Tags Images
// @Param id path string true "Image ID"
// @Success 204 "Image successfully deleted"
// @Failure 404 {object} map[string]interface{} "Image not found"
// @Router /images/delete/{id} [delete]
func (c *ImagesController) DeleteImage(ctx *gin.Context) {
	id := ctx.Param("id")

	result, err := c.mongoService.DeleteFile(id)
	if err != nil || !result {
		ctx.JSON(http.StatusNotFound, gin.H{"error": "File not found"})
		return
	}

	ctx.Status(http.StatusNoContent)
}
