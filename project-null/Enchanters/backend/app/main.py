from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.api.v1.router import api_v1_router
from app.core.exceptions import KisaanSevaException
import logging
import time

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s (env=%s)", settings.APP_NAME, settings.APP_ENV)
    from app.core.otp import get_redis
    try:
        redis = await get_redis()
        await redis.ping()
        logger.info("Redis connection OK")
    except Exception as e:
        logger.warning("Redis not available: %s", str(e))

    yield

    logger.info("Shutting down %s", settings.APP_NAME)
    from app.core.otp import _redis_client
    if _redis_client:
        await _redis_client.close()


app = FastAPI(
    title=settings.APP_NAME,
    description="A platform helping Indian farmers discover eligible government schemes, insurance options, and subsidies",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(
        "%s %s -> %d (%.3fs)",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )
    return response


@app.exception_handler(KisaanSevaException)
async def kisaanseva_exception_handler(request: Request, exc: KisaanSevaException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred"},
    )


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": "1.0.0"}
