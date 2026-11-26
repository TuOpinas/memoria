// Ejemplo de CONFIG con «CORREDOR: vitest» (kit de desarrollo): va en la carpeta de las pruebas de aceptación
// (tests/aceptacion/vitest.config.ts) y no lee nada de fuera de ella. envDir: los .env de la raíz no entran.
// Si el package.json no lleva "type": "module", sirve igual con el nombre vitest.config.mts.
import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

const aqui = fileURLToPath(new URL(".", import.meta.url));

export default defineConfig({
  envDir: aqui,
  test: { dir: aqui }, // dir: el control pasa «--root .»
});
