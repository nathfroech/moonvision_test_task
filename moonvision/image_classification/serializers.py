import base64
import imghdr
import uuid
from typing import Optional

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from rest_framework import serializers

from moonvision.image_classification import models, services


class Base64ImageField(serializers.ImageField):
    default_error_messages = {
        'invalid_image': 'Upload a valid base64-encoded image.',
    }

    def to_internal_value(self, data: bytes) -> ContentFile:
        try:
            decoded_file = base64.b64decode(data)
        except TypeError:
            self.fail('invalid_image')

        file_name = str(uuid.uuid4())
        file_extension = self.get_file_extension(file_name, decoded_file)
        file_name = '{0}.{1}'.format(file_name, file_extension)
        data = ContentFile(decoded_file, name=file_name)

        try:
            return super().to_internal_value(data)
        except ValidationError:
            self.fail('invalid_image')

    def get_file_extension(self, file_name: str, decoded_file: bytes) -> Optional[str]:
        extension = imghdr.what(file_name, decoded_file)
        return 'jpg' if extension == 'jpeg' else extension


class ImageUploadSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    model_type = serializers.ChoiceField(choices=services.ImageClassificationService.get_model_choices())

    class Meta:
        model = models.UploadedImage
        fields = ('image', 'model_type')

    def get_image_label(self) -> str:
        """
        Classify an image and return a label for it.

        We need a file path for classifier, so we should save an image somewhere. And since we have a model anyway,
        we just require here that the serializer should be validated and its instance - saved.
        (Note: check for validation is "hidden" inside `self.validated_data` property.)
        """
        if not self.instance:
            msg = 'You must call `.save()` before calling `.get_image_label()`.'
            raise AssertionError(msg)
        image_classifier = services.ImageClassificationService(self.instance.model_type)
        return image_classifier.classify_image(self.instance.image.path)
