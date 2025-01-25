import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.PROJ.service_pyrogram.main_scheduler import run

log = logging.getLogger('rich')

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
def schedule_jobs():
    log.warning('add tasks for scheduler ONLY first_run')
    # scheduler.add_job(run, id="first_run")  # first run
    # scheduler.add_job(run, "interval", seconds=3600, id="my_job_id")
    scheduler.add_job(run, "cron", day_of_week="mon-sun", hour="7-20", minute="0,30", id="parse_daily")

def start_scheduler():
    scheduler.start()
    
def stop_scheduler():
    scheduler.shutdown()

# async def run_bg_tasks(background_tasks: BackgroundTasks):
#     # background_tasks.add_task(write_log, message)
