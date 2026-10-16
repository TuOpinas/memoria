#!/usr/bin/env python3
"""Prueba la generación en dos tiempos: inventario en la computadora y generación sobre una copia.

Uso: dos_tiempos.py <generar_vista.py> <plan_subida.py> <raiz> <carpeta-de-trabajo>

Comprueba que, en los dos modos, generar sobre la copia de «leer» con el inventario da exactamente los mismos
documentos que generar sobre la raíz; que la copia en público no trae nada restringido; que una copia incompleta
o con archivos de más se rechaza; que un inventario de otro modo se rechaza; y que el plan de subida solo
propone lo que cambió.
"""
import json, os, shutil, subprocess, sys, pathlib

GEN, PLAN, RAIZ, TRAB = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3]), pathlib.Path(sys.argv[4])
fallos = 0


def ok(cond, texto):
    global fallos
    print(("  bien  " if cond else "  FALLA ") + texto)
    if not cond:
        fallos += 1


def correr(*args):
    return subprocess.run([sys.executable, GEN, *map(str, args)], capture_output=True, text=True)


def docs(carpeta):
    """{coleccion/doc: contenido sin la hora de sincronización}"""
    out = {}
    for p in sorted(pathlib.Path(carpeta).rglob("*.json")):
        if p.name == "indice.json":
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        d.pop("sincronizado", None); d.pop("generado", None)
        out[p.relative_to(carpeta).as_posix()] = d
    return out


def copiar(leer, destino):
    shutil.rmtree(destino, ignore_errors=True)
    for r in leer:
        (destino / r).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(RAIZ / r, destino / r)


print("Dos tiempos: inventario en la computadora, generación sobre la copia")
shutil.rmtree(TRAB, ignore_errors=True); TRAB.mkdir(parents=True)
for modo in ("publico", "completo"):
    r1 = correr(RAIZ, "--inventario", "--modo", modo)
    ok(r1.returncode == 0, f"{modo}: el inventario sale sin errores")
    salida = json.loads(r1.stdout)
    leer, inv = salida["leer"], salida["inventario"]
    ok(len(json.dumps(inv)) < 20_000, f"{modo}: el inventario es pequeño ({len(json.dumps(inv))} bytes), porque pasa por la conversación")
    ok(all(not r.startswith(("base/", )) or r == "base/premisas.md" for r in leer), f"{modo}: de base/ solo se trae premisas.md")
    ok(not any(seg in ("fuentes", "taller", "restringido") for r in leer for seg in r.split("/")), f"{modo}: nunca se trae nada de fuentes/, taller/ ni restringido/")
    copia = TRAB / f"copia-{modo}"
    copiar(leer, copia)
    (TRAB / f"inv-{modo}.json").write_text(json.dumps(inv, ensure_ascii=False), encoding="utf-8")
    correr(RAIZ, TRAB / f"directo-{modo}", "--modo", modo, "--version", "prueba")
    r2 = correr(copia, TRAB / f"dos-{modo}", "--desde-inventario", TRAB / f"inv-{modo}.json", "--modo", modo, "--version", "prueba")
    ok(r2.returncode == 0, f"{modo}: la generación sobre la copia sale sin errores")
    a, b = docs(TRAB / f"directo-{modo}"), docs(TRAB / f"dos-{modo}")
    distintos = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    ok(not distintos, f"{modo}: los dos caminos dan los mismos documentos" + (f" (difieren: {', '.join(distintos[:5])})" if distintos else ""))
    if modo == "publico":
        ok(not any(r.startswith("personas/") for r in leer), "público: de un área restringida no se trae ningún archivo")
        ok(not any(r.startswith(("ventas/precios/", "ventas/margenes/", "ventas/oculto/")) for r in leer),
           "público: de un proyecto declarado restringido, o fuera del índice, no se trae ningún archivo")

# una copia con un archivo de más (de una corrida anterior) o de menos no se acepta
copia = TRAB / "copia-completo"
extra = copia / "ventas" / "sobra.md"; extra.write_text("x", encoding="utf-8")
r = correr(copia, TRAB / "x", "--desde-inventario", TRAB / "inv-completo.json", "--modo", "completo")
ok(r.returncode == 3 and "no coincide" in r.stderr, "una copia con archivos de más se rechaza y dice qué hacer")
extra.unlink()
falta = sorted(copia.rglob("sesiones.md"))[0]; guardado = falta.read_bytes(); falta.unlink()
r = correr(copia, TRAB / "x", "--desde-inventario", TRAB / "inv-completo.json", "--modo", "completo")
ok(r.returncode == 3, "una copia a la que le falta un archivo se rechaza")
falta.write_bytes(guardado)
r = correr(copia, TRAB / "x", "--desde-inventario", TRAB / "inv-completo.json", "--modo", "publico")
ok(r.returncode != 0 and "modo" in (r.stderr + r.stdout), "un inventario sacado en otro modo se rechaza")

# plan de subida: con la base igual a la salida, solo meta/estado; con un proyecto cambiado, ese y meta; lo que sobra se borra
salida = TRAB / "dos-completo"
volcado = TRAB / "volcado"
shutil.rmtree(volcado, ignore_errors=True)
shutil.copytree(salida, volcado, ignore=shutil.ignore_patterns("indice.json", "enfoque-candidatos.json"))
plan = json.loads(subprocess.run([sys.executable, PLAN, salida, volcado], capture_output=True, text=True).stdout)
escr = [e for l in plan["lotes"] for e in l]
ok([(e["collection"], e["doc_id"], e["op"]) for e in escr] == [("meta", "estado", "update")], "plan: sin cambios, solo se sube meta/estado (como update)")
uno = sorted((volcado / "proyectos").glob("*.json"))[0]
d = json.loads(uno.read_text(encoding="utf-8")); d["huella"] = "otra"; uno.write_text(json.dumps(d), encoding="utf-8")
(volcado / "proyectos" / "ya-no-existe.json").write_text(json.dumps({"huella": "h"}), encoding="utf-8")
plan = json.loads(subprocess.run([sys.executable, PLAN, salida, volcado], capture_output=True, text=True).stdout)
escr = [e for l in plan["lotes"] for e in l]
ok(any(e["doc_id"] == uno.stem and e["op"] == "set" and e["existe"] for e in escr), "plan: un proyecto que cambió se sube entero, marcado como existente")
ok(any(e["doc_id"] == "ya-no-existe" and e["op"] == "delete" for e in escr), "plan: un proyecto que ya no sale de la raíz se borra")
ok(all(pathlib.Path(e["file_path"]).is_file() for e in escr if e["op"] != "delete"), "plan: cada escritura apunta a un archivo que existe")
ok(all(len(l) <= 50 for l in plan["lotes"]), "plan: ningún lote pasa de 50 entradas")

print("\nTodo bien." if not fallos else f"\n{fallos} fallos.")
sys.exit(1 if fallos else 0)
