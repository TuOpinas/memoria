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
    ['resumen', '#p-ventas--cuentas-t-resumen'], ['ayuda-cuestionar', '#ayuda-cuestionar'], ['ayuda', '#ayuda'], ['ayuda-pasar-al-dia', '#ayuda-ponerse-al-dia'], ['ayuda-frases', '#ayuda-frases'], ['ayuda-carpeta', '#ayuda-ordenada'], ['ayuda-piezas', '#ayuda-piezas'], ['ayuda-sumar', '#ayuda-sumar'], ['ayuda-pasos', '#ayuda-pasos'],
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
    // cada área dice una sola cosa: el Panorama de su director si lo tiene, y si no, la línea calculada
    const voz = await p.evaluate(() => { const filas = [...document.querySelectorAll('.ar-i')].filter(x => x.querySelector('.ar-pan')); return { brief: !!document.querySelector('.brief p'), filas: filas.length, una: filas.every(x => (!!x.querySelector('.ar-dir')) !== (!!x.querySelector('.ar-ln'))), conPanorama: filas.some(x => x.querySelector('.ar-dir')), barras: document.querySelectorAll('.ar .spark').length }; });
    if(!(voz.brief && voz.filas >= 2 && voz.una && voz.barras >= 1)) errores.push(`${etiqueta}: Inicio no lleva el párrafo de la organización, cada área no dice una sola cosa (Panorama o línea de estado) o faltan las barras de actividad (${JSON.stringify(voz)})`);
    const atraso = await p.evaluate(() => [...document.querySelectorAll('.stale')].some(x => /La carpeta usa todavía la versión 1\.11\.0/.test(x.textContent)));
    if(!atraso) errores.push(`${etiqueta}: Inicio no avisa de que la carpeta usa una versión anterior del método`);
    const boton = await p.evaluate(() => { const b = document.querySelector('.sync-ico'); return b ? { pend: b.classList.contains('pend'), off: b.classList.contains('off') } : null; });
    if(!boton || boton.off || boton.pend) errores.push(`${etiqueta}: el botón cuenta como pendiente un cambio que la sincronización dejó a propósito, o no está (${JSON.stringify(boton)})`);
    await p.goto(url + '#p-ventas--cuentas-t-resumen'); await p.waitForTimeout(400);
    const donde = await p.evaluate(() => [...document.querySelectorAll('.brief p')].map(x=>x.textContent).join(' | '));
    if(!/Última sesión .*Lo último decidido/.test(donde)) errores.push(`${etiqueta}: el Resumen del proyecto no abre con «Dónde está» (${donde.slice(0,80)})`);
    await p.goto(url + '#p-operacion--soporte-t-resumen'); await p.waitForTimeout(400);
    const corto = await p.evaluate(() => ({ t: (document.querySelector('.corto .corto-t')||{}).textContent || '', n: document.querySelectorAll('.corto .corto-l li').length, detalle: !!document.querySelector('[data-est-full]'), dos: [...document.querySelectorAll('.corto .corto-l li')].some(x=>/Beto las prueba el 24/.test(x.textContent)) }));
    if(!(corto.t.startsWith('Terminamos la lista') && corto.n === 3 && corto.detalle && corto.dos)) errores.push(`${etiqueta}: un proyecto con «En corto» no abre con «Cómo va» y el detalle plegado (${JSON.stringify(corto)})`);
    if(etiqueta === 'completo-claro') await p.screenshot({ path: path.join(out, `${etiqueta}-como-va.png`) });
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
  // cierres de sesión después de la última sincronización: al abrirlo, el dueño lo pone al día solo, una vez, y lo dice arriba
  {
    const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await ctx.newPage();
    p.on('pageerror', e => errores.push(`cierres: ${e.message}`));
    const url = 'file://' + path.resolve(dir, 'completo-cierres.html');
    await p.goto(url); await p.waitForTimeout(600);
    const r = await p.evaluate(() => ({ llamadas: (window.__llamadas || []).length, banda: [...document.querySelectorAll('.stale')].map(x => x.textContent).join(' | ') }));
    if(r.llamadas !== 1 || !/Poniéndose al día: hubo 2 sesiones .*Cuentas, Soporte/.test(r.banda)) errores.push(`cierres: al abrir con dos cierres pendientes no se pone al día solo una vez ni lo dice (${JSON.stringify(r).slice(0, 300)})`);
    await p.screenshot({ path: path.join(out, 'completo-cierres.png') });
    await p.reload(); await p.waitForTimeout(600);
    const r2 = await p.evaluate(() => (window.__llamadas || []).length);
    if(r2 !== 0) errores.push(`cierres: al volver a abrir, la misma tanda de cierres se lanzó otra vez (${r2})`);
    await ctx.close();
  }
  // la cola y los cierres los escribe la sesión sin filtrar: en el tablero público, un lector no ve nada de un
  // proyecto que el tablero no muestra, ni en Pendientes, ni en Inicio, ni en la banda de cierres
  {
    const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await ctx.newPage();
    p.on('pageerror', e => errores.push(`lector: ${e.message}`));
    const url = 'file://' + path.resolve(dir, 'publico-lector.html');
    for(const h of ['#', '#pendientes', '#a-ventas', '#p-ventas--cuentas-t-resumen']){
      await p.goto(url + h); await p.waitForTimeout(500);
      const t = await p.evaluate(() => document.body.innerText);
      if(/SECRETO-COLA|SECRETO-TITULO/.test(t)) errores.push(`lector: en ${h} se ve el texto de la cola o el título de un cierre de un proyecto que el tablero no muestra`);
    }
    await p.goto(url + '#'); await p.waitForTimeout(500);
    const banda = await p.evaluate(() => [...document.querySelectorAll('.stale')].map(x => x.textContent).join(' | '));
    if(!/2 sesiones cerradas.*Cuentas, 1 en proyecto que este tablero no muestra/.test(banda)) errores.push(`lector: la banda de cierres no dice lo justo (${banda.slice(0, 200)})`);
    await p.screenshot({ path: path.join(out, 'publico-lector.png') });
    await ctx.close();
  }
  await b.close();
  console.log(errores.length ? errores.join('\n') : 'La página no dio ningún error.');
  process.exit(errores.length ? 1 : 0);
})();
