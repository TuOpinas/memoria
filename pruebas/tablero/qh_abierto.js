// Entregables y Taller de «Qué hay» siguen abiertos después de ver una pieza y cerrarla (1.25.2): abrir la pieza
// redibuja la página, y antes los dos desplegables se cerraban. Uso: node qh_abierto.js <completo.html>. Sale con 1 si falla.
const { chromium } = require('playwright');
(async () => {
  const exe = process.env.CHROMIUM || undefined;
  const b = await chromium.launch(exe ? { executablePath: exe } : {});
  const p = await b.newPage();
  await p.goto('file://' + require('path').resolve(process.argv[2]) + '#p-ventas--cuentas-t-quehay');
  await p.waitForTimeout(500);
  let fallos = 0;
  const abierto = g => p.evaluate(s => { const x = document.querySelector(s); return !!(x && x.closest('details').open); }, `summary[data-qh-open$="|${g}"]`);
  for (const g of ['Entregables', 'Taller']) { await p.click(`summary[data-qh-open$="|${g}"]`); await p.waitForTimeout(200); }
  await p.locator('summary[data-qh-open$="|Entregables"] ~ div button').first().click(); await p.waitForTimeout(400);
  await p.keyboard.press('Escape'); await p.waitForTimeout(300);
  for (const g of ['Entregables', 'Taller']) {
    const bien = await abierto(g);
    console.log((bien ? '  bien  ' : '  FALLA ') + `${g} sigue abierto después de ver una pieza y cerrarla`);
    fallos += bien ? 0 : 1;
  }
  await b.close();
  process.exit(fallos ? 1 : 0);
})();
