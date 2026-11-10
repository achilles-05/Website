// ============================================
// SETUP
// ============================================
const root = document.documentElement;
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// ============================================
// THEME TOGGLE (dark / light, remembered per visitor)
// ============================================
const themeToggle = document.getElementById('theme-toggle');

function setTheme(theme) {
  root.setAttribute('data-theme', theme);
  try { localStorage.setItem('theme', theme); } catch (e) { /* storage unavailable */ }
  themeToggle.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
  network.refreshColour();
}

themeToggle.addEventListener('click', () => {
  setTheme(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
});

// ============================================
// NODE NETWORK BACKGROUND
// Dense on the home screen, kept clear of the hero text,
// links to the cursor, and fades into the background on scroll.
// ============================================
const network = (() => {
  const canvas = document.getElementById('network');
  const ctx = canvas.getContext('2d');
  const hero = document.getElementById('home');
  const heroContent = document.getElementById('hero-content');

  const LINK_DIST = 120;      // max distance for node-to-node links
  const MOUSE_DIST = 170;     // max distance for node-to-cursor links
  const CLEAR_PAD = 56;       // empty margin kept around the hero text
  const FADED_OPACITY = 0.16; // how visible the network stays once scrolled away

  let w = 0, h = 0, dpr = 1;
  let nodes = [];
  let colour = '214, 219, 226';
  const mouse = { x: -9999, y: -9999, active: false };
  let zone = null; // area around the hero text the nodes must stay out of

  function refreshColour() {
    colour = getComputedStyle(root).getPropertyValue('--node').trim() || colour;
    if (reduceMotion) draw();
  }

  function updateZone() {
    const r = heroContent.getBoundingClientRect();
    if (r.bottom < -CLEAR_PAD || r.top > h) { zone = null; return; }
    zone = { l: r.left - CLEAR_PAD, r: r.right + CLEAR_PAD, t: r.top - CLEAR_PAD, b: r.bottom + CLEAR_PAD };
  }

  const inZone = (x, y) => zone && x > zone.l && x < zone.r && y > zone.t && y < zone.b;

  function spawn() {
    let x, y, tries = 0;
    do { x = Math.random() * w; y = Math.random() * h; tries++; } while (inZone(x, y) && tries < 30);
    const a = Math.random() * Math.PI * 2;
    const s = 0.12 + Math.random() * 0.22;
    return { x, y, vx: Math.cos(a) * s, vy: Math.sin(a) * s, base: s, r: 1 + Math.random() * 0.9 };
  }

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    w = window.innerWidth;
    h = window.innerHeight;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    updateZone();
    const density = w < 700 ? 9000 : 6500;
    const count = Math.max(50, Math.min(300, Math.round((w * h) / density)));
    while (nodes.length < count) nodes.push(spawn());
    nodes.length = count;
  }

  // Push a node that has drifted into the clear zone back out through the nearest edge.
  function keepOut(n) {
    if (!inZone(n.x, n.y)) return;
    const d = [n.x - zone.l, zone.r - n.x, n.y - zone.t, zone.b - n.y];
    const i = d.indexOf(Math.min(...d));
    if (i === 0) { n.x = zone.l; n.vx = -Math.abs(n.vx); }
    if (i === 1) { n.x = zone.r; n.vx = Math.abs(n.vx); }
    if (i === 2) { n.y = zone.t; n.vy = -Math.abs(n.vy); }
    if (i === 3) { n.y = zone.b; n.vy = Math.abs(n.vy); }
  }

  // A link is hidden if it would cross the clear zone.
  function crossesZone(a, b) {
    if (!zone) return false;
    for (let t = 0.25; t < 1; t += 0.25) {
      if (inZone(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t)) return true;
    }
    return false;
  }

  function step() {
    for (const n of nodes) {
      // gentle push away from the cursor
      if (mouse.active) {
        const dx = n.x - mouse.x, dy = n.y - mouse.y;
        const d2 = dx * dx + dy * dy;
        if (d2 < 90 * 90 && d2 > 1) {
          const f = (1 - Math.sqrt(d2) / 90) * 0.06;
          n.vx += (dx / Math.sqrt(d2)) * f;
          n.vy += (dy / Math.sqrt(d2)) * f;
        }
      }
      // ease speed back towards each node's resting drift
      const sp = Math.hypot(n.vx, n.vy) || 1;
      const k = 1 + (n.base / sp - 1) * 0.02;
      n.vx *= k; n.vy *= k;

      n.x += n.vx; n.y += n.vy;
      if (n.x < -10) n.x = w + 10; else if (n.x > w + 10) n.x = -10;
      if (n.y < -10) n.y = h + 10; else if (n.y > h + 10) n.y = -10;
      keepOut(n);
    }
  }

  function draw() {
    ctx.clearRect(0, 0, w, h);
    ctx.lineWidth = 0.8;

    for (let i = 0; i < nodes.length; i++) {
      const a = nodes[i];
      for (let j = i + 1; j < nodes.length; j++) {
        const b = nodes[j];
        const dx = a.x - b.x, dy = a.y - b.y;
        if (Math.abs(dx) > LINK_DIST || Math.abs(dy) > LINK_DIST) continue;
        const d = Math.sqrt(dx * dx + dy * dy);
        if (d < LINK_DIST && !crossesZone(a, b)) {
          ctx.strokeStyle = `rgba(${colour}, ${(1 - d / LINK_DIST) * 0.22})`;
          ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
        }
      }
      if (mouse.active && !inZone(mouse.x, mouse.y)) {
        const d = Math.hypot(a.x - mouse.x, a.y - mouse.y);
        if (d < MOUSE_DIST && !crossesZone(a, mouse)) {
          ctx.strokeStyle = `rgba(${colour}, ${(1 - d / MOUSE_DIST) * 0.55})`;
          ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(mouse.x, mouse.y); ctx.stroke();
        }
      }
    }

    for (const n of nodes) {
      ctx.fillStyle = `rgba(${colour}, 0.6)`;
      ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2); ctx.fill();
    }
  }

  // Full strength on the home screen, fading as the hero scrolls away.
  function updateOpacity() {
    const p = Math.min(1, window.scrollY / (hero.offsetHeight * 0.75));
    canvas.style.opacity = String(1 - p * (1 - FADED_OPACITY));
  }

  function loop() {
    if (!document.hidden) {
      updateZone();
      step();
      draw();
    }
    requestAnimationFrame(loop);
  }

  window.addEventListener('resize', () => { resize(); if (reduceMotion) draw(); });
  window.addEventListener('scroll', updateOpacity, { passive: true });
  window.addEventListener('pointermove', e => {
    if (e.pointerType === 'touch') return;
    mouse.x = e.clientX; mouse.y = e.clientY; mouse.active = true;
  });
  document.addEventListener('pointerleave', () => { mouse.active = false; });
  window.addEventListener('blur', () => { mouse.active = false; });

  refreshColour();
  resize();
  updateOpacity();
  if (reduceMotion) draw(); else requestAnimationFrame(loop);

  return { refreshColour };
})();

