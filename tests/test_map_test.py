import pytest
import json

def test_map_test_md_exists():
    with open("map/map_test.md", "r", encoding="utf-8") as f:
        content = f.read()
    assert "Balance general" in content

def test_map_test_json():
    with open("map/map_test.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "Balance general" in data
