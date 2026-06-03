import re

css_path = 'style.css'
js_path = 'script.js'

with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

theme_css = """
/* ============================================
   THEME SWITCHER
   ============================================ */
.theme-switcher {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 1000;
}

.theme-switcher-toggle {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  cursor: pointer;
  box-shadow: var(--shadow-glow);
  transition: all 0.3s ease;
}

.theme-switcher-toggle:hover {
  transform: scale(1.1);
}

.theme-switcher-panel {
  position: absolute;
  bottom: 60px;
  right: 0;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 15px;
  padding: 15px;
  width: max-content;
  backdrop-filter: blur(20px);
  opacity: 0;
  visibility: hidden;
  transform: translateY(20px);
  transition: all 0.3s ease;
  box-shadow: var(--shadow-card);
}

.theme-switcher-panel.active {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.theme-switcher-panel h4 {
  font-size: 0.9rem;
  margin-bottom: 10px;
  color: var(--text-primary);
  text-align: center;
}

.theme-options {
  display: flex;
  gap: 10px;
}

.theme-btn {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: 2px solid transparent;
  background: var(--theme-color);
  cursor: pointer;
  transition: all 0.2s ease;
}

.theme-btn:hover {
  transform: scale(1.2);
}

.theme-btn.active {
  border: 2px solid #ffffff;
  box-shadow: 0 0 10px var(--theme-color);
}

/* THEME CLASSES */
body.theme-gold {
  --primary-color: #FBBF24;
  --secondary-color: #F59E0B;
  --text-primary: #FFFFFF;
  --text-secondary: #CBD5E1;
  --bg-dark: #020617;
  --bg-card: rgba(15, 23, 42, 0.72);
  --bg-card-hover: rgba(20, 30, 50, 0.72);
  --border-color: rgba(251, 191, 36, 0.15);
  --gradient-1: linear-gradient(135deg, #FBBF24 0%, #F59E0B 100%);
  --shadow-glow: 0 0 25px rgba(251, 191, 36, 0.3);
}

body.theme-violet {
  --primary-color: #8B5CF6;
  --secondary-color: #C084FC;
  --text-primary: #FFFFFF;
  --text-secondary: #D1D5DB;
  --bg-dark: #020617;
  --bg-card: rgba(17, 24, 39, 0.75);
  --bg-card-hover: rgba(25, 35, 50, 0.75);
  --border-color: rgba(139, 92, 246, 0.15);
  --gradient-1: linear-gradient(135deg, #8B5CF6 0%, #C084FC 100%);
  --shadow-glow: 0 0 25px rgba(139, 92, 246, 0.3);
}

body.theme-emerald {
  --primary-color: #10B981;
  --secondary-color: #34D399;
  --text-primary: #FFFFFF;
  --text-secondary: #E5E7EB;
  --bg-dark: #030508;
  --bg-card: rgba(10, 20, 30, 0.75);
  --bg-card-hover: rgba(15, 25, 40, 0.75);
  --border-color: rgba(16, 185, 129, 0.15);
  --gradient-1: linear-gradient(135deg, #10B981 0%, #34D399 100%);
  --shadow-glow: 0 0 25px rgba(16, 185, 129, 0.3);
}

body.theme-mars {
  --primary-color: #FF5A36;
  --secondary-color: #FF7849;
  --text-primary: #FFFFFF;
  --text-secondary: #D6DCE5;
  --bg-dark: #05070A;
  --bg-card: rgba(18, 18, 22, 0.72);
  --bg-card-hover: rgba(25, 25, 30, 0.72);
  --border-color: rgba(255, 90, 54, 0.15);
  --gradient-1: linear-gradient(135deg, #FF5A36 0%, #FF7849 100%);
  --shadow-glow: 0 0 25px rgba(255, 90, 54, 0.3);
}

body.theme-arctic {
  --primary-color: #7DD3FC;
  --secondary-color: #38BDF8;
  --text-primary: #FFFFFF;
  --text-secondary: #CBD5E1;
  --bg-dark: #08111F;
  --bg-card: rgba(255, 255, 255, 0.08);
  --bg-card-hover: rgba(255, 255, 255, 0.12);
  --border-color: rgba(125, 211, 252, 0.15);
  --gradient-1: linear-gradient(135deg, #7DD3FC 0%, #38BDF8 100%);
  --shadow-glow: 0 0 25px rgba(125, 211, 252, 0.3);
}

body.theme-teal {
  --primary-color: #14B8A6;
  --secondary-color: #D97706;
  --text-primary: #FFFFFF;
  --text-secondary: #CBD5E1;
  --bg-dark: #04070C;
  --bg-card: rgba(12, 20, 30, 0.72);
  --bg-card-hover: rgba(18, 28, 40, 0.72);
  --border-color: rgba(20, 184, 166, 0.15);
  --gradient-1: linear-gradient(135deg, #14B8A6 0%, #D97706 100%);
  --shadow-glow: 0 0 25px rgba(20, 184, 166, 0.3);
}
"""

