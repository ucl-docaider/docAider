import os
from celery import Celery

# In a containerized environment, this will be 'rabbitmq'.
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")

app = Celery(
    'doc_tasks',
    broker=f'pyamqp://guest:guest@{RABBITMQ_HOST}:5672//',
    backend='rpc://',
    include=['celery_worker.tasks']
)

# Optional configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

if __name__ == '__main__':
    app.start()