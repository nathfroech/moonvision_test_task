from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from . import serializers


def get_image_label(image: bytes, model_type: str) -> str:
    # TODO: dummy function; implement it later
    return 'dummy_label'


class ImageUploadView(GenericAPIView):
    http_method_names = ('post',)
    serializer_class = serializers.ImageUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image_label = get_image_label(serializer.validated_data['image'], serializer.validated_data['model_type'])
        return Response(
            {'image_label': image_label},
            status=status.HTTP_200_OK,
        )
