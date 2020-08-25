import numpy as np
from hamcrest import assert_that, calling, equal_to, has_properties, is_, raises  # type: ignore

from moonvision.image_classification import services


class DummyBaseImageClassificationService(services.BaseImageClassificationService):
    """Service subclass for tests to avoid pytorch/tensorflow specific implementations."""

    models = {
        'DefaultShape': 'default_shape',
        'CustomShape': ('custom_shape', 333),
    }

    def get_model(self):
        return None

    def load_image(self, image_path: str):
        return None

    def get_prediction_scores(self, model, image):
        return np.array([0.1, 0.15, 0.05, 0.5, 0.04, 0.01, 0.03, 0.04, 0.04, 0.04] + [0] * 991)  # noqa: WPS435


class TestImageClassificationService:
    # Initialisation tests
    def test_initialises_instance_with_default_shape_model(self):
        instance = DummyBaseImageClassificationService('DefaultShape')

        assert_that(instance, has_properties(
            model_reference='default_shape',
            image_shape=224,
        ))

    def test_initialises_instance_with_custom_shape_model(self):
        instance = DummyBaseImageClassificationService('CustomShape')

        assert_that(instance, has_properties(
            model_reference='custom_shape',
            image_shape=333,
        ))

    def test_raises_value_error_on_wrong_model(self):
        assert_that(calling(DummyBaseImageClassificationService).with_args('WrongModel'), raises(ValueError))

    # Test for main method
    def test_returns_highest_score_label(self):
        service_instance = DummyBaseImageClassificationService('DefaultShape')

        prediction = service_instance.classify_image('/path/to/image.jpg')

        assert_that(prediction, is_(equal_to('great white shark')))
