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
    ['memoria-al-dia', '', '[data-mt-open]', '[data-ini="mant"]'], ['prioridad', '#a-ventas', '[data-prio-toggle]', '[data-atab="estatus"]'],
    ['entregable', '#entregables', '[data-ent-open]'], ['estado', '#p-ventas--cuentas-t-estatus', '.est-btn'],
    // desde la 1.24 la lista entera de tareas va plegada en «Qué hay» del proyecto
    ['corregir-paso', '#p-ventas--cuentas-t-quehay', '.step-x', '#todas-tareas summary'], ['fecha', '#p-ventas--cuentas-t-quehay', '[data-edit-due]', '#todas-tareas summary'],
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
    // los avisos del tablero viven en Mantenimiento
    await abre(p, url, '', '[data-ini="mant"]');
    // la carpeta en una versión anterior del método se pone al día sola y no pide nada: no se avisa (1.23.3)
    const atraso = await p.evaluate(() => [...document.querySelectorAll('#main .stale')].some(x => /La carpeta usa todavía la versión/.test(x.textContent)));
    if(atraso) errores.push(`${etiqueta}: Mantenimiento avisa de algo que no pide nada (la versión del método de la carpeta)`);
    const boton = await p.evaluate(() => { const b = document.querySelector('.sync-ico'); return b ? { pend: b.classList.contains('pend'), off: b.classList.contains('off') } : null; });
    if(!boton || boton.off || boton.pend) errores.push(`${etiqueta}: el botón cuenta como pendiente un cambio que la sincronización dejó a propósito, o no está (${JSON.stringify(boton)})`);
    // las propuestas del barrido viven en la cola pero no cuentan como lo marcado aquí; salen en el detalle de «Por poner al día», y las descartadas no
    const prop = await p.evaluate(async () => { const b = document.querySelector('[data-mt-open="ventas--cuentas"]'); if(!b) return null; b.click(); await new Promise(r => setTimeout(r, 250)); const m = document.querySelector('.modal'); return m ? m.textContent : ''; });
    await p.keyboard.press('Escape');
    if(prop === null || !/Sugerencias de la memoria/.test(prop) || !/PRUEBA-PROPUESTA-VIVA/.test(prop) || /PRUEBA-PROPUESTA-DESCARTADA/.test(prop) || !/2 cosas marcadas aquí/.test(prop)) errores.push(`${etiqueta}: las propuestas del barrido no salen en el detalle de «Por poner al día», o salen las descartadas, o cuentan como marcadas aquí (${prop === null ? 'sin ventana' : prop.slice(0, 120)})`);
    // Inicio › Acciones y Actividad
    await abre(p, url, '', '[data-ini="acciones"]');
    // 1.24: lo que te toca decidir y las tareas críticas, sin «Te toca a ti» ni «Con otros»
    const acc = await p.evaluate(() => { const t = document.getElementById('main').textContent; return { toca: /Te toca decidir|Tareas críticas|Nada te espera hoy/.test(t), viejo: /Te toca a ti|Con otros/.test(t) }; });
    if(!acc.toca || acc.viejo) errores.push(`${etiqueta}: Inicio › Acciones no va como en la 1.24 (${JSON.stringify(acc)})`);
    await abre(p, url, '', '[data-ini="actividad"]');
    const act = await p.evaluate(() => { const t = document.getElementById('main').textContent; return { area: /Por área/.test(t), persona: /Por persona/.test(t), dias: !!document.querySelector('[data-act-dias]') }; });
    if(!(act.area && act.persona && act.dias)) errores.push(`${etiqueta}: Inicio › Actividad no trae «Por área», «Por persona» y el periodo (${JSON.stringify(act)})`);
    // «Por persona» (1.23) con un equipo inventado: quien colabora en un área sale; tres sesiones del mismo día son tres; un
    // documento cuenta escrito para quien lo escribió y publicado para quien lo publicó; los que no tuvieron sesión van abajo;
    // las tareas abiertas cuentan las de «Siguientes pasos» que los nombran; el combo de área reduce la lista; «Con otros» los ve del equipo
    if(etiqueta === 'completo-claro'){
      const pp = await p.evaluate(() => {
        const guardado = {AREAS, PROJ, areaBy, byId, META, ACT_AREA, ACT_DIAS};
        try{
          const d0 = addDays(-1), viejo = addDays(-40);
          AREAS = [{slug:"op", nombre:"operación", dueno:"Ana Lombardo", colaboran:["bruno@x.test", "angel@x.test"], colaboran_ver:["Bruno Esquivel", "Ángel Ruiz"]},
                   {slug:"prod", nombre:"producto", dueno:"Carmen Oyarzún", colaboran:["anar@x.test"], colaboran_ver:["Ana Ruiz"]},
                   {slug:"tec", nombre:"tecnología", dueno:"Elena Reyes", colaboran:["diego@x.test"], colaboran_ver:["Diego Antúnez"]}];
          PROJ = [{id:"op--alfa", area:"op", slug:"alfa", nombre:"Alfa", dueno:"Ana Lombardo", colaboran:[],
                   pasos:[{texto:"Esperar a que Bruno mande el informe"}, {texto:"Revisar con Diego el servidor"}, {texto:"Esperar a que Ángel confirme la fecha"},
                          {texto:"Pedir a Ana el contrato"}, {texto:"Avisar a Ana Ruiz del cierre"}],
                   sesiones_recientes:[{fecha:d0, titulo:d0, n:5, quien:"Ana Lombardo", publico:["entregables/x.md"]},
                                       {fecha:d0, titulo:d0, n:4, quien:"Bruno Esquivel", escribio:["entregables/x.md", "taller/y.md", "entregables/w.md"]},
                                       {fecha:d0, titulo:d0, n:3, quien:"Bruno Esquivel"},
                                       {fecha:d0, titulo:d0, n:2},
                                       {fecha:d0, titulo:d0, n:1, quien:"Fede Singuía"}],
                   decisiones:[{fecha:d0, decidio:"Bruno Esquivel", titulo:"Una decisión"}, {fecha:d0, decidio:"Carmen Oyarzún", titulo:"Otra, sin sesión suya"}],
                   entregables:[{nombre:"x", archivo:"x.md", estado:"vigente", actualizado:d0}, {nombre:"w", archivo:"w.md", estado:"vigente", actualizado:d0},
                                {nombre:"z", archivo:"z.md", estado:"vigente", actualizado:d0}]},
                  {id:"tec--srv", area:"tec", slug:"srv", nombre:"Servidor", dueno:"Elena Reyes", colaboran:[], pasos:[],
                   sesiones_recientes:[{fecha:d0, titulo:d0, n:9, quien:"Ana Lombardo"}], ultima_por_persona:{"Elena Reyes": viejo}, decisiones:[], entregables:[]}];
          areaBy = Object.fromEntries(AREAS.map(a=>[a.slug,a])); byId = Object.fromEntries(PROJ.map(x=>[x.id,x])); _CONOCIDOS = null;
          META = {...(guardado.META||{}), tablero_de:"Ana Lombardo", administra:"Ana Lombardo"}; ACT_AREA = ""; ACT_DIAS = 7;
          const div = document.createElement("div"); div.innerHTML = actPersonas(eventos(addDays(-6)));
          const filas = [...div.querySelectorAll(".per:not(.quiet)")].map(x=>x.textContent.replace(/\s+/g," ").trim());
          const quietas = [...div.querySelectorAll(".per.quiet")].map(x=>x.textContent.replace(/\s+/g," ").trim());
          const tipBruno = [...div.querySelectorAll(".per:not(.quiet)")].find(x=>/Bruno/.test(x.textContent)).querySelector(".tira i.on").dataset.t;
          const nota = (div.querySelector(".nota")||{}).textContent || "";
          const otros = conOtros().map(g=>({n:g.n, dentro:g.dentro}));
          ACT_AREA = "tec"; const div2 = document.createElement("div"); div2.innerHTML = actPersonas(eventos(addDays(-6)));
          const tec = [...div2.querySelectorAll(".per")].map(x=>x.textContent.replace(/\s+/g," ").trim());
          // el papel va al pasar por el nombre (1.23.3)
          const tipsDe = d => Object.fromEntries([...d.querySelectorAll(".per b[data-tip]")].map(x=>[x.textContent, x.dataset.tip]));
          const tips = tipsDe(div), tipsTec = tipsDe(div2);
          const decide = quienDecide("decide Ana si se firma");
          return {filas, quietas, tipBruno, nota, otros, tec, tips, tipsTec, decide, sel: !!div.querySelector("[data-act-area]")};
        } finally { ({AREAS, PROJ, areaBy, byId, META, ACT_AREA, ACT_DIAS} = guardado); _CONOCIDOS = null; }
      });
      const fila = n => pp.filas.find(x=>x.startsWith(n)) || "", quieta = n => pp.quietas.find(x=>x.startsWith(n)) || "";
      // 1.23.3: el papel, al pasar por el nombre; lo que vale cero no se escribe
      const bien = pp.filas.length === 4 && /no figura en la carpeta/.test(fila("Fede")) && /2 sesiones/.test(fila("Bruno")) && /^Colabora en operación$/.test(pp.tips["Bruno Esquivel"]||"") && !/colabora/.test(fila("Bruno")) && /1 decisión/.test(fila("Bruno"))
        && /3 escritos/.test(fila("Bruno")) && !/documentos/.test(fila("Bruno")) && !/publicado/.test(fila("Bruno")) && /1 tarea abierta/.test(fila("Bruno"))
        && /2 sesiones/.test(fila("Ana Lombardo")) && /1 publicado/.test(fila("Ana Lombardo")) && !/escrito/.test(fila("Ana Lombardo")) && !/tarea abierta/.test(fila("Ana Lombardo"))
        && !/sesi/.test(fila("Carmen")) && /1 decisión/.test(fila("Carmen"))
        && /· 2 sesiones/.test(pp.tipBruno) && pp.quietas.length === 4 && /1 tarea abierta/.test(quieta("Diego")) && /1 tarea abierta/.test(quieta("Ángel"))
        && /1 tarea abierta/.test(quieta("Ana Ruiz")) && /última sesión el/.test(quieta("Elena"))
        && /^1 de 6 sesiones del periodo no dice quién la cerró/.test(pp.nota) && !/documento vigente/.test(pp.nota) && !/cuenta como escrito/.test(pp.nota) && /1 tarea nombra a alguien solo por un nombre de pila/.test(pp.nota) && !/de antes/.test(pp.nota)
        && pp.otros.some(g=>g.n==="Bruno Esquivel" && g.dentro) && pp.otros.some(g=>g.n==="Diego Antúnez" && g.dentro) && pp.otros.some(g=>g.n==="Ángel Ruiz" && g.dentro)
        && pp.otros.some(g=>g.n==="Ana Ruiz" && g.dentro) && !pp.otros.some(g=>g.n==="Ana Lombardo") && pp.decide === null && /en Alfa/.test(pp.nota)
        && pp.tec.length === 3 && /^Ana Lombardo/.test(pp.tec[0]) && /^Administra la carpeta · responsable de operación · trabajó en esta área$|^Responsable de operación · trabajó en esta área$/.test(pp.tipsTec["Ana Lombardo"]||"") && pp.sel;
      if(!bien) errores.push(`${etiqueta}: «Por persona» no cuenta como debe (${JSON.stringify(pp)})`);
    }
    // 1.23.3: Acciones con «Por dónde empezar» arriba, lo vencido con su botón en la fila y «Con otros» con lo que otros
    // decidieron; Actividad sin «Lo que otros hicieron»; Mantenimiento ordenado por lo que pide
    if(etiqueta === 'completo-claro'){
      const r = await p.evaluate(() => {
        const g = {CAN, DB, META};
        try{
          META = {...(META||{}), tablero_de: "Ana Prueba"};
          const pregunta = comoPregunta("si se corrigen las plantillas para que respeten la letra (Ana)."), otra = comoPregunta("el nombre y la métrica (Beto).");
          const frase = fraseDecidir(byId["ventas--cuentas"], "si se firma ya (Ana).");
          const acc = tabAcciones().html, div = document.createElement("div"); div.innerHTML = acc;
          const orden = [...div.querySelectorAll("section h2")].map(h=>h.textContent.replace(/\?$/,"").trim()), nAfe = afectaDeOtros().length;
          CAN = true; DB = {};
          const p0 = PROJ.find(x=>!x.cerrado && !x.restringido && (x.pasos||[]).some(s=>!isHeader(s))), s0 = p0.pasos.find(s=>!isHeader(s));
          const v = document.createElement("div"); v.innerHTML = filaVencida(p0, s0, "2026-01-05", true);
          const botones = [...v.querySelectorAll("button.chip")].map(b=>b.textContent.trim());
          const act = tabActividad().html, mant = tabMant().html;
          // quien decide: «decide X» o «(Nombre)» al final; un nombre solo mencionado no se lleva la decisión (revisión 1.23.3)
          const menciona = deOtroFd("si contratamos a Beto Prueba para soporte"), parenOtro = deOtroFd("el precio de la fase 2 (Beto Prueba)"), parenYo = deOtroFd("el precio (Ana)");
          const pregunta2 = comoPregunta("qué hacemos con la fase 2; lo decide Ana"), frase2 = fraseDecidir(byId["ventas--cuentas"], "si firmamos con Beta (antes del 30 de noviembre)");
          // «Con otros» y «te afecta» solo miran tus proyectos: en una carpeta con equipo, lo de los demás no es tuyo (1.23.3)
          // de un proyecto ajeno solo sale lo que dice que tú haces algo con alguien; de uno tuyo, no lo que hace otra persona (1.23.4)
          const ajeno = PROJ.find(x=>!esMio(x) && !x.restringido && !x.cerrado), propio = PROJ.find(x=>esMio(x) && !x.restringido && !x.cerrado);
          const gp = {aj: ajeno.pasos, pr: propio.pasos};
          ajeno.pasos = [...(ajeno.pasos||[]), {texto:"Ana Prueba pide a Beto Prueba el informe"}, {texto:"Carla Prueba pregunta a Beto Prueba por el temario"}];
          propio.pasos = [...(propio.pasos||[]), {texto:"Beto Prueba pregunta a Carla Prueba por la firma"}, {texto:"Tras hablar con Carla Prueba, pedir a Beto Prueba el acta"}];
          _M = null; const co = conOtros(); ajeno.pasos = gp.aj; propio.pasos = gp.pr; _M = null;
          const textos = co.flatMap(g=>[...g.deben, ...g.debes].map(x=>x.t));
          const soloMios = co.every(g=>[...g.deben, ...g.debes].every(x=>esMio(x.p) || /^Ana Prueba pide/.test(x.t))) && textos.some(t=>/^Ana Prueba pide/.test(t))
            && !textos.some(t=>/pregunta a/.test(t)) && textos.some(t=>/^Tras hablar con Carla Prueba/.test(t)) && afectaDeOtros().every(g=>g.a.every(esMio));
          // un paso que espera a alguien sin decir a quién va a la tarjeta de su proyecto, no a «La carpeta» (1.23.5)
          const pq = PROJ.find(x=>!x.restringido && !x.cerrado); const gq = pq.pasos; pq.pasos = [...(pq.pasos||[]), {texto:"Esperar la respuesta del proveedor sobre el anexo"}]; _M = null;
          const tarjeta = porPonerAlDia().todas.find(g=>g.id===pq.id), cita = tarjeta && tarjeta.it.find(t=>/espera(?:n)? a alguien sin decir a quién/.test(t));
          // también con una sugerencia de reescribir su Estatus pendiente, y sin «.» ni «…» de más (revisión 1.23.5)
          const gpr = PROPUESTAS; PROPUESTAS = [...PROPUESTAS, {id:"t-ed", tipo:"propuesta", clase:"estado-desfasado", estado:"pendiente", proyecto:pq.id}]; _M = null;
          const tarjeta2 = porPonerAlDia().todas.find(g=>g.id===pq.id); PROPUESTAS = gpr;
          const sinQuien = !!cita && /«Esperar la respuesta [^«».…]*» y \d+ más\.$/.test(cita) && !deLaCarpeta().items.some(x=>/no reconoce/.test(x.t))
            && !!tarjeta2 && tarjeta2.it.some(t=>/sin decir a quién/.test(t));
          pq.pasos = gq; _M = null;
          return {sinQuien, soloMios, menciona, parenOtro, parenYo, pregunta2, frase2, pregunta, otra, frase, orden, nAfe, botones, venc: v.textContent, otros: /Decisiones que te afectan/.test(acc), sinAfecta: !/Con otros|Te toca a ti/.test(acc),
            act: !/Lo que otros hicieron/.test(act), mant: ["Proyectos por poner al día"].map(t=>mant.includes(t)), viejo: /Lo que no cuadra|Vencido y nadie lo movió|Avisos de la herramienta|<h2>La carpeta|<h2>El tablero|<h2>Sugerencias de la memoria/.test(mant)};
        } finally { ({CAN, DB, META} = g); }
      });
      const bien = r.pregunta === "¿Se corrigen las plantillas para que respeten la letra?" && r.otra === "El nombre y la métrica (Beto)." && /decidamos si se firma ya$/.test(r.frase)
        && r.orden[0] === "Por dónde empezar" && (r.orden.indexOf("Tareas críticas") < 0 || r.orden.indexOf("Te toca decidir") < r.orden.indexOf("Tareas críticas")) && r.otros === (r.nAfe > 0) && r.sinAfecta
        && r.soloMios && r.sinQuien && r.menciona === null && r.parenOtro === "Beto Prueba" && r.parenYo === null && r.pregunta2 === "¿Qué hacemos con la fase 2?" && /\(antes del 30 de noviembre\)$/.test(r.frase2)
        && r.botones.join("|") === "Hecha|Nueva fecha|Ya no aplica" && /hace \d+ días/.test(r.venc) && r.act && r.mant.every(Boolean) && !r.viejo;
      if(!bien) errores.push(`${etiqueta}: Acciones, Actividad o Mantenimiento no van como en la 1.24 (${JSON.stringify(r)})`);
    }
    // el proyecto: Estatus arriba, con su titular
    await abre(p, url, '#p-ventas--cuentas-t-estatus');
    const est = await p.evaluate(() => ({ tab: !!document.querySelector('.tab[data-tab="estatus"][aria-selected="true"]'), tabs: [...document.querySelectorAll('#main .tab')].map(t => t.dataset.tab).join(','), corto: !!document.querySelector('#main .corto, #main .brief') }));
    if(!(est.tab && est.tabs === 'estatus,pasos,registro,quehay' && est.corto)) errores.push(`${etiqueta}: el proyecto no abre en Estatus con sus cuatro pestañas (${JSON.stringify(est)})`);
    // «Qué hay» (1.21): la pestaña del proyecto con inventario, aportación, señales y lo reemplazado; nunca el cuerpo del taller; y la suma en el área
    await abre(p, url, '#p-ventas--cuentas-t-quehay'); await p.waitForTimeout(300);
    const qh = await p.evaluate(() => { const t = document.getElementById('main').textContent; return { tab: !!document.querySelector('.tab[data-tab="quehay"][aria-selected="true"]'), pz: document.querySelectorAll('.qh-pz').length, taller: /Precio de la fase 2/.test(t), afirma: /por encima del piloto/.test(t), sinAf: /Sin aportación/.test(t), tray: [...document.querySelectorAll('.qh-pz')].filter(x=>/Reemplazado por/.test(x.textContent)).length, flecha: !document.querySelector('.qh-tray'), resumen: /Lo publicado/.test(t) && /En el taller/.test(t), fuga: /TALLER-PRIVADO/.test(document.documentElement.outerHTML), cuerpo: /Cuerpo que el tablero no lee/.test(t) }; });
    if(!(qh.tab && qh.pz >= 5 && qh.taller && qh.afirma && qh.sinAf && qh.tray >= 1 && qh.flecha && qh.resumen && !qh.fuga && !qh.cuerpo)) errores.push(`${etiqueta}: la pestaña «Qué hay» no enseña el resumen, el inventario, la aportación y qué reemplazó a cada pieza, o filtra el cuerpo del taller (${JSON.stringify(qh)})`);
    if(etiqueta === 'completo-claro') await p.screenshot({ path: path.join(out, `${etiqueta}-que-hay.png`), fullPage: true });
    await abre(p, url, '#a-ventas', '[data-atab="quehay"]');
    const qha = await p.evaluate(() => ({ tabla: document.querySelectorAll('.qh-sum tbody tr').length, giro: /Cliente Uno se sigue atendiendo/.test((document.querySelector('.qh-sum')||{}).textContent||'') }));
    if(!(qha.tabla >= 2 && qha.giro)) errores.push(`${etiqueta}: el área no suma «Qué hay» de sus proyectos con el último cambio (${JSON.stringify(qha)})`);
    if(qha.tabla){ await p.click('.qh-sum [data-go-proj][data-tab="quehay"]'); await p.waitForTimeout(300);
      if(!(await p.evaluate(() => /-t-quehay$/.test(location.hash)))) errores.push(`${etiqueta}: la fila de «Qué hay» del área no abre la pestaña del proyecto`); }
    // la pestaña elegida se queda al pasar a otro proyecto desde el lateral (1.22.4)
    await abre(p, url, '#p-ventas--cuentas-t-estatus'); await p.click('.tab[data-tab="quehay"]').catch(() => {}); await p.waitForTimeout(200);
    if((opciones.viewport||{}).width > 760){ await p.click('#side-nav [data-go-proj="operacion--soporte"]').catch(() => {}); await p.waitForTimeout(300);
      if(!(await p.evaluate(() => /operacion--soporte-t-quehay$/.test(location.hash) && !!document.querySelector('.tab[data-tab="quehay"][aria-selected="true"]')))) errores.push(`${etiqueta}: un proyecto abierto desde el lateral no conserva la pestaña elegida`);
      // Atrás enseña la pestaña de esa dirección pero no cambia la que se recuerda (1.22.5)
      await p.evaluate(() => { history.pushState(null, '', '#p-ventas--cuentas-t-registro'); history.pushState(null, '', '#p-operacion--soporte-t-quehay'); });
      await p.goBack(); await p.waitForTimeout(300);
      const atras = await p.evaluate(() => location.hash);
      await p.click('#side-nav [data-go-proj="operacion--soporte"]').catch(() => {}); await p.waitForTimeout(300);
      if(!(atras === '#p-ventas--cuentas-t-registro' && /operacion--soporte-t-quehay$/.test(await p.evaluate(() => location.hash)))) errores.push(`${etiqueta}: Atrás cambió la pestaña que se recuerda (${atras})`); }
    await p.goto(url + '#p-operacion--soporte-t-estatus'); await p.waitForTimeout(400);
    const corto = await p.evaluate(() => ({ t: (document.querySelector('.corto .corto-t')||{}).textContent || '', n: document.querySelectorAll('.corto .corto-l li').length, detalle: !!document.querySelector('[data-est-full]'), dos: [...document.querySelectorAll('.corto .corto-l li')].some(x=>/Beto las prueba el 24/.test(x.textContent)) }));
    // 1.24: sin «En detalle» (el estado largo de antes de la 1.22 vive en el taller del proyecto migrado)
    if(!(corto.t.startsWith('Terminamos la lista') && corto.n === 3 && !corto.detalle && corto.dos)) errores.push(`${etiqueta}: un proyecto con Estatus no abre con su titular, o aún enseña «En detalle» (${JSON.stringify(corto)})`);
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
  // un proyecto cerrado abierto directo en Estatus pinta su propia cabecera (revisión 1.22.5)
  {
    const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } }); const p = await ctx.newPage();
    const url = 'file://' + path.resolve(dir, 'completo.html');
    await p.goto(url + '#p-ventas--cuentas-t-estatus'); await p.waitForTimeout(400);
    await p.goto(url + '#p-archivo--historia-t-estatus'); await p.waitForTimeout(500);
    const h = await p.evaluate(() => ({ h1: (document.querySelector('#head h1')||{}).textContent || '', nombre: (byId['archivo--historia']||{}).nombre || '' }));
    if(!(h.nombre && h.h1 === h.nombre)) errores.push(`un proyecto cerrado en Estatus no pinta su cabecera (${JSON.stringify(h)})`);
    await ctx.close();
  }
  // a 320 px: las pestañas que no caben se desvanecen por el lado que sigue; «Sincronizar ahora» va en la barra; y el número
  // de Mantenimiento cuenta solo lo que pide una acción (1.22.5)
  {
    const ctx = await b.newContext({ viewport: { width: 320, height: 700 } });
    const p = await ctx.newPage(); p.on('pageerror', e => errores.push(`320: ${e.message}`));
    const url = 'file://' + path.resolve(dir, 'completo.html');
    await p.goto(url + '#p-ventas--cuentas-t-estatus'); await p.waitForTimeout(500);
    const r1 = await p.evaluate(() => { const t = document.querySelector('.tabs'); return { desborda: t.scrollWidth > t.clientWidth + 2, der: t.classList.contains('mas-der'), izq: t.classList.contains('mas-izq'), sync: !!document.querySelector('#mob-sync [data-sync]') }; });
    await p.evaluate(() => { const t = document.querySelector('.tabs'); t.scrollLeft = t.scrollWidth; }); await p.waitForTimeout(200);
    const r2 = await p.evaluate(() => { const t = document.querySelector('.tabs'); return { der: t.classList.contains('mas-der'), izq: t.classList.contains('mas-izq') }; });
    if(!(r1.desborda && r1.der && !r1.izq && r2.izq && !r2.der)) errores.push(`320: las pestañas que no caben no se desvanecen por el lado que sigue (${JSON.stringify({ r1, r2 })})`);
    if(!r1.sync) errores.push('320: «Sincronizar ahora» no está en la barra del teléfono');
    await p.goto(url + '#'); await p.waitForTimeout(400); await p.click('[data-ini="mant"]'); await p.waitForTimeout(300);
    // 1.24: el número cuenta lo que hay que arreglar ya; los proyectos por poner al día encienden el punto
    const m = await p.evaluate(() => { const t = document.querySelector('[data-ini="mant"]'); const b = t.querySelector('.n.badge'); return { badge: b ? +b.textContent : 0, punto: !!t.querySelector('.n.punto'), arr: document.querySelectorAll('#arreglar .due-item').length, pad: document.querySelectorAll('#poner-al-dia .pd').length }; });
    if(!(m.badge === m.arr && (m.arr > 0 || (m.pad > 0) === m.punto))) errores.push(`320: el número de Mantenimiento no cuenta solo «Arreglar ya» (${JSON.stringify(m)})`);
    // lo marcado aquí que ya no coincide con la carpeta va a «Arreglar ya»
    const m2 = await p.evaluate(() => ({ orf: cambiosVis().filter(c => huerfano(c) && c.tipo!=="nota").length, linea: arreglarYa().some(x=>/ya no coincide/.test(x.t)) }));
    if(m2.orf && !m2.linea) errores.push(`320: lo marcado que ya no coincide no sale en «Arreglar ya» (${JSON.stringify(m2)})`);
    await p.evaluate(() => { PROPUESTAS = []; CAMBIOS = []; PERMISOS = null; META = {...META, version_tablero: VERSION_TABLERO, tarea_desfasada: false, sincronizado: new Date().toISOString()}; DATA_SEQ++; render(); });
    await p.waitForTimeout(200);
    const m3 = await p.evaluate(() => { const t = document.querySelector('[data-ini="mant"]'); return { badge: !!t.querySelector('.n.badge'), punto: !!t.querySelector('.n.punto'), pad: ponerAlDia().length, arr: arreglarYa().length, linea: !!document.querySelector('.alarma') }; });
    if(!(m3.badge === (m3.arr > 0) && m3.linea === (m3.arr > 0) && m3.punto === (!m3.arr && m3.pad > 0))) errores.push(`320: el número y la línea de arriba no siguen a «Arreglar ya», o falta el punto de lo que hay por poner al día (${JSON.stringify(m3)})`);
    await ctx.close();
  }
  // la raíz migrada a la 1.22: la página no da errores y el área enseña su Estatus con sus prioridades aparte
  {
    const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await ctx.newPage(); const errs = [];
    p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if(m.type() === 'error') errs.push(m.text()); });
    await p.goto('file://' + path.resolve(dir, 'estructura.html') + '#a-ventas'); await p.waitForTimeout(800);
    const v = await p.evaluate(() => { const m = document.getElementById('main'), h = document.getElementById('head');
      const pan = m.querySelector('.card.pan'); return { est: !!pan && /Tiene una sola cuenta grande abierta/.test(pan.textContent) && !/^Ventas tiene/.test(pan.textContent.trim()) && pan.querySelectorAll('ol li').length === 2,
        resp: /Responsable:/.test(h.textContent) && !/Dueño:/.test(h.textContent) }; });
    const prios = await p.evaluate(() => document.querySelectorAll('#main .card.pan .prio-l [data-prio-toggle]').length);
    if(!(v.est && v.resp && prios === 2)) errores.push(`estructura 1.22: el área no enseña su Estatus sin repetir su nombre, con su Siguiente numerado y sus dos prioridades atendibles, o su responsable (${JSON.stringify({ ...v, prios })})`);
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
    const r = await p.evaluate(() => ({ llamadas: (window.__llamadas || []).length, pend: !!document.querySelector('.sync-ico.pend') }));
    if(r.llamadas !== 0 || !r.pend) errores.push(`cierres: al abrir con dos cierres pendientes tiene que marcar el botón de sincronizar y no lanzar nada (${JSON.stringify(r).slice(0, 300)})`);
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
    const r = await p.evaluate(() => ({ llamadas: (window.__llamadas || []).length, pend: !!document.querySelector('.sync-ico.pend') }));
    if(r.llamadas !== 0) errores.push(`abierto: un cierre que llega con la página abierta, o volver a la pestaña, lanzó la puesta al día (${r.llamadas})`);
    if(!r.pend) errores.push(`abierto: el botón de sincronizar no marca el cierre que llegó con la página abierta`);
    await ctx.close();
  }
  // el detalle de un proyecto (bitácora vieja, estado entero, porqués) se vuelve a traer cuando el proyecto cambia en la
  // base con la página abierta: una sincronización que mueve una sesión al detalle no la hace desaparecer (1.19)
  {
    const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await ctx.newPage();
    p.on('pageerror', e => errores.push(`detalle: ${e.message}`));
    await p.goto('file://' + path.resolve(dir, 'completo.html') + '#p-ventas--cuentas-t-registro'); await p.waitForTimeout(800);
    // desde la 1.24 el registro enseña el periodo y «Ver anteriores» trae lo demás
    await p.evaluate(() => { REG_TODO.add('ventas--cuentas'); render(); }); await p.waitForTimeout(200);
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
