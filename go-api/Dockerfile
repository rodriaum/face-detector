FROM golang:1.24.2-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./

RUN go mod download

COPY src/ ./

RUN CGO_ENABLED=0 GOOS=linux go build -o face-detector-api

FROM alpine:latest

WORKDIR /app

COPY --from=builder /app/face-detector-api .
COPY config.yaml .

EXPOSE 8080

CMD ["./face-detector-api"]