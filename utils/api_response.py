from typing import Any, Optional
from fastapi.responses import JSONResponse


def success(
    data: Optional[Any] = None, message: str = "Success", status_code: int = 200
):
    """Standard success response.

    Payload shape:
    {
      "success": True,
      "message": "...",
      "data": {...}
    }
    """
    payload = {"success": True, "message": message, "data": data}
    return JSONResponse(content=payload, status_code=status_code)


def error(
    message: str = "Error", status_code: int = 500, details: Optional[str] = None
):
    """Standard error response.

    Payload shape:
    {
      "success": False,
      "message": "...",
      "error": "..."
    }
    """
    payload = {"success": False, "message": message, "error": details}
    return JSONResponse(content=payload, status_code=status_code)
