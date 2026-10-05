from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import get_settings
from app.schemas import HealthResponse


settings = get_settings()

app = FastAPI(
    title="LegalEase API",
    description="AI-powered legal document drafting API.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)


@app.get("/", response_model=HealthResponse)
def root():
    return HealthResponse(
        status="ok",
        app=settings.app_name,
    )


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="healthy",
        app=settings.app_name,
    )