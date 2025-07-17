package services

import (
	"bytes"
	"context"
	"errors"
	"face-detector-api/src/models"
	"io"
	"io/ioutil"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/gridfs"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type MongoService struct {
	client   *mongo.Client
	database *mongo.Database
	bucket   *gridfs.Bucket
}

// NewMongoService cria uma nova instância do serviço MongoDB
func NewMongoService(connectionString, databaseName string) (*MongoService, error) {
	// Conectar ao MongoDB
	clientOptions := options.Client().ApplyURI(connectionString)
	client, err := mongo.Connect(context.Background(), clientOptions)
	if err != nil {
		return nil, err
	}

	// Verificar a conexão
	err = client.Ping(context.Background(), nil)
	if err != nil {
		return nil, err
	}

	// Selecionar o banco de dados
	database := client.Database(databaseName)

	// Criar bucket GridFS
	bucket, err := gridfs.NewBucket(database)
	if err != nil {
		return nil, err
	}

	return &MongoService{
		client:   client,
		database: database,
		bucket:   bucket,
	}, nil
}

// UploadFile faz o upload de um arquivo para o GridFS
func (s *MongoService) UploadFile(file io.Reader, fileName string, metadata map[string]interface{}) (*models.FileUploadResponse, error) {
	// Criar opções de upload com metadata
	uploadOpts := options.GridFSUpload().SetMetadata(metadata)

	// Upload do arquivo para GridFS
	fileID, err := s.bucket.UploadFromStream(fileName, file, uploadOpts)
	if err != nil {
		return nil, err
	}

	// Buscar informações do arquivo
	filter := bson.M{"_id": fileID}
	cursor, err := s.bucket.Find(filter)
	if err != nil {
		return nil, err
	}
	defer cursor.Close(context.Background())

	// Verificar se encontrou o arquivo
	if !cursor.Next(context.Background()) {
		return nil, errors.New("arquivo não encontrado após upload")
	}

	// Obter informações do arquivo
	var fileInfo gridfs.File
	err = cursor.Decode(&fileInfo)
	if err != nil {
		return nil, err
	}

	// Obter content type dos metadados
	contentType := ""
	if metadata["contentType"] != nil {
		contentType = metadata["contentType"].(string)
	}

	// Criar e retornar a resposta
	return &models.FileUploadResponse{
		FileId:      fileID.Hex(),
		FileName:    fileInfo.Name,
		FileSize:    fileInfo.Length,
		ContentType: contentType,
		UploadDate:  fileInfo.UploadDate,
	}, nil
}

// DeleteFile exclui um arquivo pelo ID
func (s *MongoService) DeleteFile(id string) (bool, error) {
	objID, err := primitive.ObjectIDFromHex(id)
	if err != nil {
		return false, err
	}

	err = s.bucket.Delete(objID)
	if err != nil {
		return false, err
	}

	return true, nil
}

// GetAllFiles retorna todos os arquivos
func (s *MongoService) GetAllFiles() (map[string][]byte, error) {
	files := make(map[string][]byte)

	// Encontrar todos os arquivos
	cursor, err := s.bucket.Find(bson.M{})
	if err != nil {
		return files, err
	}
	defer cursor.Close(context.Background())

	// Iterar sobre os arquivos
	for cursor.Next(context.Background()) {
		var fileInfo gridfs.File
		if err := cursor.Decode(&fileInfo); err != nil {
			continue
		}

		// Abrir download stream
		downloadStream, err := s.bucket.OpenDownloadStream(fileInfo.ID)
		if err != nil {
			continue
		}
		defer downloadStream.Close()

		// Ler conteúdo para buffer
		var buf bytes.Buffer
		if _, err := io.Copy(&buf, downloadStream); err != nil {
			continue
		}

		// Adicionar ao mapa
		files[fileInfo.ID.(primitive.ObjectID).Hex()] = buf.Bytes()
	}

	return files, nil
}

// GetFileById retorna um arquivo pelo ID
func (s *MongoService) GetFileById(id string) ([]byte, error) {
	objID, err := primitive.ObjectIDFromHex(id)
	if err != nil {
		return nil, err
	}

	// Abrir download stream
	downloadStream, err := s.bucket.OpenDownloadStream(objID)
	if err != nil {
		return nil, err
	}
	defer downloadStream.Close()

	// Ler arquivo para buffer
	buffer, err := ioutil.ReadAll(downloadStream)
	if err != nil {
		return nil, err
	}

	return buffer, nil
}

// GetFileInfoById retorna informações de um arquivo pelo ID
func (s *MongoService) GetFileInfoById(id string) (*models.FileUploadResponse, error) {
	objID, err := primitive.ObjectIDFromHex(id)
	if err != nil {
		return nil, err
	}

	// Buscar informações do arquivo
	filter := bson.M{"_id": objID}
	cursor, err := s.bucket.Find(filter)
	if err != nil {
		return nil, err
	}
	defer cursor.Close(context.Background())

	// Verificar se encontrou o arquivo
	if !cursor.Next(context.Background()) {
		return nil, errors.New("arquivo não encontrado")
	}

	// Obter informações do arquivo
	var fileInfo gridfs.File
	err = cursor.Decode(&fileInfo)
	if err != nil {
		return nil, err
	}

	// Obter content type dos metadados
	contentType := ""
	if fileInfo.Metadata != nil {
		var metadata bson.M
		err := bson.Unmarshal(fileInfo.Metadata, &metadata)
		if err != nil {
			return nil, err
		}

		contentType, _ = metadata["contentType"].(string)
	}

	// Criar e retornar a resposta
	return &models.FileUploadResponse{
		FileId:      fileInfo.ID.(primitive.ObjectID).Hex(),
		FileName:    fileInfo.Name,
		FileSize:    fileInfo.Length,
		ContentType: contentType,
		UploadDate:  fileInfo.UploadDate,
	}, nil
}
