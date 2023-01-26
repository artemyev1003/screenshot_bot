import pytest


@pytest.fixture(autouse=True)
def no_http_requests(monkeypatch):
    """
    Fixture preventing test functions from making HTTP requests.
    It relies on the fact that the vast majority of
    HTTP requests (including those made with the requests module)
    eventually go through urllib3.connectionpool.HTTPConnectionPool.urlopen.
    """
    def urlopen_mock():
        raise RuntimeError("Network access not allowed during testing")

    monkeypatch.setattr("urllib3.connectionpool.HTTPConnectionPool.urlopen",
                        lambda *args, **kwargs: urlopen_mock())


@pytest.fixture(autouse=True)
def initdir(tmp_path, monkeypatch):
    """
    Changes current path to pytest-provided temporary directory.
    """
    monkeypatch.chdir(tmp_path)
