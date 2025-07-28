# Detector de Rosto: API

## Instalação

1. Instalar Dependências
```bash
go mod tidy
```

## Rodar (Local)
1. Executar o Ficheiro Principal
```bash
go run main.go
```

## Rodar (Docker)

1. Construir o Docker
```bash
docker build -t face-detector-api .
```
2. Executar o Docker
```bash
docker run -p 8080:8080 face-detector-api
```