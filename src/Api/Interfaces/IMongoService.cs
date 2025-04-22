/*
* Copyright (C) Rodrigo Ferreira, All Rights Reserved
* Unauthorized copying of this file, via any medium is strictly prohibited
* Proprietary and confidential
*/

using FaceDetector.Api.Models;

namespace FaceDetector.Api.Interfaces;

public interface IMongoService
{
    Task<FileUploadResponse> UploadFileAsync(IFormFile file, string fileName, Dictionary<string, object> metadata);
    Task<bool> DeleteFileAsync(string id);
    Task<Dictionary<string, byte[]>> GetAllFilesAsync();
    Task<byte[]?> GetFileByIdAsync(string id);
    Task<FileUploadResponse?> GetFileInfoByIdAsync(string id);
}