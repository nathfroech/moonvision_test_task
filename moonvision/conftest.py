import pytest

from model_bakery import baker
from rest_framework.test import APIRequestFactory

from moonvision.users.models import User


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> User:
    return baker.make(User)


@pytest.fixture
def api_request_factory() -> APIRequestFactory:
    return APIRequestFactory()
