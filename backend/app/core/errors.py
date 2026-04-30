from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


class BusinessError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(BusinessError)
    async def business_error_handler(_: Request, exc: BusinessError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(_: Request, exc: IntegrityError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": "Database constraint violation"})

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