themeToggle.setAttribute('aria-label', root.getAttribute('data-theme') === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');

// ============================================
// NAVIGATION: background on scroll, mobile menu, active link
// ============================================
const nav = document.querySelector('.nav');
const navLinks = document.getElementById('nav-links');
const menuToggle = document.getElementById('menu-toggle');

const updateNav = () => nav.classList.toggle('scrolled', window.scrollY > 20);
window.addEventListener('scroll', updateNav, { passive: true });
updateNav();

menuToggle.addEventListener('click', () => {
  const open = navLinks.classList.toggle('open');
  menuToggle.setAttribute('aria-expanded', String(open));
  menuToggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
});

navLinks.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => {
    navLinks.classList.remove('open');
    menuToggle.setAttribute('aria-expanded', 'false');
    menuToggle.setAttribute('aria-label', 'Open menu');
  });
});

const sectionObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    navLinks.querySelectorAll('a').forEach(a => {
      a.classList.toggle('active', a.getAttribute('href') === `#${entry.target.id}`);
    });
  });
}, { rootMargin: '-45% 0px -50% 0px' });

document.querySelectorAll('main section[id]').forEach(s => sectionObserver.observe(s));

// ============================================
// HERO ROLE ROTATION
// ============================================
const roleWord = document.getElementById('role-word');
const roles = [
  'Aerospace Enthusiast',
  'Research Focused',
  'Experienced Intern',
  'Robotics & Automation'
];
let roleIndex = 0;

if (!reduceMotion) {
  setInterval(() => {
    roleWord.classList.add('out');
    setTimeout(() => {
      roleIndex = (roleIndex + 1) % roles.length;
      roleWord.textContent = roles[roleIndex];
      roleWord.classList.remove('out');
    }, 450);
  }, 2800);
}

// ============================================
// SCROLL REVEAL
// ============================================
const revealObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('in');
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

// ============================================
// STAT COUNTER ANIMATION
// ============================================
function animateCounter(el) {
  const targetStr = el.getAttribute('data-target');
  const isFloat = targetStr.includes('.');
  const target = parseFloat(targetStr);
  if (reduceMotion) { el.textContent = targetStr; return; }
  const start = performance.now();
  const duration = 1600;

  const tick = now => {
    const p = Math.min(1, (now - start) / duration);
    const eased = 1 - Math.pow(1 - p, 3);
    const v = target * eased;
    el.textContent = p < 1 ? (isFloat ? v.toFixed(1) : Math.floor(v)) : targetStr;
    if (p < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

const statsObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      animateCounter(entry.target);
      statsObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('.stat-number').forEach(s => statsObserver.observe(s));

// ============================================
// CONTACT FORM
// There is no backend on a static site, so hand the message to the
// visitor's own email app, pre-filled and addressed to the contact email.
// ============================================
const contactForm = document.querySelector('.contact-form');

if (contactForm) {
  contactForm.addEventListener('submit', e => {
    e.preventDefault();

    const [nameInput, emailInput, subjectInput] = contactForm.querySelectorAll('input');
    const messageInput = contactForm.querySelector('textarea');
    const contactLink = document.querySelector('.contact-row a[href^="mailto:"]');
    const toAddress = contactLink ? contactLink.getAttribute('href').replace('mailto:', '') : '';

    const body = `${messageInput.value}\n\n— ${nameInput.value} (${emailInput.value})`;
    window.location.href = `mailto:${toAddress}?subject=${encodeURIComponent(subjectInput.value)}&body=${encodeURIComponent(body)}`;

    // The form is left filled in, in case the visitor has no email app set up.
    const label = contactForm.querySelector('.btn span');
    const originalText = label.textContent;
    label.textContent = 'Opening your email app...';
    setTimeout(() => { label.textContent = originalText; }, 4000);
  });
}
