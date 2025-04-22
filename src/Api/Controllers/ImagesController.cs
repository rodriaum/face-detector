/*
* Copyright (C) Rodrigo Ferreira, All Rights Reserved
* Unauthorized copying of this file, via any medium is strictly prohibited
* Proprietary and confidential
*/

using FaceDetector.Api.Helper;
using FaceDetector.Api.Interfaces;
using FaceDetector.Api.Models;
using Microsoft.AspNetCore.Mvc;

namespace FaceDetector.Api.Controllers;

[ApiController]
[Route("v1/images")]
public class ImagesController : ControllerBase
{
    private readonly IMongoService _mongoService;

    public ImagesController(IMongoService mongoService)
    {
        _mongoService = mongoService;
    }

    [HttpPost("upload")]
    [RequestSizeLimit(10 * 1024 * 1024)] // 10 MB limit
    public async Task<IActionResult> UploadImage(IFormFile file)
    {
        if (file == null || file.Length == 0)
            return BadRequest("No file was uploaded");

        // Validate the file is an image
        if (!FileHelper.IsValidImageFile(file))
            return BadRequest("Invalid image file. Only JPG, PNG, GIF, BMP, and WebP formats are allowed");

        // Get original filename and sanitize it
        string originalFileName = Path.GetFileName(file.FileName);

        if (!FileHelper.HasValidFileName(originalFileName))
            return BadRequest("Invalid file name");

        string safeFileName = FileHelper.SanitizeFileName(originalFileName);

        // Get content type
        string contentType = FileHelper.GetContentType(file);

        // Create metadata dictionary
        var metadata = new Dictionary<string, object>
            {
                { "contentType", contentType },
                { "originalFileName", originalFileName },
                { "uploadedBy", HttpContext.User.Identity?.Name ?? "anonymous" },
                { "uploadDate", DateTime.UtcNow }
            };

        try
        {
            // Upload file to GridFS
            FileUploadResponse response = await _mongoService.UploadFileAsync(file, safeFileName, metadata);
            return Ok(response);
        }
        catch (Exception ex)
        {
            return StatusCode(StatusCodes.Status500InternalServerError, $"Error uploading file: {ex.Message}");
        }
    }

    [HttpGet("get")]
    public async Task<IActionResult> GetImages()
    {
        Dictionary<string, byte[]> filesData = await _mongoService.GetAllFilesAsync();

        if (filesData == null || !filesData.Any())
            return NotFound();

        List<object> files = new();

        foreach (KeyValuePair<string, byte[]> result in filesData)
        {
            string id = result.Key;
            byte[] bytes = result.Value;

            FileUploadResponse? fileInfo = await _mongoService.GetFileInfoByIdAsync(id);

            string contentType = fileInfo?.ContentType ?? "application/octet-stream";
            string fileName = fileInfo?.FileName ?? $"{id}.bin";

            files.Add(new
            {
                Id = id,
                FileName = fileName,
                ContentType = contentType,
                Base64 = Convert.ToBase64String(bytes)
            });
        }

        return Ok(files);
    }

    [HttpGet("get/{id}")]
    public async Task<IActionResult> GetImage(string id)
    {
        byte[]? fileData = await _mongoService.GetFileByIdAsync(id);

        if (fileData == null)
            return NotFound();

        FileUploadResponse? fileInfo = await _mongoService.GetFileInfoByIdAsync(id);
        string contentType = fileInfo?.ContentType ?? "application/octet-stream";

        return File(fileData, contentType);
    }

    [HttpGet("info/{id}")]
    public async Task<IActionResult> GetImageInfo(string id)
    {
        FileUploadResponse? fileInfo = await _mongoService.GetFileInfoByIdAsync(id);

        if (fileInfo == null)
            return NotFound();

        return Ok(fileInfo);
    }

    [HttpDelete("delete/{id}")]
    public async Task<IActionResult> DeleteImage(string id)
    {
        bool result = await _mongoService.DeleteFileAsync(id);

        if (!result)
            return NotFound();

        return NoContent();
    }

    [HttpGet("ping")]
    public IActionResult PingServer()
    {
        try
        {
            return Ok("Server is up and running.");
        }
        catch (Exception ex)
        {
            return StatusCode(500, "Internal server error: " + ex.Message);
        }
    }
}