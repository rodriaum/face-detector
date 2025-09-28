/*
* Copyright (C) Rodrigo Ferreira, All Rights Reserved
* Unauthorized copying of this file, via any medium is strictly prohibited
* Proprietary and confidential
 */

package models

import "time"

// FileUploadResponse representa a resposta após o upload de um arquivo
type FileUploadResponse struct {
	FileId      string    `json:"fileId" bson:"fileId"`
	FileName    string    `json:"fileName" bson:"fileName"`
	FileSize    int64     `json:"fileSize" bson:"fileSize"`
	ContentType string    `json:"contentType" bson:"contentType"`
	UploadDate  time.Time `json:"uploadDate" bson:"uploadDate"`
}
