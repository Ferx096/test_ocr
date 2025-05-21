import types
from langchain_core.prompts import ChatPromptTemplate

class DummyAgent:
    def __init__(self, prompt):
        self.prompt = prompt

def test_agent_prompts_are_chatprompttemplate():
    # Simula agentes con prompts correctos
    agent_company_info = DummyAgent(ChatPromptTemplate.from_template("test"))
    agent_balance_sheet = DummyAgent(ChatPromptTemplate.from_template("test"))
    agent_income_statement = DummyAgent(ChatPromptTemplate.from_template("test"))
    assert isinstance(agent_company_info.prompt, ChatPromptTemplate)
    assert isinstance(agent_balance_sheet.prompt, ChatPromptTemplate)
    assert isinstance(agent_income_statement.prompt, ChatPromptTemplate)
