# -*- coding: utf-8 -*-
import pytest


@pytest.fixture
def foo():
    return True


def test_feature(foo):
    assert foo
