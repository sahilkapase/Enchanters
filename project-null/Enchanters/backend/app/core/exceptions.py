from fastapi import HTTPException, status


class KisaanSevaException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundException(KisaanSevaException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found",
        )


class BadRequestException(KisaanSevaException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedException(KisaanSevaException):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(KisaanSevaException):
    def __init__(self, detail: str = "Access denied"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ConflictException(KisaanSevaException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class RateLimitException(KisaanSevaException):
    def __init__(self, detail: str = "Too many requests. Please try again later."):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)


class OTPExpiredException(BadRequestException):
    def __init__(self):
        super().__init__(detail="OTP has expired or is invalid")


class OTPMaxAttemptsException(RateLimitException):
    def __init__(self):
        super().__init__(detail="Maximum OTP verification attempts exceeded. Locked for 15 minutes.")


class OTPRateLimitException(RateLimitException):
    def __init__(self):
        super().__init__(detail="Too many OTP requests. Maximum 5 per hour.")


class SessionExpiredException(ForbiddenException):
    def __init__(self):
        super().__init__(detail="Agent session has expired")


class InvalidFileException(BadRequestException):
    def __init__(self, detail: str = "Invalid file"):
        super().__init__(detail=detail)


class ExternalAPIException(KisaanSevaException):
    def __init__(self, service: str = "External service"):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"{service} is currently unavailable",
        )
