#!/usr/bin/env python3
"""Lo que el generador manda para «Por persona» (1.23): cada entrada de la bitácora con su posición en el archivo, para
que las de un mismo día no se junten, y con los documentos que escribió y publicó («Escribió:» y «Publicó:»); y el nombre
de quien colabora en un área. También después de reutilizar la base. La página la prueba recorrer.js.

Uso: python3 pruebas/tablero/probar_personas.py
"""
import datetime, json, pathlib, shutil, subprocess, sys, tempfile

AQUI = pathlib.Path(__file__).resolve().parent
GV = AQUI.parents[1] / "plugins" / "memoria" / "skills" / "tablero" / "generar_vista.py"


def dos_corridas(raiz, tmp):
    """Como la puesta al día real (la misma que probar_que_es.py): inventario y generación sobre la copia, y una segunda
    corrida que reutiliza la base. Devuelve (primera, segunda, reutilizó algo)."""
    def corrida(sal, previos=None, sin_cambios=None):
        a = [sys.executable, str(GV), str(raiz), "--inventario"] + (["--sin-cambios", sin_cambios] if sin_cambios else [])
        inv = json.loads(subprocess.run(a, capture_output=True, text=True, check=True).stdout)
        ip = tmp / f"inv-{sal}.json"; ip.write_text(json.dumps(inv["inventario"]), encoding="utf-8")
        cop = tmp / f"copia-{sal}"
        for r_ in inv["leer"]:
            (cop / r_).parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(raiz / r_, cop / r_)
        cop.mkdir(exist_ok=True)
        subprocess.run([sys.executable, str(GV), str(cop), str(tmp / sal), "--desde-inventario", str(ip), "--version", "prueba"]
                       + (["--previos", str(previos)] if previos else []), check=True, stdout=subprocess.DEVNULL)
        return inv
    corrida("o1")
    est = json.loads((tmp / "o1" / "meta" / "estado.json").read_text(encoding="utf-8"))
    inv = corrida("o2", tmp / "o1", ",".join(est.get("huellas") or []))
    return tmp / "o1", tmp / "o2", bool(inv["inventario"].get("reusar"))

fallos = 0


def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t); fallos += 0 if c else 1


tmp = pathlib.Path(tempfile.mkdtemp())
raiz = tmp / "raiz"
shutil.copytree(AQUI / "raiz", raiz)
from zoneinfo import ZoneInfo
hoy = datetime.datetime.now(ZoneInfo("America/Mexico_City")).date().isoformat()   # la zona de la raíz de prueba
ps = raiz / "ventas" / "cuentas" / "sesiones.md"
t = ps.read_text(encoding="utf-8")
nuevas = (f"## {hoy}\nTema: tercera.\nAvances: x.\nPublicó: entregables/kit-cuentas.md\nSesión de: Ana López · plugin 1.23.0\n\n"
          f"## {hoy}\nTema: segunda.\nAvances: y.\nEscribió: entregables/kit-cuentas.md, taller/nota-precios.md, ventas/cuentas/restringido/x.md\nSesión de: Carla Ruiz · plugin 1.23.0\n\n"
          f"## {hoy}\nTema: primera.\nAvances: z.\nSesión de: Carla Ruiz · plugin 1.23.0\n\n")
ps.write_text(t.replace("# Sesiones\n\n", "# Sesiones\n\n" + nuevas, 1), encoding="utf-8")
# Carla colabora en ventas: su nombre, junto a su cuenta, en la línea «Colabora:» de un proyecto
pp = raiz / "ventas" / "cuentas" / "proyecto.md"
pp.write_text(pp.read_text(encoding="utf-8").replace("## Quién participa\n", "## Quién participa\nColabora: Carla Ruiz (carla@ejemplo.test)\n", 1), encoding="utf-8")

