import pytest
from kb.models import Document, Chunk
from kb.retrieve import retrieve_with_fallback


@pytest.mark.django_db
def test_retrieval_fallback_creates_external_doc():
    ctx, docs = retrieve_with_fallback("nonexistent topic abc123")
    assert ctx
    assert docs
    assert docs[0].source == 'external'


@pytest.mark.django_db
def test_retrieval_hits_kb():
    d = Document.objects.create(title='Test Doc', source='local')
    Chunk.objects.create(document=d, text='Budgeting 50/30/20 rule basics', order=0)
    ctx, docs = retrieve_with_fallback("50/30/20")
    assert '50/30/20' in ctx
    assert docs[0].id == d.id

