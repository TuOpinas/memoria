#!/usr/bin/env python3
"""La computadora de mentira para los evals: las herramientas del dispositivo (get_device_info, device_list_dir,
device_bash, device_stage_files, device_commit_files y las de permisos) como un servidor MCP en el proceso del
eval, sobre una carpeta del contenedor que hace de raíz en «la computadora».

Dos modos. Con consola: device_bash corre bash con un $HOME propio en el que la raíz está montada en
$HOME/mnt/<padre>--<nombre>, como la app en Mac. Sin consola: el mismo bash, pero sin nada bajo $HOME/mnt, como
Google Drive para escritorio en Windows; device_list_dir, device_stage_files y device_commit_files sí llegan a la
raíz, que es lo que el plugin usa entonces (anexo sin-consola.md).

Lo que device_stage_files copia va a /mnt/user-data/uploads/<nombre de la raíz>/, que es donde el plugin lo espera.
"""
import asyncio
import json
import re
import os
import pathlib
import shutil
import subprocess
import time

from claude_agent_sdk import create_sdk_mcp_server, tool


class Dispositivo:
    def __init__(self, raiz_real, nombre, consola=True, plataforma="darwin", hogar=None, uploads="/mnt/user-data/uploads"):
        self.raiz = pathlib.Path(raiz_real).resolve()
        self.nombre = nombre
        self.consola = consola
        self.plataforma = plataforma
        # la ruta que «la computadora» da a la carpeta, como la vería la persona
        self.ruta_disp = (f"C:/Users/prueba/Documents/Memoria/{nombre}" if plataforma == "win32"
                          else f"/Users/prueba/Documents/Memoria/{nombre}")
        self.hogar = pathlib.Path(hogar or (self.raiz.parent / "hogar")).resolve()
        self.hogar.mkdir(parents=True, exist_ok=True)
        (self.hogar / "mnt").mkdir(exist_ok=True)
        monte = self.hogar / "mnt" / f"Memoria--{nombre}"
        if consola:
            if monte.is_symlink() or monte.exists():
                monte.unlink()
            monte.symlink_to(self.raiz)
        elif monte.is_symlink():
            monte.unlink()
        self.uploads = pathlib.Path(uploads) / nombre
        self.llamadas = []   # (herramienta, argumentos) en orden, para los evals
        self.staged = {}     # stagedPath -> devicePath
        self.borrar = False  # como la computadora: rm no funciona hasta que se concede el permiso

    # --- rutas ---
    def real(self, ruta):
        r = str(ruta).replace("\\", "/")
        if r.startswith("~/"):
            r = r.replace("~", self.ruta_disp.rsplit("/Documents", 1)[0], 1)
        base = self.ruta_disp
        rel = None
        if r == base or r.startswith(base + "/"):
            rel = r[len(base):].lstrip("/")
        else:
            # lo que dice device_bash ($HOME/mnt/...) también vale
            m = f"mnt/Memoria--{self.nombre}"
            if m in r:
                rel = r.split(m, 1)[1].lstrip("/")
        if rel is None:
            return None
        p = (self.raiz / rel).resolve() if rel else self.raiz
        # nunca fuera de la raíz, como la herramienta real
        try:
            p.relative_to(self.raiz)
        except ValueError:
            return None
        return p

    def disp(self, real):
        rel = pathlib.Path(real).resolve().relative_to(self.raiz).as_posix()
        return f"{self.ruta_disp}/{rel}" if rel != "." else self.ruta_disp

    # --- herramientas ---
    async def get_device_info(self, args):
        self.llamadas.append(("get_device_info", args))
        return self._json({"platform": self.plataforma, "arch": "arm64", "appVersion": "3.6556.2", "deviceName": "pc-de-prueba",
                           "connectedFolders": [self.ruta_disp],
                           "homeDirectories": [{"name": "Documents", "requiresGrantBeforeListing": True}, {"name": "Downloads"}],
                           "localMcpServers": [], "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})

    async def device_list_dir(self, args):
        self.llamadas.append(("device_list_dir", args))
        p = self.real(args.get("path", ""))
        if p is None or not p.is_dir():
            return self._json({"error": f"No es una carpeta conectada: {args.get('path')}"}, error=True)
        out, tope = [], 5 if args.get("recursive") else 0
        for d, dirs, fs in os.walk(p):
            prof = len(pathlib.Path(d).relative_to(p).parts)
            if prof > tope:
                dirs[:] = []
                continue
            for n in sorted(dirs):
                out.append({"name": pathlib.Path(d, n).relative_to(p).as_posix(), "type": "dir", **({"depth": prof} if prof else {})})
            for n in sorted(fs):
                st = pathlib.Path(d, n).stat()
                out.append({"name": pathlib.Path(d, n).relative_to(p).as_posix(), "type": "file", "size": st.st_size, "mtimeMs": int(st.st_mtime * 1000), **({"depth": prof} if prof else {})})
            if not args.get("recursive"):
                dirs[:] = []
        return self._json({"entries": out[:2000], **({"truncated": True} if len(out) > 2000 else {})})

    async def device_bash(self, args):
        self.llamadas.append(("device_bash", args))
        cmd = args.get("command", "")
        if not self.borrar and re.search(r"(^|[;&|\s])(rm|rmdir|unlink)\s", cmd + " ") and f"mnt/Memoria--{self.nombre}" in cmd:
            return {"content": [{"type": "text", "text": "rm: Operation not permitted\n[exit 1]"}]}
        env = {"HOME": str(self.hogar), "PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "C.UTF-8", "TZ": "America/Mexico_City"}
        try:
            r = subprocess.run(["bash", "-c", args.get("command", "")], cwd=self.hogar, env=env, capture_output=True, text=True,
                               timeout=min(int(args.get("timeout_ms") or 120000), 180000) / 1000)
            salida = r.stdout + (("\n" + r.stderr) if r.stderr else "")
            if r.returncode:
                salida += f"\n[exit {r.returncode}]"
        except subprocess.TimeoutExpired:
            salida = "[timeout]"
        return {"content": [{"type": "text", "text": salida or "(sin salida)"}]}

    async def device_stage_files(self, args):
        self.llamadas.append(("device_stage_files", args))
        out = []
        for ruta in args.get("paths") or []:
            p = self.real(ruta)
            if p is None or not p.is_file():
                return self._json({"error": f"No existe o no es un archivo: {ruta}"}, error=True)
            dest = self.uploads / p.relative_to(self.raiz)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, dest)   # como la herramienta real: la fecha de la copia es la de la traída
            st = p.stat()
            self.staged[str(dest)] = self.disp(p)
            out.append({"devicePath": self.disp(p), "stagedPath": str(dest), "mtimeMs": int(st.st_mtime * 1000), "bytes": st.st_size, "ok": True})
        return self._json({"staged": out})

    async def device_commit_files(self, args):
        self.llamadas.append(("device_commit_files", args))
        escritos, rechazados = [], []
        for f in args.get("files") or []:
            dp, sp = f.get("devicePath"), f.get("stagedPath")
            p = self.real(dp or "")
            if p is None:
                rechazados.append({"devicePath": dp, "reason": "fuera de las carpetas conectadas"}); continue
            if not sp or not pathlib.Path(sp).is_file():
                rechazados.append({"devicePath": dp, "reason": "stagedPath no existe"}); continue
            esperado = f.get("expectedMtimeMs")
            if esperado is not None and p.exists() and not args.get("force") and abs(int(p.stat().st_mtime * 1000) - int(esperado)) > 1:
                rechazados.append({"devicePath": dp, "reason": "mtime-drift", "deviceMtimeMs": int(p.stat().st_mtime * 1000), "deviceBytes": p.stat().st_size}); continue
            p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(sp, p)
            escritos.append(dp)
        return self._json({"written": escritos, "rejected": rechazados})

    async def device_request_folder_access(self, args):
        self.llamadas.append(("device_request_folder_access", args))
        return self._json({"granted": [self.ruta_disp]})

    async def device_request_delete_permission(self, args):
        self.llamadas.append(("device_request_delete_permission", args))
        self.borrar = True
        return self._json({"granted": args.get("paths") or []})

    def _json(self, d, error=False):
        return {"content": [{"type": "text", "text": json.dumps(d, ensure_ascii=False)}], **({"is_error": True} if error else {})}

    def servidor(self):
        t = [
            tool("get_device_info", "Información de la computadora conectada: plataforma y carpetas conectadas.", {})(self.get_device_info),
            tool("device_list_dir", "Lista una carpeta de la computadora (path; recursive opcional).", {"path": str, "recursive": bool})(self.device_list_dir),
            tool("device_bash", "Corre un comando de shell en la computadora (command; timeout_ms opcional).", {"command": str, "timeout_ms": int})(self.device_bash),
            tool("device_stage_files", "Copia archivos de la computadora al contenedor, en /mnt/user-data/uploads/<carpeta>/ (paths).", {"paths": list})(self.device_stage_files),
            tool("device_commit_files", "Escribe archivos del contenedor en la computadora (files: [{devicePath, stagedPath, expectedMtimeMs?}], force?).", {"files": list, "force": bool})(self.device_commit_files),
            tool("device_request_folder_access", "Pide acceso a carpetas de la computadora (paths, reason).", {"paths": list, "reason": str})(self.device_request_folder_access),
            tool("device_request_delete_permission", "Pide permiso para borrar en carpetas conectadas (paths, reason).", {"paths": list, "reason": str})(self.device_request_delete_permission),
        ]
        return create_sdk_mcp_server(name="remote-devices", version="1.0.0", tools=t)


if __name__ == "__main__":
    import sys
    d = Dispositivo(sys.argv[1], "Prueba", consola="--sin-consola" not in sys.argv)
    print(asyncio.run(d.get_device_info({})))
    print(asyncio.run(d.device_bash({"command": "ls $HOME/mnt"})))
