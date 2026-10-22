// Sustituye window.claude por una base en memoria con los datos de prueba. Solo para pruebas.
window.__D = __DATA__;
(function(){
 const D = window.__D;
 const snap = col => ({docs: Object.entries(D[col]||{}).map(([id,v])=>({id, data:()=>v}))});
 const db = {
  collection: name => ({ onSnapshot:(cb)=>{ ((window.__subs = window.__subs || {})[name] = window.__subs[name] || []).push(cb); setTimeout(()=>cb(snap(name)),0); return ()=>{}; }, add: async v=>{ const id='n'+Date.now(); (D[name]=D[name]||{})[id]=v; return {id}; } }),
  doc: path => { const [c,id]=path.split('/'); const ds = () => { const v=(D[c]||{})[id]; return {exists:!!v, data:()=>v}; }; return { onSnapshot:(cb)=>{ ((window.__subs = window.__subs || {})[path] = window.__subs[path] || []).push(()=>cb(ds())); setTimeout(()=>cb(ds()),0); return ()=>{}; }, delete: async()=>{ delete (D[c]||{})[id]; }, update: async u=>{ Object.assign(D[c][id],u); } }; }
 };
 const user = { me: async()=>({id:'u_1', __USER__}) };
 const mcp = { callTool: async(...a)=>{ (window.__llamadas = window.__llamadas || []).push(a); return {}; } };
 // simula que otra sesión escribe en una colección con la página abierta: vuelve a avisar a quien la escucha
 // name es una colección («cierres») o un documento («meta/estado»)
 window.__emitir = name => ((window.__subs||{})[name]||[]).forEach(cb => cb(snap(name)));
 window.claude = { use: async n => n==='db'?db : n==='user'?user : n==='mcp'?mcp : null };
})();