if "THEME SWITCHER" not in css:
    with open(css_path, 'a', encoding='utf-8') as f:
        f.write(theme_css)

with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Inject window.updateThreeTheme inside initEarth
inject_theme_logic = """
  // THEME SWITCHER LOGIC
  window.updateThreeTheme = function(theme) {
    const themeColors = {
      'theme-default': { earth: 0x030a18, core: 0x0088ff, node: 0x4aa0ff, light: 0x00e5ff },
      'theme-gold': { earth: 0x020617, core: 0xF59E0B, node: 0xFBBF24, light: 0xFFD54A },
      'theme-violet': { earth: 0x020617, core: 0x8B5CF6, node: 0xC084FC, light: 0x8B5CF6 },
      'theme-emerald': { earth: 0x030508, core: 0x10B981, node: 0x34D399, light: 0x10B981 },
      'theme-mars': { earth: 0x05070A, core: 0xFF5A36, node: 0xFF7849, light: 0xFF5A36 },
      'theme-arctic': { earth: 0x08111F, core: 0x38BDF8, node: 0x7DD3FC, light: 0x7DD3FC },
      'theme-teal': { earth: 0x04070C, core: 0xD97706, node: 0x14B8A6, light: 0x14B8A6 }
    };

    const colors = themeColors[theme] || themeColors['theme-default'];

    earthMaterial.color.setHex(colors.earth);
    coreMat.color.setHex(colors.core);
    nodeMaterial.color.setHex(colors.node);
    cursorLight.color.setHex(colors.light);
  };
}"""
js = js.replace('  window.addEventListener(\'resize\', () => {\n    camera.aspect = window.innerWidth / window.innerHeight;\n    camera.updateProjectionMatrix();\n    renderer.setSize(window.innerWidth, window.innerHeight);\n  });\n}', """  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });""" + inject_theme_logic)


# Add UI logic for theme switcher at the end of the script
ui_logic = """
// ============================================
// THEME SWITCHER UI LOGIC
// ============================================
const themeToggle = document.querySelector('.theme-switcher-toggle');
const themePanel = document.querySelector('.theme-switcher-panel');
const themeBtns = document.querySelectorAll('.theme-btn');

themeToggle.addEventListener('click', () => {
  themePanel.classList.toggle('active');
});

themeBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    // Update active button
    themeBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    // Get theme
    const theme = btn.getAttribute('data-theme');

    // Remove old themes
    document.body.className = document.body.className.replace(/theme-[a-z]+/g, '').trim();

    // Add new theme if not default
    if (theme !== 'theme-default') {
      document.body.classList.add(theme);
    }

    // Update Three.js
    if (window.updateThreeTheme) {
      window.updateThreeTheme(theme);
    }
  });
});

// Close panel when clicking outside
document.addEventListener('click', (e) => {
  if (!e.target.closest('.theme-switcher')) {
    themePanel.classList.remove('active');
  }
});
"""

if "THEME SWITCHER UI LOGIC" not in js:
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js + ui_logic)
else:
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js)

print("Applied theme switcher logic!")
