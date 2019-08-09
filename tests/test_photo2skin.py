import pytest
import photo2skin
from PIL import Image, ImageChops


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        photo2skin.build_skin("tests/this_file_does_not_exist.jpg", 0, 0)


def test_existing_file():
    photo2skin.build_skin("tests/test.jpg", 0, 0)
    assert True


def test_skin_creation():
    new_skin = photo2skin.build_skin("tests/test.jpg", 6, 5)
    test_skin = Image.open("tests/test-skin.png")

    assert ImageChops.difference(new_skin, test_skin).getbbox() is None


def test_thumbnail_creation():
    new_thumb = photo2skin.build_thumbnail(photo2skin.build_skin("tests/test.jpg", 6, 5), 6, 5)
    test_thumb = Image.open("tests/test-thumb.png")

    assert ImageChops.difference(new_thumb, test_thumb).getbbox() is None
