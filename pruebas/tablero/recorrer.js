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
    // un área con todos sus proyectos cerrados no sale en Inicio ni en el lateral hasta pedirla; sus entregables siguen
    await p.goto(url + '#'); await p.waitForTimeout(400);
    const arch = await p.evaluate(() => ({ inicio: [...document.querySelectorAll('.ar-i b')].some(x=>x.textContent==='Archivo'), lateral: [...document.querySelectorAll('.side-i.area span')].some(x=>x.textContent==='Archivo'), boton: !!document.querySelector('[data-arch]') }));
    if(arch.inicio || arch.lateral || !arch.boton) errores.push(`${etiqueta}: el área archivada se ve sin pedirla o falta el botón para mostrarla (${JSON.stringify(arch)})`);
    await p.click('.ar + .more [data-arch]'); await p.waitForTimeout(300);
    if(!(await p.evaluate(() => [...document.querySelectorAll('.ar-i b')].some(x=>x.textContent==='Archivo')))) errores.push(`${etiqueta}: «Mostrar el área archivada» no la muestra`);
    await p.click('.ar + .more [data-arch]'); await p.waitForTimeout(200);
    await p.goto(url + '#entregables'); await p.waitForTimeout(400);
    if(!(await p.evaluate(() => document.body.textContent.includes('Inventario del sistema anterior') && document.querySelector('h1').textContent==='Entregables'))) errores.push(`${etiqueta}: la vista Entregables no se llama así o perdió lo publicado de un área archivada`);
    // el índice de la ayuda se recorre con su propio scroll sin mover el artículo (solo en escritorio)
    if((opciones.viewport||{}).width > 760){
      await p.goto(url + '#ayuda-ponerse-al-dia'); await p.waitForTimeout(400);
      const toc = await p.$('.hc-toc'); const bx = await toc.boundingBox();
      const y0 = await p.evaluate(() => scrollY);
      await p.mouse.move(bx.x + 40, bx.y + Math.min(200, bx.height/2));
      for(let i = 0; i < 6; i++){ await p.mouse.wheel(0, 150); await p.waitForTimeout(80); }
      const r = await p.evaluate(() => ({ y: scrollY, toc: document.querySelector('.hc-toc').scrollTop, flujo: !!document.querySelector('.hc-flujo') }));
      if(r.y !== y0 || !(r.toc > 0) || !r.flujo) errores.push(`${etiqueta}: recorrer el índice de la ayuda movió el artículo o falta el diagrama (${JSON.stringify(r)})`);
    }
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
