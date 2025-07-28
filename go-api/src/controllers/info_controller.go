/*
* Copyright (C) Rodrigo Ferreira, All Rights Reserved
* Unauthorized copying of this file, via any medium is strictly prohibited
* Proprietary and confidential
 */

package controllers

import (
	"github.com/gin-gonic/gin"
	"net/http"
)

type InfoController struct{}

func NewInfoController() *InfoController {
	return &InfoController{}
}

// PingServer godoc
// @Summary Check server status
// @Description Simple endpoint to verify if the server is operational
// @Tags Info
// @Produce json
// @Success 200 {object} map[string]interface{} "Server is operational"
// @Router /info/ping [get]
func (c *InfoController) PingServer(ctx *gin.Context) {
	ctx.JSON(http.StatusOK, gin.H{
		"status": "success",
		"message": "Server is operational",
		"timestamp": ctx.GetTime("now"),
	})
}