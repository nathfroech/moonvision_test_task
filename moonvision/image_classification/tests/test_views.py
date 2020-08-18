import pytest
from hamcrest import assert_that, equal_to, has_entry, has_key, instance_of, is_  # type: ignore

from rest_framework import status

from moonvision.image_classification import models, views


class TestImageUploadView:
    view_class = views.ImageUploadView
    url = '/upload-image/'

    @pytest.mark.django_db
    def test_allows_to_upload_image(self, api_request_factory, base64_image):
        data = {
            'image': base64_image.decode(),
            'model_type': 'test',
        }
        request = api_request_factory.post(self.url, data)

        response = self.view_class.as_view()(request)

        assert_that(response.status_code, is_(equal_to(status.HTTP_200_OK)))
        assert_that(response.data, has_entry('image_label', is_(instance_of(str))))
        assert_that(models.UploadedImage.objects.count(), is_(equal_to(1)))

    @pytest.mark.django_db
    def test_request_fails_on_incorrect_data(self, api_request_factory):
        data = {
            'model_type': 'test',
        }
        request = api_request_factory.post(self.url, data)

        response = self.view_class.as_view()(request)

        assert_that(response.status_code, is_(equal_to(status.HTTP_400_BAD_REQUEST)))
        assert_that(response.data, has_key('image'))
        assert_that(not models.UploadedImage.objects.exists())
