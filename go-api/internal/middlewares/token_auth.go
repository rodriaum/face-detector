/*
* Copyright (C) Rodrigo Ferreira, All Rights Reserved
* Unauthorized copying of this file, via any medium is strictly prohibited
* Proprietary and confidential
 */

package middlewares

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

// TokenAuthMiddleware
// is a middleware provider to auth with a token in api.
func TokenAuthMiddleware(validToken string) gin.HandlerFunc {
	return func(c *gin.Context) {
		token := c.GetHeader("Authorization")

		// If the token is not provided
		if token == "" {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": "Authentication token not provided",
			})
			c.Abort()
			return
		}

		token = token[len("Bearer "):]

		// Verify if token is valid
		if token != validToken {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": "Invalid authentication token",
			})
			c.Abort()
			return
		}

		// If token is valid, continue to the next handler
		c.Next()
	}
}
