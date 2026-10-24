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
        if (R / r).is_file():
            (C / r).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(R / r, C / r)
        else:   # device_stage_files rechaza la llamada por un archivo que no existe: se apunta y se repite sin él
            corre(ESPEJO, "falta", C, r)
ok(out.strip() == "COMPLETA" and rondas == 3, f"tres rondas y COMPLETA (rondas: {rondas})")
ok(not any(re.search(r"(^|/)(fuentes|taller|restringido)/", r) for r in pedidas), "no pide nada de fuentes/, taller/ ni restringido/")
ok("ventas/cuentas/decisiones.md" in pedidas and "ventas/area.md" in pedidas, "pide area.md y los registros de los proyectos")
ok(not any(r.startswith("ventas/oculto/") for r in pedidas), "no pide un proyecto que no está en el índice de su área")
# en la misma conversación: abrir otro proyecto pide solo lo suyo; y lo del proyecto que se abre, si llegó hace rato, otra vez
_, out2, _ = corre(ESPEJO, "rutas", C, "operacion/soporte")
ok(sorted(out2.split()) == ["operacion/soporte/proyecto.md", "operacion/soporte/sesiones.md"], f"otro proyecto en la misma conversación pide solo lo suyo ({out2.split()})")
for r in ("guia.md", "ventas/area.md", "ventas/cuentas/proyecto.md", "ventas/cuentas/decisiones.md", "ventas/cuentas/sesiones.md", "operacion/soporte/decisiones.md"):
    os.utime(C / r, (time.time() - 3600, time.time() - 3600))
_, out3, _ = corre(ESPEJO, "rutas", C, ACTIVO)
ok(sorted(out3.split()) == sorted(["guia.md", "ventas/area.md", "ventas/cuentas/proyecto.md", "ventas/cuentas/decisiones.md", "ventas/cuentas/sesiones.md"]),
   f"lo del proyecto que se abre, traído hace más de diez minutos, se vuelve a pedir; lo demás no ({out3.split()})")
for r in out3.split():
    shutil.copy(R / r, C / r)
# las cabeceras de entregables del proyecto activo se traen desde su listado
for f in (R / ACTIVO / "entregables").iterdir():
    if not f.is_file():
        continue      # una subcarpeta de entregables no se trae sin consola (el tablero la cuenta, no la lista)
    (C / ACTIVO / "entregables").mkdir(parents=True, exist_ok=True)
    shutil.copy(f, C / ACTIVO / "entregables" / f.name)

# los permisos sin consola: el proyecto.md de cada proyecto del índice, y permisos.py sobre la copia ve lo mismo que sobre la raíz
PERM = PLUGIN / "skills" / "sesion" / "permisos.py"
rp, pedidas_p = 0, []
while rp < 4:
    rc, outp, _ = corre(ESPEJO, "permisos", C)
    if rc != 0 or outp.strip() == "COMPLETA":
        break
    rp += 1
    for r in outp.split():
        pedidas_p.append(r)
        if (R / r).is_file():
            (C / r).parent.mkdir(parents=True, exist_ok=True); shutil.copy(R / r, C / r)
        else:
            corre(ESPEJO, "falta", C, r)
ok(outp.strip() == "COMPLETA" and rp == 1 and "operacion/soporte/proyecto.md" in pedidas_p and "personas/bonos/proyecto.md" in pedidas_p, f"«permisos» pide el proyecto.md de cada proyecto del índice en una ronda ({rp})")
_, plan_r, _ = corre(PERM, R, "--plan"); _, plan_c, _ = corre(PERM, C, "--plan")
norm = lambda o: sorted(l for l in o.split("\n") if l.startswith("- ") and not l.startswith("- restringido "))   # las restringido/ se buscan en Drive
ok(norm(plan_r) == norm(plan_c) and "proyecto operacion/soporte/ (con «Colabora:»)" in plan_c, "permisos.py --plan sobre la copia ve los mismos proyectos que sobre la raíz")

print("Sin consola: abrir.py sobre la copia")
_, a_raiz, _ = corre(ABRIR, R, ACTIVO, "--cuenta", "ana@ejemplo.com")
rc, a_copia, err = corre(ABRIR, C, ACTIVO, "--cuenta", "ana@ejemplo.com", "--sin-fechas")
ok(rc == 0, "abrir.py --sin-fechas corre sobre la copia" + (f": {err[-300:]}" if rc else ""))


def sin_lo_de_fechas(t):
    t = re.sub(r"=== REGISTROS.*?(?====)", "", t, flags=re.S)
    # «Claude outputs» sin consola no está en la copia: se mira con device_list_dir (sale al final, en todos los modos)
    t = re.sub(r"=== CLAUDE OUTPUTS.*", "", t, flags=re.S)
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
(R / ACTIVO / "entregables" / "contrato firmado.pdf").write_bytes(b"%PDF-1.4 prueba")   # un entregable que no es .md
TC = tmp / "copia-tablero"
marcas = []
for d, ds, fs in os.walk(R):
    for f in fs:
        r = (pathlib.Path(d) / f).relative_to(R).as_posix()
        partes = r.split("/")
        if set(partes[:-1]) & {"fuentes", "taller", "restringido"} or (partes[0] == "base" and r != "base/premisas.md"):
            continue
        if f.endswith(".md"):
            (TC / r).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(R / r, TC / r)
        elif partes[-2] == "entregables":      # los de primer nivel; una subcarpeta de entregables no se lista sin consola
            marcas.append(r)
