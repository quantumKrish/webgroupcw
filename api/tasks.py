from django.core.management import call_command
from huey.contrib.djhuey import periodic_task, task
from huey import crontab

@task()
def check_bid_winners():
    # Call the Django management command you want to run
    call_command('check_bids')

@periodic_task(crontab(minute='*/2'))
def schheduled_check_winners():
    check_bid_winners()
