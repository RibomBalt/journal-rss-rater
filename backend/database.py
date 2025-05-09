from .config import get_config
from sqlmodel import create_engine, Session, SQLModel

sqlite_url = get_config().SQLITE_URL
connection_args = {"check_same_thread": False}

# database engine
# TODO is this thread safe / ok to call multiple times?
engine = create_engine(sqlite_url, connect_args=connection_args)

def get_db_session():
    """dependency to get a database session
    TODO: make this doesn't rely on fastapi
    """
    with Session(engine) as session:
        yield session

def init_db():
    """Initialize the database"""
    # init database
    SQLModel.metadata.create_all(engine)