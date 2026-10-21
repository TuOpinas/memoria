#!/usr/bin/env python3
"""La copia de la raíz en el contenedor, para trabajar sin consola en la computadora.

Sin consola quiere decir que la raíz está conectada pero el shell de la computadora no la monta (le pasa a una unidad de
Google Drive para escritorio en Windows, con letra o colgada de una carpeta). Las herramientas que traen y escriben archivos
(device_stage_files, device_commit_files) sí llegan a ella, así que se trabaja sobre una copia en el contenedor: los scripts
del plugin corren sobre la copia y lo que cambia se devuelve a la computadora. Este script no toca la computadora: dice qué
traer, lleva la cuenta de lo que se va a escribir y prepara lo que hay que devolver. Lleva su estado junto a la copia, en
<copia>.estado.json.

Devolver es lo delicado: un archivo de la copia puede estar viejo, a medias o vacío, y device_commit_files lo escribiría
encima del de verdad. Por eso solo se devuelve lo que se registró al traerlo (con su fecha y su tamaño en la computadora) o
lo que se declaró nuevo, y nunca un .md vacío, que pierde su cabecera o que encoge a menos de la mitad, salvo con --forzar.

  espejo.py rutas <copia> [<area>/<proyecto>]
      Qué traer para abrir sesión, por rondas: imprime una ruta por línea (relativa a la raíz) de lo que falta en la copia, o
      COMPLETA. Primera ronda: guia.md, metodo.md, base/premisas.md y base/contexto.md; segunda: el area.md de cada área de la
      tabla de guia.md; tercera, solo con proyecto: el decisiones.md de cada proyecto del índice de su área (lo único que
      abrir.py lee de los demás) y proyecto.md, decisiones.md y sesiones.md del proyecto activo. Lo que no se trajo se vuelve a
      pedir, salvo lo apuntado con «falta».

  espejo.py falta <copia> <ruta>...
      Apunta lo que no existe en la computadora (device_stage_files rechazó la llamada por ese archivo) para no pedirlo más.

  espejo.py registrar <copia> <ruta> <mtimeMs> <bytes> [<ruta> <mtimeMs> <bytes>...]
      Antes de escribir en un archivo de la copia: apunta la fecha y el tamaño que dio device_stage_files al traerlo, y
      comprueba que el archivo ya llegó entero a la copia (mismo tamaño). Si no, sale con 3: espera unos segundos y repite.

  espejo.py nuevo <copia> <ruta>...
      Declara un archivo que esta sesión crea y que no existe en la computadora (comprobado con device_list_dir de su carpeta).

  espejo.py devolver <copia> <ruta de la raíz en la computadora> [--forzar <ruta>]... [--salidas <carpeta>]
      Lo registrado que cambió y lo nuevo que existe, listo para device_commit_files: copia cada archivo a una carpeta nueva de
      salidas (nunca una ruta ya usada) e imprime un JSON con «lotes» (de 50 como mucho, cada entrada con stagedPath,
      devicePath y, si no es nuevo, expectedMtimeMs), «retenidos» (lo que no pasa la comprobación de contenido, con el motivo)
      y «sin_registrar» (lo que cambió en la copia sin registrar: no se devuelve). Las salidas son /mnt/project-files/ si
      existe y si no /mnt/user-data/outputs/.

  espejo.py instantanea <copia>
      Guarda cómo está la copia, para que «devolver» avise de lo que cambie sin estar registrado. Se corre en cuanto la copia
      está completa.

  espejo.py hecho <copia> <ruta>...
      Lo que device_commit_files escribió (su lista «written», en rutas relativas). Deja de estar registrado: antes de volver a
      escribir en él hay que traerlo y registrarlo otra vez. Cuando no queda nada pendiente, borra sus carpetas de salidas.

  espejo.py marcadores <copia> <archivo con una ruta por línea>
      Crea vacíos, con su nombre, los archivos que no se traen pero el tablero tiene que listar (los entregables que no son
      .md). Nunca toca uno que ya esté. Se corre antes de la instantánea; como no se registran, nunca se devuelven.

  espejo.py subcopia <copia> <destino> <archivo con una ruta por línea>
      Copia esas rutas de la copia a otra carpeta, con su estructura (la copia exacta que pide la generación del tablero).

Nunca escribe dentro de la raíz de la computadora ni pide nada de fuentes/, taller/ ni restringido/.
"""
import hashlib
import json
import os
import pathlib
import re
import shutil
import sys
import time

