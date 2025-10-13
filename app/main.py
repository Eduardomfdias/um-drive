from fastapi import FastAPI
from app.api.endpoints import router
import os

# Criar pasta storage se não existir
os.makedirs("storage", exist_ok=True)

app = FastAPI(
    title="UM Drive API",
    description="File Storage System - REST API",
    version="1.0.0"
)

# Incluir rotas
app.include_router(router, prefix="/api", tags=["files"])

@app.get("/")
async def root():
    return {
        "message": "UM Drive API is running!",
        "docs": "/docs"
    }
