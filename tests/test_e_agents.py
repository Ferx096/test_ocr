import pytest
from e_agents import get_agent, run_agent

def test_get_agent():
    agent = get_agent()
    assert agent is not None

def test_run_agent():
    agent = get_agent()
    result = run_agent(agent, "input de prueba")
    assert result is not None
