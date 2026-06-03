import sys
import re

js_path = 'script.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

start_marker = r'// 6\. STARS BACKGROUND \(Interactive\)'
end_marker = r'// ANIMATION LOOP'

new_init_code = """// 6. STARS BACKGROUND (Interactive & Colorful)
  const starsGeometry = new THREE.BufferGeometry();
  const starCount = 3500;
  
  // Custom Shader for twinkling stars
  const starsMaterial = new THREE.ShaderMaterial({
    uniforms: {
      time: { value: 0 }
    },
    vertexShader: `
      attribute vec3 color;
      attribute float sizeOffset;
      varying vec3 vColor;
      varying float vSizeOffset;
      void main() {
        vColor = color;
        vSizeOffset = sizeOffset;
        vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
        gl_PointSize = (3.0 + sizeOffset) * (5.0 / -mvPosition.z);
        gl_Position = projectionMatrix * mvPosition;
      }
    `,
    fragmentShader: `
      uniform float time;
      varying vec3 vColor;
      varying float vSizeOffset;
      void main() {
        // Create soft circular point
        vec2 xy = gl_PointCoord.xy - vec2(0.5);
        float ll = length(xy);
        if(ll > 0.5) discard;
        
        // Twinkle effect based on time and individual offset
        float twinkle = 0.5 + 0.5 * sin(time * 2.0 + vSizeOffset * 10.0);
        float alpha = (0.5 - ll) * 2.0 * twinkle;
        gl_FragColor = vec4(vColor, alpha);
      }
    `,
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  });

  const starsVertices = [];
  const starsInitialPositions = [];
  const starVelocities = [];
  const starColors = [];
  const starSizes = [];

  const colorPalette = [
    new THREE.Color(0xffffff), // White
    new THREE.Color(0x00e5ff), // Cyan
    new THREE.Color(0x3b82f6), // Blue
    new THREE.Color(0xccffff)  // Light Cyan
  ];

  for (let i = 0; i < starCount; i++) {
    const x = (Math.random() - 0.5) * 35;
    const y = (Math.random() - 0.5) * 35;
    const z = (Math.random() - 0.5) * 15 - 5;
    starsVertices.push(x, y, z);
    starsInitialPositions.push({ x, y, z });
    starVelocities.push({ x: 0, y: 0, z: 0 });
    
    const color = colorPalette[Math.floor(Math.random() * colorPalette.length)];
    starColors.push(color.r, color.g, color.b);
    starSizes.push(Math.random() * 2.0); // Size variation offset
  }

  starsGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starsVertices, 3));
  starsGeometry.setAttribute('color', new THREE.Float32BufferAttribute(starColors, 3));
  starsGeometry.setAttribute('sizeOffset', new THREE.Float32BufferAttribute(starSizes, 1));
  const stars = new THREE.Points(starsGeometry, starsMaterial);
  scene.add(stars);

  // 7. SATELLITE DATA RINGS
  const ringsGroup = new THREE.Group();
  earthGroup.add(ringsGroup); // Attach to earth so it orbits with the network
  
  const ringMaterial = new THREE.LineBasicMaterial({
    color: 0x00e5ff,
    transparent: true,
    opacity: 0.15,
    blending: THREE.AdditiveBlending
  });
  
  const ringNodes = [];
  for(let i=0; i<3; i++) {
    const ringGeo = new THREE.TorusGeometry(1.3 + i*0.2, 0.002, 16, 100);
    const ring = new THREE.Line(ringGeo, ringMaterial);
    
    // Tilt the rings
    ring.rotation.x = Math.random() * Math.PI;
    ring.rotation.y = Math.random() * Math.PI;
    ringsGroup.add(ring);
    
    // Add a glowing node (satellite) to the ring
    const nodeGeo = new THREE.SphereGeometry(0.015, 8, 8);
    const nodeMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
    const sat = new THREE.Mesh(nodeGeo, nodeMat);
    ring.add(sat);
    
    ringNodes.push({
      mesh: sat,
      angle: Math.random() * Math.PI * 2,
      speed: 0.005 + Math.random() * 0.01,
      radius: 1.3 + i*0.2
    });
  }

  // 8. DISTANT MOON/PLANET
  const moonGroup = new THREE.Group();
  scene.add(moonGroup);
  
  const moonGeo = new THREE.SphereGeometry(0.15, 32, 32);
  const moonMat = new THREE.MeshPhysicalMaterial({
    color: 0x050505,
    roughness: 0.9,
    metalness: 0.1,
  });
  const moon = new THREE.Mesh(moonGeo, moonMat);
  moon.position.set(4, 2, -5); // Distant background
  moonGroup.add(moon);
  
  // Moon Atmosphere Glow
  const moonAtmoMat = new THREE.MeshBasicMaterial({
    color: 0x3b82f6,
    transparent: true,
    opacity: 0.2,
    blending: THREE.AdditiveBlending,
    side: THREE.BackSide
  });
  const moonAtmo = new THREE.Mesh(new THREE.SphereGeometry(0.17, 32, 32), moonAtmoMat);
  moon.add(moonAtmo);

  // 9. METEORS (Shooting Stars)
  const meteors = [];
  const meteorMat = new THREE.LineBasicMaterial({
    color: 0xffffff,
    transparent: true,
    opacity: 1.0,
    blending: THREE.AdditiveBlending
  });

  function spawnMeteor() {
    // Random start position outside view
    const startX = (Math.random() - 0.5) * 20;
    const startY = 10 + Math.random() * 5;
    const startZ = -5 - Math.random() * 10;
    
    // Velocity pointing downwards diagonally
    const velX = (Math.random() - 0.5) * 0.2;
    const velY = -0.2 - Math.random() * 0.2;
    
    const meteorGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0,0,0),
      new THREE.Vector3(-velX*5, -velY*5, 0) // Tail
    ]);
    
    const meteor = new THREE.Line(meteorGeo, meteorMat.clone());
    meteor.position.set(startX, startY, startZ);
    scene.add(meteor);
    
    meteors.push({
      mesh: meteor,
      vel: new THREE.Vector3(velX, velY, 0),
      life: 1.0
    });
  }
  
  // Spawn a meteor occasionally
  setInterval(() => {
    if(Math.random() > 0.4 && document.hasFocus()) spawnMeteor();
  }, 2000);

  // 10. LIGHTING (Interactive)
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.1);
  scene.add(ambientLight);
  
  const cursorLight = new THREE.PointLight(0x00e5ff, 2.0, 10);
  cursorLight.position.set(0, 0, 3);
  scene.add(cursorLight);

  // ANIMATION LOOP
"""

