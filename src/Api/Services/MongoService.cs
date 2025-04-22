/*
* Copyright (C) Rodrigo Ferreira, All Rights Reserved
* Unauthorized copying of this file, via any medium is strictly prohibited
* Proprietary and confidential
*/

using FaceDetector.Api.Interfaces;
using FaceDetector.Api.Models;
using Microsoft.Extensions.Options;
using MongoDB.Bson;
using MongoDB.Driver;
using MongoDB.Driver.GridFS;

namespace FaceDetector.Api.Services;

public class MongoService : IMongoService
{
    private readonly IGridFSBucket _gridFSBucket;
    private readonly IMongoDatabase _database;

    public MongoService(IOptions<AppSettings> appSettings)
    {
        MongoClient client = new MongoClient(appSettings.Value.ConnectionString ?? "mongodb://localhost:27017");

        _database = client.GetDatabase(appSettings.Value.DatabaseName ?? "face-detector");
        _gridFSBucket = new GridFSBucket(_database);
    }

    public async Task<FileUploadResponse> UploadFileAsync(IFormFile file, string fileName, Dictionary<string, object> metadata)
    {
        // Create GridFS upload options with metadata
        var options = new GridFSUploadOptions
        {
            Metadata = new BsonDocument(metadata)
        };

        // Upload the file to GridFS
        using Stream stream = file.OpenReadStream();
        ObjectId fileId = await _gridFSBucket.UploadFromStreamAsync(fileName, stream, options);

        // Get the file info to return in the response
        FilterDefinition<GridFSFileInfo> filter = Builders<GridFSFileInfo>.Filter.Eq("_id", fileId);
        GridFSFileInfo fileInfo = await _gridFSBucket.Find(filter).FirstOrDefaultAsync();

        // Create and return the response
        return new FileUploadResponse
        {
            FileId = fileId.ToString(),
            FileName = fileInfo.Filename,
            FileSize = fileInfo.Length,
            ContentType = metadata.ContainsKey("contentType") ? metadata["contentType"].ToString() ?? "" : "",
            UploadDate = fileInfo.UploadDateTime
        };
    }

    public async Task<bool> DeleteFileAsync(string id)
    {
        try
        {
            if (!ObjectId.TryParse(id, out var objectId))
                return false;

            await _gridFSBucket.DeleteAsync(objectId);
            return true;
        }
        catch (GridFSFileNotFoundException)
        {
            return false;
        }
    }

    [Obsolete("This class is not recommended for use. Consider alternatives due to performance and maintenance.")]
    public async Task<Dictionary<string, byte[]>> GetAllFilesAsync()
    {
        try
        {
            Dictionary<string, byte[]> files = new();

            FilterDefinition<GridFSFileInfo> filter = Builders<GridFSFileInfo>.Filter.Empty;
            using IAsyncCursor<GridFSFileInfo> cursor = await _gridFSBucket.FindAsync(filter);

            List<GridFSFileInfo> fileInfos = await cursor.ToListAsync();

            foreach (GridFSFileInfo? fileInfo in fileInfos)
            {
                if (fileInfo == null) continue;

                using var stream = await _gridFSBucket.OpenDownloadStreamAsync(fileInfo.Id);
                using var memoryStream = new MemoryStream();

                await stream.CopyToAsync(memoryStream);

                files.Add(fileInfo.Id.ToString(), memoryStream.ToArray());
            }

            return files;
        }
        catch (Exception)
        {
            return new();
        }
    }

    public async Task<byte[]?> GetFileByIdAsync(string id)
    {
        try
        {
            if (!ObjectId.TryParse(id, out var objectId))
                return null;

            using Stream stream = await _gridFSBucket.OpenDownloadStreamAsync(objectId);
            using MemoryStream memoryStream = new MemoryStream();

            await stream.CopyToAsync(memoryStream);

            return memoryStream.ToArray();
        }
        catch (GridFSFileNotFoundException)
        {
            return null;
        }
    }

    public async Task<FileUploadResponse?> GetFileInfoByIdAsync(string id)
    {
        try
        {
            if (!ObjectId.TryParse(id, out var objectId))
                return null;

            FilterDefinition<GridFSFileInfo> filter = Builders<GridFSFileInfo>.Filter.Eq("_id", objectId);
            GridFSFileInfo fileInfo = await _gridFSBucket.Find(filter).FirstOrDefaultAsync();

            if (fileInfo == null)
                return null;

            string contentType = "";

            if (fileInfo.Metadata != null && fileInfo.Metadata.Contains("contentType"))
            {
                contentType = fileInfo.Metadata["contentType"].ToString() ?? "";
            }

            return new FileUploadResponse
            {
                FileId = fileInfo.Id.ToString(),
                FileName = fileInfo.Filename,
                FileSize = fileInfo.Length,
                ContentType = contentType,
                UploadDate = fileInfo.UploadDateTime
            };
        }
        catch (Exception)
        {
            return null;
        }
    }
}