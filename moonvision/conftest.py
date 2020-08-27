import pytest

from rest_framework.test import APIRequestFactory


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def api_request_factory() -> APIRequestFactory:
    return APIRequestFactory()
