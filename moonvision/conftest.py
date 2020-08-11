import pytest
from model_bakery import baker

from django.test import RequestFactory

from moonvision.users.models import User


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> User:
    return baker.make(User)


@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()
