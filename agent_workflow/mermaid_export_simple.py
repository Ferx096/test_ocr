# Script completamente independiente para exportar Mermaid
mermaid_code = '''graph TD
    company_info["Company Info"]
    balance_sheet["Balance Sheet"]
    final["Final"]
    end["End"]
    company_info --> balance_sheet
    balance_sheet --> final
    final --> end
'''
with open("workflow_graph.mmd", "w", encoding="utf-8") as f:
    f.write(mermaid_code)
print("Archivo workflow_graph.mmd generado.")
