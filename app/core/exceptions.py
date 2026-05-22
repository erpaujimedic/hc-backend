# File: app/core/exceptions.py
from fastapi import HTTPException, status

class DatabaseConnectionError(HTTPException):
    """Triggered when the backend fails to communicate with Supabase."""
    def __init__(self, detail: str = "Critical Failure: Unable to establish connection to the database."):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

class InvalidCredentialsError(HTTPException):
    """Triggered when authentication tokens (Firebase JWT) are missing, expired, or invalid."""
    def __init__(self, detail: str = "Unauthorized access: Invalid or missing authentication credentials."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class InsufficientPermissionsError(HTTPException):
    """Triggered when a valid user attempts to access a restricted Admin endpoint."""
    def __init__(self, detail: str = "Forbidden: You do not have the required administrative privileges to perform this action."):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class ResourceNotFoundError(HTTPException):
    """Triggered when a requested record (e.g., Branch, Transaction) does not exist."""
    def __init__(self, resource_name: str = "Requested resource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"{resource_name} could not be found in the system."
        )

class GeocodingResolutionError(HTTPException):
    """Triggered when the dispatch system fails to resolve patient coordinates."""
    def __init__(self, detail: str = "Dispatch Error: Unable to resolve geographic coordinates for the provided address."):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)

class ConfigurationUpdateError(HTTPException):
    """Triggered when dynamic system settings fail to save or synchronize."""
    def __init__(self, detail: str = "System Error: Failed to apply and synchronize the new configuration settings."):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)