"""cerrar.py 1.25.8's rotation, frozen when it moved into context_core.write (1.26): the helpers as they were, and
`rotar` as a method of the class it lived in, for tests/test_rotation.py to compare with. Not imported by anything else.
Run with `exec` in a namespace that has `re`, `os`, `leer`, `escribir`, `igual`, `Cerrojo`."""
import os, re

LIMITE_LINEAS, LIMITE_BYTES = 1500, 100_000

def motivo_rotacion(t, hoy, por_anio=True):
    """Por qué hay que archivar un registro antes de escribir en él, o None: pasa de 1.500 líneas o de 100 KB, o su entrada
    más nueva es de un año anterior al de hoy. Devuelve (motivo, año del archivado)."""
    anios = re.findall(r"^## (20\d\d)-\d\d-\d\d", t, re.M)
    if not anios:
        return None
    anio = max(anios)
    if t.count("\n") + 1 > LIMITE_LINEAS:
        return f"pasa de {LIMITE_LINEAS} líneas", anio
    if len(t.encode("utf-8")) > LIMITE_BYTES:
        return f"pasa de {LIMITE_BYTES // 1000} KB", anio
    if por_anio and anio < hoy[:4]:
        return "cambió el año", anio
    return None


def nombre_archivado(carpeta, nombre, anio):
    """«decisiones-2026.md»; si ya existe, «decisiones-2026-2.md», «-3»…"""
    k, n = 1, f"{nombre}-{anio}.md"
    while (carpeta / n).exists():
        k += 1; n = f"{nombre}-{anio}-{k}.md"
    return n


def entradas_de(t):
    """Las entradas «## …» de un registro, en orden, cada una con su texto sin los saltos del final."""
    return [x.rstrip("\n") for x in re.split(r"^(?=## )", t, flags=re.M) if x.startswith("## ")]


def archivados_en(carpeta, nombre):
    """Todos los archivados de un registro que hay en la carpeta, de más viejo a más nuevo (también los hechos a mano)."""
    vistos = []
    for x in carpeta.iterdir():
        m = re.match(r"^" + nombre + r"-(20\d\d)(?:-(\d+))?\.md$", x.name)
        if m:
            vistos.append((int(m.group(1)), int(m.group(2) or 1), x.name))
    return [n for *_, n in sorted(vistos)]


def registro_nuevo(t, nombre, archivado, hoy, carpeta):
    """El registro vivo recién abierto: su cabecera, su título y la línea «Archivado:» con todos sus archivados, de más
    viejo a más nuevo, para quien lo abra sin el plugin. Las entradas siguen en el archivado, con su identificador."""
    titulo_ = (re.search(r"^# .*$", t, re.M) or [f"# {nombre.capitalize()}"])[0]
    # los que nombraba la línea anterior (sin consola, la copia puede no tenerlos todos) y los que hay en la carpeta
    linea = (re.search(r"^Archivado:.*$", t, re.M) or [""])[0]
    clave = lambda n: tuple(int(x) for x in re.findall(r"\d+", n))
    todos = sorted(set(re.findall(r"\b(" + nombre + r"-20\d\d(?:-\d+)?\.md)", linea)) | set(archivados_en(carpeta, nombre)) | {archivado}, key=clave)
    return (f"---\nestado: vigente\nactualizado: {hoy}\n---\n{titulo_}\n\n"
            f"Archivado: {', '.join(todos)}. Las entradas anteriores están ahí y se citan igual, con su identificador.\n")


