# Face Detector API

A lightweight backend API developed in Go as part of the Face Detector project. It provides an API component for integrating face detection functionality into other applications and services.

## Requirements

- Go
- Docker (optional, for containerized deployment)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/rodriaum/face-detector.git
cd face-detector/go-api
```

### 2. Install Dependencies

Download and resolve the Go module dependencies:

```bash
go mod tidy
```

## Running Locally

Start the API using Go:

```bash
go run main.go
```

## Docker Deployment

The API can also be built and executed using Docker.

### 1. Build the Docker Image

```bash
docker build -t face-detector-api .
```

### 2. Run the Container

```bash
docker run -p 8080:8080 face-detector-api
```

The container exposes port `8080` on the host.

## Project Structure

```text
go-api/
├── main.go
├── go.mod
└── README.md
```

## License

See the repository's license information.
