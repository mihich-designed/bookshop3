from multiprocessing import cpu_count
import os
from dotenv import load_dotenv

def max_workers():
    return cpu_count()

load_dotenv()

bind = '0.0.0.0:' + os.getenv('PORT', '8000')
max_requests = 1000
worker_class = 'gevent'
workers = max_workers()

reload = True
name = 'Project_name'
