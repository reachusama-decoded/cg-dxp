"""Shared exception hierarchy for Catalyst client utilities.

All client exceptions inherit from CatalystClientError for easy catching
at skill boundaries.
"""

from __future__ import annotations


class CatalystClientError(Exception):
    """Base exception for all Catalyst client errors.
    
    Use this to catch any client-related failure in skill code:
    
        try:
            result = client.some_operation()
        except CatalystClientError as e:
            logger.error("Client operation failed: %s", e)
    """


class AuthError(CatalystClientError):
    """Authentication or authorization failure (HTTP 401/403).
    
    Raised when credentials are invalid, expired, or insufficient permissions.
    User should check their API token or request access.
    """


class RateLimitError(CatalystClientError):
    """Rate limit exceeded (HTTP 429).
    
    The client will automatically retry with exponential backoff when possible.
    This exception is raised only after all retry attempts are exhausted.
    """


class NotFoundError(CatalystClientError):
    """Requested resource not found (HTTP 404).
    
    Common causes:
    - Resource ID/key doesn't exist
    - User doesn't have permission to view the resource
    - API endpoint changed or is incorrect
    """


class ValidationError(CatalystClientError):
    """Request validation failed (HTTP 400).
    
    The API rejected the request payload or query parameters.
    Check the error message for field-specific details.
    """


class ConflictError(CatalystClientError):
    """Request conflicts with current state (HTTP 409).
    
    Common causes:
    - Attempting to create duplicate resource
    - Concurrent modification conflict
    - Resource in unexpected state
    """


class ServerError(CatalystClientError):
    """Server-side error (HTTP 5xx).
    
    The API service is experiencing issues. Retry may succeed.
    """


class NetworkError(CatalystClientError):
    """Network connectivity failure.
    
    Unable to reach the API endpoint. Check network connection,
    proxy settings, or firewall rules.
    """


class RequestTimeoutError(CatalystClientError):
    """Request timed out.
    
    The API didn't respond within the configured timeout period.
    Try increasing the timeout or check API service status.
    """


class SSLError(CatalystClientError):
    """SSL certificate verification failed.
    
    Common on corporate networks with SSL inspection.
    May need to disable verification or install corporate CA certificates.
    """
