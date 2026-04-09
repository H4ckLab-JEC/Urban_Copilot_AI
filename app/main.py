from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api import routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Urban Copilot AI Backend...")
    # await init_db()  # Temporalmente deshabilitado para evitar crash de Postgres local
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title="Urban Copilot AI API",
    description="Sistema inteligente de movilidad urbana",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
