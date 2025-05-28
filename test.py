from e_agents import app
# ======================================
# TEST
# ======================================
test = {}
def main():
    # Ejemplo de consulta
    query = app.invoke(test)
    excel_bytes = query.get("excel_bytes")
    return excel_bytes

if __name__ == "__main__":
    main()