import pytest
import photo2skin


def test_it():
    assert 4 == 4


def test_missing_file():
    with pytest.raises(FileNotFoundError) as e:
        photo2skin.main("this_file_does_not_exist.jpg", 0, 0)


def test_existing_file():
    photo2skin.main("test.jpg", 0, 0)
    assert True