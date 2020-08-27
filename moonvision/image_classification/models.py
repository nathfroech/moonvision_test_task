import uuid

from django.db import models
from django.utils.html import format_html


def image_upload(instance: 'UploadedImage', filename: str) -> str:
    # I don't catch IndexError because image file without an extension would be a pretty rare and weird case.
    extension = filename.rsplit('.', 1)[1]
    return 'images/{uuid}.{extension}'.format(uuid=str(uuid.uuid4()), extension=extension)


class UploadedImage(models.Model):
    """Stores uploaded images (and their labels) for debugging purposes."""

    image = models.ImageField(upload_to=image_upload)
    model_type = models.CharField(max_length=255)  # TODO: Limit choices?
    image_label = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        if self.image_label:
            return 'Labeled image ("{image_label}") for model type "{model_type}"; path - {path}'.format(
                image_label=self.image_label,
                model_type=self.model_type,
                path=self.image.path,
            )
        else:
            return 'Unlabeled image for model type "{model_type}"; path - {path}'.format(
                model_type=self.model_type,
                path=self.image.path,
            )

    def image_tag(self) -> str:
        return format_html('<img style="max-width: 100px; max-height: 100px" src="{0}"/>', self.image.url)
    image_tag.short_description = 'Image'  # type: ignore
