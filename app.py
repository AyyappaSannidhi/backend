from fastapi import FastAPI
from mangum import Mangum
from src.api.endpoints.user import user_router

app = FastAPI()

app.include_router(user_router, prefix="/user", tags=["user"])

handler = Mangum(app)