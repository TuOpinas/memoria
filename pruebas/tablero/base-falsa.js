// Sustituye window.claude por una base en memoria con los datos de prueba. Solo para pruebas.
window.__D = __DATA__;
(function(){
 const D = window.__D;
 const snap = col => ({docs: Object.entries(D[col]||{}).map(([id,v])=>({id, data:()=>v}))});
 // como la base de verdad, cada escritura avisa a quien escucha la colección (1.24: los flujos de la fila se prueban enteros)
 const avisa = col => setTimeout(() => ((window.__subs||{})[col]||[]).forEach(cb => cb(snap(col))), 0);
 let sec = 0;
 const db = {
  collection: name => ({ onSnapshot:(cb)=>{ ((window.__subs = window.__subs || {})[name] = window.__subs[name] || []).push(cb); setTimeout(()=>cb(snap(name)),0); return ()=>{}; }, add: async v=>{ const id='n'+Date.now()+'-'+(++sec); (D[name]=D[name]||{})[id]=v; avisa(name); return {id}; } }),
  doc: path => { const [c,id]=path.split('/'); const ds = () => { const v=(D[c]||{})[id]; return {exists:!!v, data:()=>v}; }; return { onSnapshot:(cb)=>{ ((window.__subs = window.__subs || {})[path] = window.__subs[path] || []).push(()=>cb(ds())); setTimeout(()=>cb(ds()),0); return ()=>{}; }, delete: async()=>{ delete (D[c]||{})[id]; avisa(c); }, update: async u=>{ Object.assign(D[c][id],u); avisa(c); }, set: async v=>{ (D[c]=D[c]||{})[id]=v; avisa(c); } }; }
 };
 const user = { me: async()=>({id:'u_1', __USER__}) };
 const mcp = { callTool: async(...a)=>{ (window.__llamadas = window.__llamadas || []).push(a); return {}; } };
 // simula que otra sesión escribe en una colección con la página abierta: vuelve a avisar a quien la escucha
 // name es una colección («cierres») o un documento («meta/estado»)
 window.__emitir = name => ((window.__subs||{})[name]||[]).forEach(cb => cb(snap(name)));
 // los archivos que publica la puesta al día (1.24.1), servidos desde los mismos datos: la página los pide con fetch.
 // Con window.__SIN_ARCHIVOS la página no los encuentra y lee de la base, como un tablero sin su primera sincronización 1.24.1.
 const _fetch = window.fetch;
 window.fetch = async (u, o) => {
  const m = /(?:^|\/)datos\/(\w+)(?:\/([\w.~-]+))?\.json$/.exec(String(u));
  if(!m) return _fetch(u, o);
  (window.__pedidos = window.__pedidos || []).push(String(u));
  if(window.__SIN_ARCHIVOS) return new Response("", {status: 404});
  const props = Object.fromEntries(Object.entries(D.cambios||{}).filter(([,v]) => v.tipo === "propuesta"));
  let cuerpo = {estado: (D.meta||{}).estado || {}, tablero: {areas: D.areas||{}, proyectos: D.proyectos||{}, resumenes: D.resumenes||{}, enfoque: (D.enfoque||{}).actual || null},
                  propuestas: props, detalle: D.detalle||{}}[m[1]];
  // desde la 1.24.2, datos/detalle/<área>.json: el de esa área; con window.__DETALLE_UNO (un tablero de la 1.24.1) no existe
  if(m[2] !== undefined){
   if(m[1] !== "detalle" || window.__DETALLE_UNO) return new Response("", {status: 404});
   cuerpo = Object.fromEntries(Object.entries(D.detalle||{}).filter(([id]) => id.split("--")[0] === m[2]));
  } else if(m[1] === "detalle" && !window.__DETALLE_UNO) return new Response("", {status: 404});
  return cuerpo === undefined ? new Response("", {status: 404}) : new Response(JSON.stringify(cuerpo), {status: 200, headers: {"Content-Type": "application/json"}});
 };
 window.claude = { use: async n => n==='db'?db : n==='user'?user : n==='mcp'?mcp : null };
})();
