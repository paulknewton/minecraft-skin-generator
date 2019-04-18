import pytest
import photo2skin
from PIL import Image, ImageChops


def test_it():
    assert 4 == 4


def test_missing_file():
    with pytest.raises(FileNotFoundError) as e:
        photo2skin.build_skin("this_file_does_not_exist.jpg", 0, 0)


def test_existing_file():
    photo2skin.build_skin("test.jpg", 0, 0)
    assert True


def test_skin():
    new_skin = photo2skin.build_skin("test.jpg", 6, 5)
    test_skin = Image.open("test-skin.png")

    assert ImageChops.difference(new_skin, test_skin).getbbox() is None


def test_thumbnail():
    new_thumb = photo2skin.build_thumbnail(photo2skin.build_skin("test.jpg", 6, 5), 6, 5)
    test_thumb = Image.open("test-thumb.png")

    assert ImageChops.difference(new_thumb, test_thumb).getbbox() is None
