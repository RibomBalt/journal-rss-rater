from fastapi import FastAPI, HTTPException, Depends, Query, APIRouter
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel, create_engine, Session, select, or_
import sqlite3
from typing import List, Annotated
import os
import re
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from yaml import safe_load, YAMLError
from functools import lru_cache
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import logging

from .models import RSSItem, RSS_Journal
from .config import AppSettings, get_config
from .logger import custom_logger
from .rater.req_openai_compat import rate_all_db, rate_papers, LLMResponse
from .rss import retrieve
from .database import get_db_session, init_db
from .crons import init_crons, get_cron_jobs
from .auth.httpdigest import auth_admin, security

config = get_config()
logger = custom_logger(__name__, debug=config.DEBUG)

# 加载环境变量
# load config
# ===================
ConfigDep = Annotated[AppSettings, Depends(get_config)]
# ===================


# 数据库文件
# TODO put this in separate module
# ================
SessionDep = Annotated[Session, Depends(get_db_session)]
# ================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """ """
    # init database
    init_db()
    # scheduler
    schedulers = init_crons()
    app.schedulers = schedulers

    yield


app = FastAPI(
    lifespan=lifespan,
    debug=get_config().DEBUG,
    title="RSS API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

router = APIRouter()

# routes
# ================
@router.get("/api/rss")
def get_rss_items(
    session: SessionDep,
    config: ConfigDep,
    journal: Annotated[list[str] | None, Query(alias="journal")] = None,
    time_since: Annotated[str | None, Query(alias="time_since")] = None,
    time_until: Annotated[str | None, Query(alias="time_until")] = None,
    max_number: Annotated[int | None, Query(alias="max_number")] = 100,
    order_by: Annotated[str | None, Query(alias="order_by")] = "llm_score",
    desc: Annotated[bool, Query(alias="desc")] = True,
):
    """
    Get all RSS items
    """
    selection = select(RSSItem)
    # choose the journal
    # TODO support short names
    if journal is not None:
        selection = selection.where(or_(RSSItem.source == j for j in journal))
    # if journal is not provided, get all journals

    def parse_date(time_since: str, default: datetime) -> datetime:
        # choose the time since
        if time_since is not None:
            if re.match(r'\d{4}-\d{2}-\d{2}', time_since):
                time_since_dt = datetime.strptime(time_since, "%Y-%m-%d")
            elif re.match(r'\d{4}-\d{2}', time_since):
                time_since_dt = datetime.strptime(time_since, "%Y-%m")
            elif re.match(r'\d+', time_since):
                if int(time_since) < 1e8:
                    # if the time since is less than 1e8, treat it as days
                    time_since_dt = datetime.now() - timedelta(days=int(time_since))
                else:
                    # if the time since is greater than 1e8, treat it as timestamp
                    time_since_dt = datetime.fromtimestamp(int(time_since))
            else:
                # default to 7 days
                time_since_dt = datetime.now() - timedelta(days=7)
        else:
            # default to 7 days
            time_since_dt = default
        return time_since_dt
    
    time_since_dt = parse_date(time_since, datetime.now() - timedelta(days=7))
    time_until_dt = parse_date(time_until, datetime.now())

    selection = selection.where(RSSItem.published >= time_since_dt).where(RSSItem.published <= time_until_dt)
    # limit the number of items
    if max_number is not None:
        selection = selection.limit(max_number)
    else:
        # fallback to default number
        selection = selection.limit(100)


    # order by
    if order_by is not None and order_by in RSSItem.__fields__:
        if desc:
            selection = selection.order_by(getattr(RSSItem, order_by).desc())
        else:
            selection = selection.order_by(getattr(RSSItem, order_by))

    # default order by published date descending
    selection = selection.order_by(RSSItem.published.desc())

    items = session.exec(selection).all()

    return items


@router.get("/api/rss/sources")
def get_rss_journals(config: ConfigDep):
    """
    """
    journals = [j.model_dump(mode='json') for j in config.RSS_JOURNALS.values()]

    return JSONResponse(content=journals)

@router.get("/api/rss/llm_prompt")
def get_llm_prompt(config: ConfigDep):
    """
    Get the LLM prompt
    """
    llm_prompt = config.LLM_API.model_dump(mode='json')
    # remove the api key
    llm_prompt['api_key'] = "********"
    return JSONResponse(content=llm_prompt)




@router.get("/api/rss/update", dependencies=[Depends(auth_admin)])
def update_rss(session: SessionDep, config: ConfigDep, journal_name: Annotated[str, Query(alias='j')] = "all", ):
    """
    Update from RSS sources
    """
    # get the journal config
    journal_configs = config.RSS_JOURNALS

    if not journal_name or journal_name in ["all", ""]:
        target_journals = list(config.RSS_JOURNALS.keys())
    elif journal_name in config.RSS_JOURNALS:
        target_journals = [journal_name]
    else:
        raise HTTPException(status_code=404, detail="Journal not found")

    all_results = {}
    for journal_key in target_journals:
        journal_schema = journal_configs[journal_key]
        results = retrieve(journal_schema, session=session, update_duplicate=True)

        all_results[journal_key] = results

    return JSONResponse(content=all_results)

@router.get("/api/rss/rate", dependencies=[Depends(auth_admin)])
def rate_rss(
    session: SessionDep,
    config: ConfigDep,
    rerate: Annotated[bool, Query(alias="force")] = False,
    link: Annotated[str | None, Query(alias="paper")] = None,
):
    """
    Rate all RSS items
    """
    rate_results = rate_all_db(session, config, rerate=rerate, specify_paper_link=link)
        
    return JSONResponse(content=rate_results)

# crons
# ================
@router.get("/api/crons")
def get_cron_status():
    """
    Get the cron status
    """
    scheduler: BackgroundScheduler = app.schedulers
    jobs = get_cron_jobs(scheduler)

    return JSONResponse(content={"jobs": jobs})


@router.get("/api/crons/{job_name}/now", dependencies=[Depends(auth_admin)])
def trigger_cron_now(job_name: str):
    """
    Trigger a cron job to run now
    """
    scheduler: BackgroundScheduler = app.schedulers
    jobs = get_cron_jobs(scheduler)

    for job in jobs:
        if job["id"] == job_name:
            scheduler.get_job(job["id"]).modify(next_run_time=datetime.now())
            return JSONResponse(content={"status": "success", "job": job})
        
    else:
        raise HTTPException(status_code=404, detail="Job not found")


# config
# ================
@router.get("/api/config", dependencies=[Depends(auth_admin)])
async def get_config_web(config: ConfigDep, show_secrets: bool = False):
    """
    Get the config
    """
    config_dict = config.model_dump()
    # redact secrets
    if not show_secrets:
        config_dict["LLM_API"]['api_key'] = "********"
        for key in config_dict["ADMIN_PANEL"]:
            config_dict["ADMIN_PANEL"][key] = "********"

    return JSONResponse(config_dict)

# mount the frontend
app.include_router(router, tags=["api"], prefix=config.BASE_URL)
app.mount(config.BASE_URL, StaticFiles(directory="frontend/dist", html=True), name="frontend")

def start_server():
    import uvicorn
    try:
        with open("backend/config/logging.yml", "r") as f:
            log_config = safe_load(f.read())

    except (FileNotFoundError, YAMLError) as err:
        logger.warning("Logging config file not found. Using default config.")
        log_config = None


    config = get_config()
    uvicorn.run(
        "backend.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        # log_level=logging.DEBUG if config.DEBUG else logging.INFO,
        log_config=log_config
    )


if __name__ == "__main__":
    start_server()