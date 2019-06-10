# bisite/bisite/tasks/__init__.py
from .celery import app
from .celery import task
#from ..celery import task
#from ..celery import shared_task
#from ..bi import KojitsuPos
import sys
import pathlib
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir)+'/../bi/')
import dashboard


#@app.task
#@task(name='fetch_latest_data')
@app.task(name='fetch_latest_data')
def fetch_latest_data():
    dashboard.KojitsuPos.refreshtables()

