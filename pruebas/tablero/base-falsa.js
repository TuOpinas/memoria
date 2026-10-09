// Sustituye window.claude por una base en memoria con los datos de prueba. Solo para pruebas.
window.__D = __DATA__;
(function(){
 const D = window.__D;
 const snap = col => ({docs: Object.entries(D[col]||{}).map(([id,v])=>({id, data:()=>v}))});
 const db = {
  collection: name => ({ onSnapshot:(cb)=>{ setTimeout(()=>cb(snap(name)),0); return ()=>{}; }, add: async v=>{ const id='n'+Date.now(); (D[name]=D[name]||{})[id]=v; return {id}; } }),
  doc: path => { const [c,id]=path.split('/'); return { onSnapshot:(cb)=>{ setTimeout(()=>{ const v=(D[c]||{})[id]; cb({exists:!!v, data:()=>v}); },0); return ()=>{}; }, delete: async()=>{ delete (D[c]||{})[id]; }, update: async u=>{ Object.assign(D[c][id],u); } }; }
 };
 const user = { me: async()=>({id:'u_1', isOwner:true, canEdit:true}) };
 const mcp = { callTool: async()=>({}) };
 window.claude = { use: async n => n==='db'?db : n==='user'?user : n==='mcp'?mcp : null };
})();
