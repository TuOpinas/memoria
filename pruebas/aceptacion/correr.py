#!/usr/bin/env -S python3 -I
"""Corre las pruebas de aceptación de una o varias piezas.

Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/correr.py P01 [P02 …]
Como corredor propio del control (.github/workflows/pruebas-aceptacion.yml): ./pruebas/aceptacion/correr.py <archivos>

Con archivos, escribe una línea por archivo, «PASA <ruta>», «FALLA <ruta>» o «NO_CORRIO <ruta>», que es lo que lee el
control, y sale con 0 si pudo correrlos, pasen o no, y con 2 si no le llegó ninguno. Una prueba saltada, una que no se
pudo ejecutar o un archivo que no es una prueba de esta carpeta (<pieza>_<nombre>.py, suelto en ella) son NO_CORRIO: no
cuentan como pasadas ni como fallos de prueba.

Corre, desde este mismo proceso, cada archivo .py de esta carpeta cuyo nombre empieza exactamente por «<PIEZA>_» (P1 no
toma P10_…), cada uno con «python3 -I» y desde la raíz del repositorio. Un script sale con 0 si pasa, 1 si falla y 77 si
se salta, y su última línea dice lo mismo: «RESULTADO: pasa», «RESULTADO: falla» o «RESULTADO: saltada». Termina con la
lista de piezas que fallaron y, en la última línea, «N pasan · M fallan · K saltadas», que cuenta archivos de prueba, no
escenarios.

Sale con 0 si todo pasa; con 1 si alguna prueba falla o se salta; con 2 si una pieza pedida no tiene ningún archivo o un
script no se pudo ejecutar: no arrancó, salió con otro código (por ejemplo 2, que es como salen las de esta carpeta
cuando no se pueden montar), pasó de 5 minutos o salió con 0, 1 o 77 sin su línea «RESULTADO:», que es lo que pasa con un error de sintaxis
o un import roto. Así una prueba rota no cuenta como una que falla. El 2 manda sobre el 1.
"""
import os, pathlib, re, signal, subprocess, sys

AQUI = pathlib.Path(__file__).resolve().parent
SALTADA = 77
DICE = {0: "pasa", 1: "falla", SALTADA: "saltada"}
LIMITE = 300   # segundos por archivo de prueba: uno colgado sale como «no se pudo ejecutar», con su nombre


def ejecutar(f):
    """Corre un archivo de prueba y devuelve «pasa», «falla», «saltada» o el motivo por el que no se pudo ejecutar."""
    try:
        hijo = subprocess.Popen([sys.executable, "-I", str(f)], cwd=pathlib.Path.cwd(), stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace",
                                start_new_session=True)
        try:
            salida, _ = hijo.communicate(timeout=LIMITE)
        except subprocess.TimeoutExpired:
            try:   # el grupo entero: también lo que la prueba lanzó
                os.killpg(hijo.pid, signal.SIGKILL)
            except OSError:
                pass
            salida, _ = hijo.communicate()
            sys.stdout.write(salida or "")
            return f"no se pudo ejecutar: pasó de {LIMITE} segundos"
    except OSError as e:
        return f"no se pudo ejecutar: {e}"
    rc = hijo.returncode
    sys.stdout.write(salida)
    lineas = [l.strip() for l in salida.splitlines() if l.strip()]
    if rc not in DICE:
        return f"no se pudo ejecutar (salió con {rc})"
    if not lineas or lineas[-1] != "RESULTADO: " + DICE[rc]:
        return f"no se pudo ejecutar (salió con {rc} sin su línea «RESULTADO: {DICE[rc]}»)"
    return DICE[rc]


def archivos_del_control(args):
    """El corredor propio del control: una línea PASA, FALLA o NO_CORRIO por archivo, y 0 si pudo correrlos."""
    for a in args:
        f = pathlib.Path(a)
        es_prueba = (f.is_file() and f.resolve().parent == AQUI and f.suffix == ".py"
                     and re.match(r"[A-Za-z]+[0-9]+[A-Za-z]?_.", f.name) is not None)
        if not es_prueba:
            print(f"== {a}: no es un archivo de prueba de {AQUI.name}/ (<pieza>_<nombre>.py)")
            print(f"NO_CORRIO {a}")
            continue
        print(f"== {a}", flush=True)
        r = ejecutar(f)
        print("   " + r)
        print(("PASA " if r == "pasa" else "FALLA " if r == "falla" else "NO_CORRIO ") + a, flush=True)
    return 0


def _fin(pasan, fallan, saltadas, rc):
    print(f"{pasan} pasan · {fallan} fallan · {saltadas} saltadas")
    return rc


def main(args):
    if not args:
        print(__doc__.strip().split("\n\n")[1])
        return _fin(0, 0, 0, 2)
    if any(a.endswith(".py") for a in args):
        return archivos_del_control(args)
    piezas = []
    for a in args:
        if not re.fullmatch(r"[A-Za-z]+[0-9]+[A-Za-z]?", a):
            print(f"«{a}» no es un identificador de pieza (P01).")
            return _fin(0, 0, 0, 2)
        p = re.sub(r"[a-z]+(?=[0-9])", lambda m: m.group(0).upper(), a)
        p = p[:-1] + p[-1].lower() if p[-1].isalpha() else p
        if p not in piezas:
            piezas.append(p)
    pasan = fallan = saltadas = 0
    mal, piezas_fallan, piezas_saltadas, rotas = False, [], [], []
    for pieza in piezas:
        archivos = sorted(p for p in AQUI.iterdir()   # sin mayúsculas, como el control: p05_x.py es de P05
                          if p.is_file() and p.suffix == ".py" and p.name.lower().startswith(pieza.lower() + "_"))
        if not archivos:
            print(f"== {pieza}: no hay ningún archivo {pieza}_*.py en {AQUI.name}/")
            mal = True
            continue
        for f in archivos:
            print(f"== {pieza} · {f.name}", flush=True)
            r = ejecutar(f)
            if r == "pasa":
                pasan += 1
            elif r == "falla":
                fallan += 1
                if pieza not in piezas_fallan:
                    piezas_fallan.append(pieza)
            elif r == "saltada":
                saltadas += 1
                if pieza not in piezas_saltadas:
                    piezas_saltadas.append(pieza)
            else:
                mal = True
                rotas.append(f.name)
            print("   " + r)
    print()
    print("Piezas que fallan: " + (", ".join(piezas_fallan) if piezas_fallan else "ninguna"))
    if piezas_saltadas:
        print("Piezas con pruebas saltadas: " + ", ".join(piezas_saltadas))
    if rotas:
        print("No se pudieron ejecutar: " + ", ".join(rotas))
    return _fin(pasan, fallan, saltadas, 2 if mal else 1 if (fallan or saltadas) else 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
