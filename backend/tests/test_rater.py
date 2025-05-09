import pytest
from sqlmodel import Session, select, create_engine
import random
from ..config import get_config, AppSettings
from ..models import RSSItem, RSS_Journal
from ..rater.req_openai_compat import get_openai_response, rate_all_db, LLMResponse
from ..logger import custom_logger

logger = custom_logger("uvicorn.error", __name__)

@pytest.fixture
def db_session():
    config = get_config()

    sqlite_url = config.SQLITE_URL
    connection_args = {"check_same_thread": False}

    # database engine
    engine = create_engine(sqlite_url, connect_args=connection_args)

    with Session(engine) as session:
        yield session

@pytest.fixture
def example_paper(db_session):
    papers = db_session.exec(select(RSSItem)).all()
    paper = random.choice(papers)
    return paper

def test_get_llm_response(example_paper):
    config = get_config()

    resp = get_openai_response(example_paper, config)

    print(resp)
    assert isinstance(resp, LLMResponse)

def test_db_llm_rater(db_session):
    config = get_config()

    rate_all_db(db_session, config, rerate=False)