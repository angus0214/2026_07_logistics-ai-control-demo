from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()  # 將 .env 載入到 os.environ，讓 LangChain 抓得到 OPENAI_API_KEY

# Import the database initializer and models
from core.config import settings
from db.database import create_db_and_tables
from db.models import BillOfLading

from api.endpoints import upload, rag, chat
from services.rag_service import initialize_vector_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server started, initializing database (SQLModel)...")
    create_db_and_tables()
    try:
        initialize_vector_db()
    except Exception as e:
        print(f"Error initializing Vector DB: {e}")
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

app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(rag.router, prefix="/api", tags=["RAG"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Logistics AI Control Tower API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
