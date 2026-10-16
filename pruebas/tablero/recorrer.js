// Recorre las páginas de prueba con Playwright: cada vista, cada ventana, en claro, oscuro y móvil.
// Uso: node recorrer.js <carpeta-con-las-páginas> <carpeta-de-capturas>. Sale con 1 si la página da algún error.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [dir, out] = process.argv.slice(2);
  const exe = process.env.CHROMIUM || undefined;
  const b = await chromium.launch(exe ? { executablePath: exe } : {});
  const errores = [];
  const vistas = [
    ['inicio', ''], ['pendientes', '#pendientes'], ['decisiones', '#decisiones'], ['entregables', '#entregables'],
    ['area', '#a-ventas'], ['area-restringida', '#a-personas'],
    ['proyecto', '#p-ventas--cuentas-t-estado'], ['acciones', '#p-ventas--cuentas-t-pasos'],
    ['proy-entregables', '#p-ventas--cuentas-t-entregables'], ['proy-decisiones', '#p-ventas--cuentas-t-decisiones'], ['bitacora', '#p-ventas--cuentas-t-bitacora'],
    ['proy-restringido', '#p-ventas--precios'],
    ['resumen', '#p-ventas--cuentas-t-resumen'], ['ayuda-cuestionar', '#ayuda-cuestionar'], ['ayuda', '#ayuda'], ['ayuda-pasar-al-dia', '#ayuda-ponerse-al-dia'], ['ayuda-frases', '#ayuda-frases'], ['ayuda-carpeta', '#ayuda-ordenada'],
  ];
  // ventanas y controles: se abren desde la vista indicada
  const acciones = [
    ['memoria-al-dia', '', '[data-mt-open]'], ['prioridad', '#a-ventas', '[data-prio-toggle]'],
    ['entregable', '#entregables', '[data-ent-open]'], ['estado', '#p-ventas--cuentas-t-estado', '.est-btn'],
    ['corregir-paso', '#p-ventas--cuentas-t-pasos', '.step-x'], ['fecha', '#p-ventas--cuentas-t-pasos', '[data-edit-due]'],
    ['decision', '#decisiones', '[data-dec-open]'],
    ['ayuda-desde-estado', '#p-ventas--cuentas-t-estado', '.hq'],
  ];
  async function pasada(pagina, etiqueta, opciones){
    const ctx = await b.newContext(opciones);
    const p = await ctx.newPage();
    p.on('pageerror', e => errores.push(`${etiqueta}: ${e.message}`));
    const url = 'file://' + path.resolve(dir, pagina);
    for(const [nombre, hash] of vistas){
      await p.goto(url + hash); await p.waitForTimeout(400);
      await p.screenshot({ path: path.join(out, `${etiqueta}-${nombre}.png`), fullPage: true });
    }
    for(const [nombre, hash, sel] of acciones){
      await p.goto(url + hash); await p.waitForTimeout(400);
      const el = await p.$(sel);
      if(!el){ errores.push(`${etiqueta}: no aparece ${sel} (${nombre})`); continue; }
      await el.click(); await p.waitForTimeout(250);
      await p.screenshot({ path: path.join(out, `${etiqueta}-${nombre}.png`) });
      await p.keyboard.press('Escape');
    }
    await p.goto(url + '#'); await p.waitForTimeout(400);
    const voz = await p.evaluate(() => ({ brief: !!document.querySelector('.brief p'), lineas: document.querySelectorAll('.ar-ln').length, barras: document.querySelectorAll('.ar .spark').length }));
    if(!(voz.brief && voz.lineas >= 2 && voz.barras >= 1)) errores.push(`${etiqueta}: Inicio no lleva el párrafo de la organización, las líneas de estado o las barras de actividad (${JSON.stringify(voz)})`);
    await p.goto(url + '#p-ventas--cuentas-t-resumen'); await p.waitForTimeout(400);
    const donde = await p.evaluate(() => [...document.querySelectorAll('.brief p')].map(x=>x.textContent).join(' | '));
    if(!/Última sesión .*Lo último decidido/.test(donde)) errores.push(`${etiqueta}: el Resumen del proyecto no abre con «Dónde está» (${donde.slice(0,80)})`);
    await p.goto(url + '#entregables'); await p.waitForTimeout(400);
    await p.click('[data-ent-open]'); await p.waitForTimeout(250);
    await p.click('.modal-f [data-go-proj]'); await p.waitForTimeout(300);
    if(!(await p.evaluate(() => location.hash.startsWith('#p-') && !document.querySelector('.modal')))) errores.push(`${etiqueta}: un enlace dentro de una ventana no navega`);
    await p.goto(url + '#ayuda'); await p.waitForTimeout(300);
    await p.evaluate(() => { const d = document.getElementById('hc-det'); if(d) d.open = true; });
    await p.fill('#hc-q', 'restringido'); await p.waitForTimeout(150);
    const n = await p.$$eval('#hc-list .hc-i', els => els.length);
    if(!(n > 0 && n < 22)) errores.push(`${etiqueta}: la búsqueda de la ayuda no filtra (${n} artículos)`);
    await p.click('#hc-list .hc-i'); await p.waitForTimeout(200);
    if(!(await p.evaluate(() => location.hash.startsWith('#ayuda-')))) errores.push(`${etiqueta}: un artículo de la ayuda no abre`);
    await ctx.close();
  }
  await pasada('completo.html', 'completo-claro', { viewport: { width: 1440, height: 900 }, colorScheme: 'light' });
  await pasada('completo.html', 'completo-oscuro', { viewport: { width: 1440, height: 900 }, colorScheme: 'dark' });
  await pasada('completo.html', 'completo-movil', { viewport: { width: 390, height: 844 }, colorScheme: 'light' });
  await pasada('publico.html', 'publico-claro', { viewport: { width: 1440, height: 900 }, colorScheme: 'light' });
  await b.close();
  console.log(errores.length ? errores.join('\n') : 'La página no dio ningún error.');
  process.exit(errores.length ? 1 : 0);
})();
