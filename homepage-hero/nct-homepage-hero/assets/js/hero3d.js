/* NCT homepage hero: 3D stage that replaces the flat illustrations. Needs three.js r128 and GLTFLoader loaded first.
   The original SVG figures stay in the page and are shown again if WebGL is not available. */
(function () {
  var art = document.querySelector('.hero-art'), box = document.getElementById('h3d'), canvas = document.getElementById('h3d-canvas');
  if (!art || !box || !canvas) return;
  var CFG = window.NCTHero3D || {};
  // One scene per tab, in tab order. yaw = resting angle; loop = motion repeats (wheels) instead of going back and forth.
  var SCENES = [
    { key: 'counter', yaw: -0.62 },
    { key: 'lorry', yaw: -0.95, loop: true, road: true },
    { key: 'firstaid', yaw: -0.45 },
    { key: 'fire', yaw: -0.5 },
    { key: 'mewp', yaw: -0.6 }
  ];
  var tabs = Array.prototype.slice.call(art.querySelectorAll('.fig-tab'));
  var figs = Array.prototype.slice.call(art.querySelectorAll('.hero-fig'));
  var current = 0;
  function mark(i) {
    tabs.forEach(function (t, n) { t.classList.toggle('is-active', n === i); t.setAttribute('aria-pressed', String(n === i)); });
    figs.forEach(function (f, n) { f.classList.toggle('is-active', n === i); f.hidden = n !== i; });
  }

  if (!window.THREE || !THREE.GLTFLoader) return;
  var renderer;
  try { renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true }); } catch (e) { return; }
  art.classList.add('has-3d');

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

  // Studio reflections baked from a small lit room, tinted with the brand colours
  (function () {
    var room = new THREE.Scene(); room.background = lin(0x241022);
    function panel(w, h, c, x, y, z, rx, ry) {
      var m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: lin(c), side: THREE.DoubleSide }));
      m.position.set(x, y, z); m.rotation.set(rx, ry, 0); room.add(m);
    }
    panel(14, 10, 0xffffff, 0, 9, 0, Math.PI / 2, 0);
    panel(8, 5, 0xffe9d6, 10, 4, 3, 0, -Math.PI / 2);
    panel(8, 5, 0xf0b6d6, -10, 4, -2, 0, Math.PI / 2);
    panel(10, 4, 0xc9a9d0, 0, 3, 11, 0, Math.PI);
    panel(30, 30, 0x43003f, 0, -0.5, 0, -Math.PI / 2, 0);
    var pm = new THREE.PMREMGenerator(renderer); scene.environment = pm.fromScene(room, 0.03).texture; pm.dispose();
  })();
  scene.add(new THREE.HemisphereLight(0xffffff, 0x5d0059, 0.3));
  var key = new THREE.DirectionalLight(0xfff4e6, 1.15);
  key.position.set(4.5, 9, 6); key.castShadow = true; key.shadow.mapSize.set(2048, 2048);
  key.shadow.camera.left = -5; key.shadow.camera.right = 5; key.shadow.camera.top = 5; key.shadow.camera.bottom = -5;
  key.shadow.camera.near = 1; key.shadow.camera.far = 26; key.shadow.bias = -0.0004; key.shadow.radius = 6;
  scene.add(key);
  // Coloured rim lights from behind pick the edges out in magenta and orange
  var rimA = new THREE.PointLight(lin(0xE4125D), 1.8, 22, 2); rimA.position.set(-6, 3.2, -5); scene.add(rimA);
  var rimB = new THREE.PointLight(lin(0xFB8E28), 1.3, 22, 2); rimB.position.set(6.5, 2.2, -4.5); scene.add(rimB);

  // Turntable: a low plinth with a lit rim. Everything on it turns together.
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
  // Quarter marks on the plinth, like a turntable's index marks
  for (var q = 0; q < 24; q++) {
    var tk = new THREE.Mesh(new THREE.BoxGeometry(q % 6 === 0 ? 0.3 : 0.14, 0.004, 0.022), new THREE.MeshBasicMaterial({ color: lin(q % 6 === 0 ? 0xFB8E28 : 0x7A3F77), toneMapped: false }));
    var a = q / 24 * Math.PI * 2; tk.position.set(Math.cos(a) * (R - 0.28), 0.003, Math.sin(a) * (R - 0.28)); tk.rotation.y = -a; turn.add(tk);
  }
  // Road markings that stream past under the lorry
  var road = new THREE.Group(); road.visible = false; turn.add(road);
  var dashes = [];
  for (var d = 0; d < 7; d++) {
    var dm = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.004, 0.62), new THREE.MeshBasicMaterial({ color: lin(0xEED4E9), toneMapped: false, transparent: true }));
    dm.position.set(-0.78, 0.004, 0); road.add(dm); dashes.push(dm);
  }

  var stage = new THREE.Group(); turn.add(stage);       // holds the model that is showing
  var loaded = {}, loading = {}, shown = null, pending = null;

  function load(i, done) {
    var s = SCENES[i];
    if (loaded[i]) { if (done) done(loaded[i]); return; }
    if (loading[i]) { loading[i].push(done); return; }
    loading[i] = [done];
    new THREE.GLTFLoader().load((CFG.models || 'models/') + s.key + (CFG.ext || '.glb'), function (g) {
      var root = g.scene, bb = new THREE.Box3(), size = new THREE.Vector3(), ctr = new THREE.Vector3();
      root.traverse(function (o) { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
      var mixer = new THREE.AnimationMixer(root), acts = g.animations.map(function (c) { var a = mixer.clipAction(c); a.play(); return { a: a, d: c.duration }; });
      function pose(v) { acts.forEach(function (x) { x.a.time = Math.min(x.d * v, x.d - 0.0001); }); mixer.update(0); }
      // Fit every model to the plinth whatever its real size: measure it at rest and fully worked
      pose(1); root.updateMatrixWorld(true); bb.setFromObject(root);
      pose(0); root.updateMatrixWorld(true); bb.union(new THREE.Box3().setFromObject(root));
      bb.getSize(size); bb.getCenter(ctr);
      var k = Math.min((R * 2 - 0.9) / Math.max(size.x, size.z), 3.7 / size.y);
      var holder = new THREE.Group(); holder.add(root);
      root.scale.setScalar(k); root.position.set(-ctr.x * k, -bb.min.y * k, -ctr.z * k);
      holder.visible = false; stage.add(holder);
      var m = { g: holder, pose: pose, s: s, top: size.y * k };
      loaded[i] = m; loading[i].forEach(function (f) { if (f) f(m); }); loading[i] = null;
    }, undefined, function () { loading[i] = null; });
  }

  // View: a fixed three-quarter look; the pointer nudges it, a drag turns the table
  var yaw = SCENES[0].yaw, yawGoal = yaw, spin = 0, px = 0, py = 0, pxs = 0, pys = 0, dragging = false, lastX = 0, vel = 0, grow = 1, swapAt = -1, t0 = performance.now(), dirty = true;
  function resize() {
    var w = box.clientWidth, h = box.clientHeight; if (!w || !h) return;
    renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); dirty = true;
  }
  if (window.ResizeObserver) new ResizeObserver(resize).observe(box); else window.addEventListener('resize', resize);
  resize();
  window.addEventListener('pointermove', function (e) {
    var r = box.getBoundingClientRect();
    px = Math.max(-1, Math.min(1, ((e.clientX - r.left) / r.width - 0.5) * 2)); py = Math.max(-1, Math.min(1, ((e.clientY - r.top) / r.height - 0.5) * 2));
  }, { passive: true });
  canvas.addEventListener('pointerdown', function (e) { dragging = true; lastX = e.clientX; vel = 0; try { canvas.setPointerCapture(e.pointerId); } catch (x) {} });
  canvas.addEventListener('pointermove', function (e) { if (!dragging) return; var dx = (e.clientX - lastX) * 0.009; lastX = e.clientX; yawGoal += dx; yaw += dx; vel = dx; });
  ['pointerup', 'pointercancel'].forEach(function (ev) { canvas.addEventListener(ev, function () { dragging = false; }); });

  function show(m) {
    if (shown) shown.g.visible = false;
    shown = m; m.g.visible = true; road.visible = !!m.s.road; dirty = true;
  }
  function select(i) {
    if (i === current && shown) return;
    current = i; mark(i);
    pending = i;
    if (reduce) { load(i, function (m) { if (pending === i) { yaw = yawGoal = m.s.yaw; show(m); } }); return; }
    // The table spins once; the outgoing model shrinks away and the new one grows in half-way round
    yawGoal = SCENES[i].yaw + Math.PI * 2 * Math.round((yaw + Math.PI * 2 - SCENES[i].yaw) / (Math.PI * 2));
    if (yawGoal - yaw < Math.PI) yawGoal += Math.PI * 2;
    swapAt = performance.now();
    load(i);
  }
  tabs.forEach(function (t, n) { t.addEventListener('click', function () { select(n); }); });

  var last = performance.now();
  function frame(now) {
    var dt = Math.min(0.1, (now - last) / 1000); last = now;
    var time = (now - t0) / 1000;
    if (!dragging) { yawGoal += vel; vel *= 0.92; yaw += (yawGoal - yaw) * Math.min(1, dt * 3.2); }
    pxs += (px - pxs) * Math.min(1, dt * 3); pys += (py - pys) * Math.min(1, dt * 3);
    // model swap
    if (swapAt >= 0) {
      var e = (now - swapAt) / 1000, want = loaded[pending];
      if (e < 0.32 || !want) grow = Math.max(0.001, 1 - Math.min(1, e / 0.32));
      else { if (shown !== want) show(want); grow = Math.min(1, (e - 0.32) / 0.5); if (grow >= 1) swapAt = -1; }
    }
    var gz = grow * grow * (3 - 2 * grow);
    stage.scale.setScalar(0.55 + 0.45 * gz); stage.position.y = -(1 - gz) * 0.5;
    turn.rotation.y = yaw + (reduce ? 0 : pxs * 0.22);
    outer.rotation.z = reduce ? 0 : time * 0.12;
    if (shown) {
      if (reduce) shown.pose(shown.s.loop ? 0 : 0.35);
      else if (shown.s.loop) shown.pose((time * 0.55) % 1);
      else { var c = 0.5 - 0.5 * Math.cos(time * 0.7); shown.pose(c * c * (3 - 2 * c)); }
      if (road.visible && !reduce) dashes.forEach(function (dm, n) {
        var z = ((n * 0.95 - time * 2.2) % 6.65 + 6.65) % 6.65 - 3.3; dm.position.z = z;
        dm.material.opacity = Math.max(0, Math.min(1, (2.75 - Math.abs(z)) / 0.6));
      });
    }
    camera.position.set(0, 3.15 - pys * 0.35, 13.2); camera.lookAt(0, 1.45, 0);
    renderer.render(scene, camera);
    requestAnimationFrame(frame);
  }

  mark(0);
  load(0, function (m) { show(m); });
  requestAnimationFrame(frame);
  // Fetch the other scenes one at a time once the first is up, so switching is instant
  SCENES.forEach(function (s, n) { if (n) setTimeout(function () { load(n); }, 1200 + n * 900); });
  window.__hero3d = { select: select, ready: function (i) { return !!loaded[i]; } };
})();
