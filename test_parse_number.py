from c_tools import parse_number, fallback_parse_balance_totals, extract_account_values_from_text

def test_parse_number():
    casos = [
        ("1.234.567", 1234567),
        ("1,234,567", 1234567),
        ("1.234.567,89", 1234567.89),
        ("1,234,567.89", 1234567.89),
        ("1234567", 1234567),
        ("(1.234.567)", -1234567),
        ("-1.234.567", -1234567),
        ("+1.234.567", 1234567),
        ("1 234 567", 1234567),
        ("1.234.567,00", 1234567.0),
        ("(1.234.567,89)", -1234567.89),
        ("1.234.567-", 1234567),
        ("1'234'567", 1234567),
        ("1'234'567.89", 1234567.89),
        ("1'234'567,89", 1234567.89),
        ("1,234,567", 1234567),
        ("1,234,567.00", 1234567),
        ("1,234,567,00", 123456700),
        ("1.234.567.000", 1234567000),
        ("1.234.567,8", 1234567.8),
        ("1.234.567,8", 1234567.8),
        ("1.234.567,", 1234567),
        (".123", 0.123),
        (",123", 0.123),
        ("abc", None),
        ("", None),
    ]
    for s, esperado in casos:
        r = parse_number(s)
        print(f"parse_number('{s}') = {r} (esperado: {esperado})")

def test_fallback_parse_balance_totals():
    texto = '''\
TOTAL ACTIVOS 1.234.567,89\nTotal Pasivos: 2.345.678\nTotal Patrimonio 3.456.789\n'''
    res = fallback_parse_balance_totals(texto)
    print("fallback_parse_balance_totals:", res)

def test_extract_account_values_from_text():
    texto = '''\
Efectivo y equivalentes de efectivo: 1.000.000\nCuentas por cobrar: 2.000.000\nTotal activos: 3.000.000\n'''
    cuentas = {"efectivo_equivalentes_efectivo": None, "cuentas_por_cobrar": None, "total_activos": None}
    res = extract_account_values_from_text(texto, cuentas)
    print("extract_account_values_from_text:", res)

if __name__ == "__main__":
    test_parse_number()
    test_fallback_parse_balance_totals()
    test_extract_account_values_from_text()
