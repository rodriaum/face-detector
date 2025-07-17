/*
 * Copyright (C) Rodrigo Ferreira, All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 */

//go:generate swag init

package main

import (
	"face-detector-api/src/controllers"
	"face-detector-api/src/middlewares"
	"face-detector-api/src/services"
	"log"

	"os"

	_ "face-detector-api/src/docs"

	"github.com/joho/godotenv"

	"github.com/gin-gonic/gin"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
)

// @title Face Detector API
// @version 1.0
// @description API for face detection with image upload and management
// @host localhost:8080
// @BasePath /v1
func main() {
	// Load env
	godotenv.Load("../.env")

	// Get environment variables
	mongodbConnectionString, mongodbConnExists := os.LookupEnv("MONGODB_CONNECTION_STRING")
	mongodbDatabaseName, mongodbDbExists := os.LookupEnv("MONGODB_DATABASE_NAME")
	apiToken, apiTokenExists := os.LookupEnv("API_TOKEN")
	apiPort, apiPortExists := os.LookupEnv("API_PORT")

	if !mongodbConnExists || !mongodbDbExists || !apiTokenExists || !apiPortExists {
		if !mongodbConnExists {
			log.Println("Missing environment variable: MONGODB_CONNECTION_STRING")
		}
		if !mongodbDbExists {
			log.Println("Missing environment variable: MONGODB_DATABASE_NAME")
		}
		if !apiTokenExists {
			log.Println("Missing environment variable: API_TOKEN")
		}
		if !apiPortExists {
			log.Println("Missing environment variable: API_PORT")
		}
		log.Fatalln("One or more required environment variables are missing")
	}

	// Initialize MongoDB service
	mongoService, err := services.NewMongoService(mongodbConnectionString, mongodbDatabaseName)
	if err != nil {
		log.Fatalf("Error connecting to MongoDB: %v", err)
	}

	// Initialize Gin router
	router := gin.Default()

	// Configure Swagger route
	router.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	// Register middlewares
	router.Use(middlewares.TokenAuthMiddleware(apiToken))

	// Configure image routes
	imagesController := controllers.NewImagesController(mongoService)

	imagesGroup := router.Group("/v1/images")
	{
		imagesGroup.POST("/upload", imagesController.UploadImage)
		imagesGroup.GET("/list", imagesController.GetImages)
		imagesGroup.GET("/view/:id", imagesController.GetImage)
		imagesGroup.GET("/metadata/:id", imagesController.GetImageInfo)
		imagesGroup.DELETE("/remove/:id", imagesController.DeleteImage)
	}

	// Configure info routes
	infoController := controllers.NewInfoController()

	infoGroup := router.Group("/v1/info")
	{
		infoGroup.GET("/ping", infoController.PingServer)
	}

	// Start the server
	err = router.Run(":" + apiPort)
	if err != nil {
		log.Fatalf("Error starting server: %v", err)
	}
}
