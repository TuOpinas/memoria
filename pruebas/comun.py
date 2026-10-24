"""Lo que comparten las pruebas: la raíz inventada de pruebas/tablero/raiz en su forma de la 1.22.

guia_122(texto) pasa la tabla de áreas de su guia.md a la de la 1.22 («Responsable» y la columna «Acceso»), con las mismas
áreas y cuentas; raiz_migrada() copia la raíz a una carpeta temporal y la migra de verdad con migrar_estructura.py, por la
cuenta de Ana (responsable de contexto: migra todo lo que su carpeta deja leer). Así ninguna prueba fabrica a mano su propia
versión de la 1.22.
"""
import json, pathlib, shutil, subprocess, sys, tempfile

PRUEBAS = pathlib.Path(__file__).resolve().parent
RAIZ = PRUEBAS / "tablero" / "raiz"
MIG = PRUEBAS.parent / "plugins" / "memoria" / "skills" / "sesion" / "migrar_estructura.py"


def guia_122(texto, personas="Dirección", legal="Ana Prueba y Beto Prueba"):
    """La tabla de áreas de la guia.md de prueba, con «Responsable» y «Acceso»; «Quién la lee» de las dos áreas
    restringidas pasa a decir solo quién la lee (personas y legal, por defecto «Dirección» y «Ana Prueba y Beto Prueba»)."""
    return (texto.replace("| Área | Qué es | Dueño | Cuenta | Quién la lee |\n|---|---|---|---|---|",
                          "| Área | Qué es | Responsable | Cuenta | Quién la lee | Acceso |\n|---|---|---|---|---|---|")
            .replace("| Todo el equipo |\n", "| Todo el equipo | Abierta |\n")
            .replace("| Todo el equipo, nada restringido |", "| Todo el equipo, nada restringido | Abierta |")
            .replace("| Restringida: dirección |", f"| {personas} | Restringida |")
            .replace("| Restringida: Ana Prueba y Beto Prueba |", f"| {legal} | Restringida |"))


def raiz_migrada(cuenta="ana@ejemplo.test", nombre="Ana Prueba"):
    """Una copia de la raíz de prueba migrada a la 1.22 con el script de verdad; devuelve (ruta, salida del script)."""
    r = pathlib.Path(tempfile.mkdtemp()) / "raiz"
    shutil.copytree(RAIZ, r)
    p = subprocess.run([sys.executable, str(MIG), str(r), "--cuenta", cuenta, "--nombre", nombre, "--plugin", "1.22.1"],
                       capture_output=True, text=True)
    return r, json.loads(p.stdout)
