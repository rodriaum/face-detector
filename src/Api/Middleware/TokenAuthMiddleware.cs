/*
* Copyright (C) Rodrigo Ferreira, All Rights Reserved
* Unauthorized copying of this file, via any medium is strictly prohibited
* Proprietary and confidential
*/

using FaceDetector.Api.Models;
using Microsoft.Extensions.Options;
using Microsoft.Extensions.Primitives;
using System.Net;

namespace FaceDetector.Api.Middleware;

public class TokenAuthMiddleware
{
    private readonly RequestDelegate _next;
    private readonly AppSettings _appSettings;

    public TokenAuthMiddleware(RequestDelegate next, IOptions<AppSettings> appSettings)
    {
        _next = next;
        _appSettings = appSettings.Value;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        // Skip auth for non-API routes or if you want to allow some endpoints without auth
        if (!context.Request.Path.StartsWithSegments("/api"))
        {
            await _next(context);
            return;
        }

        // Check if the Authorization header exists
        if (!context.Request.Headers.TryGetValue("Authorization", out StringValues authHeader))
        {
            context.Response.StatusCode = (int)HttpStatusCode.Unauthorized;
            await context.Response.WriteAsJsonAsync(new { message = "Authorization header is missing" });
            return;
        }

        // Check if the token is in the correct format
        string headerValue = authHeader.ToString();

        if (!headerValue.StartsWith("Bearer ", StringComparison.OrdinalIgnoreCase))
        {
            context.Response.StatusCode = (int)HttpStatusCode.Unauthorized;
            await context.Response.WriteAsJsonAsync(new { message = "Invalid authorization format" });
            return;
        }

        // Extract and validate the token
        string token = headerValue.Substring("Bearer ".Length).Trim();

        if (string.IsNullOrEmpty(token) || token != _appSettings.ApiToken)
        {
            context.Response.StatusCode = (int)HttpStatusCode.Unauthorized;
            await context.Response.WriteAsJsonAsync(new { message = "Invalid token" });
            return;
        }

        // Token is valid, proceed to the next middleware
        await _next(context);
    }
}