(tmp / "marcas.txt").write_text("\n".join(marcas), encoding="utf-8")
corre(ESPEJO, "marcadores", TC, tmp / "marcas.txt")
ok(all((TC / r).is_file() and (TC / r).stat().st_size == 0 for r in marcas), f"los entregables que no son .md, como marcadores vacíos ({len(marcas)})")
ok(len(marcas) == 1, "el PDF de prueba sale como marcador")


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

print("Sin consola: devolver solo lo registrado o nuevo, sin pisar")
corre(ESPEJO, "instantanea", C)
WIN = "C:\\Users\\Ana\\Drive\\Unidades compartidas\\Raiz"
dev = lambda *x: json.loads(corre(ESPEJO, "devolver", C, WIN, "--salidas", tmp / "salidas", *x)[1])
d = dev()
ok(d["lotes"] == [] and d["retenidos"] == [] and d["sin_registrar"] == [], "sin cambios no devuelve nada")
S, P, G = f"{ACTIVO}/sesiones.md", f"{ACTIVO}/proyecto.md", "guia.md"
for r in (S, P, G):
    corre(ESPEJO, "registrar", C, r, "1790000000123", (C / r).stat().st_size)
rc, _, err = corre(ESPEJO, "registrar", C, S, "1790000000123", "999999")
ok(rc == 3, "registrar sale con 3 si el archivo aún no llegó entero")
corre(ESPEJO, "registrar", C, S, "1790000000123", (C / S).stat().st_size)
(C / S).write_text((C / S).read_text(encoding="utf-8") + "\nx\n", encoding="utf-8")
(C / G).write_text("", encoding="utf-8")                                    # vaciado por error
(C / P).write_text("# corto\n", encoding="utf-8")                          # pierde cabecera y encoge
(C / ACTIVO / "decisiones.md").write_text("tocado sin registrar\n", encoding="utf-8")
(C / ACTIVO / "taller").mkdir(parents=True, exist_ok=True)
(C / ACTIVO / "taller" / "nota.md").write_text("---\nestado: borrador\n---\nnueva\n", encoding="utf-8")
(C / ACTIVO / "taller" / "otra.md").write_text("sin declarar\n", encoding="utf-8")
corre(ESPEJO, "nuevo", C, f"{ACTIVO}/taller/nota.md")
d = dev()
ent = [x for l in d["lotes"] for x in l]
rels = sorted(x["rel"] for x in ent)
ok(rels == [S, f"{ACTIVO}/taller/nota.md"], f"devuelve lo registrado que cambió y lo nuevo declarado ({rels})")
ok(next(x for x in ent if x["rel"] == S).get("expectedMtimeMs") == 1790000000123 and "expectedMtimeMs" not in next(x for x in ent if x["rel"].endswith("nota.md")),
   "con la fecha que protege lo que otra persona escribió, salvo en lo nuevo")
ret = {x["rel"]: x["motivo"] for x in d["retenidos"]}
ok(set(ret) == {G, P} and "vacío" in ret[G], f"retiene el .md vaciado y el que pierde su cabecera ({ret})")
ok(f"{ACTIVO}/decisiones.md" in d["sin_registrar"] and f"{ACTIVO}/taller/otra.md" in d["sin_registrar"], "avisa de lo que cambió sin registrar y no lo devuelve")
ok(all(x["devicePath"].startswith(WIN + "\\ventas\\cuentas\\") for x in ent), "la ruta en la computadora con el separador de la raíz (Windows)")
ok(all(pathlib.Path(x["stagedPath"]).is_file() for x in ent), "cada archivo en una carpeta de salidas nueva")
d2 = dev("--forzar", P)
ok(any(x["rel"] == P for l in d2["lotes"] for x in l), "con --forzar sí devuelve lo retenido")
corre(ESPEJO, "hecho", C, S, f"{ACTIVO}/taller/nota.md", P)
d3 = dev()
ok(not any(x["rel"] in (S, P) for l in d3["lotes"] for x in l), "lo escrito deja de estar registrado: hay que traerlo otra vez antes de volver a escribir")
corre(ESPEJO, "hecho", C, G)
ok(not any(pathlib.Path(tmp / "salidas").glob("espejo-*")), "sin nada pendiente, borra sus carpetas de salidas")
rc, _, _ = corre(ESPEJO, "nuevo", C, "../fuera.md")
ok(rc != 0, "no admite rutas que salen de la raíz")

print()
print("Todo bien." if not fallos else f"{fallos} fallos.")
shutil.rmtree(tmp, ignore_errors=True)
sys.exit(1 if fallos else 0)
