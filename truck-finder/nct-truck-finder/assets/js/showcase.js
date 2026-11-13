/* NCT Truck Finder, showcase view: each truck shown on a turntable, as in the homepage hero.
   Needs three.js r128 and its GLTFLoader, loaded before this file. */
(function () {
  var root = document.getElementById('nctf');
  if (!root) return;
  if (root.getAttribute('data-place') === 'top') {
    var main = document.querySelector('main') || document.getElementById('main');
    if (main && main.firstElementChild !== root) { main.insertBefore(root, main.firstElementChild); root.classList.remove('nctf-breakout'); }
  }
  var CFG = window.NCTTruckFinder || {};
  var TRUCKS = [
    { key: 'counter', name: 'Counterbalance', aka: 'The standard forklift',
      spot: ['Forks stick straight out at the front', 'Heavy counterweight at the back, no legs in front', 'Driver sits facing forwards under a cage'],
      where: 'loading bays, yards and warehouses with wide aisles.', link: 'See RTITB Counterbalance courses' },
    { key: 'reach', name: 'Reach truck', aka: 'Tall mast, built for racking',
      spot: ['Two legs run forward along the floor either side of the forks', 'The mast slides forward to reach into the racking', 'Driver sits sideways'],
      where: 'indoor warehouses with high racking and narrower aisles.', link: 'See RTITB Reach courses' },
    { key: 'pivot', name: 'Pivot Steer', aka: 'Also called an articulated truck',
      spot: ['Looks like a counterbalance, but hinged in the middle', 'The front end and mast swing to either side', 'Stacks side-on without turning the whole truck'],
      where: 'very narrow aisles, and it can still work outside in the yard.', link: 'See RTITB Pivot Steer courses' },
    { key: 'vna', name: 'VNA', aka: 'Very narrow aisle truck',
      spot: ['The forks turn to face sideways into the racking', 'On many models the driver rises with the load', 'Runs up and down an aisle barely wider than itself'],
      where: 'high-bay warehouses with the tightest aisles.', link: 'See RTITB VNA courses' },
    { key: 'tele', name: 'Telehandler', aka: 'Telescopic handler',
      spot: ['A telescopic boom in place of an upright mast', 'Big wheels and a side-mounted cab', 'Forks on the end of the boom reach up and out'],
      where: 'construction sites, farms and rough ground.', link: 'See RTITB Telehandler courses' },
    { key: 'ppt', name: 'Powered pallet truck', aka: 'Often shortened to PPT',
      spot: ['Low forks that lift a pallet just clear of the floor', 'Steered with a tiller arm, not a wheel', 'Operator walks with it or stands on a small platform'],
      where: 'loading docks, shop floors and the backs of lorries.', link: 'See RTITB PPT courses' },
    { key: 'pump', name: 'Pump truck', aka: 'Manual hand pallet truck',
      spot: ['No motor or battery: you pump the handle to lift', 'Long handle with a loop grip', 'Two low forks on small rollers'],
      where: 'shop floors, stockrooms and the backs of delivery vehicles.', link: 'See RTITB Pump Truck training' },
    { key: 'picker_low', name: 'Low-level order picker', aka: 'Ride-on picking truck',
      spot: ['Operator rides standing, between the drive unit and the forks', 'Very long forks that carry two pallets', 'Step-through sides for hopping on and off'],
      where: 'distribution centres, picking at floor and first level.', link: 'See RTITB Order Picker courses' },
    { key: 'picker_high', name: 'High-level order picker', aka: 'The operator goes up with the forks',
      spot: ['Operator stands on a platform that rises up the mast', 'Forks fixed straight ahead, with a pallet to pick onto', 'Guard rails and a cage around the operator'],
      where: 'warehouses where goods are picked by hand from high racking.', link: 'See RTITB Order Picker courses' },
    { key: 'mewp', name: 'MEWP: scissor lift', aka: 'Mobile elevating work platform',
      spot: ['Lifts people, not loads', 'A railed platform on a criss-cross scissor stack', 'Goes straight up and down'],
      where: 'maintenance, installation and work at height on site.', link: 'See RTITB MEWP courses' },
    { key: 'boom', name: 'MEWP: boom lift', aka: 'Often called a cherry picker',
      spot: ['A basket on the end of a jointed, telescopic boom', 'Reaches up and over obstacles', 'Turntable and counterweight on a four-wheel chassis'],
      where: 'construction, maintenance and outdoor work at height.', link: 'See RTITB MEWP courses' },
    { key: 'gantry', name: 'Gantry crane', aka: 'Overhead lifting on a frame',
      spot: ['A beam across two A-frame legs', 'A hoist that travels along the beam', 'Loads are slung from a hook, not carried on forks'],
      where: 'workshops, yards and fabrication bays.', link: 'See RTITB Gantry Crane courses' }
  ];
  var LINKS = {"counter": "rtitb-counterbalance-courses", "reach": "rtitb-reach-courses", "pivot": "rtitb-pivotsteer-courses", "vna": "rtitb-vna-courses", "tele": "rtitb-telehander-courses", "ppt": "rtitb-ppt-courses", "pump": "rtitb-pump-truck-training", "picker_low": "rtitb-manual-handling-courses-2", "picker_high": "rtitb-manual-handling-courses-2", "mewp": "rtitb-mewp-courses", "boom": "rtitb-mewp-courses", "gantry": "rtitb-gantry-courses"};
  // Trucks whose load hides them from the front are shown from behind
  var YAW = { ppt: 2.5, pump: 2.55, picker_low: 2.4, gantry: -0.45, boom: -0.95, tele: -0.8 };

  var current = 0;
  var tabs = Array.prototype.slice.call(document.querySelectorAll('#nctf-tabs .nctf-tab'));
  var onSelect = function () {};
  function show(i) {
    current = (i + TRUCKS.length) % TRUCKS.length;
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
    document.getElementById('nctf-yard').setAttribute('aria-label', '3D model of a ' + t.name + '. ' + t.spot.join('. ') + '.');
    onSelect(current);
  }
  tabs.forEach(function (el, n) { el.addEventListener('click', function () { show(n); }); });
  document.getElementById('nctf-prev').addEventListener('click', function () { show(current - 1); });
  document.getElementById('nctf-next').addEventListener('click', function () { show(current + 1); });

  var box = document.getElementById('nctf-stage'), canvas = document.getElementById('nctf-yard');
  if (!window.THREE || !THREE.GLTFLoader) { box.hidden = true; return; }
  var renderer;
  try { renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true }); } catch (e) { box.hidden = true; return; }

  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function lin(c) { return new THREE.Color(c).convertSRGBToLinear(); }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setClearColor(0x000000, 0);
  renderer.outputEncoding = THREE.sRGBEncoding;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.92;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  var scene = new THREE.Scene();
  var camera = new THREE.PerspectiveCamera(26, 1, 0.1, 100);
  (function () {       // studio reflections baked from a small lit room, tinted with the brand colours
    var room = new THREE.Scene(); room.background = lin(0x241022);
    function panel(w, h, c, x, y, z, rx, ry) {
      var m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: lin(c), side: THREE.DoubleSide }));
      m.position.set(x, y, z); m.rotation.set(rx, ry, 0); room.add(m);
    }
    panel(14, 10, 0xffffff, 0, 9, 0, Math.PI / 2, 0); panel(8, 5, 0xffe9d6, 10, 4, 3, 0, -Math.PI / 2);
    panel(8, 5, 0xf0b6d6, -10, 4, -2, 0, Math.PI / 2); panel(10, 4, 0xc9a9d0, 0, 3, 11, 0, Math.PI);
    panel(30, 30, 0x43003f, 0, -0.5, 0, -Math.PI / 2, 0);
    var pm = new THREE.PMREMGenerator(renderer); scene.environment = pm.fromScene(room, 0.03).texture; pm.dispose();
  })();
  scene.add(new THREE.HemisphereLight(0xffffff, 0x5d0059, 0.3));
  var key = new THREE.DirectionalLight(0xfff4e6, 1.15);
  key.position.set(4.5, 9, 6); key.castShadow = true; key.shadow.mapSize.set(2048, 2048);
  key.shadow.camera.left = -5; key.shadow.camera.right = 5; key.shadow.camera.top = 6; key.shadow.camera.bottom = -5;
  key.shadow.camera.near = 1; key.shadow.camera.far = 26; key.shadow.bias = -0.0004; key.shadow.radius = 6;
  scene.add(key);
  var rimA = new THREE.PointLight(lin(0xE4125D), 1.8, 22, 2); rimA.position.set(-6, 3.2, -5); scene.add(rimA);
  var rimB = new THREE.PointLight(lin(0xFB8E28), 1.3, 22, 2); rimB.position.set(6.5, 2.2, -4.5); scene.add(rimB);

  // Turntable: a low plinth with a lit rim and index marks
  var R = 3.05;
  var turn = new THREE.Group(); scene.add(turn);
  var plinth = new THREE.Mesh(new THREE.CylinderGeometry(R, R * 0.97, 0.22, 96), new THREE.MeshStandardMaterial({ color: lin(0x2B0028), roughness: 0.78, metalness: 0, envMapIntensity: 0.35 }));
  plinth.position.y = -0.11; plinth.receiveShadow = true; turn.add(plinth);
  function ring(r, tube, c, y) {
    var m = new THREE.Mesh(new THREE.TorusGeometry(r, tube, 10, 160), new THREE.MeshBasicMaterial({ color: lin(c), toneMapped: false }));
    m.rotation.x = Math.PI / 2; m.position.y = y; turn.add(m); return m;
  }
  ring(R, 0.028, 0xFB8E28, 0.002);
  var outer = ring(R + 0.34, 0.012, 0xE4125D, -0.2);
  for (var q = 0; q < 24; q++) {
    var tk = new THREE.Mesh(new THREE.BoxGeometry(q % 6 === 0 ? 0.3 : 0.14, 0.004, 0.022), new THREE.MeshBasicMaterial({ color: lin(q % 6 === 0 ? 0xFB8E28 : 0x7A3F77), toneMapped: false }));
    var a = q / 24 * Math.PI * 2; tk.position.set(Math.cos(a) * (R - 0.28), 0.003, Math.sin(a) * (R - 0.28)); tk.rotation.y = -a; turn.add(tk);
  }
  var stage = new THREE.Group(); turn.add(stage);
  var loaded = {}, loading = {}, shown = null, pending = 0;

  function yawOf(i) { var y = YAW[TRUCKS[i].key]; return y === undefined ? -0.62 : y; }
  function load(i, done) {
    if (loaded[i]) { if (done) done(loaded[i]); return; }
    if (loading[i]) { loading[i].push(done); return; }
    loading[i] = [done];
    new THREE.GLTFLoader().load((CFG.models || 'models/') + TRUCKS[i].key + (CFG.ext || '.glb'), function (g) {
      var mroot = g.scene, bb = new THREE.Box3(), size = new THREE.Vector3(), ctr = new THREE.Vector3();
      mroot.traverse(function (o) { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
      var mixer = new THREE.AnimationMixer(mroot), acts = g.animations.map(function (c) { var a = mixer.clipAction(c); a.play(); return { a: a, d: c.duration }; });
      function pose(v) { acts.forEach(function (x) { x.a.time = Math.min(x.d * v, x.d - 0.0001); }); mixer.update(0); }
      // Fit every machine to the plinth whatever its real size: measure it at rest and fully worked
      pose(1); mroot.updateMatrixWorld(true); bb.setFromObject(mroot);
      pose(0); mroot.updateMatrixWorld(true); bb.union(new THREE.Box3().setFromObject(mroot));
      bb.getSize(size); bb.getCenter(ctr);
      var k = Math.min((R * 2 - 0.9) / Math.max(size.x, size.z), 4.3 / size.y);
      var holder = new THREE.Group(); holder.add(mroot);
      mroot.scale.setScalar(k); mroot.position.set(-ctr.x * k, -bb.min.y * k, -ctr.z * k);
      holder.visible = false; stage.add(holder);
      var m = { g: holder, pose: pose };
      loaded[i] = m; loading[i].forEach(function (f) { if (f) f(m); }); loading[i] = null;
    }, undefined, function () { loading[i] = null; });
  }

  var pull = 1, yaw = yawOf(0), yawGoal = yaw, px = 0, py = 0, pxs = 0, pys = 0, dragging = false, lastX = 0, vel = 0, grow = 1, swapAt = -1, t0 = performance.now();
  function resize() {
    var w = canvas.clientWidth, h = canvas.clientHeight; if (!w || !h) return;
    renderer.setSize(w, h, false); camera.aspect = w / h; pull = Math.max(1, 1.42 / camera.aspect); camera.updateProjectionMatrix();
  }
  if (window.ResizeObserver) new ResizeObserver(resize).observe(canvas); else window.addEventListener('resize', resize);
  resize();
  window.addEventListener('pointermove', function (e) {
    var r = canvas.getBoundingClientRect();
    px = Math.max(-1, Math.min(1, ((e.clientX - r.left) / r.width - 0.5) * 2)); py = Math.max(-1, Math.min(1, ((e.clientY - r.top) / r.height - 0.5) * 2));
  }, { passive: true });
  canvas.addEventListener('pointerdown', function (e) { dragging = true; lastX = e.clientX; vel = 0; try { canvas.setPointerCapture(e.pointerId); } catch (x) {} });
  canvas.addEventListener('pointermove', function (e) { if (!dragging) return; var dx = (e.clientX - lastX) * 0.009; lastX = e.clientX; yawGoal += dx; yaw += dx; vel = dx; });
  ['pointerup', 'pointercancel'].forEach(function (ev) { canvas.addEventListener(ev, function () { dragging = false; }); });

  function reveal(m) { if (shown) shown.g.visible = false; shown = m; m.g.visible = true; }
  onSelect = function (i) {
    pending = i;
    if (reduce) { load(i, function (m) { if (pending === i) { yaw = yawGoal = yawOf(i); reveal(m); } }); return; }
    // The table spins once; the outgoing truck shrinks away and the new one grows in part-way round
    var y = yawOf(i); yawGoal = y + Math.PI * 2 * Math.round((yaw + Math.PI * 2 - y) / (Math.PI * 2));
    if (yawGoal - yaw < Math.PI) yawGoal += Math.PI * 2;
    vel = 0; swapAt = performance.now();
    load(i, function () { load((i + 1) % TRUCKS.length); });       // have the next one ready
  };

  var last = performance.now();
  function frame(now) {
    var dt = Math.min(0.1, (now - last) / 1000); last = now;
    var time = (now - t0) / 1000;
    if (!dragging) { yawGoal += vel; vel *= 0.92; yaw += (yawGoal - yaw) * Math.min(1, dt * 3.2); }
    pxs += (px - pxs) * Math.min(1, dt * 3); pys += (py - pys) * Math.min(1, dt * 3);
    if (swapAt >= 0) {
      var e = (now - swapAt) / 1000, want = loaded[pending];
      if (e < 0.32 || !want) grow = Math.max(0.001, 1 - Math.min(1, e / 0.32));
      else { if (shown !== want) reveal(want); grow = Math.min(1, (e - 0.32) / 0.5); if (grow >= 1) swapAt = -1; }
    }
    var gz = grow * grow * (3 - 2 * grow);
    stage.scale.setScalar(0.55 + 0.45 * gz); stage.position.y = -(1 - gz) * 0.5;
    turn.rotation.y = yaw + (reduce ? 0 : pxs * 0.22);
    outer.rotation.z = reduce ? 0 : time * 0.12;
    if (shown) { var c = reduce ? 0.3 : 0.5 - 0.5 * Math.cos(time * 0.7); shown.pose(c * c * (3 - 2 * c)); }
    camera.position.set(0, (3.5 - pys * 0.35) * pull, 14.6 * pull); camera.lookAt(0, 1.75, 0);
    renderer.render(scene, camera);
    requestAnimationFrame(frame);
  }
  load(0, function (m) { if (!shown) reveal(m); load(1); });
  requestAnimationFrame(frame);
  window.__nctf = { pick: show, ready: function (i) { return !!loaded[i]; } };
})();
