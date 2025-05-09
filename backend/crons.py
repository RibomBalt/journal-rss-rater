from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from .models import AllowExtraModel
from .rss import retrieve
from .rater.req_openai_compat import rate_all_db
from .config import get_config
from .database import get_db_session
from contextlib import contextmanager
from .logger import custom_logger

config = get_config()
logger = custom_logger(__name__, debug=config.DEBUG)

class APS_Jobs(AllowExtraModel):
    id: str
    name: str
    next_run_time: datetime


def cron_retreive():
    """Cron job to retrieve RSS feeds"""
    config = get_config()
    with contextmanager(get_db_session)() as session:
        for journal in config.RSS_JOURNALS.values():
            retrieve(journal, session=session, update_duplicate=False)
            logger.info(f"Cron job to retrieve {journal.source} completed.")

    logger.info("Cron job to retrieve ALL RSS feeds completed.")

def cron_rate():
    """Cron job to rate papers"""
    config = get_config()
    with contextmanager(get_db_session)() as session:
        rate_all_db(session, config, rerate=False)

    logger.info("Cron job to rate papers completed.")

def init_crons():
    """Initialize cron jobs"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(cron_retreive, 'cron', hour=3 , id='cron_retrieve', max_instances=1)
    scheduler.add_job(cron_rate, 'cron', hour=4, id='cron_rate', max_instances=1)
    scheduler.start()

    logger.info("Cron jobs initialized.")

    return scheduler

def get_cron_jobs(scheduler: BackgroundScheduler):
    """Get all cron jobs"""
    jobs = []
    for job in scheduler.get_jobs():
        job_info = APS_Jobs.model_validate({
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time
        })
        jobs.append(job_info.model_dump(mode='json'))
    return jobs