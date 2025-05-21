# test_ocr

## Convención de prompts y agentes (LangChain)

**Todos los prompts utilizados en agentes y cadenas de LangChain deben ser instancias de `ChatPromptTemplate` (no strings).**

- Los prompts se definen como strings en `b_prompts.py`.
- En `c_tools.py`, los strings se convierten explícitamente a `ChatPromptTemplate` antes de ser usados en la creación de agentes o cadenas.
- Los agentes y herramientas en `d_agents.py` deben importar los agentes ya construidos desde `c_tools.py`, asegurando el tipado correcto.
- Está prohibido pasar strings como prompt directamente a agentes/cadenas.

### Ejemplo correcto
```python
from langchain_core.prompts import ChatPromptTemplate
prompt = ChatPromptTemplate.from_template(prompt_string)
agent = create_react_agent(llm, tools=[...], prompt=prompt)
```

### Ejemplo incorrecto
```python
agent = create_react_agent(llm, tools=[...], prompt=prompt_string)  # ❌
```

### Test automático sugerido
Existe un test sugerido (ver `test_prompt_types.py`) que verifica que los prompts de los agentes principales sean instancias de `ChatPromptTemplate`.

---
