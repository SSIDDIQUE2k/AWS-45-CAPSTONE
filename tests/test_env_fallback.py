from config.settings.base import get_env


def test_get_env_dummy(monkeypatch):
    monkeypatch.delenv('NON_EXISTENT_ENV', raising=False)
    val = get_env('NON_EXISTENT_ENV', 'dummy')
    assert val == 'dummy'