class Rotador:
    """Only what rotar uses of cerrar.py's Cierre."""

    def __init__(self, raiz, hoy):
        self.raiz, self.hoy, self.vistos, self.propios = raiz, hoy, set(), {}
        self.salida = {"escritos": [], "fallidos": []}

    def rel(self, p):
        return p.relative_to(self.raiz).as_posix()

    def ajeno(self, rel, firma):
        pass

    def rotar(self, p, nombre, por_anio=True):
        """Archiva el registro antes de escribir en él si toca (escribir.md, sección 8): lo copia entero a «<nombre>-<año>.md»
        y deja el vivo con su cabecera, su título y la línea «Archivado:». Bajo el mismo cerrojo que las escrituras. Si ya
        hay un archivado idéntico (una rotación que no llegó a encoger el vivo), no lo duplica: solo encoge el vivo. Si el
        vivo cambia entre medias o no se puede escribir, el archivado recién creado se borra y no queda nada a medias."""
        rel = self.rel(p)
        try:
            # una mirada rápida, sin cerrojo: por el tamaño, y si es pequeño, su texto (que entonces cabe en 100 KB)
            if os.stat(p).st_size <= LIMITE_BYTES:
                with open(p, "rb") as f_:
                    if not motivo_rotacion(f_.read().decode("utf-8-sig", errors="replace"), self.hoy, por_anio):
                        return
            with Cerrojo(p):
                t, firma, crlf = leer(p)
                m = motivo_rotacion(t, self.hoy, por_anio)
                if not m:
                    return
                if rel not in self.vistos:
                    self.ajeno(rel, firma); self.vistos.add(rel)
                n_ent = len(re.findall(r"^## ", t, re.M))
                # el archivado lleva cabecera aunque el vivo no la tuviera: un archivado no se edita después
                # sin barras dentro de las llaves de un f-string: Python anterior a 3.12 no lo admite (1.23.1)
                mas_nueva = max(re.findall(r"^## (20\d\d-\d\d-\d\d)", t, re.M))
                arch_txt = t if re.match(r"^---\n", t) else f"---\nestado: vigente\nactualizado: {mas_nueva}\n---\n" + t
                # un archivado del mismo año cuyas entradas están todas en el vivo es una rotación que no llegó a encoger el
                # vivo (o se devolvió a medias y después alguien escribió): no se duplica, y el vivo se queda con lo que el
                # archivado no tiene (revisión de la 1.23, segunda vuelta)
                ents_vivo = entradas_de(t)
                igual_a = None
                for x in archivados_en(p.parent, nombre):
                    if not x.startswith(f"{nombre}-{m[1]}"):
                        continue
                    ea = entradas_de((p.parent / x).read_text(encoding="utf-8-sig", errors="replace").replace("\r\n", "\n"))
                    if ea and all(e in ents_vivo for e in ea):
                        igual_a, quedan = x, [e for e in ents_vivo if e not in ea]
                        break
                creado = None
                if igual_a:
                    arch = igual_a
                else:
                    arch = nombre_archivado(p.parent, nombre, m[1])
                    creado = p.parent / arch
                    fd = os.open(creado, os.O_WRONLY | os.O_CREAT | os.O_EXCL)   # nunca encima de un archivado que ya existe
                    with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
                        f.write(arch_txt.replace("\n", "\r\n") if crlf else arch_txt)
                try:
                    if not igual(p, firma):
                        raise OSError("el registro cambió mientras se archivaba; se archiva en el próximo cierre")
                    nuevo_vivo = registro_nuevo(t, nombre, arch, self.hoy, p.parent)
                    if igual_a and quedan:
                        nuevo_vivo = nuevo_vivo.rstrip("\n") + "\n\n" + "\n\n".join(quedan) + "\n"
                    self.propios[rel] = escribir(p, nuevo_vivo, crlf)
                except OSError:
                    if creado:
                        creado.unlink(missing_ok=True)
                    raise
                if creado:
                    self.propios[self.rel(creado)] = os.stat(creado).st_mtime_ns
                    self.salida["escritos"].append(self.rel(creado))
                self.salida["escritos"].append(rel)
                self.salida.setdefault("rotados", []).append({"de": rel, "a": self.rel(p.parent / arch), "motivo": m[0], "entradas": n_ent,
                                                             **({"ya_estaba": True} if igual_a else {})})
        except (OSError, UnicodeDecodeError) as ex:
            self.salida["fallidos"].append({"ruta": rel, "motivo": f"al archivar: {ex}"})
