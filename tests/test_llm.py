import pytest

from music_to_text.llm import _json_object_candidates, _parse_json_content


def test_parse_json_content_accepts_raw_json() -> None:
    assert _parse_json_content('{"ok": true}') == {"ok": True}


def test_parse_json_content_accepts_fenced_json() -> None:
    content = '```json\n{"ok": true}\n```'

    assert _parse_json_content(content) == {"ok": True}


def test_parse_json_content_accepts_json_inside_text() -> None:
    content = 'Here is the object:\n{"ok": true}\nThanks.'

    assert _parse_json_content(content) == {"ok": True}


def test_parse_json_content_prefers_last_valid_json_object() -> None:
    content = '<think>Example: {ok: true}</think>\nFinal answer:\n{"ok": true}'

    assert _parse_json_content(content) == {"ok": True}


def test_json_object_candidates_respects_strings() -> None:
    content = 'before {"text": "brace } inside string"} after {"ok": true}'

    assert _json_object_candidates(content) == ['{"text": "brace } inside string"}', '{"ok": true}']


def test_parse_json_content_requires_object() -> None:
    with pytest.raises(ValueError):
        _parse_json_content("[1, 2, 3]")
