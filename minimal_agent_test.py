from c_tools import agent_company_info

query = "Extrae el nombre, RUT y fecha de reporte de la empresa."
response = agent_company_info.invoke(query)
print(f"DEBUG: type={type(response)} value={response}")
if isinstance(response, list):
    for i, item in enumerate(response):
        print(f"  item[{i}]: type={type(item)} value={item}")
    if response and isinstance(response[0], dict) and 'content' in response[0]:
        print(f"  content: {response[0]['content']}")
elif hasattr(response, 'content'):
    print(f"  content: {response.content}")
