from celery import shared_task
from .ingest import ingest_path


@shared_task
def task_ingest_path(path: str, source: str = 'local') -> int:
    return ingest_path(path, source=source)

