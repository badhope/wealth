"""Main FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from wealth.api.routes import router
from wealth.security.middleware import AntiScrapMiddleware, RateLimiter, security_monitor

rate_limiter = RateLimiter()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Wealth API starting up...")
    yield
    logger.info("Wealth API shutting down...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Wealth API",
        description="Quantitative Analysis Platform for Stocks and Funds",
        version="0.2.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(AntiScrapMiddleware, rate_limiter=rate_limiter)

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(exc)}
        )

    @app.get("/api/v1/health")
    async def health_check():
        return {
            "status": "healthy",
            "version": "0.2.0",
            "security": security_monitor.get_stats()
        }

    @app.get("/api/v1/security/stats")
    async def security_stats():
        return security_monitor.get_stats()

    app.include_router(router, prefix="/api/v1")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "wealth.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