o1, o2, reuso = dos_corridas(raiz, tmp)
for etiqueta, sal in (("al generar", o1), ("al reutilizar la base", o2)):
    d = json.loads((sal / "proyectos" / "ventas--cuentas.json").read_text(encoding="utf-8"))
    ses = [s for s in (d.get("sesiones_recientes") or []) + (d.get("sesiones") or []) if s.get("fecha") == hoy]
    por_n = {s["n"]: s for s in ses}
    ok(len(por_n) == 3 and len({s.get("titulo") for s in ses}) == 1, f"{etiqueta}: las tres entradas de hoy llegan, distintas por su posición ({sorted(por_n)})")
    tercera = max(por_n.values(), key=lambda s: s["n"]) if por_n else {}
    segunda = sorted(por_n.values(), key=lambda s: s["n"])[1] if len(por_n) == 3 else {}
    ok(tercera.get("publico") == ["entregables/kit-cuentas.md"] and tercera.get("quien") == "Ana López", f"{etiqueta}: «Publicó:» llega como lista, con quién ({tercera})")
    ok(segunda.get("escribio") == ["entregables/kit-cuentas.md", "taller/nota-precios.md"], f"{etiqueta}: «Escribió:» llega como lista, sin lo de restringido/ ({segunda.get('escribio')})")
    a = json.loads((sal / "areas" / "ventas.json").read_text(encoding="utf-8"))
    ok("Carla Ruiz" in (a.get("colaboran_ver") or []), f"{etiqueta}: quien colabora en el área va por su nombre ({a.get('colaboran_ver')})")
ok(reuso, "la segunda corrida reutilizó la base")

# los registros archivados (1.23): la generación los lee junto al vivo, con los mismos identificadores
print("Los registros archivados")
def generar(r_, sal):
    subprocess.run([sys.executable, str(GV), str(r_), str(tmp / sal), "--version", "prueba"], check=True, stdout=subprocess.DEVNULL)
    return json.loads((tmp / sal / "proyectos" / "ventas--cuentas.json").read_text(encoding="utf-8"))
ra = tmp / "raiz-arch"; shutil.copytree(AQUI / "raiz", ra)
antes = generar(ra, "arch-antes")
pc_ = ra / "ventas" / "cuentas"; anio_ = hoy[:4]
(pc_ / f"decisiones-{anio_}.md").write_text((pc_ / "decisiones.md").read_text(encoding="utf-8"), encoding="utf-8")
(pc_ / "decisiones.md").write_text(f"---\nestado: vigente\n---\n# Decisiones\n\nArchivado: decisiones-{anio_}.md.\n\n## {hoy} · Una nueva\nDecidió: Ana López\nPor qué: x.\n", encoding="utf-8")
(pc_ / f"sesiones-{anio_}.md").write_text((pc_ / "sesiones.md").read_text(encoding="utf-8"), encoding="utf-8")
(pc_ / "sesiones.md").write_text(f"---\nestado: vigente\n---\n# Sesiones\n\nArchivado: sesiones-{anio_}.md.\n", encoding="utf-8")
despues = generar(ra, "arch-despues")
ids = lambda d: sorted((x.get("id"), x.get("titulo")) for x in d.get("decisiones") or [])
viejas = [x for x in despues.get("decisiones") or [] if x.get("archivada")]
ok(set(ids(antes)) <= set(ids(despues)) and len(viejas) == len(antes.get("decisiones") or []) and not any(x.get("archivada") for x in despues["decisiones"] if x.get("titulo") == "Una nueva"),
   "las decisiones archivadas llegan con sus identificadores de siempre, marcadas «archivada»; la nueva no")
ok(despues.get("sesiones_total") == antes.get("sesiones_total") and despues.get("ultima_sesion") == antes.get("ultima_sesion"), "las sesiones archivadas siguen contando: el total y la última sesión no cambian")

print("\n" + ("Todo bien." if not fallos else f"{fallos} fallo(s)."))
sys.exit(1 if fallos else 0)
