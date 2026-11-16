/* NCT Truck Simulator: drive each truck round a yard and move pallets with it. Needs three.js r128 and its GLTFLoader, loaded before this file. */
(function () {
  var root = document.getElementById('nctf');
  if (!root) return;
  // Optionally lift the block to the top of the page's main area so it spans the full width under the site header
  if (root.getAttribute('data-place') === 'top') {
    var main = document.querySelector('main') || document.getElementById('main');
    if (main && main.firstElementChild !== root) { main.insertBefore(root, main.firstElementChild); root.classList.remove('nctf-breakout'); }
  }

  var TRUCKS = [
    { key: 'counter', gd: 11, gty: 1.2, name: 'Counterbalance', aka: 'The standard forklift', work: 'Raise the forks',
      spot: ['Forks stick straight out at the front', 'Heavy counterweight at the back, no legs in front', 'Driver sits facing forwards under a cage'],
      where: 'loading bays, yards and warehouses with wide aisles.', link: 'See RTITB Counterbalance courses', d: 13.5, ty: 1.15 },
    { key: 'reach', gd: 12.5, gty: 1.8, name: 'Reach truck', aka: 'Tall mast, built for racking', work: 'Reach into the racking',
      spot: ['Two legs run forward along the floor either side of the forks', 'The mast slides forward to reach into the racking', 'Driver sits sideways'],
      where: 'indoor warehouses with high racking and narrower aisles.', link: 'See RTITB Reach courses', d: 15, ty: 1.6 },
    { key: 'pivot', gd: 11, gty: 1.1, name: 'Pivot Steer', aka: 'Also called an articulated truck', work: 'Swing the mast',
      spot: ['Looks like a counterbalance, but hinged in the middle', 'The front end and mast swing to either side', 'Stacks side-on without turning the whole truck'],
      where: 'very narrow aisles, and it can still work outside in the yard.', link: 'See RTITB Pivot Steer courses', d: 13.5, ty: 1.15 },
    { key: 'vna', gd: 17, gty: 2.7, name: 'VNA', aka: 'Very narrow aisle truck', work: 'Lift and turn the forks',
      spot: ['The forks turn to face sideways into the racking', 'On many models the driver rises with the load', 'Runs up and down an aisle barely wider than itself'],
      where: 'high-bay warehouses with the tightest aisles.', link: 'See RTITB VNA courses', d: 16.5, ty: 2.0 },
    { key: 'tele', gd: 19, gty: 2.4, name: 'Telehandler', aka: 'Telescopic handler', work: 'Raise the boom',
      spot: ['A telescopic boom in place of an upright mast', 'Big wheels and a side-mounted cab', 'Forks on the end of the boom reach up and out'],
      where: 'construction sites, farms and rough ground.', link: 'See RTITB Telehandler courses', d: 17, ty: 1.5 },
    { key: 'ppt', az: 2.35, gd: 7.5, gty: 0.6, name: 'Powered pallet truck', aka: 'Often shortened to PPT', work: 'Lift the pallet',
      spot: ['Low forks that lift a pallet just clear of the floor', 'Steered with a tiller arm, not a wheel', 'Operator walks with it or stands on a small platform'],
      where: 'loading docks, shop floors and the backs of lorries.', link: 'See RTITB PPT courses', d: 9, ty: 0.55 },
    { key: 'pump', gd: 6.5, gty: 0.5, az: 2.5, name: 'Pump truck', aka: 'Manual hand pallet truck', work: 'Pump it up',
      spot: ['No motor or battery: you pump the handle to lift', 'Long handle with a loop grip', 'Two low forks on small rollers'],
      where: 'shop floors, stockrooms and the backs of delivery vehicles.', link: 'See RTITB Pump Truck training', d: 6.5, ty: 0.55 },
    { key: 'picker_low', gd: 11.5, gty: 0.7, az: 2.35, name: 'Low-level order picker', aka: 'Ride-on picking truck', work: 'Lift the pallets',
      spot: ['Operator rides standing, between the drive unit and the forks', 'Very long forks that carry two pallets', 'Step-through sides for hopping on and off'],
      where: 'distribution centres, picking at floor and first level.', link: 'See RTITB Order Picker courses', d: 11, ty: 0.8 },
    { key: 'picker_high', gd: 15.5, gty: 2.4, name: 'High-level order picker', aka: 'The operator goes up with the forks', work: 'Raise the platform',
      spot: ['Operator stands on a platform that rises up the mast', 'Forks fixed straight ahead, with a pallet to pick onto', 'Guard rails and a cage around the operator'],
      where: 'warehouses where goods are picked by hand from high racking.', link: 'See RTITB Order Picker courses', d: 15, ty: 2.4 },
    { key: 'mewp', gd: 15.5, gty: 2.4, name: 'MEWP: scissor lift', aka: 'Mobile elevating work platform', work: 'Raise the platform',
      spot: ['Lifts people, not loads', 'A railed platform on a criss-cross scissor stack', 'Goes straight up and down'],
      where: 'maintenance, installation and work at height on site.', link: 'See RTITB MEWP courses', d: 16, ty: 1.9 },
    { key: 'boom', gd: 22, gty: 3.8, az: -0.95, name: 'MEWP: boom lift', aka: 'Often called a cherry picker', work: 'Raise the boom',
      spot: ['A basket on the end of a jointed, telescopic boom', 'Reaches up and over obstacles', 'Turntable and counterweight on a four-wheel chassis'],
      where: 'construction, maintenance and outdoor work at height.', link: 'See RTITB MEWP courses', d: 26, ty: 4.0 },
    { key: 'gantry', gd: 18, gty: 2.0, az: -0.5, name: 'Gantry crane', aka: 'Overhead lifting on a frame', work: 'Lift the load',
      spot: ['A beam across two A-frame legs', 'A hoist that travels along the beam', 'Loads are slung from a hook, not carried on forks'],
      where: 'workshops, yards and fabrication bays.', link: 'See RTITB Gantry Crane courses', d: 20, ty: 2.2 }
  ];

  // Each machine's levers. The first lever drives every moving part not claimed by a later one (matched by part name).
  var CFG = window.NCTTruckFinder || {}, LINKS = {"counter": "rtitb-counterbalance-courses", "reach": "rtitb-reach-courses", "pivot": "rtitb-pivotsteer-courses", "vna": "rtitb-vna-courses", "tele": "rtitb-telehander-courses", "ppt": "rtitb-ppt-courses", "pump": "rtitb-pump-truck-training", "picker_low": "rtitb-manual-handling-courses-2", "picker_high": "rtitb-manual-handling-courses-2", "mewp": "rtitb-mewp-courses", "boom": "rtitb-mewp-courses", "gantry": "rtitb-gantry-courses"};
  var CONTROLS = {
    counter: [['Lift']], reach: [['Lift'], ['Reach', '^reach$']], pivot: [['Lift'], ['Swing', '^front_pivot$']],
    vna: [['Lift'], ['Turn forks', '^turret$']], tele: [['Raise boom'], ['Extend boom', '^boom_inner$']], ppt: [['Lift']],
    pump: [['Lower'], ['Pump handle', '^(tiller|plunger|spring)$', 'stroke']], picker_low: [['Lift']], picker_high: [['Raise platform']],
    mewp: [['Raise platform']], boom: [['Raise boom']], gantry: [['Hoist'], ['Travel', '^(trolley|feed_cable)$']]
  };
  TRUCKS.forEach(function (t) { t.controls = CONTROLS[t.key]; t.drive = t.key !== 'gantry'; t.tiller = t.key === 'ppt' || t.key === 'pump' || t.key === 'picker_low'; });
  var current = 0, targets = [0, 0], vals = [0, 0], defl = [0, 0], stroke = 0;
  var tabs = Array.prototype.slice.call(document.querySelectorAll('#nctf-tabs .nctf-tab'));
  var leversEl = document.getElementById('nctf-levers');
  var onSelect = function () {};
  function show(i) {
    current = (i + TRUCKS.length) % TRUCKS.length; targets = [0, 0]; vals = [0, 0]; defl = [0, 0]; stroke = 0;
    var t = TRUCKS[current];
    document.getElementById('nctf-t-name').textContent = t.name;
    document.getElementById('nctf-t-aka').textContent = t.aka;
    var ul = document.getElementById('nctf-t-spot'); ul.textContent = '';
    t.spot.forEach(function (s) { var li = document.createElement('li'); li.textContent = s; ul.appendChild(li); });
    var w = document.getElementById('nctf-t-where'); w.textContent = '';
    var b = document.createElement('b'); b.textContent = 'Where you see it: '; w.appendChild(b); w.appendChild(document.createTextNode(t.where));
    var lk = document.getElementById('nctf-t-link'); lk.textContent = t.link; lk.href = (CFG.courses || '/courses/') + LINKS[t.key] + '/';
    document.getElementById('nctf-count').textContent = (current + 1) + ' of ' + TRUCKS.length;
    tabs.forEach(function (el, n) { el.setAttribute('aria-pressed', String(n === current)); });
    leversEl.textContent = '';
    t.controls.forEach(function (c, n) {
      var row = document.createElement('div'); row.className = 'nctf-hlever';
      var slot = document.createElement('div'); slot.className = 'nctf-slot'; slot.id = 'nctf-lever-' + n; slot.tabIndex = 0;
      slot.setAttribute('role', 'slider'); slot.setAttribute('aria-label', c[0] + ' lever: pull up to raise, push down to lower');
      slot.setAttribute('aria-valuemin', 0); slot.setAttribute('aria-valuemax', 100); slot.setAttribute('aria-valuenow', 0);
      var knob = document.createElement('span'); knob.className = 'nctf-knob'; slot.appendChild(knob);
      var nm = document.createElement('span'); nm.className = 'nctf-hl-name'; nm.textContent = c[0];
      var out = document.createElement('span'); out.className = 'nctf-hl-val'; out.id = 'nctf-lever-' + n + '-out'; out.textContent = '0%';
      function set(d) { defl[n] = Math.max(-1, Math.min(1, d)); knob.style.transform = 'translateY(' + (-defl[n] * 30) + 'px)'; }
      var y0 = 0;
      slot.addEventListener('pointerdown', function (e) { e.preventDefault(); y0 = e.clientY; slot.classList.add('nctf-drag'); try { slot.setPointerCapture(e.pointerId); } catch (x) {} slot.focus(); });
      slot.addEventListener('pointermove', function (e) { if (slot.classList.contains('nctf-drag')) set((y0 - e.clientY) / 30); });
      ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(function (ev) { slot.addEventListener(ev, function () { slot.classList.remove('nctf-drag'); set(0); }); });
      slot.addEventListener('keydown', function (e) { if (e.key === 'ArrowUp') { set(1); e.preventDefault(); } else if (e.key === 'ArrowDown') { set(-1); e.preventDefault(); } });
      slot.addEventListener('keyup', function (e) { if (e.key === 'ArrowUp' || e.key === 'ArrowDown') set(0); });
      slot.addEventListener('blur', function () { set(0); });
      row.appendChild(slot); row.appendChild(nm); row.appendChild(out); leversEl.appendChild(row);
    });
    document.getElementById('nctf-drive').hidden = !t.drive;
    document.getElementById('nctf-ped').hidden = !t.tiller; document.getElementById('nctf-rider').hidden = t.tiller;
    document.getElementById('nctf-throttle-name').textContent = t.key === 'pump' ? 'Push / pull' : 'Travel';
    document.getElementById('nctf-yard').setAttribute('aria-label', '3D model of a ' + t.name + '. ' + t.spot.join('. ') + '.');
    onSelect();
  }
  tabs.forEach(function (el, n) { el.addEventListener('click', function () { show(n); }); });
  document.getElementById('nctf-prev').addEventListener('click', function () { show(current - 1); });
  document.getElementById('nctf-next').addEventListener('click', function () { show(current + 1); });
  show(0);

  var stage = document.getElementById('nctf-stage');
  var canvas = document.getElementById('nctf-yard');
  function useFallback() { stage.hidden = true; }
  if (!window.THREE) { useFallback(); return; }
  var renderer;
  try { renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true }); } catch (e) { useFallback(); return; }

  var PLUM = 0x43003F, MAG = 0xE4125D, ORANGE = 0xF08418;
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setClearColor(PLUM, 1);
  renderer.outputEncoding = THREE.sRGBEncoding;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  function lin(c) { return new THREE.Color(c).convertSRGBToLinear(); }
  var scene = new THREE.Scene();
  scene.fog = new THREE.Fog(lin(PLUM), 26, 48);
  var camera = new THREE.PerspectiveCamera(30, 1, 0.1, 100);

  // Studio reflections: a small lit room baked into an environment map
  (function () {
    var room = new THREE.Scene(); room.background = lin(0x2a1428);
    function panel(w, h, c, x, y, z, rx, ry) {
      var m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: lin(c), side: THREE.DoubleSide }));
      m.position.set(x, y, z); m.rotation.set(rx, ry, 0); room.add(m);
    }
    panel(14, 10, 0xffffff, 0, 9, 0, Math.PI / 2, 0);
    panel(8, 5, 0xfff0e0, 10, 4, 3, 0, -Math.PI / 2);
    panel(8, 5, 0xd9c0e6, -10, 4, -2, 0, Math.PI / 2);
    panel(10, 4, 0xbfa8c8, 0, 3, 11, 0, Math.PI);
    panel(30, 30, 0x43003f, 0, -0.5, 0, -Math.PI / 2, 0);
    var pm = new THREE.PMREMGenerator(renderer);
    scene.environment = pm.fromScene(room, 0.03).texture; pm.dispose();
  })();
  scene.add(new THREE.HemisphereLight(0xffffff, 0x5d0059, 0.5));
  var sun = new THREE.DirectionalLight(0xfff6ea, 1.5);
  sun.position.set(5, 10, 5); sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.left = -12; sun.shadow.camera.right = 12; sun.shadow.camera.top = 12; sun.shadow.camera.bottom = -12;
  sun.shadow.camera.near = 1; sun.shadow.camera.far = 28; sun.shadow.bias = -0.0004; sun.shadow.radius = 5;
  scene.add(sun);

  function std(c, r, m, more) { var o = new THREE.MeshStandardMaterial({ color: lin(c), roughness: r, metalness: m }); if (more) { if (more.emissive !== undefined) more.emissive = lin(more.emissive); o.setValues(more); } return o; }
  function coat(c) { return new THREE.MeshPhysicalMaterial({ color: lin(c), roughness: 0.42, metalness: 0, clearcoat: 0.8, clearcoatRoughness: 0.22 }); }
  var M = {
    paint: coat(ORANGE), mag: coat(MAG), dark: std(0x2a262d, 0.55, 0.3), mast: std(0x1b191d, 0.42, 0.65),
    steel: std(0x9a9ca3, 0.34, 0.95), chrome: std(0xe3e5ea, 0.1, 1), rubber: std(0x0e0d0f, 0.93, 0), vinyl: std(0x17151a, 0.62, 0),
    rim: std(0xd9d6d2, 0.45, 0.4), card: std(0xb58a5a, 0.9, 0), card2: std(0xa27a4e, 0.9, 0), tape: std(0xd8c39a, 0.5, 0), wood: std(0xcdaa78, 0.85, 0),
    lamp: std(0xfff6dd, 0.3, 0, { emissive: 0xfff0c0, emissiveIntensity: 1.1 }), beacon: std(0xff9a2a, 0.35, 0, { emissive: 0xff7a00, emissiveIntensity: 0.9 }),
    tail: std(0xc01818, 0.35, 0, { emissive: 0xa00808, emissiveIntensity: 0.7 }),
    glass: new THREE.MeshPhysicalMaterial({ color: lin(0xa9bccb), roughness: 0.05, metalness: 0, transparent: true, opacity: 0.3 }),
    rackU: std(ORANGE, 0.6, 0.25), rackB: std(MAG, 0.6, 0.25)
  };
  function add(m, x, y, z, parent) { m.position.set(x, y, z); m.castShadow = true; m.receiveShadow = true; (parent || scene).add(m); return m; }
  function box(w, h, d, mt, x, y, z, parent) { return add(new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mt), x, y, z, parent); }
  // Box with rounded edges and corners, so painted panels catch the light like pressed steel
  function rbox(w, h, d, mt, x, y, z, parent, r) {
    var b = Math.min(r || 0.035, w / 2 - 0.002, h / 2 - 0.002, d / 2 - 0.002);
    var sw = w - 2 * b, sh = h - 2 * b, c = Math.min(b, sw / 2, sh / 2) * 0.98, s = new THREE.Shape();
    s.moveTo(-sw / 2 + c, -sh / 2); s.lineTo(sw / 2 - c, -sh / 2); s.absarc(sw / 2 - c, -sh / 2 + c, c, -Math.PI / 2, 0, false);
    s.lineTo(sw / 2, sh / 2 - c); s.absarc(sw / 2 - c, sh / 2 - c, c, 0, Math.PI / 2, false);
    s.lineTo(-sw / 2 + c, sh / 2); s.absarc(-sw / 2 + c, sh / 2 - c, c, Math.PI / 2, Math.PI, false);
    s.lineTo(-sw / 2, -sh / 2 + c); s.absarc(-sw / 2 + c, -sh / 2 + c, c, Math.PI, Math.PI * 1.5, false);
    var g = new THREE.ExtrudeGeometry(s, { depth: d - 2 * b, bevelEnabled: true, bevelThickness: b, bevelSize: b, bevelSegments: 3, curveSegments: 5 });
    g.center(); return add(new THREE.Mesh(g, mt), x, y, z, parent);
  }
  function cyl(r, len, mt, x, y, z, parent, axis) {
    var m = add(new THREE.Mesh(new THREE.CylinderGeometry(r, r, len, 24), mt), x, y, z, parent);
    if (axis === 'x') m.rotation.z = Math.PI / 2; else if (axis === 'z') m.rotation.x = Math.PI / 2; return m;
  }
  function group(parent, x, y, z) { var g = new THREE.Group(); g.position.set(x || 0, y || 0, z || 0); (parent || scene).add(g); return g; }
  function tyre(r, w, x, z, parent, rimMat) {
    var v = function (a, b) { return new THREE.Vector2(a * r, b * w); };
    var t = add(new THREE.Mesh(new THREE.LatheGeometry([v(0.6, -0.5), v(0.88, -0.5), v(0.97, -0.42), v(1, -0.28), v(1, 0.28), v(0.97, 0.42), v(0.88, 0.5), v(0.6, 0.5)], 36), M.rubber), x, r, z, parent);
    t.rotation.z = Math.PI / 2;
    cyl(r * 0.61, w * 0.78, rimMat || M.paint, x, r, z, parent, 'x');
    cyl(r * 0.22, w * 0.98, M.dark, x, r, z, parent, 'x');
    for (var k = 0; k < 6; k++) cyl(r * 0.045, w * 0.86, M.steel, x, r + Math.sin(k * 1.047) * r * 0.4, z + Math.cos(k * 1.047) * r * 0.4, parent, 'x');
  }
  function paint(w, d, c, x, z, rot) {
    var m = new THREE.Mesh(new THREE.PlaneGeometry(w, d), new THREE.MeshBasicMaterial({ color: lin(c), toneMapped: false }));
    m.rotation.x = -Math.PI / 2; if (rot) m.rotation.z = rot; m.position.set(x, 0.004, z); scene.add(m);
  }
  function pallet(parent, x, y, z) {
    var pal = group(parent, x, y, z), k;
    for (k = 0; k < 5; k++) box(1.2, 0.025, 0.16, M.wood, 0, 0.132, -0.42 + k * 0.21, pal);
    [-0.52, 0, 0.52].forEach(function (px) { box(0.12, 0.1, 1.0, M.wood, px, 0.07, 0, pal); });
    for (k = 0; k < 3; k++) box(1.2, 0.02, 0.14, M.wood, 0, 0.01, -0.42 + k * 0.42, pal);
    [0, 1].forEach(function (row) { [-1, 1].forEach(function (sd) {
      var cy = 0.145 + 0.2 + row * 0.41, cx = sd * 0.285;
      rbox(0.55, 0.4, 0.88, (row + sd) % 2 ? M.card : M.card2, cx, cy, 0, pal, 0.012);
      box(0.07, 0.004, 0.885, M.tape, cx, cy + 0.2, 0, pal);
    }); });
    box(1.135, 0.035, 0.89, M.mag, 0, 0.56, 0, pal);
    return pal;
  }
  // Fork carriage: load backrest, two tapered steel tines and a loaded pallet. z0 is the face of the uprights.
  var tineGeo = (function () {
    var s = new THREE.Shape(); s.moveTo(0, 0); s.lineTo(1.22, 0); s.lineTo(1.22, 0.012); s.lineTo(1.0, 0.045); s.lineTo(0.05, 0.045); s.lineTo(0.05, 0.56); s.lineTo(0, 0.56); s.lineTo(0, 0);
    return new THREE.ExtrudeGeometry(s, { depth: 0.11, bevelEnabled: false });
  })();
  function forkSet(parent, z0) {
    rbox(0.98, 0.42, 0.07, M.dark, 0, 0.4, z0 - 0.06, parent, 0.015);
    box(0.98, 0.05, 0.05, M.dark, 0, 1.14, z0 - 0.06, parent);
    [-0.465, 0.465].forEach(function (x) { box(0.05, 0.76, 0.05, M.dark, x, 0.78, z0 - 0.06, parent); });
    [-0.23, 0, 0.23].forEach(function (x) { box(0.028, 0.72, 0.028, M.dark, x, 0.78, z0 - 0.06, parent); });
    [-0.27, 0.27].forEach(function (x) { var t = add(new THREE.Mesh(tineGeo, M.steel), x + 0.055, 0.02, z0 - 0.02, parent); t.rotation.y = -Math.PI / 2; });
    pallet(parent, 0, 0.065, z0 + 0.6);
  }
  function mast(parent, hx, h, z) {
    [-hx, hx].forEach(function (x) {
      rbox(0.1, h, 0.17, M.mast, x, h / 2 + 0.12, z, parent, 0.012);
      box(0.06, h - 0.3, 0.1, M.dark, x * 0.8, h / 2 + 0.2, z + 0.04, parent);
      box(0.022, h - 0.5, 0.03, M.steel, x * 0.45, h / 2 + 0.15, z + 0.07, parent);
    });
    rbox(hx * 2 + 0.12, 0.12, 0.14, M.mast, 0, h + 0.1, z, parent, 0.012);
    rbox(hx * 2 + 0.12, 0.12, 0.14, M.mast, 0, h * 0.55, z - 0.02, parent, 0.012);
    rbox(hx * 2 + 0.12, 0.14, 0.14, M.mast, 0, 0.42, z, parent, 0.012);
    cyl(0.055, h * 0.5, M.dark, 0, 0.4 + h * 0.25, z - 0.03, parent, 'y');
    cyl(0.032, h * 0.48, M.chrome, 0, 0.4 + h * 0.73, z - 0.03, parent, 'y');
  }
  function guard(parent, hx, zf, zr, y0, y1, lamps) {
    [[-hx, zf], [hx, zf], [-hx, zr], [hx, zr]].forEach(function (q) { rbox(0.065, y1 - y0, 0.075, M.mast, q[0], (y0 + y1) / 2, q[1], parent, 0.015); });
    [-hx, hx].forEach(function (x) { rbox(0.07, 0.06, zf - zr + 0.1, M.mast, x, y1, (zf + zr) / 2, parent, 0.015); });
    var n = Math.max(3, Math.round((zf - zr) / 0.19)), k;
    for (k = 0; k <= n; k++) box(hx * 2, 0.03, 0.04, M.mast, 0, y1 + 0.005, zr + (zf - zr) * k / n, parent);
    cyl(0.055, 0.03, M.dark, hx - 0.12, y1 + 0.05, zr + 0.1, parent, 'y'); cyl(0.045, 0.09, M.beacon, hx - 0.12, y1 + 0.1, zr + 0.1, parent, 'y');
    if (lamps !== false) [-hx, hx].forEach(function (x) { cyl(0.06, 0.07, M.dark, x, y1 - 0.2, zf + 0.06, parent, 'z'); cyl(0.045, 0.02, M.lamp, x, y1 - 0.2, zf + 0.1, parent, 'z'); });
  }
  function seat(parent, x, y, z, side) {
    rbox(0.5, 0.13, 0.48, M.vinyl, x, y, z, parent, 0.05);
    var b = side ? rbox(0.13, 0.56, 0.48, M.vinyl, x - 0.22, y + 0.3, z, parent, 0.05) : rbox(0.5, 0.56, 0.13, M.vinyl, x, y + 0.3, z - 0.22, parent, 0.05);
    if (side) b.rotation.z = 0.1; else b.rotation.x = -0.1;
  }
  function steering(parent, x, y, z) {
    var c = cyl(0.03, 0.42, M.dark, x, y, z, parent, 'y'); c.rotation.x = -0.45;
    var w = add(new THREE.Mesh(new THREE.TorusGeometry(0.17, 0.022, 10, 28), M.vinyl), x, y + 0.2, z - 0.1, parent); w.rotation.x = Math.PI / 2 - 0.45;
    cyl(0.02, 0.05, M.dark, x + 0.12, y + 0.24, z - 0.02, parent, 'y');
  }

  // Floor, painted markings and loaded racking
  var floor = new THREE.Mesh(new THREE.PlaneGeometry(90, 90), new THREE.MeshBasicMaterial({ color: lin(PLUM), toneMapped: false, fog: false }));
  floor.rotation.x = -Math.PI / 2; scene.add(floor);
  var shade = new THREE.Mesh(new THREE.PlaneGeometry(40, 40), new THREE.ShadowMaterial({ color: 0x000000, opacity: 0.42, fog: false }));
  shade.rotation.x = -Math.PI / 2; shade.position.y = 0.008; shade.receiveShadow = true; scene.add(shade);
  // The yard: a pick-up area on the left, three marked bays on the right, racking with two free slots at the back
  var lw = 0.12, i;
  var YARD = { x: 7.4, zMax: 7.0 };
  for (i = 0; i < 9; i++) paint(0.14, 1.5, 0xEED4E9, -7.4 + i * 0.5, 6.4, Math.PI / 4);        // hatched edge by the pick-up area
  paint(0.12, 13.4, 0xEED4E9, -3.6, 0.2); paint(0.12, 13.4, 0xEED4E9, 3.6, 0.2);                  // lane lines
  paint(7.3, lw, MAG, -0.2, -6.55);                                                              // rack approach line
  var goals = [];
  function bay(x, z) {            // a square painted on the floor that changes colour when a pallet is set down in it
    var mt = new THREE.MeshBasicMaterial({ color: lin(0xFB8E28), toneMapped: false }), w = 1.9;
    [[w, lw, 0, -w / 2], [w, lw, 0, w / 2], [lw, w, -w / 2, 0], [lw, w, w / 2, 0]].forEach(function (q) {
      var m = new THREE.Mesh(new THREE.PlaneGeometry(q[0], q[1]), mt); m.rotation.x = -Math.PI / 2; m.position.set(x + q[2], 0.005, z + q[3]); scene.add(m);
    });
    goals.push({ x: x, z: z, y: 0, mat: mt });
  }
  bay(5.5, -2.7); bay(5.5, 0); bay(5.5, 2.7);
  var PICKUP = [[-5.5, -2.7], [-5.5, 0], [-5.5, 2.7], [-5.5, 5.2]];
  PICKUP.forEach(function (q) { paint(1.5, 0.08, 0x7A3F77, q[0], q[1] - 0.85); paint(1.5, 0.08, 0x7A3F77, q[0], q[1] + 0.85); });
  var rack = group(scene, -0.2, 0, -7.6), p, s;
  for (p = 0; p < 4; p++) [0.5, -0.5].forEach(function (z) { box(0.1, 5.5, 0.08, M.rackU, -3.6 + p * 2.4, 2.75, z, rack); });
  for (p = 0; p < 4; p++) for (s = 0; s < 5; s++) { var br = box(0.03, 0.03, 1.25, M.rackU, -3.6 + p * 2.4, 0.6 + s * 1.05, 0, rack); br.rotation.x = s % 2 ? 0.7 : -0.7; }
  for (s = 0; s < 4; s++) [0.5, -0.5].forEach(function (z) { box(7.3, 0.12, 0.06, M.rackB, 0, 1.2 + s * 1.2, z, rack); });
  [[-2.4, 0], [0, 0], [-2.4, 1], [2.4, 1], [0, 2], [2.4, 2], [-2.4, 3], [0, 3]].forEach(function (l) { pallet(rack, l[0], l[1] === 0 ? 0 : 1.2 + (l[1] - 1) * 1.2 + 0.06, 0); });
  // Four rack positions are left empty for pallets to be put away in: floor level and one on each of the three beams
  var RACK_Z = -6.95;
  var SLOTS = [{ x: 2.2, y: 0, z: -7.6, taken: null }, { x: -0.2, y: 1.26, z: -7.6, taken: null }, { x: -2.6, y: 2.46, z: -7.6, taken: null }, { x: 2.2, y: 3.66, z: -7.6, taken: null }];
  SLOTS.forEach(function (sl) {
    var mt = new THREE.MeshBasicMaterial({ color: lin(0xFB8E28), toneMapped: false });
    var m = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.03, 0.05), mt); m.position.set(sl.x, sl.y + (sl.y ? 0.075 : 0.02), sl.z + 0.56); scene.add(m);
    sl.mat = mt; goals.push(sl);
  });

  // ---- Pallets are separate objects in the yard, not part of the truck
  var pallets = [], carry = null, proto = null, lastH = 0, fp = new THREE.Vector3(), fq = new THREE.Quaternion(), UP = new THREE.Vector3(0, 1, 0);
  var PAL_RE = /^(pallet|pal|pal_front|pal_rear|cartons)$/;
  function setPalletPose(pl) { pl.o.position.set(pl.x, pl.y, pl.z); pl.o.quaternion.setFromAxisAngle(UP, pl.yaw); }
  function resetYard() {
    if (!proto) return;
    carry = null; SLOTS.forEach(function (sl) { sl.taken = null; });
    PICKUP.forEach(function (q, n) {
      var pl = pallets[n];
      if (!pl) { pl = { o: proto.clone(true) }; scene.add(pl.o); pallets.push(pl); }
      pl.x = q[0]; pl.z = q[1]; pl.y = 0; pl.yaw = Math.PI / 2; pl.slot = null; pl.eng = false; setPalletPose(pl);
    });
    score();
  }
  function yawOf(q) { var v = new THREE.Vector3(0, 0, 1).applyQuaternion(q); return Math.atan2(v.x, v.z); }
  function fold(a) { var h = Math.PI / 2; a = ((a % h) + h) % h; return a > h / 2 ? a - h : a; }
  function onTarget(pl) {
    if (pl.slot) return pl.slot;
    if (pl.y !== 0) return null;
    for (var n = 0; n < 3; n++) if (Math.abs(pl.x - goals[n].x) < 0.6 && Math.abs(pl.z - goals[n].z) < 0.6) return goals[n];
    return null;
  }
  var taskEl = document.getElementById('nctf-task'), hintEl = document.getElementById('nctf-hint'), lastHint = '';
  function hint(t) { if (t !== lastHint && hintEl) { lastHint = t; hintEl.textContent = t; } }
  function score() {
    var n = 0; goals.forEach(function (tg) { tg.hit = false; });
    pallets.forEach(function (pl) { if (carry && carry.p === pl) return; var tg = onTarget(pl); if (tg) { tg.hit = true; n++; } });
    goals.forEach(function (tg) { tg.mat.color.copy(lin(tg.hit ? 0xEED4E9 : 0xFB8E28)); });
    if (taskEl) taskEl.textContent = pallets.length ? (n === pallets.length ? 'All ' + n + ' pallets placed. Reset the yard to go again.' : n + ' of ' + pallets.length + ' pallets placed') : 'Loading the yard';
  }
  // Where a carried pallet would come to rest if lowered here: a free rack slot, the floor, or nowhere (null)
  function supportAt(x, z, h, self) {
    var best = null;
    for (var n = 0; n < SLOTS.length; n++) { var sl = SLOTS[n]; if (!sl.taken && Math.abs(x - sl.x) < 0.5 && Math.abs(z - sl.z) < 0.6 && h > sl.y - 0.1 && (!best || sl.y > best.y)) best = sl; }
    if (best) return { y: best.y, slot: best };
    if (z < -6.85) return null;
    for (var k = 0; k < pallets.length; k++) { var o = pallets[k]; if (o !== self && o.y === 0 && Math.abs(o.x - x) < 1.15 && Math.abs(o.z - z) < 1.15) return null; }
    return { y: 0, slot: null };
  }
  // Solid things: the truck body, its forks and a carried pallet cannot pass through pallets or racking.
  // Forks may only enter a pallet at the right height and roughly square on, and only enter the racking at a free position.
  var bumpAt = 0, blockedFor = 0;
  // Returns null when nothing is touching, otherwise what is touching and a function giving how far apart the two are,
  // so a move can be judged as heading into the obstacle (refused) or away from it (always allowed).
  function collide(m) {
    var gp = m.g.position, b = m.body, k, n, q;
    function circ(kk) { var hd = m.g.rotation.y; return [gp.x + Math.sin(hd) * b.zs[kk], gp.z + Math.cos(hd) * b.zs[kk]]; }
    function fork() { m.g.updateMatrixWorld(true); m.forkRef.getWorldPosition(fp); return fp; }
    if (b) for (k = 0; k < b.zs.length; k++) {
      var c = circ(k);
      if (c[1] - b.r < RACK_Z) return (function (kk) { return function () { return circ(kk)[1]; }; })(k);
      for (n = 0; n < pallets.length; n++) {
        q = pallets[n]; if ((carry && carry.p === q) || q.y > 0.5) continue;
        var dx = c[0] - q.x, dz = c[1] - q.z;
        if (dx * dx + dz * dz < (b.r + 0.56) * (b.r + 0.56)) return (function (kk, qq) { return function () { var cc = circ(kk); return Math.sqrt((cc[0] - qq.x) * (cc[0] - qq.x) + (cc[1] - qq.z) * (cc[1] - qq.z)); }; })(k, q);
      }
    }
    if (m.forkRef) {
      fork(); m.forkRef.getWorldQuaternion(fq);
      var fy = yawOf(fq), h = fp.y - m.y0, T = m.liftT;
      for (n = 0; n < pallets.length; n++) {
        q = pallets[n]; if (carry && carry.p === q) continue;
        var ex = fp.x - q.x, ez = fp.z - q.z, d2 = ex * ex + ez * ez, hit = false;
        if (carry) hit = d2 < 1.21 && Math.abs(h - q.y) < 1.0;
        else hit = d2 < 0.85 && h < q.y + 1.0 && h > q.y - 0.08 && !(h <= q.y + T + 0.12 && Math.abs(fold(fy - q.yaw)) < 0.4);
        if (hit) { var tf = (function (qq) { return function () { var f = fork(); return Math.sqrt((f.x - qq.x) * (f.x - qq.x) + (f.z - qq.z) * (f.z - qq.z)); }; })(q); tf.fork = true; return tf; }
      }
      if (fp.z - 0.5 < RACK_Z) {
        var ok = fp.z >= -7.95;
        if (ok) { ok = false; for (n = 0; n < SLOTS.length; n++) if (Math.abs(fp.x - SLOTS[n].x) < 0.5 && h >= SLOTS[n].y - 0.08 && h <= SLOTS[n].y + 0.4) ok = true; }
        if (!ok) { var tr = function () { return fork().z; }; tr.fork = true; return tr; }
      }
    }
    return null;
  }
  function forkWork(m) {
    if (!m.forkRef || !pallets.length) { hint(m.forkRef ? '' : 'This machine does not carry pallets. Drive it and work its controls.'); return; }
    m.g.updateMatrixWorld(true); m.forkRef.getWorldPosition(fp); m.forkRef.getWorldQuaternion(fq);
    var fy = yawOf(fq), h = fp.y - m.y0, T = m.liftT;
    if (carry) {
      var sup = supportAt(fp.x, fp.z, h, carry.p), pl = carry.p;
      if (sup && h <= sup.y + T * 0.5 && h <= lastH + 0.0005) {        // lowered onto something: set it down
        pl.y = sup.y; pl.yaw = fy + carry.off; pl.x = fp.x; pl.z = fp.z;
        if (sup.slot) { pl.x = sup.slot.x; pl.z = sup.slot.z; pl.yaw = Math.round(pl.yaw / Math.PI) * Math.PI; sup.slot.taken = pl; pl.slot = sup.slot; }
        setPalletPose(pl); pl.eng = true; carry = null; score(); hint('Pallet down. Reverse out, or raise the forks to lift it again.');
      } else {
        pl.o.position.copy(fp); pl.o.quaternion.copy(fq).multiply(new THREE.Quaternion().setFromAxisAngle(UP, carry.off));
        hint(performance.now() - bumpAt < 900 ? (blockedFor > 1.2 ? 'Blocked. Reverse away, or press Recover truck.' : 'Something is in the way.') : sup ? 'Carrying a pallet. Lower the forks to set it down.' : 'Carrying a pallet. There is no room to set it down here.');
      }
    } else {
      var msg = performance.now() - bumpAt < 900 ? (blockedFor > 1.2 ? 'Blocked. Reverse away, or press Recover truck.' : 'Something is in the way. Check the fork height and line up square.') : 'Line the forks up with a pallet, drive in low, then raise them.';
      for (var n = 0; n < pallets.length; n++) {
        var q = pallets[n], d = Math.sqrt((fp.x - q.x) * (fp.x - q.x) + (fp.z - q.z) * (fp.z - q.z)), ok = d < 0.36 && Math.abs(fold(fy - q.yaw)) < 0.32;
        if (ok && h >= q.y - 0.05 && h <= q.y + T) q.eng = true; else if (!ok || h < q.y - 0.05) q.eng = false;
        if (q.eng && ok) msg = 'Forks are in. Raise them to lift the pallet.';
        else if (d < 1.4 && Math.abs(h - q.y) > T + 0.05 && d > 0.36) msg = h > q.y ? 'Forks are too high for this pallet. Lower them first.' : 'Raise the forks to the height of this pallet.';
        if (q.eng && ok && h > q.y + T) {
          if (q.slot) { q.slot.taken = null; q.slot = null; }
          carry = { p: q, off: Math.round((q.yaw - fy) / (Math.PI / 2)) * (Math.PI / 2) }; q.eng = false; score(); break;
        }
      }
      if (!carry) hint(msg);
    }
    lastH = h;
  }
  var resetBtn = document.getElementById('nctf-reset-yard'); if (resetBtn) resetBtn.addEventListener('click', function () { resetYard(); park(); });


  var models = {};
  function cbRear(g, z) {   // shared rear half of a counterbalance-style truck; z is the centre of the hood
    rbox(1.1, 0.34, 2.2, M.dark, 0, 0.42, z + 0.08, g, 0.05);
    rbox(1.14, 0.5, 1.25, M.paint, 0, 0.82, z, g, 0.08);
    rbox(1.18, 0.8, 0.62, M.paint, 0, 0.68, z - 0.86, g, 0.15);
    rbox(0.86, 0.05, 0.36, M.dark, 0, 1.085, z - 0.86, g, 0.02);
    cyl(0.035, 0.22, M.steel, 0, 0.45, z - 1.19, g, 'y');
    [-0.44, 0.44].forEach(function (x) { rbox(0.13, 0.07, 0.03, M.tail, x, 0.93, z - 1.17, g, 0.012); });
    rbox(1.0, 0.46, 0.14, M.dark, 0, 1.05, z + 0.76, g, 0.04);
    steering(g, 0, 1.3, z + 0.68); seat(g, 0, 1.13, z - 0.1);
    [0, 1, 2].forEach(function (k) { cyl(0.012, 0.2, M.steel, 0.3 + k * 0.055, 1.33, z + 0.66, g, 'y'); cyl(0.022, 0.03, M.dark, 0.3 + k * 0.055, 1.44, z + 0.66, g, 'y'); });
    guard(g, 0.5, z + 0.84, z - 0.52, 1.05, 2.3);
  }
  // Counterbalance
  (function () {
    var g = group(); g.visible = false;
    cbRear(g, -0.5);
    [-0.62, 0.62].forEach(function (x) { rbox(0.36, 0.06, 0.92, M.paint, x, 0.8, 0.42, g, 0.025); cyl(0.032, 0.62, M.chrome, x * 0.78, 0.82, 0.58, g, 'z').rotation.x = Math.PI / 2 - 0.5; });
    tyre(0.37, 0.3, -0.62, 0.42, g); tyre(0.37, 0.3, 0.62, 0.42, g); tyre(0.28, 0.24, -0.56, -1.15, g); tyre(0.28, 0.24, 0.56, -1.15, g);
    mast(g, 0.36, 2.7, 0.88);
    var car = group(g); forkSet(car, 1.06);
    models.counter = { g: g, pose: function (e) { car.position.y = 0.01 + e * 1.55; } };
  })();
  // Reach
  (function () {
    var g = group(); g.visible = false;
    rbox(1.16, 0.3, 1.2, M.dark, 0, 0.36, -1.08, g, 0.04); rbox(1.16, 0.78, 1.05, M.paint, 0, 0.88, -1.12, g, 0.09);
    rbox(1.0, 0.05, 0.9, M.dark, 0, 1.285, -1.12, g, 0.02);
    [-0.52, 0.52].forEach(function (x) { rbox(0.17, 0.17, 1.95, M.dark, x, 0.19, 0.3, g, 0.03); tyre(0.11, 0.13, x, 1.12, g, M.steel); });
    tyre(0.2, 0.18, -0.48, -1.32, g); tyre(0.2, 0.18, 0.48, -1.32, g);
    seat(g, 0.1, 1.36, -1.12, true); rbox(0.14, 0.4, 0.5, M.dark, 0.42, 1.5, -1.12, g, 0.04);
    guard(g, 0.5, -0.68, -1.58, 1.28, 2.5, false);
    var m = group(g, 0, 0, -0.44); mast(m, 0.34, 3.8, 0);
    var car = group(m); forkSet(car, 0.2);
    models.reach = { g: g, pose: function (e) { m.position.z = -0.44 + e * 0.8; car.position.y = 0.19 + e * 2.3; } };
  })();
  // Pivot steer
  (function () {
    var g = group(); g.visible = false;
    cbRear(g, -1.2);
    tyre(0.28, 0.24, -0.55, -1.86, g); tyre(0.28, 0.24, 0.55, -1.86, g);
    cyl(0.2, 0.5, M.dark, 0, 0.62, -0.14, g, 'y');
    var front = group(g, 0, 0, -0.14);
    rbox(1.2, 0.42, 0.52, M.paint, 0, 0.55, 0.46, front, 0.07);
    tyre(0.35, 0.28, -0.67, 0.46, front); tyre(0.35, 0.28, 0.67, 0.46, front);
    mast(front, 0.36, 2.7, 0.82);
    var car = group(front); forkSet(car, 1.0);
    models.pivot = { g: g, pose: function (e) { front.rotation.y = e * 1.3; car.position.y = 0.01 + e * 0.45; } };
  })();
  // VNA
  (function () {
    var g = group(); g.visible = false;
    rbox(1.06, 0.3, 1.75, M.dark, 0, 0.36, -0.98, g, 0.04); rbox(1.06, 0.86, 1.5, M.paint, 0, 0.93, -1.02, g, 0.09);
    rbox(0.9, 0.05, 1.3, M.dark, 0, 1.375, -1.02, g, 0.02);
    tyre(0.2, 0.2, -0.5, -1.52, g); tyre(0.2, 0.2, 0.5, -1.52, g); tyre(0.2, 0.2, -0.5, -0.42, g); tyre(0.2, 0.2, 0.5, -0.42, g);
    mast(g, 0.38, 4.7, -0.12);
    var lift = group(g);
    rbox(1.0, 0.08, 0.92, M.dark, 0, 0.32, 0.5, lift, 0.02);
    [[-0.47, 0.08], [0.47, 0.08], [-0.47, 0.92], [0.47, 0.92]].forEach(function (q) { rbox(0.05, 1.75, 0.05, M.mast, q[0], 1.2, q[1], lift, 0.012); });
    rbox(1.04, 0.05, 0.96, M.dark, 0, 2.1, 0.5, lift, 0.02);
    [-0.47, 0.47].forEach(function (x) { box(0.04, 0.04, 0.84, M.mag, x, 1.25, 0.5, lift); box(0.04, 0.04, 0.84, M.mag, x, 0.8, 0.5, lift); });
    rbox(0.52, 0.36, 0.14, M.paint, 0, 1.05, 0.86, lift, 0.04); seat(lift, 0, 0.75, 0.3);
    cyl(0.045, 0.09, M.beacon, 0.35, 2.17, 0.2, lift, 'y');
    var turret = group(lift, 0, 0.12, 1.14);
    rbox(0.24, 1.05, 0.24, M.mast, 0, 0.52, 0, turret, 0.03); forkSet(turret, 0.22);
    models.vna = { g: g, pose: function (e) { lift.position.y = e * 2.3; turret.rotation.y = e * Math.PI / 2; } };
  })();
  // Telehandler
  (function () {
    var g = group(); g.visible = false;
    rbox(1.2, 0.3, 2.4, M.dark, 0, 0.62, -0.25, g, 0.04); rbox(1.5, 0.5, 2.75, M.paint, 0, 0.94, -0.25, g, 0.1);
    [[-0.9, 0.75], [0.9, 0.75], [-0.9, -1.25], [0.9, -1.25]].forEach(function (q) { tyre(0.6, 0.44, q[0], q[1], g, M.rim); rbox(0.5, 0.06, 0.9, M.dark, q[0], 1.26, q[1], g, 0.025); });
    rbox(0.72, 0.5, 1.15, M.paint, -0.42, 1.44, -0.1, g, 0.07);
    box(0.64, 0.9, 1.05, M.glass, -0.42, 2.14, -0.1, g).castShadow = false;
    [[-0.75, 0.44], [-0.09, 0.44], [-0.75, -0.64], [-0.09, -0.64]].forEach(function (q) { rbox(0.06, 0.95, 0.06, M.mast, q[0], 2.14, q[1], g, 0.015); });
    rbox(0.8, 0.07, 1.22, M.dark, -0.42, 2.64, -0.1, g, 0.03); seat(g, -0.42, 1.74, -0.3); steering(g, -0.42, 1.8, 0.22);
    cyl(0.05, 0.1, M.beacon, -0.42, 2.72, -0.5, g, 'y');
    rbox(0.52, 0.36, 1.55, M.dark, 0.5, 1.34, -0.3, g, 0.07); cyl(0.04, 0.5, M.steel, 0.62, 1.7, -0.9, g, 'y');
    rbox(0.5, 0.56, 0.44, M.dark, 0.15, 1.5, -1.42, g, 0.05);
    [-0.5, 0.5].forEach(function (x) { cyl(0.07, 0.03, M.lamp, x, 1.0, 1.13, g, 'z'); });
    var boom = group(g, 0.15, 1.82, -1.42);
    rbox(0.3, 0.32, 3.1, M.paint, 0, 0, 1.55, boom, 0.03);
    var inner = group(boom); rbox(0.22, 0.24, 3.0, M.dark, 0, 0, 1.75, inner, 0.02);
    var head = group(inner, 0, 0, 3.25);
    rbox(0.24, 0.5, 0.2, M.dark, 0, -0.2, 0, head, 0.03);
    var fk = group(head, 0, -1.08, 0); forkSet(fk, 0.14);
    models.tele = { g: g, pose: function (e) { boom.rotation.x = 0.19 - e * 0.85; inner.position.z = 0.2 + e * 1.3; head.rotation.x = -boom.rotation.x; } };
  })();
  // Powered pallet truck
  (function () {
    var g = group(); g.visible = false;
    rbox(0.8, 0.22, 0.54, M.dark, 0, 0.16, -0.36, g, 0.04); rbox(0.76, 0.72, 0.48, M.paint, 0, 0.6, -0.36, g, 0.08);
    rbox(0.66, 0.04, 0.4, M.dark, 0, 0.975, -0.36, g, 0.015); rbox(0.1, 0.06, 0.02, M.mag, 0.22, 0.8, -0.115, g, 0.008);
    rbox(0.62, 0.05, 0.44, M.dark, 0, 0.1, -0.86, g, 0.02); tyre(0.1, 0.1, 0, -0.36, g, M.steel);
    var till = group(g, 0, 0.92, -0.54); till.rotation.x = -0.55;
    cyl(0.03, 0.85, M.dark, 0, 0.42, 0, till, 'y'); rbox(0.46, 0.11, 0.15, M.dark, 0, 0.9, 0, till, 0.04);
    [-0.2, 0.2].forEach(function (x) { cyl(0.022, 0.12, M.vinyl, x * 1.4, 0.9, 0.09, till, 'x'); });
    rbox(0.06, 0.035, 0.05, M.mag, 0, 0.96, 0, till, 0.012);
    var fk = group(g);
    [-0.2, 0.2].forEach(function (x) { rbox(0.18, 0.075, 1.32, M.paint, x, 0.085, 0.55, fk, 0.02); cyl(0.04, 0.12, M.steel, x, 0.04, 1.0, fk, 'x'); });
    rbox(0.6, 0.3, 0.06, M.paint, 0, 0.2, -0.1, fk, 0.02);
    pallet(fk, 0, 0.125, 0.62);
    models.ppt = { g: g, pose: function (e) { fk.position.y = e * 0.14; } };
  })();
  // MEWP (scissor lift)
  (function () {
    var g = group(); g.visible = false;
    rbox(1.2, 0.46, 2.3, M.paint, 0, 0.53, 0, g, 0.07); rbox(1.0, 0.12, 2.0, M.dark, 0, 0.27, 0, g, 0.03);
    [[-0.63, 0.8], [0.63, 0.8], [-0.63, -0.8], [0.63, -0.8]].forEach(function (q) { tyre(0.22, 0.2, q[0], q[1], g, M.rim); });
    rbox(0.4, 0.26, 0.03, M.dark, 0, 0.55, 1.155, g, 0.01);
    var N = 4, L = 2.0, arms = [], n;
    for (n = 0; n < N; n++) [-0.42, 0.42].forEach(function (x) { [1, -1].forEach(function (sg) {
      arms.push({ m: rbox(0.05, 0.1, L, M.mast, x + sg * 0.03, 0, 0, g, 0.012), n: n, sg: sg });
    }); });
    var pins = []; for (n = 0; n < N; n++) pins.push(cyl(0.03, 0.96, M.steel, 0, 0, 0, g, 'x'));
    var plat = group(g);
    rbox(1.15, 0.08, 2.2, M.dark, 0, 0.04, 0, plat, 0.02);
    [[-0.55, 1.07], [0.55, 1.07], [-0.55, -1.07], [0.55, -1.07], [-0.55, 0], [0.55, 0]].forEach(function (q) { cyl(0.022, 1.05, M.paint, q[0], 0.58, q[1], plat, 'y'); });
    [0.6, 1.1].forEach(function (y) {
      cyl(0.022, 2.18, M.paint, -0.55, y, 0, plat, 'z'); cyl(0.022, 2.18, M.paint, 0.55, y, 0, plat, 'z');
      cyl(0.022, 1.12, M.paint, 0, y, 1.07, plat, 'x'); cyl(0.022, 1.12, M.paint, 0, y, -1.07, plat, 'x');
    });
    [-0.555, 0.555].forEach(function (x) { box(0.012, 0.15, 2.16, M.paint, x, 0.15, 0, plat); });
    [-1.075, 1.075].forEach(function (z) { box(1.1, 0.15, 0.012, M.paint, 0, 0.15, z, plat); });
    rbox(0.3, 0.24, 0.18, M.dark, 0.3, 0.98, 0.94, plat, 0.03); rbox(0.05, 0.05, 0.03, M.mag, 0.3, 1.12, 0.94, plat, 0.012);
    models.mewp = { g: g, pose: function (e) {
      var h = 0.36 + e * 3.1, lh = h / N, ang = Math.asin(Math.min(0.95, lh / L));
      arms.forEach(function (a) { a.m.rotation.x = a.sg * ang; a.m.position.y = 0.78 + lh * (a.n + 0.5); });
      pins.forEach(function (pn, k) { pn.position.y = 0.78 + lh * (k + 0.5); });
      plat.position.y = 0.76 + h;
    } };
  })();

  ['pump', 'picker_low', 'picker_high', 'boom', 'gantry'].forEach(function (k) { var g = group(); g.visible = false; models[k] = { g: g, pose: function () {} }; });

  // Fixed three-quarter view; drag to turn. Nothing moves until the visitor asks.
  var az = -0.75, el = 0.34, dist = 13.5, ty = 1.15, wide = 1, target = new THREE.Vector3(0, 1.15, 0.3);
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var dragging = false, lastX = 0, lastY = 0, dirty = true, shown = null, keys = { f: 0, b: 0, l: 0, r: 0 }, steer = 0, dir = 1, pedal = 0, speed = 0, thr = 0;
  function ease(v) { return v * v * (3 - 2 * v); }
  var zoom = 1;
  [['nctf-zoom-in', 0.85], ['nctf-zoom-out', 1.18]].forEach(function (z) { var b = document.getElementById(z[0]); if (b) b.addEventListener('click', function () { zoom = Math.max(0.5, Math.min(1.6, zoom * z[1])); }); });
  function place() {
    var d = dist * wide * 1.75 * zoom; target.y = ty;
    if (shown) { target.x += (shown.g.position.x * 0.8 - target.x) * 0.08; target.z += (shown.g.position.z * 0.8 + 0.3 - target.z) * 0.08; }
    camera.position.set(target.x + d * Math.sin(az) * Math.cos(el), target.y + d * Math.sin(el), target.z + d * Math.cos(az) * Math.cos(el));
    camera.lookAt(target);
  }
  function resize() {
    var w = canvas.clientWidth, h = canvas.clientHeight; if (!w || !h) return;
    renderer.setSize(w, h, false); camera.aspect = w / h;
    wide = w / h < 1.25 ? 1.25 : 1;
    var overlay = getComputedStyle(document.getElementById('nctf-controls')).position === 'absolute';
    if (overlay) camera.setViewOffset(w, h, 0, 70, w, h); else camera.clearViewOffset();
    camera.updateProjectionMatrix(); dirty = true;
  }
  if (window.ResizeObserver) new ResizeObserver(resize).observe(canvas); else window.addEventListener('resize', resize);
  resize();

  canvas.addEventListener('pointerdown', function (e) { dragging = true; lastX = e.clientX; lastY = e.clientY; canvas.setPointerCapture(e.pointerId); });
  canvas.addEventListener('pointermove', function (e) {
    if (!dragging) return;
    az -= (e.clientX - lastX) * 0.008; el = Math.max(0.1, Math.min(0.95, el + (e.clientY - lastY) * 0.004));
    lastX = e.clientX; lastY = e.clientY; dirty = true;
  });
  function end() { dragging = false; }
  canvas.addEventListener('pointerup', end); canvas.addEventListener('pointercancel', end);

  // Truck-style driving: a steering wheel you turn, a forward/neutral/reverse selector and an accelerator pedal you hold
  var wheelEl = document.getElementById('nctf-wheel'), wheelG = document.getElementById('nctf-wheel-g'), pedalEl = document.getElementById('nctf-pedal');
  var tillerEl = document.getElementById('nctf-tiller'), tillerG = document.getElementById('nctf-tiller-g'), thrEl = document.getElementById('nctf-throttle'), thrKnob = thrEl.firstElementChild;
  // Pedestrian trucks: swing the tiller arm to steer, and hold the travel control on its head to move at walking pace
  var tdrag = false;
  function tillerTo(e) { var r = tillerEl.getBoundingClientRect(), px = r.left + r.width * 0.5, py = r.top + r.height * 0.904; setSteer(Math.atan2(e.clientX - px, Math.max(4, py - e.clientY)) / (55 * Math.PI / 180)); }
  tillerEl.addEventListener('pointerdown', function (e) { e.preventDefault(); tdrag = true; try { tillerEl.setPointerCapture(e.pointerId); } catch (x) {} tillerTo(e); });
  tillerEl.addEventListener('pointermove', function (e) { if (tdrag) tillerTo(e); });
  ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(function (ev) { tillerEl.addEventListener(ev, function () { tdrag = false; }); });
  tillerEl.addEventListener('keydown', function (e) { if (e.key === 'ArrowLeft') { setSteer(steer - 0.1); e.preventDefault(); } else if (e.key === 'ArrowRight') { setSteer(steer + 0.1); e.preventDefault(); } });
  function setThr(v) { thr = Math.max(-1, Math.min(1, v)); thrKnob.style.transform = 'translateY(' + (-thr * 30) + 'px)'; thrEl.setAttribute('aria-valuenow', Math.round(thr * 100)); }
  var ty0 = 0;
  thrEl.addEventListener('pointerdown', function (e) { e.preventDefault(); ty0 = e.clientY; thrEl.classList.add('nctf-drag'); try { thrEl.setPointerCapture(e.pointerId); } catch (x) {} thrEl.focus(); });
  thrEl.addEventListener('pointermove', function (e) { if (thrEl.classList.contains('nctf-drag')) setThr((ty0 - e.clientY) / 30); });
  ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(function (ev) { thrEl.addEventListener(ev, function () { thrEl.classList.remove('nctf-drag'); setThr(0); }); });
  thrEl.addEventListener('keydown', function (e) { if (e.key === 'ArrowUp') { setThr(1); e.preventDefault(); } else if (e.key === 'ArrowDown') { setThr(-1); e.preventDefault(); } });
  thrEl.addEventListener('keyup', function (e) { if (e.key === 'ArrowUp' || e.key === 'ArrowDown') setThr(0); });
  thrEl.addEventListener('blur', function () { setThr(0); });
  function setSteer(v) { steer = Math.max(-1, Math.min(1, v)); wheelG.setAttribute('transform', 'rotate(' + (steer * 160) + ' 52 52)'); wheelEl.setAttribute('aria-valuenow', Math.round(steer * 100));
    tillerG.setAttribute('transform', 'rotate(' + (steer * 55) + ' 62 94)'); tillerEl.setAttribute('aria-valuenow', Math.round(steer * 100)); dirty = true; }
  var wa = 0, wdrag = false;
  function ang(e) { var r = wheelEl.getBoundingClientRect(); return Math.atan2(e.clientY - (r.top + r.height / 2), e.clientX - (r.left + r.width / 2)); }
  wheelEl.addEventListener('pointerdown', function (e) { e.preventDefault(); wdrag = true; wa = ang(e); try { wheelEl.setPointerCapture(e.pointerId); } catch (x) {} });
  wheelEl.addEventListener('pointermove', function (e) {
    if (!wdrag) return; var a = ang(e), d = a - wa; wa = a;
    if (d > Math.PI) d -= 2 * Math.PI; if (d < -Math.PI) d += 2 * Math.PI;
    setSteer(steer + d / (160 * Math.PI / 180));
  });
  ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(function (ev) { wheelEl.addEventListener(ev, function () { wdrag = false; }); });
  wheelEl.addEventListener('keydown', function (e) { if (e.key === 'ArrowLeft') { setSteer(steer - 0.1); e.preventDefault(); } else if (e.key === 'ArrowRight') { setSteer(steer + 0.1); e.preventDefault(); } });
  function setDir(d) { dir = d; [['nctf-dir-f', 1], ['nctf-dir-n', 0], ['nctf-dir-r', -1]].forEach(function (p) { document.getElementById(p[0]).setAttribute('aria-pressed', String(p[1] === d)); }); }
  [['nctf-dir-f', 1], ['nctf-dir-n', 0], ['nctf-dir-r', -1]].forEach(function (p) { document.getElementById(p[0]).addEventListener('click', function () { setDir(p[1]); }); });
  function setPedal(v) { pedal = v; pedalEl.classList.toggle('nctf-on', !!v); }
  pedalEl.addEventListener('pointerdown', function (e) { e.preventDefault(); setPedal(1); try { pedalEl.setPointerCapture(e.pointerId); } catch (x) {} });
  ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(function (ev) { pedalEl.addEventListener(ev, function () { setPedal(0); }); });
  pedalEl.addEventListener('keydown', function (e) { if (e.key === ' ' || e.key === 'Enter') { setPedal(1); e.preventDefault(); } });
  pedalEl.addEventListener('keyup', function () { setPedal(0); });
  pedalEl.addEventListener('blur', function () { setPedal(0); });
  var arrows = { ArrowUp: 'f', ArrowDown: 'b', ArrowLeft: 'l', ArrowRight: 'r' };
  canvas.addEventListener('keydown', function (e) { if (arrows[e.key]) { keys[arrows[e.key]] = 1; e.preventDefault(); } });
  canvas.addEventListener('keyup', function (e) { if (arrows[e.key]) keys[arrows[e.key]] = 0; });
  canvas.addEventListener('blur', function () { keys.f = keys.b = keys.l = keys.r = 0; });
  function park() {
    speed = 0; setSteer(0); setDir(1); dirty = true; blockedFor = 0;
    if (!shown) return;
    var spots = [[0, 0.5], [0, 3.5], [-2, 2], [2, 2], [0, -2.5], [-2, 5], [2, 5]];
    for (var n = 0; n < spots.length; n++) {      // the first parking spot with nothing in it
      shown.g.position.set(spots[n][0], 0, spots[n][1]); shown.g.rotation.y = 0;
      if (!shown.multi || !pallets.length || !collide(shown)) break;
    }
  }
  document.getElementById('nctf-park').addEventListener('click', function () { park(); targets = [0, 0]; stroke = 0; });
  onSelect = function () {
    var t = TRUCKS[current];
    if (carry) { var cp = carry.p; cp.x = cp.o.position.x; cp.z = cp.o.position.z; cp.y = 0; cp.yaw = yawOf(cp.o.quaternion); setPalletPose(cp); carry = null; score(); }
    if (shown) shown.g.visible = false;
    shown = models[t.key]; shown.g.visible = true;
    park(); dist = t.d; ty = t.ty; az = -0.75; el = 0.5; dirty = true;
    if (!t.asked && typeof loadModel === 'function') loadModel(t);
  };
  onSelect();

  // Swap each code-built stand-in for its modelled .glb file as soon as that file has loaded
  function loadModel(t) {
    if (!THREE.GLTFLoader || t.asked) return;
    t.asked = true;
    new THREE.GLTFLoader().load((CFG.models || 'models/') + t.key + (CFG.ext || '.glb'), function (g) {
      g.scene.traverse(function (o) { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
      var mixer = new THREE.AnimationMixer(g.scene);
      var acts = g.animations.map(function (c) {
        var a = mixer.clipAction(c), idx = 0; a.play();
        for (var k = 1; k < t.controls.length; k++) if (new RegExp(t.controls[k][1]).test(c.name)) idx = k;
        return { a: a, i: idx, d: c.duration };
      });
      var wheels = [], bb = new THREE.Box3(), sz = new THREE.Vector3();
      g.scene.updateMatrixWorld(true);
      g.scene.traverse(function (o) {       // wheels are the parts modelled round a sideways axle that carry a rim
        var q = o.quaternion;
        if (o.isMesh && o.children.length && Math.abs(q.x) < 0.03 && Math.abs(q.y) < 0.03 && Math.abs(q.z + 0.7071) < 0.03 && Math.abs(q.w - 0.7071) < 0.03) {
          bb.setFromObject(o).getSize(sz); wheels.push({ o: o, r: Math.max(0.05, sz.y / 2) });
        }
      });
      var m = { g: g.scene, multi: true, wheels: wheels, pose: function (v) {
        acts.forEach(function (x) { x.a.time = Math.min(x.d * (v[x.i] || 0), x.d - 0.0001); }); mixer.update(0);
      } };
      if (t.gd) { t.d = t.gd; t.ty = t.gty; }
      // The model was built with a pallet on its forks. Hide that one and remember its position on the forks instead.
      var baked = [], prim = null;
      g.scene.traverse(function (o) { if (PAL_RE.test(o.name)) { baked.push(o); if (!prim && /^(pallet|pal|pal_front)$/.test(o.name)) prim = o; } });
      if (prim) {
        m.pose([0, 0]); g.scene.updateMatrixWorld(true);
        if (!proto && t.key === 'counter') { proto = new THREE.Group(); prim.children.forEach(function (c) { proto.add(c.clone(true)); }); }
        var carrier = prim.parent && prim.parent !== g.scene ? prim.parent : g.scene.getObjectByName('forks');
        if (carrier) {
          var ref = new THREE.Object3D(), mm = new THREE.Matrix4();
          mm.copy(carrier.matrixWorld).invert().multiply(prim.matrixWorld); mm.decompose(ref.position, ref.quaternion, ref.scale); ref.scale.set(1, 1, 1);
          carrier.add(ref); g.scene.updateMatrixWorld(true);
          var w0 = new THREE.Vector3(), w1 = new THREE.Vector3(); ref.getWorldPosition(w0);
          m.pose([1, 0]); g.scene.updateMatrixWorld(true); ref.getWorldPosition(w1); m.pose([0, 0]);
          m.forkRef = ref; m.y0 = w0.y; m.liftT = Math.max(0.02, Math.min(0.06, (w1.y - w0.y) * 0.4)); m.forkZ = w0.z;
          m.liftRate = Math.max(0.12, Math.min(0.42, 0.6 / Math.max(0.1, w1.y - w0.y)));
          m.zMin = Math.max(-6.7, Math.min(-5.0, -7.6 + Math.abs(w0.z) - 0.05));
        }
        baked.forEach(function (o) { o.visible = false; });
      }
      // Footprint of the truck body (not the forks) as a row of circles along its length
      (function () {
        m.pose([0, 0]); g.scene.updateMatrixWorld(true);
        var bb = new THREE.Box3(), one = new THREE.Box3();
        g.scene.traverse(function (o) {
          if (!o.isMesh) return;
          for (var a = o; a; a = a.parent) if (baked.indexOf(a) >= 0) return;
          one.setFromObject(o); bb.union(one);
        });
        if (bb.isEmpty()) return;
        var hw = Math.max(0.3, Math.min(1.25, (bb.max.x - bb.min.x) / 2 * 0.9)), z0 = bb.min.z + 0.05, z1 = m.forkRef ? m.forkZ - 0.62 : bb.max.z - 0.05;
        if (z1 < z0 + 0.3) z1 = z0 + 0.3;
        var r = Math.min(hw, (z1 - z0) / 2), cnt = Math.max(1, Math.ceil((z1 - z0 - 2 * r) / r) + 1), zs = [];
        for (var c = 0; c < cnt; c++) zs.push(cnt === 1 ? (z0 + z1) / 2 : z0 + r + (z1 - z0 - 2 * r) * c / (cnt - 1));
        m.body = { r: r, zs: zs };
      })();
      g.scene.visible = false; scene.add(g.scene);
      if (proto && !pallets.length) resetYard();
      var old = models[t.key]; models[t.key] = m;
      if (shown === old) { old.g.visible = false; shown = m; m.g.visible = true; dist = t.d; ty = t.ty; dirty = true; }
    }, undefined, function () {});
  }
  loadModel(TRUCKS[0]); if (current) loadModel(TRUCKS[current]);

  var last = performance.now();
  function frame(now) {
    var dt = Math.min(0.1, (now - last) / 1000); last = now;
    var was = shown.multi ? !!collide(shown) : true, sx0 = shown.g.position.x, sz0 = shown.g.position.z, sh0 = shown.g.rotation.y, t0v = targets.slice(), v0v = vals.slice();
    var T = TRUCKS[current], n;
    // Hydraulic levers: how far a lever is held sets how fast that function moves; let go and it stays where it is
    for (n = 0; n < T.controls.length; n++) {
      if (T.controls[n][2] === 'stroke') {           // pump handle: follows the lever, each full stroke lifts the forks a little
        targets[n] = Math.abs(defl[n]);
        if (stroke === 0 && targets[n] > 0.85) { stroke = 1; targets[0] = Math.min(1, targets[0] + 0.2); }
        if (stroke === 1 && targets[n] < 0.15) stroke = 0;
      } else if (defl[n]) targets[n] = Math.max(0, Math.min(1, targets[n] + defl[n] * ((n === 0 && shown.liftRate) || 0.42) * dt));
    }
    for (n = 0; n < 2; n++) if (Math.abs(targets[n] - vals[n]) > 0.0005) {
      vals[n] += (targets[n] - vals[n]) * Math.min(1, dt * (reduce ? 60 : 9)); dirty = true;
      var o = document.getElementById('nctf-lever-' + n + '-out'); if (o) { o.textContent = Math.round(targets[n] * 100) + '%'; document.getElementById('nctf-lever-' + n).setAttribute('aria-valuenow', Math.round(targets[n] * 100)); }
    }
    if (T.drive) {
      if (keys.l || keys.r) setSteer(steer + (keys.r - keys.l) * 1.6 * dt);
      var top = T.tiller ? 1.2 : 1.7, want = keys.f ? top : keys.b ? -top : T.tiller ? thr * top : pedal * dir * top;
      speed += Math.max(-2.4 * dt, Math.min(2.4 * dt, want - speed));
      if (Math.abs(speed) > 0.003) {
        // rear-wheel steering, as on a lift truck: the front axle follows the heading and the tail swings round it
        var gp = shown.g, h = gp.rotation.y, a = 0.75, L = 1.6;
        var fx = gp.position.x + Math.sin(h) * a + Math.sin(h) * speed * dt, fz = gp.position.z + Math.cos(h) * a + Math.cos(h) * speed * dt;
        h -= speed * Math.tan(steer * 1.05) / L * dt;
        var nx = fx - Math.sin(h) * a, nz = fz - Math.cos(h) * a;
        if (Math.abs(nx) < YARD.x && nz > -9 && nz < YARD.zMax) {
          gp.position.x = nx; gp.position.z = nz; gp.rotation.y = h;
          (shown.wheels || []).forEach(function (w) { w.o.rotateY(speed * dt / w.r); });
        } else speed = 0;
        dirty = true;
      }
      var mph = Math.abs(speed) * 2.237, sp = document.getElementById('nctf-speed'), txt = mph.toFixed(1); if (sp.textContent !== txt) sp.textContent = txt;
    }
    if (shown.multi) shown.pose(vals); else shown.pose(ease(vals[0]));
    var touch = shown.multi ? collide(shown) : null;
    if (touch) {
      var gpp = shown.g, nx1 = gpp.position.x, nz1 = gpp.position.z, nh1 = gpp.rotation.y, moved = nx1 !== sx0 || nz1 !== sz0 || nh1 !== sh0, refuse = false;
      if (moved) {                           // heading into it is refused; backing away from it is always allowed
        var dNew = touch(); gpp.position.x = sx0; gpp.position.z = sz0; gpp.rotation.y = sh0;
        var dOld = touch();
        var backing = (nx1 - sx0) * Math.sin(sh0) + (nz1 - sz0) * Math.cos(sh0) < 0;   // forks drawn straight back always come free
        if (dNew < dOld - 0.00001 && !(touch.fork && backing)) { refuse = true; speed = 0; bumpAt = now; }
        else { gpp.position.x = nx1; gpp.position.z = nz1; gpp.rotation.y = nh1; }
      }
      if (!was && (!moved || refuse) && collide(shown)) { targets = t0v; vals = v0v; shown.pose(vals); bumpAt = now; }   // a lever move that would push through something
      blockedFor = refuse ? blockedFor + dt : 0;
    } else blockedFor = 0;
    forkWork(shown); place(); renderer.render(scene, camera); dirty = false;
    requestAnimationFrame(frame);
  }
  shown.pose(shown.multi ? vals : 0); place(); renderer.render(scene, camera);
  requestAnimationFrame(frame);
  window.__nctf = { hit: function () { return !!collide(shown); }, where: function () { return [shown.g.position.x, shown.g.position.z, shown.g.rotation.y]; }, yard: function () { return { carry: !!carry, placed: pallets.filter(function (pl) { return (!carry || carry.p !== pl) && onTarget(pl); }).length, pallets: pallets.map(function (pl) { return [+pl.o.position.x.toFixed(2), +pl.o.position.y.toFixed(2), +pl.o.position.z.toFixed(2)]; }), hint: lastHint, fork: shown && shown.forkRef ? [+fp.x.toFixed(2), +(fp.y - shown.y0).toFixed(2), +fp.z.toFixed(2)] : null }; }, truck: function (x, z, h) { shown.g.position.set(x, 0, z); shown.g.rotation.y = h; }, pick: show, work: function (a, b) { targets = [a, b === undefined ? a : b]; vals = targets.slice(); dirty = true; }, key: function (k, v) { keys[k] = v; }, drive: function (d, p, st) { setDir(d); setPedal(p); setSteer(st); }, thr: setThr, lever: function (n, d) { defl[n] = d; } };
})();
