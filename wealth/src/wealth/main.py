"""Main FastAPI application entry point with performance optimizations."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
from port_utils import get_port_with_retry

from wealth.api.routes import router
from wealth.security.middleware import AntiScrapMiddleware, RateLimiter, security_monitor
from wealth.utils.performance import request_cache, performance_monitor, get_performance_stats

rate_limiter = RateLimiter()

request_count = 0
start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Wealth API starting up...")
    logger.info("Performance monitoring enabled")
    logger.info("Caching system initialized")
    yield
    uptime = time.time() - start_time
    logger.info(f"Wealth API shutting down... (uptime: {uptime:.2f}s)")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Wealth API",
        description="Quantitative Analysis Platform for Stocks and Funds",
        version="0.4.0",
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

    @app.middleware("http")
    async def performance_middleware(request: Request, call_next):
        global request_count
        request_count += 1

        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start

        performance_monitor.record_timing(f"{request.method} {request.url.path}", duration)
        performance_monitor.increment_counter("total_requests")

        response.headers["X-Process-Time"] = str(duration)
        response.headers["X-Request-ID"] = str(request_count)

        return response

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global exception: {exc}")
        performance_monitor.increment_counter("errors")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(exc)}
        )

    @app.get("/api/v1/health")
    async def health_check():
        uptime = time.time() - start_time
        return {
            "status": "healthy",
            "version": "0.4.0",
            "uptime_seconds": round(uptime, 2),
            "security": security_monitor.get_stats(),
            "performance": {
                "total_requests": request_count,
                "cache_stats": request_cache.get_stats()
            }
        }

    @app.get("/api/v1/security/stats")
    async def security_stats():
        return security_monitor.get_stats()

    @app.get("/api/v1/performance/stats")
    async def performance_stats():
        return get_performance_stats()

    @app.get("/api/v1/performance/cache/clear")
    async def clear_cache():
        request_cache._cache.clear()
        request_cache._timed_cache.cache.clear()
        request_cache.reset_stats()
        return {"message": "Cache cleared successfully"}

    app.include_router(router, prefix="/api/v1")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    actual_port = get_port_with_retry(port)
    logger.info(f"Starting server on port {actual_port}")
    uvicorn.run(
        "wealth.main:app",
        host="0.0.0.0",
        port=actual_port,
        reload=False,
        log_level="info",
        workers=1,
        limit_concurrency=100,
        limit_max_requests=10000,
        timeout_keep_alive=30,
    )
