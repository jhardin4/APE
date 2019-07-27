# -*- coding: utf-8 -*-
import pytest

from GUI.main.ape.base.helpers import value_to_str, str_to_value


@pytest.mark.parametrize(
    'data, expected',
    [
        ({'foo': 'bar'}, '{"foo": "bar"}'),
        ([1, 2, 3], "[1, 2, 3]"),
        ("apology", "apology"),
        (12.4, "12.4"),
        (object(), "<class 'object'>"),
    ],
)
def test_converting_value_to_string_works(data, expected):
    assert value_to_str(data) == expected


@pytest.mark.parametrize(
    'data, old_data, expected',
    [
        ('{"foo":"bar"}', '', {'foo': 'bar'}),
        ('[1, 3]', '', [1, 3]),
        ("2.3", 1, 2.3),
        ("True", False, True),
        ("{'asd'}", "", "{'asd'}"),
    ],
)
def test_converting_string_to_value_works(data, old_data, expected):
    assert str_to_value(data, old_value=old_data) == expected
