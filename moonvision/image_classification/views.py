from rest_framework import generics, status
from rest_framework.response import Response

from moonvision.image_classification import serializers


def get_image_label(image: bytes, model_type: str) -> str:
    # TODO: dummy function; implement it later
    return 'dummy_label'


class ImageUploadView(generics.CreateAPIView):
    http_method_names = ('post',)
    serializer_class = serializers.ImageUploadSerializer

    def create(self, request, *args, **kwargs):
        """
        Validate request data, save the received image and label it.

        There are two changes, comparing to the default method:
        1. Since the main purpose of this view is to label image, not to create a model instance, we return 200 (OK)
        instead of 201 (CREATED). CreateAPIView is used just because it is technically close to what we need to do.
        2. We get an image label and modify our response accordingly - our model is just for debugging purposes;
        we don't need to return all its fields.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        image_label = get_image_label(serializer.validated_data['image'], serializer.validated_data['model_type'])
        headers = self.get_success_headers(serializer.data)
        return Response({'image_label': image_label}, status=status.HTTP_200_OK, headers=headers)
