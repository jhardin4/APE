import pytest

from GUI.main.ape.apparatus.app_image_data import AppImageData, AppImageDataWalker


def test_setting_app_image_key_creates_keys():
    data = AppImageData(name='root')

    data.set_key('foo/bar', 353)

    first = data.get('foo')
    assert first is not None
    assert first.parent is data
    second = first.get('bar')
    assert second is not None
    assert second.value == 353
    assert second.parent is first


@pytest.fixture
def simple_app_image():
    data = AppImageData(name='root')
    data["drink"] = AppImageData(name='drink', value=105, parent=data)
    child = data["promise"] = AppImageData(name='promise', parent=data)
    child["industry"] = AppImageData(name='industry', value=976, parent=child)
    return data


def test_getting_app_image_key_returns_child_value(simple_app_image):
    result = simple_app_image.get_key('promise/industry')

    assert result.name == 'industry'
    assert result.value == 976


def test_key_returns_full_app_image_key(simple_app_image):
    child = simple_app_image['promise']['industry']

    assert child.key == 'promise/industry'


def test_app_image_data_walker_walks_over_item_tree_bfs(simple_app_image):
    data = AppImageData.from_dict(simple_app_image, 'root')

    unfolded = [image.name for image in AppImageDataWalker(data)]

    assert unfolded == ['root', 'drink', 'promise', 'industry']


def test_app_image_data_walker_walks_over_item_tree_dfs(simple_app_image):
    data = AppImageData.from_dict(simple_app_image, 'root')

    unfolded = [image.name for image in AppImageDataWalker(data, dfs=True)]

    assert unfolded == ['drink', 'industry', 'promise', 'root']
