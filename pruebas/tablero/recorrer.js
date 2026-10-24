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
    ['area', '#a-ventas'], ['area-restringida', '#a-personas'], ['area-sin-acceso', '#a-legal'], ['proy-sin-acceso', '#p-ventas--ronda'],
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
    // las propuestas del barrido viven en la cola pero no cuentan como lo marcado aquí; salen en «la memoria al día», y las descartadas no
    const prop = await p.evaluate(async () => { const b = document.querySelector('[data-mt-open="ventas--cuentas"]'); if(!b) return null; b.click(); await new Promise(r => setTimeout(r, 250)); const m = document.querySelector('.modal'); return m ? m.textContent : ''; });
    await p.keyboard.press('Escape');
    if(prop === null || !/Propuestas de la memoria/.test(prop) || !/PRUEBA-PROPUESTA-VIVA/.test(prop) || /PRUEBA-PROPUESTA-DESCARTADA/.test(prop) || !/2 cosas marcadas aquí/.test(prop)) errores.push(`${etiqueta}: las propuestas del barrido no salen en «la memoria al día», o salen las descartadas, o cuentan como marcadas aquí (${prop === null ? 'sin ventana' : prop.slice(0, 120)})`);
    await p.goto(url + '#p-ventas--cuentas-t-resumen'); await p.waitForTimeout(400);
    const donde = await p.evaluate(() => [...document.querySelectorAll('.brief p')].map(x=>x.textContent).join(' | '));
    if(!/Última sesión .*Lo último decidido/.test(donde)) errores.push(`${etiqueta}: el Resumen del proyecto no abre con «Dónde está» (${donde.slice(0,80)})`);
    // «Qué hay» (1.21): la pestaña del proyecto con inventario, afirma, señales y trayectoria; nunca el cuerpo del taller; y la suma en el área
    await p.goto(url + '#p-ventas--cuentas-t-quehay'); await p.waitForTimeout(600);
    const qh = await p.evaluate(() => { const t = document.getElementById('main').textContent; return { tab: !!document.querySelector('.tab[data-tab="quehay"][aria-selected="true"]'), pz: document.querySelectorAll('.qh-pz').length, taller: /Precio de la fase 2/.test(t), afirma: /por encima del piloto/.test(t), sinAf: /Sin «afirma»/.test(t), tray: document.querySelectorAll('.qh-tray li').length, flecha: /→/.test(t), paso: /la nombra un paso/.test(t), fuga: /TALLER-PRIVADO/.test(document.documentElement.outerHTML), cuerpo: /Cuerpo que el tablero no lee/.test(t) }; });
    if(!(qh.tab && qh.pz >= 5 && qh.taller && qh.afirma && qh.sinAf && qh.tray === 2 && qh.flecha && qh.paso && !qh.fuga && !qh.cuerpo)) errores.push(`${etiqueta}: la pestaña «Qué hay» no enseña el inventario, el afirma, las señales y la trayectoria, o filtra el cuerpo del taller (${JSON.stringify(qh)})`);
    if(etiqueta === 'completo-claro') await p.screenshot({ path: path.join(out, `${etiqueta}-que-hay.png`), fullPage: true });
    await p.goto(url + '#a-ventas'); await p.waitForTimeout(400);
    const qha = await p.evaluate(() => ({ tabla: document.querySelectorAll('.qh-sum tbody tr').length, giro: /Cliente Uno se sigue atendiendo/.test((document.querySelector('.qh-sum')||{}).textContent||'') }));
    if(!(qha.tabla >= 2 && qha.giro)) errores.push(`${etiqueta}: el área no suma «Qué hay» de sus proyectos con el último giro (${JSON.stringify(qha)})`);
    await p.click('.qh-sum [data-go-proj][data-tab="quehay"]'); await p.waitForTimeout(300);
    if(!(await p.evaluate(() => /-t-quehay$/.test(location.hash)))) errores.push(`${etiqueta}: la fila de «Qué hay» del área no abre la pestaña del proyecto`);
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
  // un tablero que era público, ya puesto al día con la 1.18: Inicio lo dice, con lo que implica
  {
    const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await ctx.newPage();
    p.on('pageerror', e => errores.push(`migrado: ${e.message}`));
    await p.goto('file://' + path.resolve(dir, 'migrado.html')); await p.waitForTimeout(600);
    const banda = await p.evaluate(() => [...document.querySelectorAll('.stale')].map(x => x.textContent).join(' | '));
    if(!/un solo tablero por persona/.test(banda) || !/quítale el acceso/.test(banda)) errores.push(`migrado: Inicio no avisa de que el tablero pasó a mostrarlo todo (${banda.slice(0, 200)})`);
    const titulo = await p.title();
    if(/completo/.test(titulo)) errores.push(`migrado: el título sigue diciendo «completo» (${titulo})`);
    await p.screenshot({ path: path.join(out, 'migrado.png') });
    await ctx.close();
  }
  // cierres de sesión después de la última sincronización: al abrirlo no lanza nada (1.19), avisa arriba con el botón
  {
    const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await ctx.newPage();
    p.on('pageerror', e => errores.push(`cierres: ${e.message}`));
    const url = 'file://' + path.resolve(dir, 'completo-cierres.html');
    await p.goto(url); await p.waitForTimeout(600);
    const r = await p.evaluate(() => ({ llamadas: (window.__llamadas || []).length, banda: [...document.querySelectorAll('.stale')].map(x => x.textContent).join(' | ') }));
    if(r.llamadas !== 0 || !/2 sesiones cerradas.*Cuentas, Soporte.*Sincronizar ahora/.test(r.banda)) errores.push(`cierres: al abrir con dos cierres pendientes tiene que avisar con el botón y no lanzar nada (${JSON.stringify(r).slice(0, 300)})`);
    await p.screenshot({ path: path.join(out, 'completo-cierres.png') });
    await p.reload(); await p.waitForTimeout(600);
    const r2 = await p.evaluate(() => (window.__llamadas || []).length);
    if(r2 !== 0) errores.push(`cierres: al volver a abrir, la misma tanda de cierres se lanzó otra vez (${r2})`);
    await ctx.close();
  }
  // un cierre que llega con el tablero abierto no lanza nada (desde la 1.19 nada se pone al día solo): sale el aviso con su botón
  {
    const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await ctx.newPage();
    p.on('pageerror', e => errores.push(`abierto: ${e.message}`));
    await p.goto('file://' + path.resolve(dir, 'completo.html')); await p.waitForTimeout(600);
    await p.evaluate(() => {
      window.__D.meta.estado.sincronizado = new Date(Date.now() - 3600000).toISOString();
      (window.__D.cierres = window.__D.cierres || {})['ventas--cuentas--x'] = { proyecto: 'ventas--cuentas', nombre: 'Cuentas', hora: new Date(Date.now() - 120000).toISOString().slice(0, 16) + 'Z', cuenta: 'ana@ejemplo.test' };
      window.__emitir('meta/estado'); window.__emitir('cierres');
    });
    await p.waitForTimeout(400);
    await p.evaluate(() => window.dispatchEvent(new Event('focus')));
    await p.waitForTimeout(300);
    const r = await p.evaluate(() => ({ llamadas: (window.__llamadas || []).length, banda: [...document.querySelectorAll('.stale')].map(x => x.textContent).join(' | ') }));
    if(r.llamadas !== 0) errores.push(`abierto: un cierre que llega con la página abierta, o volver a la pestaña, lanzó la puesta al día (${r.llamadas})`);
    if(!/1 sesión cerrada.*Cuentas.*Sincronizar ahora/.test(r.banda)) errores.push(`abierto: no avisa con el botón del cierre que llegó con la página abierta (${r.banda.slice(0, 200)})`);
    await ctx.close();
  }
  // el detalle de un proyecto (bitácora vieja, estado entero, porqués) se vuelve a traer cuando el proyecto cambia en la
  // base con la página abierta: una sincronización que mueve una sesión al detalle no la hace desaparecer (1.19)
  {
    const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await ctx.newPage();
    p.on('pageerror', e => errores.push(`detalle: ${e.message}`));
    await p.goto('file://' + path.resolve(dir, 'completo.html') + '#p-ventas--cuentas-t-bitacora'); await p.waitForTimeout(800);
    const fechas = () => p.evaluate(() => [...document.querySelectorAll('#main article.dec time')].map(t => t.textContent));
    const antes = await fechas();
    if(antes.length !== 2) errores.push(`detalle: la bitácora de Cuentas tenía que enseñar dos sesiones, una del proyecto y otra del detalle (${antes.join(', ')})`);
    const pie = await p.evaluate(() => [...document.querySelectorAll('#main .more')].map(x => x.textContent).join(' | '));
    if(/Las 1 entradas/.test(pie)) errores.push(`detalle: el pie de la bitácora cuenta mal (${pie.slice(0, 120)})`);
    await p.evaluate(() => {
      const D = window.__D, pr = D.proyectos['ventas--cuentas'], de = D.detalle['ventas--cuentas'];
      de.sesiones = pr.sesiones.concat(de.sesiones || []);
      pr.sesiones = [{ fecha: '2026-10-20', titulo: '2026-10-20 (cierre nuevo)', trabajamos: 'NUEVA-SESION en la llamada.', avances: 'cerrada', pendiente: '' }];
      pr.sesiones_total = 3; pr.sesiones_registro = 3; pr.huella = 'otra'; de.huella = 'otra';
      window.__emitir('proyectos');
    });
    await p.waitForTimeout(800);
    const despues = await fechas();
    if(despues.length !== 3 || !(await p.evaluate(() => document.querySelector('#main').textContent.includes('NUEVA-SESION')))) errores.push(`detalle: tras cambiar el proyecto en la base, la bitácora tenía que enseñar tres sesiones con la nueva (${despues.join(', ')})`);
    // un detalle que la base no tiene no se pinta como vacío
    await p.evaluate(() => { delete window.__D.detalle['ventas--cuentas']; window.__D.proyectos['ventas--cuentas'].huella = 'otra-mas'; window.__emitir('proyectos'); });
    await p.waitForTimeout(600);
    const txt = await p.evaluate(() => document.querySelector('#main').textContent);
    if(!/No se pudo traer el detalle/.test(txt)) errores.push(`detalle: sin el documento de detalle, la bitácora tenía que decirlo y no pintarse vacía`);
    await ctx.close();
  }
  await b.close();
  console.log(errores.length ? errores.join('\n') : 'La página no dio ningún error.');
  process.exit(errores.length ? 1 : 0);
})();
