/*
* Copyright (C) Rodrigo Ferreira, All Rights Reserved
* Unauthorized copying of this file, via any medium is strictly prohibited
* Proprietary and confidential
*/

using System.Text.RegularExpressions;

namespace FaceDetector.Api.Helper;

public class FileHelper
{
    public static string GetContentType(IFormFile file)
    {
        // Try to get the content type from the file itself
        if (!string.IsNullOrEmpty(file.ContentType))
        {
            return file.ContentType.ToLower();
        }

        // If content type is not available, try to determine it from the extension
        string extension = Path.GetExtension(file.FileName).ToLowerInvariant();

        return extension switch
        {
            ".jpg" or ".jpeg" => "image/jpeg",
            ".png" => "image/png",
            ".gif" => "image/gif",
            ".bmp" => "image/bmp",
            ".webp" => "image/webp",
            _ => "application/octet-stream" // Default binary
        };
    }

    public static bool IsValidImageFile(IFormFile file)
    {
        if (file == null || file.Length == 0)
            return false;

        string contentType = GetContentType(file);

        string[] allowedImageTypes =
        {
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/bmp",
            "image/webp"
        };

        return allowedImageTypes.Contains(contentType);
    }

    public static bool HasValidFileName(string fileName)
    {
        if (string.IsNullOrWhiteSpace(fileName))
            return false;

        // Check for valid file name (avoid path traversal and invalid characters)
        var regex = new Regex(@"^[a-zA-Z0-9_\-\. ]+$");
        return regex.IsMatch(fileName);
    }

    public static string SanitizeFileName(string fileName)
    {
        // Remove any invalid characters
        var invalidChars = Path.GetInvalidFileNameChars();
        var sanitizedName = new string(fileName.Where(c => !invalidChars.Contains(c)).ToArray());

        // Additional sanitization
        return Regex.Replace(sanitizedName, @"[^\w\-\. ]", "_");
    }
}