FUERA = ("fuentes", "taller", "restringido")
LOTE = 50


def leer(p):
    try:
        return pathlib.Path(p).read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return None


def seccion(texto, nombre):
    m = re.search(r"^##\s+" + re.escape(nombre) + r"\s*$(.*?)(?=^##\s|\Z)", texto or "", re.M | re.S)
    return m.group(1) if m else ""


def sin_cabecera(texto):
    if texto and texto.startswith("---"):
        partes = texto.split("\n---", 1)
        if len(partes) == 2:
            return partes[1]
    return texto or ""


def areas_de(guia):
    """Los slugs de la tabla de áreas de guia.md, como la leen abrir.py y el tablero: la primera columna, sin comillas ni barra."""
    slugs, cab = [], False
    for l in seccion(guia, "Áreas").split("\n"):
        if not l.startswith("|") or re.match(r"^\|[\s:|-]+\|?\s*$", l):
            continue
        if not cab:
            cab = True
            continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        s = c[0].strip("`").rstrip("/").strip() if c else ""
        if s and "/" not in s and s not in (".", ".."):
            slugs.append(s)
    return slugs


def proyectos_de(texto_area):
    return [m.group(1) for m in re.finditer(r"^- `([^`/]+)/?`", seccion(sin_cabecera(texto_area), "Proyectos"), re.M)]


def limpia(r):
    r = r.strip().replace("\\", "/").strip("/")
    if not r or any(p in ("", ".", "..") for p in r.split("/")):
        raise SystemExit(f"Ruta no válida: «{r}» (va relativa a la raíz, sin «..»).")
    return r


def ruta_estado(copia):
    return pathlib.Path(str(copia).rstrip("/") + ".estado.json")


def estado(copia):
    p = ruta_estado(copia)
    e = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    for k, v in (("faltan", []), ("registrados", {}), ("nuevos", []), ("pendientes", {}), ("salidas", [])):
        e.setdefault(k, v)
    return e


