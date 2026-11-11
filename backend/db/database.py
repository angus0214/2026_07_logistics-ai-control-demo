import os
from pathlib import Path
from urllib.parse import quote
from sqlmodel import create_engine, SQLModel, Session

sqlite_file_name = os.getenv("SQLITE_FILE_PATH", "logistics.db")
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_readonly_engine(db_path: str):
    """
    建立 SQLite 唯讀連線 (mode=ro)，供 SQL Agent 使用 (ADR-0005)。
    在這條連線上任何寫入都會被 SQLite 本身拒絕，與 SQL 解析防線互相獨立。
    """
    uri_path = quote(Path(db_path).as_posix(), safe="/:")
    return create_engine(
        f"sqlite:///file:{uri_path}?mode=ro&uri=true",
        connect_args={"check_same_thread": False},
    )


# SQL Agent 專用：不要拿這條連線以外的 engine 給 Agent
readonly_engine = create_readonly_engine(sqlite_file_name)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
