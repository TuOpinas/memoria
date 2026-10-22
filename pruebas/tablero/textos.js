// Prueba los textos de la página para lo que no se lee (noLeido, soloNombre, lectoresDe) con celdas reales de guia.md.
// Saca las funciones de vista.html y las corre solas. Uso: node textos.js <vista.html>. Sale con 1 si algo falla.
const fs = require('fs');
const h = fs.readFileSync(process.argv[2], 'utf8');
const desde = h.indexOf('const soloNombre'), hasta = h.indexOf('function projStatus(p){');
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const { noLeido, soloNombre } = new Function('esc', h.slice(desde, hasta) + '; return { noLeido, soloNombre };')(esc);
let fallos = 0;
const ok = (c, q) => { console.log((c ? '  bien  ' : '  FALLA ') + q); if(!c) fallos++; };
const area = (lectores, dueno = 'Beto Prueba', motivo = 'restringido') => noLeido({ motivo, lectores, dueno }, true).txt;
console.log('Textos de lo que no se lee');
ok(area('Restringida: Ana Prueba y Beto Prueba') === 'Restringida a Ana Prueba y Beto Prueba. Si necesitas acceso, pídeselo a Beto Prueba.', '«Restringida: X y Y»');
ok(area('Restringida a dirección') === 'Restringida a dirección. Si necesitas acceso, pídeselo a Beto Prueba.', '«Restringida a X» no repite la «a»');
ok(area('Restringida (dirección)') === 'Restringida a dirección. Si necesitas acceso, pídeselo a Beto Prueba.', '«Restringida (X)» sin paréntesis');
ok(area('**Restringida**: dirección') === 'Restringida a dirección. Si necesitas acceso, pídeselo a Beto Prueba.', 'con negrita');
ok(area('Restringida') === 'Restringida. Si necesitas acceso, pídeselo a Beto Prueba.', 'sin nombres');
ok(area('Restringida: dirección', 'Agustín Torres (escribe también Patricio Torres, dueño de `ronda-semilla/`)').endsWith('pídeselo a Agustín Torres.'), 'del dueño se quita la nota entre paréntesis');
ok(area('Restringida al equipo directivo') === 'Restringida al equipo directivo. Si necesitas acceso, pídeselo a Beto Prueba.', '«Restringida al …» no añade otra «a»');
ok(area('Restringida para dirección') === 'Restringida para dirección. Si necesitas acceso, pídeselo a Beto Prueba.', '«Restringida para …»');
ok(area('Restringida: la leen Ana y Beto') === 'Restringida a Ana y Beto. Si necesitas acceso, pídeselo a Beto Prueba.', '«la leen …» se quita');
ok(area('«Restringida» — dirección') === 'Restringida a dirección. Si necesitas acceso, pídeselo a Beto Prueba.', 'con comillas y raya');
ok(soloNombre('Dirección (Ana, Beto)') === 'Dirección (Ana, Beto)', 'un paréntesis con nombres se queda');
ok(noLeido({ motivo: 'restringido', dueno: 'Beto Prueba' }, false).txt === 'Restringido. Si necesitas acceso, pídeselo a Beto Prueba.', 'un proyecto restringido, sin lectores');
const sc = noLeido({ motivo: 'sin-carpeta', dueno: 'Ana Prueba' }, true);
ok(sc.pill === 'No disponible' && sc.txt === 'Aún no se creó, no está sincronizada o tu cuenta no tiene acceso. Pregunta a Ana Prueba.', 'sin carpeta: las tres causas, sin mandar a pedir acceso');
const mio = noLeido({ motivo: 'sin-carpeta', dueno: 'Ana Prueba', mio: true }, true);
ok(mio.txt === 'Aún no se creó o no está sincronizada en tu computadora.', 'sin carpeta de la propia cuenta: no le dice «pregunta a» a su dueño');
ok(!area('Restringida: <img src=x onerror=alert(1)>').includes('<img'), 'lo que viene de la carpeta se escapa');
process.exit(fallos ? 1 : 0);
