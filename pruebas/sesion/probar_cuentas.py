#!/usr/bin/env python3
"""Quién escribe: la misma función en los cuatro sitios, y los casos que no pueden convertir a nadie en dueño.

Uso: python3 pruebas/sesion/probar_cuentas.py
"""
import pathlib, re, sys
AQUI = pathlib.Path(__file__).resolve().parent
PL = AQUI.parent.parent / "plugins" / "memoria"
sitios = [PL / "skills/sesion/abrir.py", PL / "skills/sesion/permisos.py", PL / "skills/sesion/cerrar.py", PL / "skills/tablero/aplicar_cambios.py", PL / "skills/tablero/generar_vista.py", PL / "verificar.sh"]
fallos = 0
def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t); fallos += 0 if c else 1
def bloque(p):
    t = p.read_text(encoding="utf-8")
    a = t.index("# --- quién escribe"); b = t.index("# --- fin de quién escribe ---")
    return t[a:b]
print("Quién escribe")
bs = [bloque(p) for p in sitios]
ok(all(b == bs[0] for b in bs), "la función es idéntica en abrir.py, permisos.py, cerrar.py, aplicar_cambios.py, generar_vista.py y verificar.sh")
ns = {"re": re}; exec(bs[0], ns); cuentas, colaboran_en = ns["cuentas"], ns["colaboran_en"]
ok(cuentas("ana@x.com")[:2] == ({"ana@x.com"}, set()) and cuentas("ana@x.com")[2] is None, "una sola cuenta sigue siendo la del dueño, sin aviso")
ok(cuentas("Ana@X.com · colabora: b@x.com, c+1@sub.x.com")[:2] == ({"ana@x.com"}, {"b@x.com", "c+1@sub.x.com"}), "dueño y colaboradores, sin mayúsculas, con «+» y subdominios")
for v in ("colaboradora:", "colaborador:", "colabora", "colaboran:", "Colaboración:", "co-labora:"):
    de, co, av = cuentas(f"ana@x.com · {v} carla@x.com")
    ok(de == {"ana@x.com"} and co == {"carla@x.com"} and (v == "colaboran:" or av), f"«{v}» no convierte a quien colabora en dueño" + ("" if v == "colaboran:" else ", y avisa"))
de, co, av = cuentas("ana@x.com y luis@x.com")
ok(de == set() and av, "dos correos sin «colabora:»: nadie es dueño, y avisa")
ok(cuentas("ana@")[0] == set(), "una cuenta incompleta no es la de nadie")
ok(cuentas("o'brien@x.com")[0] == {"o'brien@x.com"} and cuentas("ana@empresa")[0] == {"ana@empresa"}, "correos con apóstrofo y dominios sin punto")
q = "Dueño: Ana\nColabora: Dani (dani@x.com)\n- **Colabora:** Eva (eva@x.com)\nColabora : Fer (fer@x.com)\nConsumen esto: Luis (luis@x.com)"
ok(colaboran_en(q) == {"dani@x.com", "eva@x.com", "fer@x.com"}, "todas las líneas «Colabora:», con viñeta, negrita o espacio; «Consumen esto» no da permiso")
met = (PL / "metodo.md").read_text(encoding="utf-8")
ok(not re.search(r"^#{3,} 20\d\d-", met, re.M), "metodo.md: los ejemplos de registro conservan su «## AAAA-MM-DD» dentro de los bloques de código")
print("\n" + ("Todo bien." if not fallos else f"{fallos} fallo(s)."))
sys.exit(1 if fallos else 0)
