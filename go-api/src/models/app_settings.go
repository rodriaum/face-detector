/*
* Copyright (C) Rodrigo Ferreira, All Rights Reserved
* Unauthorized copying of this file, via any medium is strictly prohibited
* Proprietary and confidential
 */

package models

// AppSettings representa as configurações da aplicação
type AppSettings struct {
	ConnectionString string `json:"ConnectionString"`
	DatabaseName     string `json:"DatabaseName"`
	ApiToken         string `json:"ApiToken"`
}
