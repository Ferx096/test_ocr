from e_agents import app
# ======================================
# TEST
# ======================================

def main():
    test = {}
    query = app.invoke(test)
    excel_bytes = query.get("excel_bytes")
    if excel_bytes:
        with open("resultado.xlsx", "wb") as f:
            f.write(excel_bytes)
        print("Archivo Excel guardado como resultado.xlsx")
    else:
        print("No se recibió archivo Excel.")

if __name__ == "__main__":
    main()