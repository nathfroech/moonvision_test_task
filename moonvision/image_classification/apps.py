from django.apps import AppConfig as BaseAppConfig


class AppConfig(BaseAppConfig):
    name = 'moonvision.image_classification'
    verbose_name = 'Image Classification'
