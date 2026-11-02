#!/usr/bin/env python3
"""El tablero de mentira para los evals (1.24.8): las herramientas del conector claude-artifacts que la apertura usa
(list_artifacts, db_query, db_get, read_file y db_write) como un servidor MCP en el proceso del eval, con la cola
`cambios` que trae el escenario (`tablero: <archivo .json de escenarios/>`).

El archivo es {"organizacion": "...", "cambios": [{"id": "...", "data": {...}}, ...], "meta": {"permisos": {...}}}.
`read_file` dice que los archivos no existen: sin propuestas y sin página que partir. Lo que se escribe con db_write se
apunta en `escritos` para las comprobaciones, y se aplica a la cola.
"""
import json

from claude_agent_sdk import create_sdk_mcp_server, tool

SLUG = "00000000-0000-4000-8000-000000000001"


class TableroFalso:
    def __init__(self, datos):
        self.org = datos.get("organizacion", "Organización de prueba")
        self.cambios = {c["id"]: dict(c["data"]) for c in datos.get("cambios", [])}
        self.versiones = {k: 1 for k in self.cambios}
        self.meta = datos.get("meta", {})
        self.escritos = []

    def _json(self, d, error=False):
        return {"content": [{"type": "text", "text": json.dumps(d, ensure_ascii=False)}], **({"is_error": True} if error else {})}

    async def list_artifacts(self, args):
        return self._json({"artifacts": [{"slug": SLUG, "title": f"Tablero {self.org}", "version": "1-a", "rel": "mine"}]})

    def _cumple(self, d, where):
        if isinstance(where, dict):
            where = [{"field": k, "op": "==", "value": v} for k, v in where.items()]
        for w in where or []:
            v = d.get(w.get("field"))
            if w.get("op") in ("==", "eq") and v != w.get("value"):
                return False
        return True

    async def db_query(self, args):
        if args.get("collection") != "cambios":
            return self._json({"docs": [], "nextCursor": ""})
        docs = [{"id": k, "data": d, "version": self.versiones[k]} for k, d in self.cambios.items() if self._cumple(d, args.get("where"))]
        return self._json({"count": len(docs), "nextCursor": "", "docs": docs})

    async def db_get(self, args):
        col, _, i = (args.get("path") or "").partition("/")
        if col == "meta" and i in self.meta:
            return self._json({"exists": True, "version": 1, "data": self.meta[i]})
        if col == "cambios" and i in self.cambios:
            return self._json({"exists": True, "version": self.versiones[i], "data": self.cambios[i]})
        return self._json({"exists": False})

    async def read_file(self, args):
        return self._json({"error": "not_found: el archivo no existe en este artifact"}, error=True)

    async def db_write(self, args):
        for op in args.get("ops") or []:
            self.escritos.append(op)
            col, _, i = (op.get("path") or "").partition("/")
            if col != "cambios":
                continue
            if op.get("op") == "delete":
                self.cambios.pop(i, None)
            else:
                self.cambios.setdefault(i, {}).update(op.get("data") or {})
                self.versiones[i] = self.versiones.get(i, 0) + 1
        return self._json({"ok": True})

    def servidor(self):
        t = [
            tool("list_artifacts", "Lista los artifacts de la cuenta.", {"limit": int})(self.list_artifacts),
            tool("db_query", "Consulta una colección de la base de un artifact (slug, collection, where, limit).", {"slug": str, "collection": str, "where": list, "limit": int})(self.db_query),
            tool("db_get", "Lee un documento de la base de un artifact (slug, path).", {"slug": str, "path": str})(self.db_get),
            tool("read_file", "Lee archivos de un artifact (slug, path o paths).", {"slug": str, "path": str, "paths": list})(self.read_file),
            tool("db_write", "Escribe documentos en la base de un artifact (slug, ops).", {"slug": str, "ops": list})(self.db_write),
        ]
        return create_sdk_mcp_server(name="claude-artifacts", version="1.0.0", tools=t)
