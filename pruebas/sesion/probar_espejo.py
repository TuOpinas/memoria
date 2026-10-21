#!/usr/bin/env python3
"""Prueba espejo.py y el modo sin consola de abrir.py y del generador del tablero contra la raíz inventada.

Uso: python3 pruebas/sesion/probar_espejo.py
Simula device_stage_files copiando de la raíz a una copia lo que espejo.py pide, ronda a ronda; comprueba que abrir.py
--sin-fechas sobre la copia dice lo mismo que abrir.py sobre la raíz (salvo las fechas de archivo), que el inventario del
tablero sin fechas no cambia por tocar fechas y sí por tocar contenido, y que devolver solo saca lo que cambió.
"""
import json, os, pathlib, re, shutil, subprocess, sys, tempfile, time

AQUI = pathlib.Path(__file__).resolve().parent
PLUGIN = AQUI.parent.parent / "plugins" / "memoria"
ESPEJO, ABRIR = PLUGIN / "espejo.py", PLUGIN / "skills" / "sesion" / "abrir.py"
GEN = PLUGIN / "skills" / "tablero" / "generar_vista.py"
tmp = pathlib.Path(tempfile.mkdtemp())
R, C = tmp / "raiz", tmp / "uploads" / "Raiz Prueba"
shutil.copytree(AQUI.parent / "tablero" / "raiz", R)
viejo = time.mktime((2026, 8, 1, 12, 0, 0, 0, 0, -1))
for d, _, fs in os.walk(R):
    for f in fs:
        os.utime(os.path.join(d, f), (viejo, viejo))
fallos = 0


def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t)
    fallos += 0 if c else 1


