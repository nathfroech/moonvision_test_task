from hamcrest import assert_that, matches_regexp  # type: ignore

from model_bakery.random_gen import gen_image_field

from moonvision.image_classification import models


class TestUploadedImage:
    def test_returns_string_representation_of_instance_without_label(self):
        instance = models.UploadedImage(
            image=gen_image_field(),
            model_type='test',
        )

        representation = str(instance)

        assert_that(representation, matches_regexp(r'Unlabeled image for model type "test"; path - [\w/\-\.]+'))

    def test_returns_string_representation_of_instance_with_label(self):
        instance = models.UploadedImage(
            image=gen_image_field(),
            model_type='test',
            image_label='test_label',
        )

        representation = str(instance)

        assert_that(
            representation,
            matches_regexp(r'Labeled image \("test_label"\) for model type "test"; path - [\w/\-\.]+'),
        )