animate_start = r'    // 4\. Star Ripple Effect'
animate_end = r'    stars\.geometry\.attributes\.position\.needsUpdate = true;'

animate_replacement = """    // 4. Star Ripple Effect & Twinkle Update
    starsMaterial.uniforms.time.value = time;
    
    const positions = stars.geometry.attributes.position.array;
    const cursorWorldX = mouseX * 15;
    const cursorWorldY = -mouseY * 10;

    for (let i = 0; i < starCount; i++) {
      const px = starsInitialPositions[i].x;
      const py = starsInitialPositions[i].y;
      const dx = cursorWorldX - px;
      const dy = cursorWorldY - py;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < 3.0) {
        const force = (3.0 - dist) * 0.02;
        starVelocities[i].x -= (dx / dist) * force;
        starVelocities[i].y -= (dy / dist) * force;
      }

      starVelocities[i].x *= 0.95;
      starVelocities[i].y *= 0.95;

      const currentX = positions[i * 3];
      const currentY = positions[i * 3 + 1];

      positions[i * 3] += starVelocities[i].x + (starsInitialPositions[i].x - currentX) * 0.02;
      positions[i * 3 + 1] += starVelocities[i].y + (starsInitialPositions[i].y - currentY) * 0.02;
    }
    stars.geometry.attributes.position.needsUpdate = true;

    // 5. Satellite Rings Animation
    ringsGroup.rotation.y += 0.001;
    ringsGroup.rotation.x += 0.0005;
    ringNodes.forEach(node => {
      node.angle += node.speed;
      node.mesh.position.x = Math.cos(node.angle) * node.radius;
      node.mesh.position.y = Math.sin(node.angle) * node.radius;
    });

    // 6. Moon Orbit Animation
    moonGroup.rotation.y = time * 0.5;
    
    // 7. Meteors Update
    for(let i=meteors.length-1; i>=0; i--) {
      const m = meteors[i];
      m.mesh.position.add(m.vel);
      m.life -= 0.015;
      m.mesh.material.opacity = m.life;
      
      if(m.life <= 0) {
        scene.remove(m.mesh);
        m.mesh.geometry.dispose();
        m.mesh.material.dispose();
        meteors.splice(i, 1);
      }
    }
    
    // 8. Update Cursor Light Position
    cursorLight.position.x += (mouseX * 5 - cursorLight.position.x) * 0.1;
    cursorLight.position.y += (-mouseY * 5 - cursorLight.position.y) * 0.1;
"""

js = re.sub(start_marker + r'[\s\S]*?' + end_marker, new_init_code, js, count=1)
js = re.sub(animate_start + r'[\s\S]*?' + animate_end, animate_replacement, js, count=1)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("js updated!")
