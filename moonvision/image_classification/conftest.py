import base64
from io import BytesIO

import pytest
from PIL import Image


@pytest.fixture()
def base64_image(tmp_path) -> bytes:
    image = Image.new('RGB', (25, 25))
    buffered = BytesIO()
    image.save(buffered, format='PNG')
    return base64.b64encode(buffered.getvalue())


@pytest.fixture()
def classifier_mock(mocker):
    mocked_image_classifier = mocker.patch('moonvision.image_classification.services.ImageClassificationService')
    mocked_image_classifier.return_value.classify_image.return_value = 'dummy_label'
    return mocked_image_classifier
