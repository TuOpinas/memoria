#!/usr/bin/env python3
"""Corre las pruebas de aceptación de una o varias piezas.

Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/correr.py P01 [P02 …]

Corre, desde este mismo proceso, cada archivo .py de esta carpeta cuyo nombre empieza exactamente por «<PIEZA>_» (P1 no
toma P10_…), cada uno con «python3 -I» y desde la raíz del repositorio. Un script sale con 0 si pasa, 1 si falla y 77 si
se salta, y su última línea dice lo mismo: «RESULTADO: pasa», «RESULTADO: falla» o «RESULTADO: saltada». Termina con la
lista de piezas que fallaron y, en la última línea, «N pasan · M fallan · K saltadas», que cuenta archivos de prueba, no
escenarios.

Sale con 0 si todo pasa; con 1 si alguna prueba falla o se salta; con 2 si una pieza pedida no tiene ningún archivo o un
script no se pudo ejecutar: no arrancó, salió con otro código (por ejemplo 2, que es como salen las de esta carpeta
cuando no se pueden montar), pasó de 10 minutos o salió con 0, 1 o 77 sin su línea «RESULTADO:», que es lo que pasa con un error de sintaxis
o un import roto. Así una prueba rota no cuenta como una que falla. El 2 manda sobre el 1.
"""
import pathlib, re, subprocess, sys

AQUI = pathlib.Path(__file__).resolve().parent
SALTADA = 77
DICE = {0: "pasa", 1: "falla", SALTADA: "saltada"}
LIMITE = 600   # segundos por archivo de prueba: uno colgado sale como «no se pudo ejecutar», con su nombre


def _fin(pasan, fallan, saltadas, rc):
    print(f"{pasan} pasan · {fallan} fallan · {saltadas} saltadas")
    return rc


def main(args):
    if not args:
        print(__doc__.strip().split("\n\n")[1])
        return _fin(0, 0, 0, 2)
    piezas = []
    for a in args:
        if not re.fullmatch(r"[A-Za-z]+[0-9]+", a):
            print(f"«{a}» no es un identificador de pieza (P01).")
            return _fin(0, 0, 0, 2)
        if a.upper() not in piezas:
            piezas.append(a.upper())
    pasan = fallan = saltadas = 0
    mal, piezas_fallan, piezas_saltadas, rotas = False, [], [], []
    for pieza in piezas:
        archivos = sorted(p for p in AQUI.iterdir() if p.is_file() and p.suffix == ".py" and p.name.startswith(pieza + "_"))
        if not archivos:
            print(f"== {pieza}: no hay ningún archivo {pieza}_*.py en {AQUI.name}/")
            mal = True
            continue
        for f in archivos:
            print(f"== {pieza} · {f.name}", flush=True)
            try:
                r = subprocess.run([sys.executable, "-I", str(f)], cwd=pathlib.Path.cwd(), stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace",
                                   timeout=LIMITE)
                rc = r.returncode
                sys.stdout.write(r.stdout)
                lineas = [l.strip() for l in r.stdout.splitlines() if l.strip()]
                if rc in DICE and (not lineas or lineas[-1] != "RESULTADO: " + DICE[rc]):
                    print(f"   no se pudo ejecutar (salió con {rc} sin su línea «RESULTADO: {DICE[rc]}»)")
                    mal = True
                    rotas.append(f.name)
                    continue
            except OSError as e:
                print(f"   no se pudo ejecutar: {e}")
                mal = True
                rotas.append(f.name)
                continue
            except subprocess.TimeoutExpired:
                print(f"   no se pudo ejecutar: pasó de {LIMITE} segundos")
                mal = True
                rotas.append(f.name)
                continue
            if rc == 0:
                pasan += 1
                print("   pasa")
            elif rc == 1:
                fallan += 1
                print("   falla")
                if pieza not in piezas_fallan:
                    piezas_fallan.append(pieza)
            elif rc == SALTADA:
                saltadas += 1
                print("   saltada")
                if pieza not in piezas_saltadas:
                    piezas_saltadas.append(pieza)
            else:
                mal = True
                rotas.append(f.name)
                print(f"   no se pudo ejecutar (salió con {rc})")
    print()
    print("Piezas que fallan: " + (", ".join(piezas_fallan) if piezas_fallan else "ninguna"))
    if piezas_saltadas:
        print("Piezas con pruebas saltadas: " + ", ".join(piezas_saltadas))
    if rotas:
        print("No se pudieron ejecutar: " + ", ".join(rotas))
    return _fin(pasan, fallan, saltadas, 2 if mal else 1 if (fallan or saltadas) else 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
