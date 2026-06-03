import re
import json

js_path = 'script.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Make stars brighter
js = js.replace('size: 0.025,', 'size: 0.035,')
js = js.replace('opacity: 0.8, // More visible', 'opacity: 1.0, // Maximum visibility')

# 2. Continent Nodes
with open('continents.json', 'r') as f:
    continents_data = f.read()

fibonacci_start = r'  for \(let i = 0; i < nodeCount; i\+\+.*?\}'
fibonacci_replacement = f"""  // Continent-shaped network dots
  const continentPoints = {continents_data};
  const actualNodeCount = continentPoints.length;
  // Re-instantiate with correct count
  const newNodeMesh = new THREE.InstancedMesh(nodeGeometry, nodeMaterial, actualNodeCount);
  
  for (let i = 0; i < actualNodeCount; i++) {{
    const phi = continentPoints[i][0];
    const theta = continentPoints[i][1] + Math.PI; // Offset theta to center the map nicely
    
    const r = 1.005;
    // Map to spherical coords. Depending on how the camera is set up:
    const x = r * Math.sin(phi) * Math.cos(theta);
    const z = r * Math.sin(phi) * Math.sin(theta);
    const y = r * Math.cos(phi);

    dummy.position.set(x, y, z);
    dummy.updateMatrix();
    newNodeMesh.setMatrixAt(i, dummy.matrix);

    nodePositions.push(new THREE.Vector3(x, y, z));
  }}
  
  // Replace the old nodeMesh in the group logic
  nodeMesh.geometry.dispose();
  nodeMesh.material.dispose();
"""

# Wait, the nodeMesh is already added to earthGroup via `earthGroup.add(nodeMesh);` later.
# So I should replace the entire block that generates it.
nodes_start = r'  // 2\. NETWORK NODES \(Instanced Mesh for high performance\)'
nodes_end = r'  earthGroup\.add\(nodeMesh\);'

nodes_replacement = f"""  // 2. NETWORK NODES (Continent Shaped)
  const continentPoints = {continents_data};
  const nodeCount = continentPoints.length;
  const nodeGeometry = new THREE.SphereGeometry(0.006, 8, 8);
  const nodeMaterial = new THREE.MeshBasicMaterial({{
    color: 0x4aa0ff,
  }});
  const nodeMesh = new THREE.InstancedMesh(nodeGeometry, nodeMaterial, nodeCount);

  const dummy = new THREE.Object3D();
  const nodePositions = []; 

  for (let i = 0; i < nodeCount; i++) {{
    const phi = continentPoints[i][0];
    const theta = continentPoints[i][1] + Math.PI; // Rotate to center Europe/Africa
    
    const r = 1.005;
    // Using standard mapping
    const x = r * Math.sin(phi) * Math.cos(theta);
    const z = r * Math.sin(phi) * Math.sin(theta);
    const y = r * Math.cos(phi);

    dummy.position.set(x, y, z);
    dummy.updateMatrix();
    nodeMesh.setMatrixAt(i, dummy.matrix);

    nodePositions.push(new THREE.Vector3(x, y, z));
  }}

  earthGroup.add(nodeMesh);"""

js = re.sub(nodes_start + r'[\s\S]*?' + nodes_end, nodes_replacement, js, count=1)


# 3. Meteors every 20 seconds.
# We will insert the meteor system right before // ANIMATION LOOP
meteor_init = """  // Minimal scientific lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.2);
  scene.add(ambientLight);

  // METEORS SYSTEM
  const meteors = [];
  const meteorMat = new THREE.LineBasicMaterial({
    color: 0xffffff,
    transparent: true,
    opacity: 1.0,
    blending: THREE.AdditiveBlending
  });

  function spawnMeteor() {
    const startX = -20; // Left side
    const startY = 10 + Math.random() * 5;
    const startZ = -5 - Math.random() * 10;
    
    // Goes left to right, slightly downwards
    const velX = 0.5 + Math.random() * 0.2;
    const velY = -0.1 - Math.random() * 0.2;
    
    const meteorGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0,0,0),
      new THREE.Vector3(-velX*8, -velY*8, 0)
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
  
  // Every 20 seconds
  setInterval(() => {
    spawnMeteor();
  }, 20000);
"""
js = js.replace('  // Minimal scientific lighting\n  const ambientLight = new THREE.AmbientLight(0xffffff, 0.2);\n  scene.add(ambientLight);', meteor_init)

# And inside animate loop, add update logic before `renderer.render(scene, camera);`
meteor_anim = """
    // Update Meteors
    for(let i=meteors.length-1; i>=0; i--) {
      const m = meteors[i];
      m.mesh.position.add(m.vel);
      m.life -= 0.005; // Lives for roughly 200 frames
      m.mesh.material.opacity = m.life;
      
      if(m.life <= 0) {
        scene.remove(m.mesh);
        m.mesh.geometry.dispose();
        m.mesh.material.dispose();
        meteors.splice(i, 1);
      }
    }
    
    renderer.render(scene, camera);"""
js = js.replace('    renderer.render(scene, camera);', meteor_anim)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Changes applied!")
