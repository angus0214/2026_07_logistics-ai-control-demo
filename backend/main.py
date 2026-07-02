from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import the database initializer and models
from core.config import settings
from db.database import create_db_and_tables
from db.models import LogisticsRecord

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 正在啟動伺服器，並初始化資料庫 (SQLModel)...")
    create_db_and_tables()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FDE Backend with FastAPI and LangChain",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev, allow all.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Logistics AI Control Tower API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
