// Recorre las páginas de prueba con Playwright: cada vista, cada ventana, en claro, oscuro y móvil.
// Uso: node recorrer.js <carpeta-con-las-páginas> <carpeta-de-capturas>. Sale con 1 si la página da algún error.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [dir, out] = process.argv.slice(2);
  const exe = process.env.CHROMIUM || undefined;
  const b = await chromium.launch(exe ? { executablePath: exe } : {});
  const errores = [];
  // desde la 1.22.3 Inicio, área y proyecto tienen cuatro pestañas; «-t-» abre la del proyecto, y las de Inicio y área se pulsan
  const vistas = [
    ['inicio', ''], ['agenda', '#pendientes'], ['decisiones', '#decisiones'], ['entregables', '#entregables'],
    ['area', '#a-ventas'], ['area-restringida', '#a-personas'], ['area-sin-acceso', '#a-legal'], ['proy-sin-acceso', '#p-ventas--ronda'],
    ['proyecto', '#p-ventas--cuentas-t-estatus'], ['acciones', '#p-ventas--cuentas-t-pasos'], ['actividad', '#p-ventas--cuentas-t-registro'], ['que-hay', '#p-ventas--cuentas-t-quehay'],
    ['proy-restringido', '#p-ventas--precios'],
    ['ayuda-cuestionar', '#ayuda-cuestionar'], ['ayuda', '#ayuda'], ['ayuda-pasar-al-dia', '#ayuda-ponerse-al-dia'], ['ayuda-frases', '#ayuda-frases'], ['ayuda-carpeta', '#ayuda-ordenada'], ['ayuda-piezas', '#ayuda-piezas'], ['ayuda-sumar', '#ayuda-sumar'], ['ayuda-pasos', '#ayuda-pasos'],
  ];
  const pestanas = [['inicio', '', 'data-ini', ['estatus', 'acciones', 'actividad', 'mant']], ['area', '#a-ventas', 'data-atab', ['estatus', 'acciones', 'actividad', 'quehay']]];
  // ventanas y controles: se abren desde la vista indicada, con la pestaña que haga falta
  const acciones = [
    ['memoria-al-dia', '', '[data-mt-open]', '[data-ini="mant"]'], ['prioridad', '#a-ventas', '[data-prio-toggle]', '[data-atab="acciones"]'],
    ['entregable', '#entregables', '[data-ent-open]'], ['estado', '#p-ventas--cuentas-t-estatus', '.est-btn'],
    ['corregir-paso', '#p-ventas--cuentas-t-pasos', '.step-x'], ['fecha', '#p-ventas--cuentas-t-pasos', '[data-edit-due]'],
    ['decision', '#decisiones', '[data-dec-open]'],
    ['ayuda-desde-estado', '#p-ventas--cuentas-t-estatus', '.hq'],
  ];
  const abre = async (p, url, hash, pestana) => { await p.goto(url + '#'); await p.goto(url + hash); await p.waitForTimeout(400);
    if(pestana){ await p.click(pestana); await p.waitForTimeout(300); await p.evaluate(() => document.querySelectorAll('#main details').forEach(d => d.open = true)); } };
  async function pasada(pagina, etiqueta, opciones){
    const ctx = await b.newContext(opciones);
    const p = await ctx.newPage();
    p.on('pageerror', e => errores.push(`${etiqueta}: ${e.message}`));
    const url = 'file://' + path.resolve(dir, pagina);
    for(const [nombre, hash] of vistas){
      await p.goto(url + hash); await p.waitForTimeout(400);
      await p.screenshot({ path: path.join(out, `${etiqueta}-${nombre}.png`), fullPage: true });
    }
    for(const [nombre, hash, attr, tabs] of pestanas){
      for(const t of tabs){ await abre(p, url, hash, `[${attr}="${t}"]`);
        if(!(await p.evaluate(([a, t]) => !!document.querySelector(`[${a}="${t}"][aria-selected="true"]`), [attr, t]))) errores.push(`${etiqueta}: la pestaña ${t} de ${nombre} no se abre`);
        await p.screenshot({ path: path.join(out, `${etiqueta}-${nombre}-${t}.png`), fullPage: true }); }
    }
    for(const [nombre, hash, sel, pestana] of acciones){
      await abre(p, url, hash, pestana);
      const el = await p.$(sel);
      if(!el){ errores.push(`${etiqueta}: no aparece ${sel} (${nombre})`); continue; }
      await el.click(); await p.waitForTimeout(250);
      await p.screenshot({ path: path.join(out, `${etiqueta}-${nombre}.png`) });
      await p.keyboard.press('Escape');
    }
    // Inicio › Estatus: qué es la organización (primer párrafo de la guía), una ficha por área con su titular y ningún aviso de la herramienta
    await abre(p, url, '', '[data-ini="estatus"]');
    const ini = await p.evaluate(() => { const fichas = [...document.querySelectorAll('#main .area-card')]; return { que: /Raíz inventada para probar el tablero/.test((document.querySelector('.org-q')||{}).textContent||''), fichas: fichas.length,
      panorama: fichas.some(x => /una sola cuenta grande abierta/.test(x.textContent)), avisos: document.querySelectorAll('#main .stale').length, etiqueta: /Personal · no compartir/.test(document.body.textContent) }; });
    if(!(ini.que && ini.fichas >= 2 && ini.panorama && ini.avisos === 0 && !ini.etiqueta)) errores.push(`${etiqueta}: Inicio › Estatus no dice qué es la organización, le faltan fichas de área (el Panorama vale de titular), o enseña avisos o la etiqueta vieja (${JSON.stringify(ini)})`);
    // los avisos de la herramienta viven en Mantenimiento
    await abre(p, url, '', '[data-ini="mant"]');
    const atraso = await p.evaluate(() => [...document.querySelectorAll('#main .stale')].some(x => /La carpeta usa todavía la versión 1\.11\.0/.test(x.textContent)));
    if(!atraso) errores.push(`${etiqueta}: Mantenimiento no avisa de que la carpeta usa una versión anterior del método`);
    const boton = await p.evaluate(() => { const b = document.querySelector('.sync-ico'); return b ? { pend: b.classList.contains('pend'), off: b.classList.contains('off') } : null; });
    if(!boton || boton.off || boton.pend) errores.push(`${etiqueta}: el botón cuenta como pendiente un cambio que la sincronización dejó a propósito, o no está (${JSON.stringify(boton)})`);
    // las propuestas del barrido viven en la cola pero no cuentan como lo marcado aquí; salen en «la memoria al día», y las descartadas no
    const prop = await p.evaluate(async () => { const b = document.querySelector('[data-mt-open="ventas--cuentas"]'); if(!b) return null; b.click(); await new Promise(r => setTimeout(r, 250)); const m = document.querySelector('.modal'); return m ? m.textContent : ''; });
    await p.keyboard.press('Escape');
    if(prop === null || !/Propuestas de la memoria/.test(prop) || !/PRUEBA-PROPUESTA-VIVA/.test(prop) || /PRUEBA-PROPUESTA-DESCARTADA/.test(prop) || !/2 cosas marcadas aquí/.test(prop)) errores.push(`${etiqueta}: las propuestas del barrido no salen en «la memoria al día», o salen las descartadas, o cuentan como marcadas aquí (${prop === null ? 'sin ventana' : prop.slice(0, 120)})`);
    // Inicio › Acciones y Actividad
    await abre(p, url, '', '[data-ini="acciones"]');
    const acc = await p.evaluate(() => { const t = document.getElementById('main').textContent; return { toca: /Te toca a ti/.test(t), empezar: /Por dónde empezar/.test(t) }; });
    if(!acc.toca) errores.push(`${etiqueta}: Inicio › Acciones no abre con «Te toca a ti» (${JSON.stringify(acc)})`);
    await abre(p, url, '', '[data-ini="actividad"]');
    const act = await p.evaluate(() => { const t = document.getElementById('main').textContent; return { area: /Por área/.test(t), persona: /Por persona/.test(t), dias: !!document.querySelector('[data-act-dias]') }; });
    if(!(act.area && act.persona && act.dias)) errores.push(`${etiqueta}: Inicio › Actividad no trae «Por área», «Por persona» y el periodo (${JSON.stringify(act)})`);
    // el proyecto: Estatus arriba, con su titular
    await abre(p, url, '#p-ventas--cuentas-t-estatus');
    const est = await p.evaluate(() => ({ tab: !!document.querySelector('.tab[data-tab="estatus"][aria-selected="true"]'), tabs: [...document.querySelectorAll('#main .tab')].map(t => t.dataset.tab).join(','), corto: !!document.querySelector('#main .corto, #main .brief') }));
    if(!(est.tab && est.tabs === 'estatus,pasos,registro,quehay' && est.corto)) errores.push(`${etiqueta}: el proyecto no abre en Estatus con sus cuatro pestañas (${JSON.stringify(est)})`);
    // «Qué hay» (1.21): la pestaña del proyecto con inventario, aportación, señales y trayectoria; nunca el cuerpo del taller; y la suma en el área
    await abre(p, url, '#p-ventas--cuentas-t-quehay'); await p.waitForTimeout(300);
    const qh = await p.evaluate(() => { const t = document.getElementById('main').textContent; return { tab: !!document.querySelector('.tab[data-tab="quehay"][aria-selected="true"]'), pz: document.querySelectorAll('.qh-pz').length, taller: /Precio de la fase 2/.test(t), afirma: /por encima del piloto/.test(t), sinAf: /Sin aportación/.test(t), tray: document.querySelectorAll('.qh-tray li').length, flecha: /→/.test(t), resumen: /Lo publicado/.test(t) && /En el taller/.test(t), fuga: /TALLER-PRIVADO/.test(document.documentElement.outerHTML), cuerpo: /Cuerpo que el tablero no lee/.test(t) }; });
    if(!(qh.tab && qh.pz >= 5 && qh.taller && qh.afirma && qh.sinAf && qh.tray === 2 && qh.flecha && qh.resumen && !qh.fuga && !qh.cuerpo)) errores.push(`${etiqueta}: la pestaña «Qué hay» no enseña el resumen, el inventario, la aportación y la trayectoria, o filtra el cuerpo del taller (${JSON.stringify(qh)})`);
    if(etiqueta === 'completo-claro') await p.screenshot({ path: path.join(out, `${etiqueta}-que-hay.png`), fullPage: true });
    await abre(p, url, '#a-ventas', '[data-atab="quehay"]');
    const qha = await p.evaluate(() => ({ tabla: document.querySelectorAll('.qh-sum tbody tr').length, giro: /Cliente Uno se sigue atendiendo/.test((document.querySelector('.qh-sum')||{}).textContent||'') }));
    if(!(qha.tabla >= 2 && qha.giro)) errores.push(`${etiqueta}: el área no suma «Qué hay» de sus proyectos con el último cambio (${JSON.stringify(qha)})`);
    if(qha.tabla){ await p.click('.qh-sum [data-go-proj][data-tab="quehay"]'); await p.waitForTimeout(300);
      if(!(await p.evaluate(() => /-t-quehay$/.test(location.hash)))) errores.push(`${etiqueta}: la fila de «Qué hay» del área no abre la pestaña del proyecto`); }
    // la pestaña elegida se queda al pasar a otro proyecto desde el lateral (1.22.4)
    await abre(p, url, '#p-ventas--cuentas-t-estatus'); await p.click('.tab[data-tab="quehay"]').catch(() => {}); await p.waitForTimeout(200);
    if((opciones.viewport||{}).width > 760){ await p.click('#side-nav [data-go-proj="operacion--soporte"]').catch(() => {}); await p.waitForTimeout(300);
      if(!(await p.evaluate(() => /operacion--soporte-t-quehay$/.test(location.hash) && !!document.querySelector('.tab[data-tab="quehay"][aria-selected="true"]')))) errores.push(`${etiqueta}: un proyecto abierto desde el lateral no conserva la pestaña elegida`); }
    await p.goto(url + '#p-operacion--soporte-t-estatus'); await p.waitForTimeout(400);
    const corto = await p.evaluate(() => ({ t: (document.querySelector('.corto .corto-t')||{}).textContent || '', n: document.querySelectorAll('.corto .corto-l li').length, detalle: !!document.querySelector('[data-est-full]'), dos: [...document.querySelectorAll('.corto .corto-l li')].some(x=>/Beto las prueba el 24/.test(x.textContent)) }));
    if(!(corto.t.startsWith('Terminamos la lista') && corto.n === 3 && corto.detalle && corto.dos)) errores.push(`${etiqueta}: un proyecto con Estatus no abre con su titular y el detalle plegado (${JSON.stringify(corto)})`);
    if(etiqueta === 'completo-claro') await p.screenshot({ path: path.join(out, `${etiqueta}-como-va.png`) });
    await p.goto(url + '#entregables'); await p.waitForTimeout(400);
    await p.click('[data-ent-open]'); await p.waitForTimeout(250);
    await p.click('.modal-f [data-go-proj]'); await p.waitForTimeout(300);
    if(!(await p.evaluate(() => location.hash.startsWith('#p-') && !document.querySelector('.modal')))) errores.push(`${etiqueta}: un enlace dentro de una ventana no navega`);
    // un área con todos sus proyectos cerrados no sale en Inicio ni en el lateral hasta pedirla; sus entregables siguen
    await abre(p, url, '', '[data-ini="estatus"]');
    const arch = await p.evaluate(() => ({ inicio: [...document.querySelectorAll('.area-card b')].some(x=>x.textContent==='Archivo'), lateral: [...document.querySelectorAll('.side-i.area span')].some(x=>x.textContent==='Archivo'), boton: !!document.querySelector('[data-arch]') }));
    if(arch.inicio || arch.lateral || !arch.boton) errores.push(`${etiqueta}: el área archivada se ve sin pedirla o falta el botón para mostrarla (${JSON.stringify(arch)})`);
    await p.evaluate(() => document.querySelector('[data-arch]').click()); await p.waitForTimeout(300);
    if(!(await p.evaluate(() => [...document.querySelectorAll('.area-card b, .side-i.area span')].some(x=>x.textContent==='Archivo')))) errores.push(`${etiqueta}: «Mostrar el área archivada» no la muestra`);
    await p.evaluate(() => document.querySelector('[data-arch]').click()); await p.waitForTimeout(200);
    await p.goto(url + '#entregables'); await p.waitForTimeout(400);
    if(!(await p.evaluate(() => document.body.textContent.includes('Inventario del sistema anterior') && document.querySelector('h1').textContent==='Entregables'))) errores.push(`${etiqueta}: la vista Entregables no se llama así o perdió lo publicado de un área archivada`);
    // en el teléfono el menú es un botón con icono que abre y cierra el lateral; un velo lo cierra
    if((opciones.viewport||{}).width <= 760){
      await p.goto(url + '#'); await p.waitForTimeout(300);
      const t0 = await p.evaluate(() => { const t = document.getElementById('side-toggle'); return { icono: !!t.querySelector('svg'), texto: t.textContent.trim(), org: (document.getElementById('mob-org')||{}).textContent || '' }; });
      await p.click('#side-toggle'); await p.waitForTimeout(200);
      const abierto = await p.evaluate(() => document.body.classList.contains('side-open'));
      await p.click('.side-veil', { position: { x: 380, y: 400 } }).catch(() => {}); await p.waitForTimeout(200);
      const cerrado = await p.evaluate(() => !document.body.classList.contains('side-open'));
      if(!(t0.icono && t0.texto === '' && t0.org === 'Organización de prueba' && abierto && cerrado)) errores.push(`${etiqueta}: el menú del teléfono no es un icono que abre y cierra el lateral, o la barra no dice la organización (${JSON.stringify({ ...t0, abierto, cerrado })})`);
    }
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
  // la raíz migrada a la 1.22: la página no da errores y el área enseña su Estatus con sus prioridades aparte
  {
    const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await ctx.newPage(); const errs = [];
    p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if(m.type() === 'error') errs.push(m.text()); });
    await p.goto('file://' + path.resolve(dir, 'estructura.html') + '#a-ventas'); await p.waitForTimeout(800);
    const v = await p.evaluate(() => { const m = document.getElementById('main'), h = document.getElementById('head');
      const pan = m.querySelector('.card.pan'); return { est: !!pan && /Tiene una sola cuenta grande abierta/.test(pan.textContent) && !/^Ventas tiene/.test(pan.textContent.trim()) && pan.querySelectorAll('ol li').length === 2,
        resp: /Responsable:/.test(h.textContent) && !/Dueño:/.test(h.textContent) }; });
    await p.click('[data-atab="acciones"]'); await p.waitForTimeout(300);
    const prios = await p.evaluate(() => document.querySelectorAll('#main .prios .prio-l li').length);
    if(!(v.est && v.resp && prios === 2)) errores.push(`estructura 1.22: el área no enseña su Estatus sin repetir su nombre y con su Siguiente numerado, sus dos prioridades en Acciones o su responsable (${JSON.stringify({ ...v, prios })})`);
    await p.goto('file://' + path.resolve(dir, 'estructura.html') + '#p-operacion--soporte-t-estatus'); await p.waitForTimeout(800);
    const w = await p.evaluate(() => { const t = document.getElementById('main').textContent; return { corto: !!document.querySelector('.corto'), term: /Terminado significa/.test(t) }; });
    if(!(w.corto && !w.term)) errores.push(`estructura 1.22: el proyecto no enseña su Estatus o aún dice «Terminado significa» (${JSON.stringify(w)})`);
    if(errs.length) errores.push(`estructura 1.22: la página dio errores: ${errs.slice(0, 3).join(' | ')}`);
    await ctx.close();
  }
  // un tablero que era público, ya puesto al día con la 1.18: Inicio lo dice, con lo que implica
  {
    const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await ctx.newPage();
    p.on('pageerror', e => errores.push(`migrado: ${e.message}`));
    await p.goto('file://' + path.resolve(dir, 'migrado.html')); await p.waitForTimeout(600); await p.click('[data-ini="mant"]'); await p.waitForTimeout(300);
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
    await p.goto(url); await p.waitForTimeout(600); await p.click('[data-ini="mant"]'); await p.waitForTimeout(300);
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
    await p.waitForTimeout(400); await p.click('[data-ini="mant"]'); await p.waitForTimeout(300);
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
    await p.goto('file://' + path.resolve(dir, 'completo.html') + '#p-ventas--cuentas-t-registro'); await p.waitForTimeout(800);
    const fechas = () => p.evaluate(() => [...document.querySelectorAll('#main article.dec.ses time')].map(t => t.textContent));
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
