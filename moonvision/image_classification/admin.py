from django.contrib import admin

from moonvision.image_classification import models


@admin.register(models.UploadedImage)
class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'image_tag', 'image_label')
    list_display_links = ('__str__',)
