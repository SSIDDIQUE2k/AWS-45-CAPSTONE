from django.core.management.base import BaseCommand, CommandError
from kb.ingest import ingest_path


class Command(BaseCommand):
    help = 'Ingest knowledge base from a local folder path'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str, help='Folder path of KB files (.txt/.md)')
        parser.add_argument('--source', type=str, default='local')

    def handle(self, *args, **options):
        path = options['path']
        source = options['source']
        try:
            count = ingest_path(path, source=source)
        except Exception as e:
            raise CommandError(str(e))
        self.stdout.write(self.style.SUCCESS(f'Ingested {count} chunks from {path}'))

