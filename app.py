from fastapi import FastAPI
from mangum import Mangum
from src.api.user import user_router
from src.api.auth import auth_router
from src.api.assets import assets_router
from src.core.config import Config
from starlette.middleware.cors import CORSMiddleware
from src.core.logging import logger


app = FastAPI(
    docs_url="/docs" if Config.APP_ENV != "PROD" else None,
    redoc_url="/redoc" if Config.APP_ENV != "PROD" else None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,  # Allowed origins for CORS
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Allowed HTTP methods
    allow_headers=["Authorization", "Content-Type"],  # Allowed headers
)

app.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(assets_router, prefix="/assets", tags=["assets"])

handler = Mangum(app)

# Add logging
handler = logger.inject_lambda_context(handler, clear_state=True)