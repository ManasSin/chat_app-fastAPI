from typing import Callable, List
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import logging

from services.auth_service import auth_service

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to protect HTTP routes with JWT authentication.

    Excludes an allowlist of public paths (auth endpoints, docs, openapi, root).
    On success, attaches `request.state.user` (decoded token dict) for downstream handlers.
    """

    def __init__(self, app, allowlist: List[str] = None):
        super().__init__(app)
        self.allowlist = allowlist or [
            "/",
            "/auth/login",
            "/auth/register",
            "/openapi.json",
            "/docs",
            "/redoc",
            "/docs/oauth2-redirect",
        ]

    async def dispatch(self, request: Request, call_next: Callable):
        path = request.url.path

        # Allow anything in allowlist or docs/openapi paths
        if any(path == p or path.startswith(p.rstrip("/")) for p in self.allowlist):
            return await call_next(request)

        # Allow static and swagger assets
        if path.startswith("/static") or path.startswith("/swagger"):
            return await call_next(request)

        # Extract token: Authorization header or ?token= query param
        token = None
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1]
        else:
            token = request.query_params.get("token")

        if not token:
            return JSONResponse(
                {"detail": "Authentication credentials were not provided."},
                status_code=401,
            )

        decoded = auth_service.verify_token(token)
        if not decoded:
            return JSONResponse(
                {"detail": "Invalid or expired token."}, status_code=401
            )

        # Attach user info to request.state for downstream usage
        request.state.user = decoded

        # Proceed to the route
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.exception("Error in AuthMiddleware call_next: %s", e)
            return JSONResponse({"detail": "Internal server error"}, status_code=500)
