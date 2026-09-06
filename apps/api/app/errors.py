"""Structured API errors.

Every error response body follows the envelope documented in
docs/api-contract.md: `{"error": {"code", "message", "details"}}`.
Raise one of these from anywhere in a router/service; `app.main`
registers the handler that turns them into that envelope.
"""

from __future__ import annotations


class ApiError(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


class ValidationApiError(ApiError):
    def __init__(self, message: str, details: dict[str, object] | None = None) -> None:
        super().__init__(422, "VALIDATION_ERROR", message, details)


class InvalidUnicodeError(ApiError):
    def __init__(self, message: str = "text contains invalid Unicode (lone surrogate)") -> None:
        super().__init__(400, "INVALID_UTF8", message)


class TextTooLongError(ApiError):
    def __init__(self, max_len: int) -> None:
        super().__init__(413, "TEXT_TOO_LONG", f"text exceeds {max_len} codepoints")


class NotFoundError(ApiError):
    def __init__(self, message: str = "resource not found") -> None:
        super().__init__(404, "NOT_FOUND", message)


class ConflictError(ApiError):
    def __init__(self, message: str) -> None:
        super().__init__(409, "LEXICON_CONFLICT", message)


class SessionNotFoundError(ApiError):
    def __init__(self, session_id: str) -> None:
        super().__init__(404, "SESSION_NOT_FOUND", f"session {session_id!r} not found")
