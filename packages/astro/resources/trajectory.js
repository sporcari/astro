var trajectory = {
    initialized: false,
    scene: null,
    camera: null,
    renderer: null,
    controls: null,
    line: null,
    startMarker: null,
    movingMarker: null,
    orbitLine: null,
    markerSpeed: 3600,
    traversal: null,

    init: function(containerId) {
        if (trajectory.initialized) return;
        var setup = function() { trajectory._setupScene(containerId); };
        var loadOrbit = function() {
            genro.dom.loadJs(
                'https://unpkg.com/three@0.128.0/examples/js/controls/OrbitControls.js',
                setup);
        };
        if (typeof THREE === 'undefined') {
            genro.dom.loadJs(
                'https://unpkg.com/three@0.128.0/build/three.min.js',
                loadOrbit);
        } else {
            loadOrbit();
        }
    },

    _setupScene: function(containerId) {
        var container = genro.dom.getDomNode(containerId);
        if (!container) {
            console.warn('[trajectory] container not found yet, retry in 100ms');
            setTimeout(function() { trajectory._setupScene(containerId); }, 100);
            return;
        }
        var w = container.clientWidth || 800;
        var h = container.clientHeight || 600;

        trajectory.scene = new THREE.Scene();
        trajectory.scene.background = new THREE.Color(0x000010);

        trajectory.camera = new THREE.PerspectiveCamera(50, w/h, 0.001, 100000);
        trajectory.camera.position.set(2, 2, 2);

        trajectory.renderer = new THREE.WebGLRenderer({antialias: true});
        trajectory.renderer.setSize(w, h);
        container.appendChild(trajectory.renderer.domElement);

        trajectory.controls = new THREE.OrbitControls(
            trajectory.camera, trajectory.renderer.domElement);
        trajectory.controls.enableDamping = true;

        var earthGeo = new THREE.SphereGeometry(0.06, 32, 32);
        var earthMat = new THREE.MeshBasicMaterial(
            {color: 0x3399ff, wireframe: true});
        trajectory.scene.add(new THREE.Mesh(earthGeo, earthMat));

        var axes = new THREE.AxesHelper(1);
        trajectory.scene.add(axes);

        var animate = function() {
            requestAnimationFrame(animate);
            trajectory.controls.update();
            trajectory._stepMarker();
            trajectory.renderer.render(trajectory.scene, trajectory.camera);
        };
        animate();

        window.addEventListener('resize', function() {
            var w = container.clientWidth;
            var h = container.clientHeight;
            trajectory.camera.aspect = w / h;
            trajectory.camera.updateProjectionMatrix();
            trajectory.renderer.setSize(w, h);
        });

        trajectory.initialized = true;
    },

    _stepMarker: function() {
        var t = trajectory.traversal;
        if (!trajectory.movingMarker || !t || t.totalTime <= 0) return;

        t.cumTime += trajectory.markerSpeed;
        if (t.cumTime >= t.totalTime) t.cumTime %= t.totalTime;

        var rem = t.cumTime;
        var idx = 0;
        while (idx < t.segTimes.length && rem >= t.segTimes[idx]) {
            rem -= t.segTimes[idx];
            idx++;
        }
        if (idx >= t.positions.length - 1) {
            idx = t.positions.length - 2;
            rem = t.segTimes[idx];
        }
        var frac = t.segTimes[idx] > 0 ? rem / t.segTimes[idx] : 0;
        var a = t.positions[idx];
        var b = t.positions[idx + 1];
        var px = a[0] + (b[0]-a[0])*frac;
        var py = a[1] + (b[1]-a[1])*frac;
        var pz = a[2] + (b[2]-a[2])*frac;
        var s = t.scale;
        trajectory.movingMarker.position.set(px*s, py*s, pz*s);

        t.tick = (t.tick + 1) % 6;
        if (t.tick === 0) {
            genro.setData('main.current_v', t.v.toFixed(3) + ' km/s');
        }
    },

    _buildTraversal: function(oNodes, sNodes, scale, muHint) {
        if (oNodes.length < 2 || sNodes.length < 1) return null;

        // Uniform speed = average of sample speed moduli
        var vSum = 0;
        for (var i = 0; i < sNodes.length; i++) {
            var a = sNodes[i].attr;
            vSum += Math.sqrt(a.vx*a.vx + a.vy*a.vy + a.vz*a.vz);
        }
        var vUniform = vSum / sNodes.length;
        if (vUniform < 1e-6) vUniform = 1.0;
        console.log('[trajectory] uniform speed:', vUniform.toFixed(3), 'km/s');

        var positions = [];
        for (var i = 0; i < oNodes.length; i++) {
            var a = oNodes[i].attr;
            positions.push([a.x, a.y, a.z]);
        }
        var segTimes = [];
        var totalTime = 0;
        for (var i = 0; i < positions.length - 1; i++) {
            var a = positions[i];
            var b = positions[i+1];
            var dx = b[0]-a[0], dy = b[1]-a[1], dz = b[2]-a[2];
            var ds = Math.sqrt(dx*dx + dy*dy + dz*dz);
            var t = ds / vUniform;
            segTimes.push(t);
            totalTime += t;
        }
        return {
            positions: positions,
            segTimes: segTimes,
            totalTime: totalTime,
            cumTime: 0,
            scale: scale,
            v: vUniform,
            tick: 0
        };
    },

    _nodesOf: function(bag) {
        if (!bag || typeof bag.getNodes !== 'function') return [];
        return bag.getNodes();
    },

    _maxAbs: function(nodes, current) {
        var m = current || 0;
        for (var i = 0; i < nodes.length; i++) {
            var a = nodes[i].attr;
            m = Math.max(m, Math.abs(a.x), Math.abs(a.y), Math.abs(a.z));
        }
        return m;
    },

    _buildLine: function(nodes, scale, material) {
        var positions = [];
        for (var i = 0; i < nodes.length; i++) {
            var a = nodes[i].attr;
            positions.push(a.x*scale, a.y*scale, a.z*scale);
        }
        var geo = new THREE.BufferGeometry();
        geo.setAttribute('position',
            new THREE.Float32BufferAttribute(positions, 3));
        var line = new THREE.Line(geo, material);
        if (material.isLineDashedMaterial) line.computeLineDistances();
        return line;
    },

    _ready: function() {
        if (!trajectory.initialized) {
            console.warn('[trajectory] scene not initialized yet — wait and retry');
            return false;
        }
        return true;
    },

    plotSamples: function(samples) {
        if (!trajectory._ready()) return;
        var sNodes = trajectory._nodesOf(samples);
        if (!sNodes.length) {
            console.warn('[trajectory.plotSamples] no samples');
            return;
        }

        if (trajectory.line)        trajectory.scene.remove(trajectory.line);
        if (trajectory.startMarker) trajectory.scene.remove(trajectory.startMarker);

        var maxAbs = trajectory._maxAbs(sNodes, 0);
        trajectory.scale = maxAbs > 0 ? 1/maxAbs : 1;
        var s = trajectory.scale;

        trajectory.line = trajectory._buildLine(sNodes, s,
            new THREE.LineBasicMaterial({color: 0xff6633}));
        trajectory.scene.add(trajectory.line);

        var first = sNodes[0].attr;
        var last = sNodes[sNodes.length - 1].attr;

        var stGeo = new THREE.SphereGeometry(0.04, 16, 16);
        var stMat = new THREE.MeshBasicMaterial({color: 0xffff66});
        trajectory.startMarker = new THREE.Mesh(stGeo, stMat);
        trajectory.startMarker.position.set(first.x*s, first.y*s, first.z*s);
        trajectory.scene.add(trajectory.startMarker);

        var dx = (first.x + last.x)*0.5*s;
        var dy = (first.y + last.y)*0.5*s;
        var dz = (first.z + last.z)*0.5*s;
        trajectory.controls.target.set(dx, dy, dz);
        trajectory.camera.position.set(dx + 2, dy + 2, dz + 2);
        trajectory.controls.update();
    },

    plotOrbit: function(orbit) {
        if (!trajectory._ready()) return;
        var oNodes = trajectory._nodesOf(orbit);
        if (!oNodes.length) {
            console.warn('[trajectory.plotOrbit] no orbit points');
            return;
        }
        if (!trajectory.scale) {
            // No samples drawn yet — derive scale from orbit
            var maxAbs = trajectory._maxAbs(oNodes, 0);
            trajectory.scale = maxAbs > 0 ? 1/maxAbs : 1;
        }
        if (trajectory.orbitLine) trajectory.scene.remove(trajectory.orbitLine);
        trajectory.orbitLine = trajectory._buildLine(oNodes, trajectory.scale,
            new THREE.LineDashedMaterial({
                color: 0x55ddff,
                dashSize: 0.04, gapSize: 0.025,
                transparent: true, opacity: 0.7}));
        trajectory.scene.add(trajectory.orbitLine);
    },

    toggleAnimation: function(samples, orbit, mu) {
        if (!trajectory._ready()) return;
        if (trajectory.traversal) {
            console.log('[trajectory] animation stopped');
            trajectory.traversal = null;
            if (trajectory.movingMarker) {
                trajectory.scene.remove(trajectory.movingMarker);
                trajectory.movingMarker = null;
            }
            return;
        }
        var sNodes = trajectory._nodesOf(samples);
        var oNodes = trajectory._nodesOf(orbit);
        if (!sNodes.length || !oNodes.length) {
            console.warn('[trajectory.toggleAnimation] need both samples and orbit');
            return;
        }
        if (!trajectory.scale) {
            var maxAbs = trajectory._maxAbs(sNodes, 0);
            trajectory.scale = maxAbs > 0 ? 1/maxAbs : 1;
        }
        trajectory.traversal = trajectory._buildTraversal(
            oNodes, sNodes, trajectory.scale, mu);
        if (!trajectory.traversal) {
            console.warn('[trajectory.toggleAnimation] failed to build traversal');
            return;
        }
        var first = sNodes[0].attr;
        var s = trajectory.scale;
        var movGeo = new THREE.SphereGeometry(0.035, 16, 16);
        var movMat = new THREE.MeshBasicMaterial({
            color: 0xffff66, transparent: true, opacity: 0.45});
        trajectory.movingMarker = new THREE.Mesh(movGeo, movMat);
        trajectory.movingMarker.position.set(first.x*s, first.y*s, first.z*s);
        trajectory.scene.add(trajectory.movingMarker);
        console.log('[trajectory] animation started');
    }
};
