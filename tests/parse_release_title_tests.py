import pytest
from progtool.cli.setup import parse_release_title


@pytest.mark.parametrize('title, expected', [
    (f'v{major}.{minor}.{patch}', (major, minor, patch))
    for major in [0, 1, 4, 19]
    for minor in [0, 1, 6, 15]
    for patch in [0, 1, 8, 23]
])
def test_parse_release_title(title, expected):
    actual = parse_release_title(title)
    assert expected == actual