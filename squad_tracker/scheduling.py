import asyncio
import config
import pytz
import sys
import transaction
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from datetime import datetime, timedelta

jobstores = {
    'default': MemoryJobStore() # no persistent jobs
}

_scheduler = None

def init_scheduler():
    '''Initializes the scheduler. Must be run **after**
    config has been initialized.'''
    sys.stdout.write("Starting scheduler...")
    global _scheduler
    _scheduler = AsyncIOScheduler(jobstores=jobstores)
    _scheduler.start()
    sys.stdout.write("done\n")

def delayed_execute(func, args, timedelta):
    exec_time = datetime.now(config.TIMEZONE) + timedelta

    id = _scheduler.add_job(_execute_wrapper, 'date',
            args=[func]+args, run_date = exec_time).id
    return id

def daily_execute(func, args=[], *, misfire_grace_time_hours=1,
                  hour=None, minute=None, second=None):
    misfire_grace_time_seconds = misfire_grace_time_hours * 3600

    id = _scheduler.add_job(_execute_wrapper, 'cron',
            args=[func]+args, hour=hour, minute=minute, second=second,
            timezone=config.TIMEZONE,
            misfire_grace_time=misfire_grace_time_seconds).id
    return id

def interval_execute(func, args=[], *, misfire_grace_time_seconds=1,
                  interval_seconds):

    id = _scheduler.add_job(_execute_wrapper, 'interval',
            args=[func]+args, seconds=interval_seconds,
            timezone=config.TIMEZONE,
            misfire_grace_time=misfire_grace_time_seconds).id
    return id

# wrap function to include transaction.commit
async def _execute_wrapper(func, *args, **kwargs):
    ret = func(*args, **kwargs)
    if asyncio.iscoroutine(ret):
        ret = await ret
    transaction.commit()
    return ret

def deschedule(job_id):
    _scheduler.remove_job(job_id)

