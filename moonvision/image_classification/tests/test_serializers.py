import pytest
from hamcrest import (  # type: ignore # noqa: WPS235
    assert_that,
    calling,
    contains_exactly,
    equal_to,
    has_entries,
    has_length,
    instance_of,
    is_,
    matches_regexp,
    raises,
)

from django.core.files.base import ContentFile
from rest_framework.exceptions import ValidationError

from moonvision.image_classification import serializers


class TestBase64ImageField:
    def test_base64_string_converted_to_image(self, base64_image):
        field = serializers.Base64ImageField()

        output = field.to_internal_value(base64_image)

        assert_that(output, is_(instance_of(ContentFile)))
        assert_that(output.name, matches_regexp(r'[a-z0-9-]{36}\.png'))

    def test_validation_fails_on_bad_type(self):
        field = serializers.Base64ImageField()

        try:
            field.to_internal_value(None)  # type: ignore
        except ValidationError as exception:
            assert_that(exception.detail, has_length(1))
            assert_that(str(exception.detail[0]), is_(equal_to('Upload a valid base64-encoded image.')))
        else:
            raise AssertionError('ValidationError has not been raised')

    def test_validation_fails_on_bad_string(self):
        field = serializers.Base64ImageField()

        try:
            field.to_internal_value(b'bad_image')
        except ValidationError as exception:
            assert_that(exception.detail, has_length(1))
            assert_that(str(exception.detail[0]), is_(equal_to('Upload a valid base64-encoded image.')))
        else:
            raise AssertionError('ValidationError has not been raised')


class TestImageUploadSerializer:
    serializer_class = serializers.ImageUploadSerializer

    def test_validates_correct_data_and_decodes_image(self, base64_image):
        data = {
            'image': base64_image,
            'model_type': 'AlexNet',
        }
        serializer = self.serializer_class(data=data)

        is_valid = serializer.is_valid()

        assert_that(is_valid)
        assert_that(serializer.validated_data, has_entries({
            'image': is_(instance_of(ContentFile)),
            'model_type': 'AlexNet',
        }))

    def test_fail_validation_on_bad_image(self):
        data = {
            'image': b'bad_image',
            'model_type': 'test',
        }
        serializer = self.serializer_class(data=data)

        is_valid = serializer.is_valid()

        assert_that(not is_valid)
        assert_that(serializer.errors, has_entries({
            'image': contains_exactly(equal_to('Upload a valid base64-encoded image.')),
        }))

    def test_raises_error_on_requesting_image_label_without_data_validation(self, base64_image, classifier_mock):
        data = {
            'image': base64_image,
            'model_type': 'test',
        }
        serializer = self.serializer_class(data=data)

        assert_that(calling(serializer.get_image_label).with_args(), raises(AssertionError))

    def test_raises_error_on_requesting_image_label_without_saved_instance(self, base64_image, classifier_mock):
        data = {
            'image': base64_image,
            'model_type': 'AlexNet',
        }
        serializer = self.serializer_class(data=data)
        serializer.is_valid()

        assert_that(calling(serializer.get_image_label).with_args(), raises(AssertionError))

    @pytest.mark.django_db
    def test_returns_image_label_calling_classifier_service(self, base64_image, classifier_mock):
        data = {
            'image': base64_image,
            'model_type': 'AlexNet',
        }
        serializer = self.serializer_class(data=data)
        serializer.is_valid()
        serializer.save()

        image_label = serializer.get_image_label()

        classifier_mock.assert_called_once_with('AlexNet')
        assert_that(image_label, is_(equal_to('dummy_label')))
