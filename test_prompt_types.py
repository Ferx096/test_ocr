from langchain_core.prompts import ChatPromptTemplate
from c_tools import agent_company_info, agent_balance_sheet, agent_income_statement

def test_agent_prompts_are_chatprompttemplate():
    # Acceso directo a los prompts de los agentes
    assert isinstance(agent_company_info.prompt, ChatPromptTemplate), "agent_company_info.prompt no es ChatPromptTemplate"
    assert isinstance(agent_balance_sheet.prompt, ChatPromptTemplate), "agent_balance_sheet.prompt no es ChatPromptTemplate"
    assert isinstance(agent_income_statement.prompt, ChatPromptTemplate), "agent_income_statement.prompt no es ChatPromptTemplate"
