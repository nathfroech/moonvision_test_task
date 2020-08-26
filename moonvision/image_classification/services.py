import logging
from typing import Any, Dict, List, Tuple, Union

import numpy as np
import torch
from PIL import Image
from torchvision import models, transforms

from django.conf import settings

logger = logging.getLogger('debug')

DEFAULT_IMAGE_SHAPE = 224
PREDICTIONS_TO_LOG = 10  # Log this number of predictions for debugging purposes

ModelsDict = Dict[str, Union[str, Tuple[str, int]]]


class BaseImageClassificationService:
    models: ModelsDict = {}

    def __init__(self, model_name: str) -> None:
        try:
            model_data = self.models[model_name]
        except KeyError:
            raise ValueError('Name {0} is not in the list of supported models'.format(model_name))
        if isinstance(model_data, str):
            self.model_reference = model_data
            self.image_shape = DEFAULT_IMAGE_SHAPE
        else:
            self.model_reference, self.image_shape = model_data  # noqa: WPS414

    def get_model(self) -> Any:
        raise NotImplementedError('Method should be implemented in subclasses')

    def load_image(self, image_path: str) -> Any:
        raise NotImplementedError('Method should be implemented in subclasses')

    def get_prediction_scores(self, model: Any, image: Any) -> np.array:
        raise NotImplementedError('Method should be implemented in subclasses')

    def get_labels(self) -> np.array:
        # I am using only models, trained on ImageNet dataset. So, it's fine to hardcode the labels.
        labels_file = settings.APPS_DIR / 'image_classification' / 'imagenet_labels.txt'
        return np.array(labels_file.read_text().strip().splitlines())

    def classify_image(self, image_path: str) -> str:
        model = self.get_model()
        img_array = self.load_image(image_path)
        scores = self.get_prediction_scores(model, img_array)

        highest_scores_indices = np.argsort(scores)[::-1][:PREDICTIONS_TO_LOG]

        imagenet_labels = self.get_labels()
        logger.debug(
            'Classes with the highest scores:\n    %s',
            ',\n    '.join(
                '{0} ({1})'.format(imagenet_labels[index], scores[index]) for index in highest_scores_indices
            ),
        )
        return imagenet_labels[highest_scores_indices[0]]

    @classmethod
    def get_model_choices(cls) -> List[Tuple[str, str]]:
        return [(model, model) for model in cls.models]


class ImageClassificationServiceTorch(BaseImageClassificationService):
    models = {
        'AlexNet': 'alexnet',
        'ResNet': 'resnet101',
        'DenseNet': 'densenet121',
        'GoogleNet': 'googlenet',
        'Inception3': ('inception_v3', 299),
        'MobileNetV2': 'mobilenet_v2',
    }

    def get_model(self) -> torch.nn.Module:
        return getattr(models, self.model_reference)(pretrained=True)

    def load_image(self, image_path: str) -> torch.Tensor:
        transform = transforms.Compose([
            transforms.Resize(self.image_shape + 32),  # noqa: WPS432 # Keep some space before cropping
            transforms.CenterCrop(self.image_shape),
            transforms.ToTensor(),
            # Values are taken from PyTorch model documentations. Should be the same for all models that are used here.
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ])

        image = Image.open(image_path)
        transformed_image = transform(image)
        return torch.unsqueeze(transformed_image, 0)  # type: ignore # pylint: disable=no-member

    def get_prediction_scores(self, model, image):
        model.eval()
        predictions = model(image)
        return torch.nn.functional.softmax(predictions, dim=1)[0].detach().numpy()


ImageClassificationService = ImageClassificationServiceTorch
