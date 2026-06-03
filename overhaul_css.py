import re

css_path = 'c:/Users/shree/Downloads/Website-main/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# 1. Replace the :root block completely
new_root = '''
:root {
  --primary-color: #00f0ff;
  --secondary-color: #5a32fa;
  --accent-color: #00c3ff;
  --text-primary: #ffffff;
  --text-secondary: #b4c6d4;
  --text-light: #94a3b8;
  --bg-dark: #030508;
  --bg-card: rgba(10, 15, 30, 0.5);
  --bg-card-hover: rgba(20, 25, 45, 0.7);
  --border-color: rgba(0, 240, 255, 0.15);
  --gradient-1: linear-gradient(135deg, #00f0ff 0%, #5a32fa 100%);
  --gradient-2: linear-gradient(135deg, #5a32fa 0%, #150a30 100%);
  --gradient-3: linear-gradient(135deg, #00c3ff 0%, #00f0ff 100%);
  --gradient-space: linear-gradient(180deg, #030508 0%, #0a0a0a 50%, #030508 100%);
  --shadow-glow: 0 0 25px rgba(0, 240, 255, 0.3);
  --shadow-card: 0 10px 40px rgba(0, 0, 0, 0.6);
}
'''
css = re.sub(r':root\s*\{[\s\S]*?\}', new_root.strip(), css, count=1)

# 2. Update typography (add Space Grotesk after the body rule)
body_rule_pattern = r'(body\s*\{[\s\S]*?\})'
typography_rule = '''
h1, h2, h3, h4, h5, h6, .logo, .hero-name, .section-title, .nav-link, .btn {
  font-family: 'Space Grotesk', sans-serif;
  letter-spacing: -0.02em;
}
'''
if 'Space Grotesk' not in css:
    css = re.sub(body_rule_pattern, r'\1\n' + typography_rule, css, count=1)

# 3. Add backdrop-filter to cards if not present, and update background
cards = ['.project-card', '.timeline-content', '.publication-card', '.education-card', '.achievement-card']
for card in cards:
    pattern = rf'({card}\s*\{{[^\}}]*?)\}}'
    
    def replacer(match):
        content = match.group(1)
        if 'backdrop-filter' not in content:
            content += '  backdrop-filter: blur(20px);\n  -webkit-backdrop-filter: blur(20px);\n'
        return content + '}'
        
    css = re.sub(pattern, replacer, css)

# 4. Update section backgrounds from 0.02/0.03 white to completely transparent to let earth and stars show, or darker.
css = css.replace('rgba(255, 255, 255, 0.02)', 'transparent')
css = css.replace('background: rgba(255, 255, 255, 0.03)', 'background: transparent')

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

print("CSS Overhaul successfully completed.")
