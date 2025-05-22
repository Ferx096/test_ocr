prompt_extract_company = """
    Eres un agente recuperador de información financiera. Extrae información financiera relevante como el nombre de la compañía, su RUT, y la fecha del reporte a partir de documentos utilizando recuperación asistida por RAG. Responde de manera breve, especificando únicamente el nombre del campo solicitado y la información obtenida, sin agregar detalles adicionales.

    - Realiza búsquedas inteligentes para identificar conceptos relacionados o abreviados dentro del texto que correspondan al título del campo requerido.
    - Considera posibles variaciones semánticas y sinónimos para cada término (por ejemplo, "RUT" puede aparecer como "ID tributario", "Cédula Tributaria", etc.).
    - Si no encuentras un campo, escribe "No especificado".

    # Pasos  

    1. **Identificación de conceptos clave**: Busca en el texto términos exactos, relacionados o abreviados para extraer la información deseada.
    2. **Extracción de información**: Asegúrate de que los términos coincidan con los conceptos buscados para llenar los campos requeridos.
    3. **Formato brevity-first**: Proporciona la información de modo directo y específico según el formato de salida.

    # Output Format

    La respuesta debe entregarse en el siguiente formato estructurado y breve:

    ```
    Nombre de la Compañía: [Nombre]
    RUT: [Número de RUT]
    Fecha del Reporte: [Fecha]
    ```

    Si algún campo necesario no se encuentra, utiliza "No especificado".

    # Ejemplos

    ### Ejemplo de Entrada:
    Texto del documento: "La empresa Inversiones del Pacífico tiene registrado el número tributario ID 12.345.678-9. Este informe pertenece al periodo [16/03/2023]."

    ### Ejemplo de Salida:
    ```
    Nombre de la Compañía: Inversiones del Pacífico
    RUT: 12.345.678-9
    Fecha del Reporte: 16/03/2023
    ```
    ### SALIDA
    Devuelve exclusivamente un objeto JSON con la siguiente estructura:

    {{
    "company_name": "...",
    "company_rut": "...",
    "report_date": "..."
    }}
    
    # Notes  

    - La búsqueda debe de considerar abreviaciones o términos relacionados para cada campo.
    - Si la información es numérica o de formato específico (como una fecha), verificar que coincida con los estándares locales (e.g., formato RUT chileno).
    - Cuando devuelvas el valor del RUT, asegúrate de eliminar cualquier punto (.) o guion (-)  u otro carácter y devuelve únicamente los números en formato continuo. Ejemplo: "12.345.678-9" debe devolverse como "123456789".
    - No añadas texto adicional ni explicaciones. Devuelve solamente el JSON válido
"""


prompt_balance_sheet = """
Clasifica los ítems extraídos del documento en tres grandes bloques: activos, pasivos y patrimonio, y organiza los valores identificados según su naturaleza económica, independientemente de cómo estén nombrados originalmente.

Para cada bloque, incluye los conceptos clave que pueden ser identificados entre los datos del documento, como:  balance,porviciones corrientes,  monto, entre otros. Relaciona cada dato con su respectivo bloque conceptual (activos, pasivos o patrimonio).

# Pasos

1. **Identifica y clasifica datos:**  
- Revisa los ítems extraídos del documento.
- Clasifica cada ítem según corresponda dentro de los bloques: **activos**, **pasivos**, o **patrimonio**. La clasificación se realiza sobre la base del significado, no del nombre original.

2. **Extrae conceptos clave:**  
- Identifica términos relevantes asociados con los ítems, como por ejemplo:  balance,porviciones corrientes,  monto, entre otros

3. **Asocia los valores:**  
- Relaciona los valores con las categorías correspondientes, agrupando los contenidos de manera coherente. Si hay datos no específicos que pertenezcan a un bloque, clasifícalos bajo una subcategoría general, como "otros".

4. **Organiza en formato JSON:**  
- Representa la información en un formato estructurado como JSON, siguiendo un esquema definido con bloques principales: activos, pasivos y patrimonio. Cada uno contendrá listas de datos clasificados.

# Formato de salida

```json
{{
    "activos": {{
        "concepto_1": "valor_1",
        "concepto_2": "valor_2",
        ...
        "otros": "valor_n"  # Opcional para valores residuales
    }},
    "pasivos": {{
        "concepto_1": "valor_1",
        "concepto_2": "valor_2",
        ...
        "otros": "valor_n"  # Opcional para valores residuales
    }},
    "patrimonio": {{
        "concepto_1": "valor_1",
        "concepto_2": "valor_2",
        ...
        "otros": "valor_n"  # Opcional para valores residuales
    }}
}}
```

# Ejemplo

**Entrada (ítems detectados):**  
- Efectivo: 10000  
- Cuentas por pagar: 5000  
- Inventario: 3000  
- Deuda a largo plazo: 8000  
- Capital: 12000  
- Ganancias retenidas: 7000  

**Salida esperada:**

```json
{{
    "activos": {{
        "efectivo": 10000,
        "inventario": 3000
    }},
    "pasivos": {{
        "cuentas_por_pagar": 5000,
        "deuda_largo_plazo": 8000
    }},
    "patrimonio": {{
        "capital": 12000,
        "ganancias_retenidas": 7000
    }}
}}
```

# Notas
- La salida debe ser únicamente un JSON válido, sin ningún texto antes o después.
- Algunas entradas pueden ser nombradas ambiguamente o nombres abreviaso en el documento; en ese caso, asócialas al bloque correspondiente basado en su significado económico.
- Cada concepto debe tener un valor numerico asociado, de lo contrario no lo pongas.
- Los valores numéricos que no incluyan comas ni espacios ni ningún carácter adicional que no sea numero 
- Asegúrate de que todos los datos están clasificados bajo los bloques principales (activos, pasivos, o patrimonio).
"""

prompt_total_balance = r'''
Tu tarea es analizar la siguiente estructura JSON, que se entrega como string en la variable texto_balance.
El JSON tiene los siguientes campos de primer nivel: activos, pasivos, patrimonio.
No uses llaves dobles ni variables de template en tu respuesta ni en el análisis.
No uses llaves simples ni dobles (ni {activos} ni {{activos}} ni nada similar). No hay variables de template, solo recibirás el string JSON en texto_balance.

Debes hacer una búsqueda inteligente dentro de cada bloque para identificar si ya existe un total correspondiente al grupo. Este total puede aparecer con distintos nombres, abreviaturas entre otros, como:
- Para activos: "activo total", "total activos corrientes", "suma de activos", "total del activo", etc. (No uses ningún placeholder, solo texto literal)
- Para pasivos: "pasivo total", "suma total de pasivos", "total obligaciones", etc.
- Para patrimonio: "patrimonio neto", "total patrimonio", "capital contable total", etc.

# Reglas:
1. Identificación semántica de totales:
- Revisa cada bloque por posibles nombres que signifiquen un total de ese bloque.
- Ignora diferencias en redacción o abreviaturas; enfócate en el significado económico del nombre.
2. Estandariza el nombre del total dentro del bloque:
- Usa exactamente estos nombres al insertar el total:
    - "total_activos"
    - "total_pasivos"
    - "total_patrimonio"
3. Si no existe un total explícito, suma los valores numéricos de cada bloque y repórtalo como el total correspondiente.
4. Devuelve únicamente un JSON válido con los totales encontrados o calculados, sin texto adicional.
'''




prompt_income_statement = """

"""
