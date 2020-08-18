from django.contrib import admin

from moonvision.image_classification import models


@admin.register(models.UploadedImage)
class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'image')
    list_display_links = ('id', '__str__')
