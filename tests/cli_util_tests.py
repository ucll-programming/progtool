from progtool.cli.util import *
import pytest


@pytest.mark.parametrize("string", [
    "0-abc",
    "1-xyz",
    "01-tralala",
    "99-test",
    "192-x",
    "41",
])
def test_is_indexed(string):
    assert is_indexed(string)


@pytest.mark.parametrize("string", [
    "abc",
    "1xyz",
    "14-",
])
def test_is_not_indexed(string):
    assert not is_indexed(string)


@pytest.mark.parametrize("string, expected", [
    ("1-abc", "abc"),
    ("0", ""),
    ("491-xyz", "xyz"),
])
def test_remove_number(string, expected):
    actual = remove_index(string)
    assert actual == expected


@pytest.mark.parametrize("string, expected_number, expected_name", [
    ("1-abc", 1, "abc"),
    ("0", 0, ""),
    ("491-xyz", 491, "xyz"),
])
def test_extract_number_and_name(string, expected_number, expected_name):
    actual_number, actual_name = extract_index_and_name(string)
    assert actual_number == expected_number
    assert actual_name == expected_name


@pytest.mark.parametrize("string, number, expected", [
    ('', 0, '00'),
    ('', 10, '10'),
    ('x', 1, '01-x'),
    ('abc', 8, '08-abc'),
    ('abc', 73, '73-abc'),
])
def test_add_number(string, number, expected):
    actual = add_index(string, number)
    assert actual == expected


@pytest.mark.parametrize("strings, expected", [
    (
        ["01-a"],
        {"01-a": "01-a"},
    ),
    (
        ["02-a"],
        {"02-a": "01-a"},
    ),
    (
        ["01-a", "02-b"],
        {"01-a": "01-a", "02-b": "02-b"},
    ),
    (
        ["02-a", "01-b"],
        {"02-a": "02-a", "01-b": "01-b"},
    ),
    (
        ["05-a", "04-b"],
        {"05-a": "02-a", "04-b": "01-b"},
    ),
])
def test_create_renumbering_mapping(strings, expected):
    actual = create_reindexing_mapping(strings)
    assert actual == expected
