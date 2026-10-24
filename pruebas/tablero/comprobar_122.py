#!/usr/bin/env python3
"""La raíz de prueba migrada a la 1.22 da al tablero lo mismo que sin migrar: prioridades, estado, cerrado,
responsable y aportacion. Uso: comprobar_122.py <salida sin migrar> <salida migrada>."""
import json, pathlib, sys
A, B = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
j = lambda d, *r: json.loads((d.joinpath(*r)).read_text(encoding="utf-8"))
fallos = 0
def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t); fallos += 0 if c else 1
print("El tablero sobre la raíz migrada a la 1.22")
va, vb = j(A, "areas", "ventas.json"), j(B, "areas", "ventas.json")
ok(va["prioridades"] == vb["prioridades"] and len(vb["prioridades"]) == 2, "las prioridades del área salen de «Siguiente» del Estatus, las mismas que de «Prioridades ahora»")
ok(vb.get("panorama", {}).get("fecha") == va["panorama"]["fecha"] and vb["panorama"]["texto"].startswith("Ventas tiene") and "**" not in vb["panorama"]["texto"], "el panorama de las listas sale del Estatus, con su fecha y sin asteriscos")
ok(vb.get("en_corto", "").startswith("2026-10-03 · **Ventas"), "el área lleva su Estatus entero para la página")
ha, hb = j(A, "proyectos", "archivo--historia.json"), j(B, "proyectos", "archivo--historia.json")
ok(ha["cerrado"] and hb["cerrado"], "un proyecto cerrado sigue cerrado: «Proyecto terminado» pasó al Estatus")
sa, sb = j(A, "proyectos", "operacion--soporte.json"), j(B, "proyectos", "operacion--soporte.json")
ok(sa["en_corto"] == sb["en_corto"] and sb["dueno"] == sa["dueno"] == "Ana Prueba", "En corto pasa a Estatus tal cual, y Responsable da el mismo nombre que Dueño")
ok(not sb.get("terminado") and not sb.get("estado_actual") and not sb.get("consumen"), "sin Terminado significa, Estado actual ni Consumen esto")
ca, cb = j(A, "proyectos", "ventas--cuentas.json"), j(B, "proyectos", "ventas--cuentas.json")
pa = {z["archivo"]: z.get("afirma") for z in (ca.get("que_hay") or {}).get("piezas", [])} if ca.get("que_hay") else None
det = lambda d: json.loads((d / "detalle" / "ventas--cuentas.json").read_text(encoding="utf-8")) if (d / "detalle" / "ventas--cuentas.json").exists() else {}
pz = lambda d, p: {z["archivo"]: z.get("afirma") for z in ((det(d).get("que_hay") or {}).get("piezas") or [])}
pb = pz(B, cb); ea = pb.pop("estado-anterior.md", None)
ok(pz(A, ca) == pb and any(v for v in pb.values()), "lo que aportaba cada pieza («afirma») se lee igual como «aportacion»")
ok(bool(ea) and "antes de la 1.22" in ea, "el Estado actual que salió de proyecto.md está en el taller, con su aportacion")
pa_, pb_ = j(A, "areas", "personas.json"), j(B, "areas", "personas.json")
ok(pa_.get("restringido") == pb_.get("restringido") is True, "un área restringida sigue restringida, ahora por la columna Acceso")
print("\n" + ("Todo bien." if not fallos else f"{fallos} fallo(s)."))
sys.exit(1 if fallos else 0)
