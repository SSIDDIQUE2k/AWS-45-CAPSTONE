import os
import tempfile
import pytest
from kb.ingest import ingest_path
from kb.models import Document, Chunk


@pytest.mark.django_db
def test_ingest_from_folder_creates_chunks():
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, 'example.md')
        with open(f, 'w') as fh:
            fh.write('# Title\n\nBudgeting basics.\nMore content here.')
        n = ingest_path(d)
        assert n > 0
        assert Document.objects.count() == 1
        assert Chunk.objects.count() == n