def corre(*a):
    r = subprocess.run([sys.executable, *map(str, a)], capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


print("Sin consola: la copia de la raíz (espejo.py)")
ACTIVO = "ventas/cuentas"
rondas, pedidas = 0, []
while rondas < 6:
    rc, out, err = corre(ESPEJO, "rutas", C, ACTIVO)
    if rc != 0 or out.strip() == "COMPLETA":
        break
    rondas += 1
    for r in out.split():
        pedidas.append(r)
        if (R / r).is_file():   # lo que no existe no llega, como con device_stage_files
            (C / r).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(R / r, C / r)
ok(out.strip() == "COMPLETA" and rondas == 3, f"tres rondas y COMPLETA (rondas: {rondas})")
ok(not any(re.search(r"(^|/)(fuentes|taller|restringido)/", r) for r in pedidas), "no pide nada de fuentes/, taller/ ni restringido/")
ok("ventas/cuentas/decisiones.md" in pedidas and "ventas/area.md" in pedidas, "pide area.md y los registros de los proyectos")
ok(not any(r.startswith("ventas/oculto/") for r in pedidas), "no pide un proyecto que no está en el índice de su área")
# las cabeceras de entregables del proyecto activo se traen desde su listado
for f in (R / ACTIVO / "entregables").iterdir():
    (C / ACTIVO / "entregables").mkdir(parents=True, exist_ok=True)
    shutil.copy(f, C / ACTIVO / "entregables" / f.name)

print("Sin consola: abrir.py sobre la copia")
_, a_raiz, _ = corre(ABRIR, R, ACTIVO, "--cuenta", "ana@ejemplo.com")
rc, a_copia, err = corre(ABRIR, C, ACTIVO, "--cuenta", "ana@ejemplo.com", "--sin-fechas")
ok(rc == 0, "abrir.py --sin-fechas corre sobre la copia" + (f": {err[-300:]}" if rc else ""))


def sin_lo_de_fechas(t):
    t = re.sub(r"=== REGISTROS.*?(?====)", "", t, flags=re.S)
    return [l for l in t.split("\n") if "Trabajo sin sesión" not in l and "fecha de archivo" not in l]


ok(sin_lo_de_fechas(a_raiz) == sin_lo_de_fechas(a_copia), "dice lo mismo que en la computadora, salvo las fechas de archivo")
ok("mtimeMs mayor o igual que" in a_copia, "da el instante desde el que mirar el trabajo sin sesión en el listado")
ok("bytes (sin consola" in a_copia and not re.search(r"proyecto\.md: 20\d\d-", a_copia), "REGISTROS sin la hora de la copia")

print("Sin consola: el inventario del tablero sin fechas")
T = tmp / "tablero"
shutil.copytree(R, T, ignore=shutil.ignore_patterns())
inv = lambda: json.loads(corre(GEN, T, "--inventario", "--modo", "publico", "--sin-fechas")[1])["inventario"]
i1 = inv()
for d, _, fs in os.walk(T):
    for f in fs:
        os.utime(os.path.join(d, f), None)   # como una copia nueva: todas las fechas, de ahora
i2 = inv()
ok(i1["huella_raiz"] == i2["huella_raiz"] and i1["huellas"] == i2["huellas"], "las fechas de la copia no cambian las huellas")
ok(not i2.get("sin_sesion"), "sin fechas no hay trabajo sin sesión inventado")
p = T / ACTIVO / "proyecto.md"
p.write_text(p.read_text(encoding="utf-8").replace("a", "e", 1), encoding="utf-8")   # mismo tamaño, otro contenido
i3 = inv()
ok(i3["huella_raiz"] != i2["huella_raiz"] and i3["huellas"].get("ventas--cuentas") != i2["huellas"].get("ventas--cuentas"),
   "un cambio de contenido del mismo tamaño sí cambia la huella")

print("Sin consola: el tablero entero sobre la copia")
# la copia que arma la puesta al día sin consola, desde el listado: los .md fuera de fuentes/, taller/, restringido/ y base/
# (salvo base/premisas.md) y todo entregables/; con fechas de ahora, como las deja device_stage_files
TC = tmp / "copia-tablero"
for d, ds, fs in os.walk(R):
    for f in fs:
        r = (pathlib.Path(d) / f).relative_to(R).as_posix()
        partes = r.split("/")
        if set(partes[:-1]) & {"fuentes", "taller", "restringido"} or (partes[0] == "base" and r != "base/premisas.md"):
            continue
        if f.endswith(".md") or "entregables" in partes[:-1]:
            (TC / r).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(R / r, TC / r)


def docs(carpeta):
    out = {}
    for q in sorted(pathlib.Path(carpeta).rglob("*.json")):
        if q.name in ("indice.json", "enfoque-candidatos.json"):
            continue
        d = json.loads(q.read_text(encoding="utf-8"))
        for k in ("sincronizado", "generado", "huella_raiz", "huellas", "huella"):
            d.pop(k, None)
        out[q.relative_to(carpeta).as_posix()] = d
    return out


for modo in ("publico", "completo"):
    rc, out, err = corre(GEN, TC, "--inventario", "--modo", modo, "--sin-fechas")
    sal = json.loads(out) if rc == 0 else {"leer": [], "inventario": {}}
    ok(rc == 0, f"{modo}: el inventario corre sobre la copia" + (f": {err[-300:]}" if rc else ""))
    sub = tmp / f"sub-{modo}"
    for r in sal["leer"]:
        (sub / r).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(TC / r, sub / r)
    (tmp / f"inv-{modo}.json").write_text(json.dumps(sal["inventario"], ensure_ascii=False), encoding="utf-8")
    rc, _, err = corre(GEN, sub, tmp / f"out-{modo}", "--desde-inventario", tmp / f"inv-{modo}.json", "--modo", modo, "--version", "prueba", "--sin-fechas")
    ok(rc == 0, f"{modo}: genera desde ese inventario" + (f": {err[-300:]}" if rc else ""))
    rc, _, err = corre(GEN, R, tmp / f"directo-{modo}", "--modo", modo, "--version", "prueba", "--sin-fechas")
    a_, b_ = docs(tmp / f"out-{modo}"), docs(tmp / f"directo-{modo}")
    ok(a_ == b_ and len(a_) > 3, f"{modo}: sale lo mismo que sobre la raíz ({len(a_)} documentos)")

print("Sin consola: devolver lo que cambió")
corre(ESPEJO, "instantanea", C)
rc, out, _ = corre(ESPEJO, "devolver", C, "C:\\Users\\Ana\\Drive\\Unidades compartidas\\Raiz", tmp / "salidas")
ok(rc == 0 and json.loads(out) == [], "sin cambios no devuelve nada")
(C / ACTIVO / "sesiones.md").write_text((C / ACTIVO / "sesiones.md").read_text(encoding="utf-8") + "\nx\n", encoding="utf-8")
(C / ACTIVO / "taller").mkdir(parents=True, exist_ok=True)
(C / ACTIVO / "taller" / "nota.md").write_text("nueva\n", encoding="utf-8")
rc, out, _ = corre(ESPEJO, "devolver", C, "C:\\Users\\Ana\\Drive\\Unidades compartidas\\Raiz", tmp / "salidas")
d = json.loads(out) if rc == 0 else []
rels = sorted(x["rel"] for x in d)
ok(rels == [f"{ACTIVO}/sesiones.md", f"{ACTIVO}/taller/nota.md"], f"devuelve lo editado y lo nuevo ({rels})")
ok(all(x["devicePath"].startswith("C:\\Users\\Ana\\Drive\\Unidades compartidas\\Raiz\\ventas\\cuentas\\") for x in d),
   "la ruta en la computadora con el separador de la raíz (Windows)")
ok(all(pathlib.Path(x["stagedPath"]).is_file() for x in d) and [x["nuevo"] for x in sorted(d, key=lambda x: x["rel"])] == [False, True],
   "cada archivo en una carpeta de salidas nueva, y marca cuál es nuevo")
corre(ESPEJO, "instantanea", C)
rc, out, _ = corre(ESPEJO, "devolver", C, "/Users/ana/Raiz", tmp / "salidas")
ok(json.loads(out) == [], "tras la instantánea, nada pendiente")

print()
print("Todo bien." if not fallos else f"{fallos} fallos.")
shutil.rmtree(tmp, ignore_errors=True)
sys.exit(1 if fallos else 0)
