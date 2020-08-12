from hamcrest import (  # type: ignore
    assert_that,
    contains_exactly,
    equal_to,
    has_entries,
    has_length,
    instance_of,
    is_,
    matches_regexp,
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
            'model_type': 'test',
        }
        serializer = self.serializer_class(data=data)

        is_valid = serializer.is_valid()

        assert_that(is_valid)
        assert_that(serializer.validated_data, has_entries({
            'image': is_(instance_of(ContentFile)),
            'model_type': 'test',
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
