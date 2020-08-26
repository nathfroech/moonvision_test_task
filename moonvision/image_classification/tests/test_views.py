import base64
import pathlib
from io import BytesIO

import pytest
from hamcrest import assert_that, equal_to, has_entry, has_key, instance_of, is_  # type: ignore
from PIL import Image

from django.conf import settings
from rest_framework import status

from moonvision.image_classification import models, views


class TestImageUploadView:
    view_class = views.ImageUploadView
    url = '/upload-image/'

    @pytest.mark.django_db
    def test_allows_to_upload_image(self, api_request_factory, base64_image, classifier_mock):
        data = {
            'image': base64_image.decode(),
            'model_type': 'AlexNet',
        }
        request = api_request_factory.post(self.url, data)

        response = self.view_class.as_view()(request)

        assert_that(response.status_code, is_(equal_to(status.HTTP_200_OK)))
        assert_that(response.data, has_entry('image_label', is_(instance_of(str))))
        uploaded_image = models.UploadedImage.objects.get()
        assert_that(uploaded_image.image_label, is_(equal_to(response.data['image_label'])))

    @pytest.mark.django_db
    def test_request_fails_on_incorrect_data(self, api_request_factory, classifier_mock):
        data = {
            'model_type': 'test',
        }
        request = api_request_factory.post(self.url, data)

        response = self.view_class.as_view()(request)

        assert_that(response.status_code, is_(equal_to(status.HTTP_400_BAD_REQUEST)))
        assert_that(response.data, has_key('image'))
        assert_that(not models.UploadedImage.objects.exists())

    @pytest.mark.django_db
    @pytest.mark.skipif(
        settings.SKIP_HEAVY_TESTS,
        reason='This test makes calls to external services and should be used only during the development process.',
    )
    def test_full_run(self, api_request_factory):
        image_path = pathlib.Path(__file__).absolute().parent / 'test_image.jpg'
        image = Image.open(image_path)
        buffered = BytesIO()
        image.save(buffered, format='JPEG')
        encoded_image = base64.b64encode(buffered.getvalue()).decode()
        request = api_request_factory.post(self.url, {
            'image': encoded_image,
            'model_type': 'AlexNet',
        })

        response = self.view_class.as_view()(request)

        assert_that(response.status_code, is_(equal_to(status.HTTP_200_OK)))
        # Well, we can't be sure what will be predicted here, but at least we will know that the whole process works.
        # And we will see the highest predictions in logs.
        assert_that(response.data, has_entry('image_label', is_(instance_of(str))))