def guarda(copia, e):
    p = ruta_estado(copia)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(e, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")


def huella(p):
    return hashlib.sha1(pathlib.Path(p).read_bytes()).hexdigest()


def rutas(copia, activo):
    copia = pathlib.Path(copia)
    faltan = set(estado(copia)["faltan"])
    falta = lambda r: not (copia / r).is_file() and r not in faltan
    ronda = [r for r in ("guia.md", "metodo.md", "base/premisas.md", "base/contexto.md") if falta(r)]
    if not ronda:
        guia = leer(copia / "guia.md")
        if guia is None:
            print("Sin guia.md en la copia: no es la raíz, o la cuenta no la lee.", file=sys.stderr)
            return 1
        areas = areas_de(guia)
        ronda = [f"{a}/area.md" for a in areas if falta(f"{a}/area.md")]
        if not ronda:
            # sin proyecto, abrir.py solo lee hasta los area.md; con proyecto, de los demás solo lee decisiones.md (el barrido
            # de «Afecta a», «Cuestiona a» y «Responde a»), y del activo sus tres archivos
            if activo:
                for a in areas:
                    ronda += [f"{a}/{p}/decisiones.md" for p in proyectos_de(leer(copia / a / "area.md"))]
                ronda += [f"{activo}/{n}" for n in ("proyecto.md", "decisiones.md", "sesiones.md")]
            ronda = [r for r in dict.fromkeys(ronda) if falta(r) and not set(r.split("/")[:-1]) & set(FUERA)]
    print("\n".join(ronda) if ronda else "COMPLETA")
    return 0


def falta(copia, rs):
    e = estado(copia)
    e["faltan"] = sorted(set(e["faltan"]) | {limpia(r) for r in rs})
    guarda(copia, e)
    return 0


def registrar(copia, args):
    if not args or len(args) % 3:
        print("registrar va con tríos: <ruta> <mtimeMs> <bytes>", file=sys.stderr)
        return 2
    copia, e, mal = pathlib.Path(copia), estado(copia), []
    for i in range(0, len(args), 3):
        r, mt, by = limpia(args[i]), int(float(args[i + 1])), int(args[i + 2])
        p = copia / r
        if not p.is_file() or p.stat().st_size != by:
            mal.append(f"{r} (en la copia: {p.stat().st_size if p.is_file() else 'no está'} bytes; en la computadora: {by})")
            continue
        e["registrados"][r] = {"mtimeMs": mt, "bytes": by, "huella": huella(p),
                               "cabecera": p.read_bytes().lstrip(b"\xef\xbb\xbf").startswith(b"---")}
        if r in e["nuevos"]:
            e["nuevos"].remove(r)
    guarda(copia, e)
    if mal:
        print("Aún no llegó entero a la copia: espera unos segundos y vuelve a registrar " + "; ".join(mal), file=sys.stderr)
        return 3
    print(f"{len(args) // 3} registrados")
    return 0


def nuevo(copia, rs):
    e = estado(copia)
    for r in map(limpia, rs):
        if r in e["registrados"]:
            print(f"{r} ya existe en la computadora (se trajo y se registró): no es nuevo.", file=sys.stderr)
            return 2
        if r not in e["nuevos"]:
            e["nuevos"].append(r)
    guarda(copia, e)
    return 0


def motivo_retenido(antes_bytes, ruta, contenido_antes_tenia_cabecera):
    t = ruta.read_bytes()
    if ruta.suffix.lower() != ".md":
        return None
    if not t.strip():
        return "está vacío"
    if contenido_antes_tenia_cabecera and not t.lstrip(b"\xef\xbb\xbf").startswith(b"---"):
        return "perdió su cabecera"
    if antes_bytes and len(t) < antes_bytes / 2:
        return f"encoge de {antes_bytes} a {len(t)} bytes"
    return None


def devolver(copia, raiz_dispositivo, forzar, salidas):
    copia, e = pathlib.Path(copia), estado(copia)
    if salidas is None:
        salidas = "/mnt/project-files" if os.path.isdir("/mnt/project-files") else "/mnt/user-data/outputs"
    destino = pathlib.Path(salidas) / f"espejo-{time.strftime('%Y%m%d%H%M%S')}-{os.getpid()}"
    sep = "\\" if "\\" in raiz_dispositivo and "/" not in raiz_dispositivo else "/"
    base = raiz_dispositivo.rstrip("/\\")
    entradas, retenidos = [], []
    for r, reg in sorted(e["registrados"].items()):
        p = copia / r
        if not p.is_file() or huella(p) == reg["huella"]:
            continue
        motivo = None if r in forzar else motivo_retenido(reg["bytes"], p, reg.get("cabecera", False))
        if motivo:
            retenidos.append({"rel": r, "motivo": motivo})
            continue
        entradas.append((r, reg["mtimeMs"]))
    for r in sorted(e["nuevos"]):
        p = copia / r
        if not p.is_file():
            continue
        motivo = None if r in forzar else motivo_retenido(0, p, False)
        if motivo:
            retenidos.append({"rel": r, "motivo": motivo})
            continue
        entradas.append((r, None))
    # lo que cambió en la copia desde la instantánea sin estar registrado ni declarado nuevo: no se devuelve, se avisa
    conocidos = set(e["registrados"]) | set(e["nuevos"])
    sin_registrar = []
    if e.get("instantanea"):
        for d, ds, fs in os.walk(copia):
            for f in fs:
                r = (pathlib.Path(d) / f).relative_to(copia).as_posix()
                if r not in conocidos and e["instantanea"].get(r) != huella(pathlib.Path(d) / f):
                    sin_registrar.append(r)
    lotes, lote = [], []
    for r, mt in entradas:
        dst = destino / r
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(copia / r, dst)
        x = {"stagedPath": str(dst), "devicePath": base + sep + sep.join(r.split("/")), "rel": r}
        if mt is not None:
            x["expectedMtimeMs"] = mt
        e["pendientes"][r] = str(dst)
        lote.append(x)
        if len(lote) == LOTE:
            lotes.append(lote); lote = []
    if lote:
        lotes.append(lote)
    if entradas:
        e["salidas"] = sorted(set(e["salidas"]) | {str(destino)})
    guarda(copia, e)
    print(json.dumps({"lotes": lotes, "retenidos": retenidos, "sin_registrar": sorted(sin_registrar)}, ensure_ascii=False, indent=1))
    return 0


def instantanea(copia):
    copia, e = pathlib.Path(copia), estado(copia)
    e["instantanea"] = {(pathlib.Path(d) / f).relative_to(copia).as_posix(): huella(pathlib.Path(d) / f)
                        for d, ds, fs in os.walk(copia) for f in fs}
    guarda(copia, e)
    print(f"{len(e['instantanea'])} archivos")
    return 0


def hecho(copia, rs):
    e = estado(copia)
    for r in map(limpia, rs):
        e["registrados"].pop(r, None)
        e["pendientes"].pop(r, None)
        p = pathlib.Path(copia) / r
        if e.get("instantanea") is not None and p.is_file():
            e["instantanea"][r] = huella(p)
        if r in e["nuevos"]:
            e["nuevos"].remove(r)
    if not e["pendientes"]:
        for s in e["salidas"]:
            shutil.rmtree(s, ignore_errors=True)
        e["salidas"] = []
    guarda(copia, e)
    print(f"pendientes: {len(e['pendientes'])}")
    return 0


def marcadores(copia, lista):
    """Archivos vacíos con el nombre de los que no se traen (los entregables que no son .md), para que el tablero los liste.
    Nunca toca uno que ya esté en la copia. No se devuelven: no están registrados."""
    copia, n = pathlib.Path(copia), 0
    for r in pathlib.Path(lista).read_text(encoding="utf-8").split("\n"):
        if not r.strip():
            continue
        p = copia / limpia(r)
        if not p.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.touch(); n += 1
    print(f"{n} marcadores")
    return 0


def subcopia(copia, destino, lista):
    copia, destino = pathlib.Path(copia), pathlib.Path(destino)
    for r in pathlib.Path(lista).read_text(encoding="utf-8").split("\n"):
        if not r.strip():
            continue
        r = limpia(r)
        (destino / r).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(copia / r, destino / r)
    return 0


def main(argv):
    if len(argv) < 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    orden, copia, resto = argv[1], argv[2], argv[3:]
    if orden == "rutas":
        return rutas(copia, resto[0].strip("/") if resto else None)
    if orden == "falta":
        return falta(copia, resto)
    if orden == "registrar":
        return registrar(copia, resto)
    if orden == "nuevo":
        return nuevo(copia, resto)
    if orden == "instantanea":
        return instantanea(copia)
    if orden == "hecho":
        return hecho(copia, resto)
    if orden == "marcadores" and len(resto) == 1:
        return marcadores(copia, resto[0])
    if orden == "subcopia" and len(resto) == 2:
        return subcopia(copia, resto[0], resto[1])
    if orden == "devolver" and resto:
        raiz, forzar, salidas, i = resto[0], set(), None, 1
        while i < len(resto):
            if resto[i] == "--forzar" and i + 1 < len(resto):
                forzar.add(limpia(resto[i + 1])); i += 2
            elif resto[i] == "--salidas" and i + 1 < len(resto):
                salidas = resto[i + 1]; i += 2
            else:
                print(f"No entiendo «{resto[i]}».", file=sys.stderr)
                return 2
        return devolver(copia, raiz, forzar, salidas)
    print(__doc__.strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
