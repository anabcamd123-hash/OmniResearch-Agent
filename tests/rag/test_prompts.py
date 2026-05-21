import pytest
from backend.prompts.loader import load_prompt


def test_load_planner_prompt():

    prompt = load_prompt("planner")
    assert "workflow planner" in prompt
    assert "{task}" in prompt


def test_load_research_prompt():

    prompt = load_prompt("research")
    assert "Summarize" in prompt
    assert "{task}" in prompt


def test_load_coding_prompt():

    prompt = load_prompt("coding")
    assert "Python code" in prompt


def test_load_verify_prompt():

    prompt = load_prompt("verify")
    assert "Score" in prompt


def test_load_reflection_prompt():

    prompt = load_prompt("reflection")
    assert "reflection system" in prompt


def test_load_nonexistent_prompt():

    with pytest.raises(FileNotFoundError):
        load_prompt("nonexistent")
