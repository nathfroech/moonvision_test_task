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
