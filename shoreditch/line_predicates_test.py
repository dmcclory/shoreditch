import pytest

from .line_predicates import parse_title_line


@pytest.mark.parametrize('line, expected', [
    ('Cool Title', 'Cool Title'),
    ('Cool Title 2', 'Cool Title 2'),
])
def test_returns_title_if_that_is_all_there_is(line, expected):
    title, annotation = parse_title_line(line)
    assert(title == expected)

@pytest.mark.parametrize('line, expected_title, expected_annotation', [
    ('Cool Title', 'Cool Title', {}),
    ('Cool Title (type: movie)', 'Cool Title', {'type': 'movie'}),
])
def test_returns_title_and_annotion_dict(line, expected_title, expected_annotation):
    title, annotation = parse_title_line(line)
    assert(title == expected_title)
    assert(annotation == expected_annotation)

@pytest.mark.parametrize('line, expected_title, expected_annotation', [
    ('Cool Title (s2)', 'Cool Title (s2)', {'season': '2', 'type': 'tv_show'}),
    ('Cool Title (vol.2)', 'Cool Title (vol.2)', {'volume': '2'}),
])
def test_seasons_and_volumes_extract_but_are_preserved(line, expected_title, expected_annotation):
    title, annotation = parse_title_line(line)
    assert(title == expected_title)
    assert(annotation == expected_annotation)
