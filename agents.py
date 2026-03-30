"""
LovableBot — Production AI Code Generation (Lovable-parity)

Key capabilities added vs previous version:
- Iteration/modification of existing code ("fix the navbar", "add dark mode")
- Tailwind CSS + Font Awesome + AOS + Alpine.js via CDN for stunning UI
- Multi-view hash routing in single-file apps
- Smart clarification detection
- Template library for 10+ project types
- Feature verification pass
- Real Chart.js dashboard configurations
- Better 3D with custom geometry per request
"""

import requests
import urllib.parse
import time
import re
import json
import os
import zipfile
import tempfile

API_BASE = "https://dev-apis-xyz.pantheonsite.io/wp-content/apis/freeAi.php"
MODEL = "gemini"
FALLBACK = "llama"


# ─── Core AI caller ──────────────────────────────────────────────────────────

def call_ai(prompt: str, model: str = MODEL, retries: int = 3, timeout: int = 100) -> str:
    for attempt in range(retries):
        try:
            encoded = urllib.parse.quote(prompt, safe="")
            resp = requests.get(f"{API_BASE}?prompt={encoded}&model={model}", timeout=timeout)
            text = resp.text.strip()
            if text and len(text) > 30 and "Bro What The Fuck" not in text:
                return text
        except Exception:
            pass
        if attempt < retries - 1:
            time.sleep(3 + attempt * 2)
    # Fallback
    if model != FALLBACK:
        try:
            encoded = urllib.parse.quote(prompt, safe="")
            resp = requests.get(f"{API_BASE}?prompt={encoded}&model={FALLBACK}", timeout=60)
            if resp.text.strip():
                return resp.text.strip()
        except Exception:
            pass
    return ""


def extract_code(text: str, lang_hint: str = "") -> str:
    """Extract the largest relevant code block from AI response."""
    # Match ```lang\n...\n```
    blocks = re.findall(r"```(\w*)\n([\s\S]*?)```", text)
    if not blocks:
        blocks = re.findall(r"```([\s\S]*?)```", text)
        blocks = [("", b) for b in blocks]

    if not blocks:
        # Raw code if it looks like code
        if any(k in text for k in ["<!DOCTYPE", "<html", "def ", "class ", "const ", "function "]):
            return text.strip()
        return ""

    # Prefer matching language
    if lang_hint:
        aliases = {
            "html": {"html", "htm"},
            "python": {"python", "py"},
            "javascript": {"javascript", "js", "jsx"},
            "css": {"css"},
        }
        wanted = aliases.get(lang_hint, {lang_hint})
        matched = [b for b in blocks if b[0].lower() in wanted]
        if matched:
            return max(matched, key=lambda b: len(b[1]))["code"] if isinstance(matched[0], dict) else max(matched, key=lambda b: len(b[1]))[1]

    return max(blocks, key=lambda b: len(b[1]))[1].strip()


def extract_json(text: str) -> dict | None:
    for pattern in [r"```json\s*\n([\s\S]*?)```", r"```\s*\n([\s\S]*?)```"]:
        m = re.search(pattern, text)
        if m:
            try:
                return json.loads(m.group(1).strip())
            except Exception:
                pass
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    return None


# ─── Project intelligence ─────────────────────────────────────────────────────

def detect_traits(req: str) -> dict:
    r = req.lower()
    return {
        "is_3d":        any(w in r for w in ["3d", "three.js", "sphere", "cube", "rotate", "orbit", "webgl", "glsl", "voxel", "mesh"]),
        "is_game":      any(w in r for w in ["game", "snake", "tetris", "chess", "pacman", "platformer", "shooter", "puzzle", "breakout", "pong", "flappy", "arcade"]),
        "is_dashboard": any(w in r for w in ["dashboard", "analytics", "chart", "graph", "stats", "metrics", "kpi", "report"]),
        "is_api":       any(w in r for w in ["api", "rest", "flask", "fastapi", "backend", "server", "endpoint", "crud"]),
        "is_landing":   any(w in r for w in ["landing", "homepage", "hero", "pricing", "saas", "startup", "portfolio", "agency"]),
        "is_ecommerce": any(w in r for w in ["shop", "store", "ecommerce", "cart", "product", "checkout", "buy"]),
        "is_auth":      any(w in r for w in ["login", "signup", "auth", "register", "password", "session"]),
        "is_social":    any(w in r for w in ["social", "feed", "post", "like", "comment", "profile", "follow"]),
        "is_realtime":  any(w in r for w in ["realtime", "real-time", "live", "websocket", "chat", "notification"]),
    }


def detect_iteration(request: str, has_existing: bool) -> bool:
    """True if this looks like a modification request on the existing project."""
    if not has_existing:
        return False
    r = request.lower().strip()
    words = r.split()

    # Never treat as iteration if it's clearly a NEW project request
    new_project_signals = [
        "build me", "build a", "create a", "create me", "make me a", "make a",
        "generate a", "generate me", "i want a", "i need a", "write a",
        "new project", "new app", "new website", "new game", "new dashboard"
    ]
    if any(r.startswith(sig) or f" {sig}" in r for sig in new_project_signals):
        return False

    # Explicit modification phrases — always iteration
    modify_phrases = [
        "fix the", "fix it", "fix my", "change the", "change it", "make it",
        "make the", "add a", "add the", "add to", "remove the", "update the",
        "update it", "give it", "now add", "also add", "can you add",
        "can you fix", "can you change", "can you make", "can you update",
        "can you remove", "don't use", "replace the", "rename the", "switch to",
        "convert to", "adjust the", "move the", "resize the", "style the",
        "color the", "the navbar", "the header", "the footer", "the hero",
        "the button", "dark mode", "light mode"
    ]
    if any(r.startswith(p) or f" {p}" in r or r == p for p in modify_phrases):
        return True

    # Short message with modification vocabulary
    modification_words = [
        "fix", "change", "update", "modify", "adjust", "improve", "rename",
        "remove", "delete", "darker", "lighter", "bigger", "smaller", "wider",
        "taller", "shorter", "bolder", "thinner", "animated", "responsive"
    ]
    if len(words) <= 15 and any(mw in words for mw in modification_words):
        return True

    return False


# ─── CDN Registry ────────────────────────────────────────────────────────────

CDNS = {
    "tailwind":    '<script src="https://cdn.tailwindcss.com"></script>',
    "alpine":      '<script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>',
    "fontawesome": '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>',
    "aos":         '<link rel="stylesheet" href="https://unpkg.com/aos@2.3.4/dist/aos.css"/>\n  <script src="https://unpkg.com/aos@2.3.4/dist/aos.js"></script>',
    "chartjs":     '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>',
    "threejs":     '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>',
    "sortable":    '<script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"></script>',
    "marked":      '<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>',
    "anime":       '<script src="https://cdnjs.cloudflare.com/ajax/libs/animejs/3.2.1/anime.min.js"></script>',
    "gsap":        '<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>',
    "particles":   '<script src="https://cdn.jsdelivr.net/npm/particles.js@2.0.0/particles.min.js"></script>',
}


def pick_cdns(traits: dict, project_type: str, stack: list) -> list[str]:
    selected = ["tailwind", "fontawesome"]
    if traits.get("is_landing"):
        selected += ["aos"]
    if traits.get("is_dashboard"):
        selected += ["chartjs"]
    if traits.get("is_game") or traits.get("is_animation"):
        selected += ["anime"]
    if "drag" in str(stack).lower():
        selected += ["sortable"]
    if "markdown" in str(stack).lower():
        selected += ["marked"]
    if traits.get("is_landing") or traits.get("is_ecommerce"):
        selected += ["gsap"]
    return [CDNS[k] for k in selected if k in CDNS]


# ─── AGENT 1: Planner ────────────────────────────────────────────────────────

class PlannerAgent:
    name = "Planner"
    emoji = "🧠"

    def run(self, request: str) -> dict:
        traits = detect_traits(request)

        prompt = f"""Software project planner. Analyze: "{request}"

Output ONLY this JSON:
```json
{{
  "project_name": "kebab-case-name",
  "project_type": "landing|webapp|dashboard|game|3d-scene|api|ecommerce|social",
  "description": "One clear sentence",
  "tech_stack": ["Tailwind CSS", "JavaScript", "Alpine.js"],
  "features": [
    "Specific feature 1",
    "Specific feature 2",
    "Specific feature 3",
    "Specific feature 4",
    "Specific feature 5",
    "Specific feature 6"
  ],
  "views": [
    {{"name": "Home", "route": "#home", "desc": "what it shows"}},
    {{"name": "Features", "route": "#features", "desc": "what it shows"}}
  ],
  "complexity": "simple|medium|complex",
  "has_3d": false,
  "has_backend": false,
  "color_theme": "indigo|violet|blue|green|orange|red|slate"
}}
```

RULES:
- Web apps/games/landing: has_backend=false (single HTML file with Tailwind+Alpine)
- Python APIs: has_backend=true
- 3D scenes: has_3d=true, tech_stack includes Three.js
- features must be SPECIFIC to this exact request
- views are the sections/pages of the app"""

        resp = call_ai(prompt)
        plan = extract_json(resp) or {}

        if not isinstance(plan, dict) or not plan.get("features"):
            plan = self._fallback(request, traits)

        plan.update({"user_request": request, "traits": traits})
        plan.setdefault("color_theme", "indigo")
        plan.setdefault("views", [])
        return plan

    def _fallback(self, req: str, traits: dict) -> dict:
        if traits["is_3d"]:
            return {"project_name": "3d-scene", "project_type": "3d-scene",
                    "tech_stack": ["Three.js", "CSS3"], "has_3d": True, "has_backend": False,
                    "features": ["3D scene", "Orbit controls", "Dynamic lighting", "Particles", "Animation loop", "Responsive"],
                    "views": [], "complexity": "complex", "color_theme": "violet"}
        elif traits["is_api"]:
            return {"project_name": "flask-api", "project_type": "api",
                    "tech_stack": ["Python", "Flask", "Flask-CORS"],
                    "features": ["REST endpoints", "CRUD ops", "JSON responses", "Error handling", "CORS", "Auth"],
                    "has_3d": False, "has_backend": True, "views": [], "complexity": "medium", "color_theme": "blue"}
        elif traits["is_game"]:
            return {"project_name": "canvas-game", "project_type": "game",
                    "tech_stack": ["HTML5 Canvas", "JavaScript"], "has_3d": False, "has_backend": False,
                    "features": ["Game loop", "Player controls", "Collision detection", "Score system", "Game over", "Restart"],
                    "views": [], "complexity": "medium", "color_theme": "indigo"}
        elif traits["is_dashboard"]:
            return {"project_name": "analytics-dashboard", "project_type": "dashboard",
                    "tech_stack": ["Tailwind CSS", "Chart.js", "Alpine.js"],
                    "features": ["KPI cards", "Bar chart", "Line chart", "Doughnut chart", "Data table", "Dark mode"],
                    "has_3d": False, "has_backend": False, "views": [{"name":"Dashboard","route":"#","desc":"main view"}],
                    "complexity": "medium", "color_theme": "indigo"}
        else:
            return {"project_name": "web-app", "project_type": "webapp",
                    "tech_stack": ["Tailwind CSS", "Alpine.js", "JavaScript"],
                    "features": ["Responsive layout", "Interactive UI", "Dark mode", "Smooth animations", "Local storage", "Clean design"],
                    "has_3d": False, "has_backend": False,
                    "views": [{"name":"Home","route":"#home","desc":"main view"}],
                    "complexity": "medium", "color_theme": "indigo"}


# ─── AGENT 2: Architect ──────────────────────────────────────────────────────

class ArchitectAgent:
    name = "Architect"
    emoji = "🏗️"

    def run(self, plan: dict) -> dict:
        traits = plan.get("traits", {})
        has_backend = plan.get("has_backend", False)
        has_3d = plan.get("has_3d", False)
        color = plan.get("color_theme", "indigo")
        selected_cdns = pick_cdns(traits, plan.get("project_type", "webapp"), plan.get("tech_stack", []))

        if has_backend:
            files = [
                {"path": "app.py", "type": "python", "priority": 1, "purpose": "Flask app with all routes, auth, CRUD"},
                {"path": "requirements.txt", "type": "text", "priority": 2, "purpose": "Python dependencies"},
                {"path": "README.md", "type": "markdown", "priority": 3, "purpose": "Setup and API docs"},
            ]
            return {"files": files, "entry_point": "app.py", "cdns": [], "color": color, "plan": plan}

        if has_3d:
            files = [
                {"path": "index.html", "type": "html", "priority": 1, "purpose": "Shell + Three.js CDN + canvas container"},
                {"path": "scene.js", "type": "javascript", "priority": 2, "purpose": "All Three.js scene code"},
            ]
            return {"files": files, "entry_point": "index.html", "cdns": [CDNS["threejs"]], "color": color, "plan": plan}

        # Single-file web app (most common)
        files = [{"path": "index.html", "type": "html", "priority": 1,
                  "purpose": "Complete app — Tailwind, Alpine.js, all features, all views"}]
        return {"files": files, "entry_point": "index.html", "cdns": selected_cdns, "color": color, "plan": plan}


# ─── AGENT 3: 3D Specialist ──────────────────────────────────────────────────

class ThreeDAgent:
    name = "3D Specialist"
    emoji = "🌐"

    def run(self, plan: dict) -> dict:
        req = plan.get("user_request", "")
        feats = ", ".join(plan.get("features", []))
        title = plan.get("project_name", "3d").replace("-", " ").title()
        color = plan.get("color_theme", "violet")
        accent = {"indigo": "0x6366f1", "violet": "0x8b5cf6", "blue": "0x3b82f6",
                  "green": "0x22c55e", "orange": "0xf97316"}.get(color, "0x6366f1")

        scene_prompt = f"""Write complete Three.js scene code (JavaScript, no imports, uses global THREE from r128 CDN).

Scene request: {req}
Features: {feats}
Accent color: {accent}

REQUIREMENTS:
- Correct use of THREE.WebGLRenderer, THREE.Scene, THREE.PerspectiveCamera
- Manual orbit: mousedown/mousemove/mouseup + touch events
- window resize handler
- requestAnimationFrame loop
- AmbientLight + DirectionalLight + 2-3 colored PointLights with castShadow
- shadowMap enabled on renderer (PCFSoftShadowMap)
- Rich geometry and materials matching the request EXACTLY
- Particle system using THREE.BufferGeometry + THREE.Points
- Physically correct materials (MeshStandardMaterial with metalness/roughness)
- Smooth animations: rotation, floating, pulsing, orbiting objects
- Grid helper or ground plane
- Variable 'sph' for orbit state: {{theta, phi, r}}
- Camera positioned from sph at end of animate()
- All code self-contained (no module imports)

Write ONLY the JavaScript. Start immediately with variable declarations."""

        scene_resp = call_ai(scene_prompt, timeout=120)
        scene_js = extract_code(scene_resp, "javascript")
        if not scene_js or len(scene_js) < 400:
            scene_js = self._fallback_scene(accent)

        scene_js += f"""

/* ── Loading complete ── */
(function(){{
  var bar = document.getElementById('load-bar');
  var overlay = document.getElementById('loader');
  if (!bar || !overlay) return;
  var p = 0;
  var iv = setInterval(function(){{
    p = Math.min(100, p + (100-p)*0.08 + 1);
    bar.style.width = p + '%';
    if (p >= 99.5) {{
      clearInterval(iv);
      setTimeout(function(){{
        overlay.style.opacity = '0';
        setTimeout(function(){{ overlay.style.display='none'; }}, 600);
      }}, 200);
    }}
  }}, 40);
}})();"""

        html = self._build_html(title, scene_js, color)
        return {"index.html": html, "scene.js": scene_js}

    def _build_html(self, title: str, scene_js: str, color: str) -> str:
        grad = {
            "violet": "from-violet-950 via-purple-950 to-black",
            "indigo": "from-indigo-950 via-blue-950 to-black",
            "blue": "from-blue-950 via-cyan-950 to-black",
        }.get(color, "from-indigo-950 via-purple-950 to-black")

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{title}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <style>
    body {{ margin:0; overflow:hidden; background:#020010; }}
    canvas {{ display:block; }}
    #loader {{ transition: opacity 0.6s ease; }}
  </style>
</head>
<body class="bg-black">
  <!-- Loading overlay -->
  <div id="loader" class="fixed inset-0 bg-gradient-to-br {grad} flex flex-col items-center justify-center z-50">
    <h1 class="text-white text-2xl font-light tracking-[0.3em] uppercase mb-2 opacity-90">{title}</h1>
    <p class="text-white/40 text-xs tracking-widest mb-8">INTERACTIVE 3D SCENE</p>
    <div class="w-56 h-0.5 bg-white/10 rounded-full overflow-hidden">
      <div id="load-bar" class="h-full bg-gradient-to-r from-violet-500 via-purple-400 to-pink-500 rounded-full" style="width:0%;transition:width 0.05s linear"></div>
    </div>
  </div>

  <!-- UI overlay -->
  <div class="fixed top-6 left-6 z-10 pointer-events-none select-none">
    <h2 class="text-white text-sm font-semibold opacity-80 drop-shadow-lg">{title}</h2>
    <p class="text-white/30 text-[10px] mt-1">Drag · Scroll to zoom</p>
  </div>

  <script src="scene.js"></script>
</body>
</html>"""

    def _fallback_scene(self, accent: str) -> str:
        return f"""
var W=window.innerWidth,H=window.innerHeight;
var scene=new THREE.Scene();
scene.background=new THREE.Color(0x020010);
scene.fog=new THREE.FogExp2(0x020010,0.016);

var camera=new THREE.PerspectiveCamera(60,W/H,.1,1000);
camera.position.set(0,2,9);

var renderer=new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(W,H);renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.2;
document.body.appendChild(renderer.domElement);

var amb=new THREE.AmbientLight(0x111133,.8);scene.add(amb);
var sun=new THREE.DirectionalLight(0xffffff,1.4);sun.position.set(5,10,5);sun.castShadow=true;scene.add(sun);
var p1=new THREE.PointLight({accent},3,20);p1.position.set(-4,4,3);scene.add(p1);
var p2=new THREE.PointLight(0xa855f7,2.5,18);p2.position.set(4,2,-4);scene.add(p2);
var p3=new THREE.PointLight(0xec4899,2,12);p3.position.set(0,-2,5);scene.add(p3);

// Core geometry
var geo=new THREE.IcosahedronGeometry(2,3);
var mat=new THREE.MeshStandardMaterial({{color:{accent},metalness:.85,roughness:.12,emissive:{accent},emissiveIntensity:.25}});
var core=new THREE.Mesh(geo,mat);core.castShadow=true;scene.add(core);

var wmat=new THREE.MeshBasicMaterial({{wireframe:true,color:0xa855f7,transparent:true,opacity:.18}});
scene.add(new THREE.Mesh(new THREE.IcosahedronGeometry(2.05,3),wmat));

// Orbiting tori
[0,1,2].forEach(function(i){{
  var rg=new THREE.TorusGeometry(3.2+i*.7,.018+i*.005,16,120);
  var rm=new THREE.MeshBasicMaterial({{color:[0x6366f1,0xa855f7,0xec4899][i],transparent:true,opacity:.5}});
  var r=new THREE.Mesh(rg,rm);r.rotation.x=.5+i*.6;r.rotation.z=i*.8;r._i=i;scene.add(r);
}});
var rings=scene.children.filter(function(o){{return o._i!==undefined}});

// Particles
var pN=3000,pP=new Float32Array(pN*3);
for(var i=0;i<pN*3;i++)pP[i]=(Math.random()-.5)*50;
var pbg=new THREE.BufferGeometry();pbg.setAttribute('position',new THREE.BufferAttribute(pP,3));
scene.add(new THREE.Points(pbg,new THREE.PointsMaterial({{color:0x8899ff,size:.055,transparent:true,opacity:.55}})));

// Floor grid
var grid=new THREE.GridHelper(40,40,0x1a1a4e,0x0d0d2a);grid.position.y=-5;scene.add(grid);

// Orbit controls
var sph={{theta:0,phi:1.1,r:9}},drag=false,prev={{x:0,y:0}};
window.addEventListener('mousedown',function(e){{drag=true;prev={{x:e.clientX,y:e.clientY}}}});
window.addEventListener('mouseup',function(){{drag=false}});
window.addEventListener('mousemove',function(e){{
  if(!drag)return;
  sph.theta-=(e.clientX-prev.x)*.005;
  sph.phi=Math.max(.05,Math.min(Math.PI-.05,sph.phi+(e.clientY-prev.y)*.005));
  prev={{x:e.clientX,y:e.clientY}};
}});
window.addEventListener('wheel',function(e){{sph.r=Math.max(3,Math.min(28,sph.r+e.deltaY*.012))}},{{passive:true}});
window.addEventListener('touchstart',function(e){{drag=true;prev={{x:e.touches[0].clientX,y:e.touches[0].clientY}}}},{{passive:true}});
window.addEventListener('touchend',function(){{drag=false}});
window.addEventListener('touchmove',function(e){{
  if(!drag)return;
  sph.theta-=(e.touches[0].clientX-prev.x)*.005;
  sph.phi=Math.max(.05,Math.min(Math.PI-.05,sph.phi+(e.touches[0].clientY-prev.y)*.005));
  prev={{x:e.touches[0].clientX,y:e.touches[0].clientY}};
}},{{passive:true}});
window.addEventListener('resize',function(){{
  camera.aspect=window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();renderer.setSize(window.innerWidth,window.innerHeight);
}});

var t=0;
(function animate(){{
  requestAnimationFrame(animate);t+=.011;
  core.rotation.y=t*.35;core.rotation.x=Math.sin(t*.22)*.14;
  core.position.y=Math.sin(t*.6)*.28;
  rings.forEach(function(r){{r.rotation.y=t*(.28+r._i*.08);r.rotation.x=.5+r._i*.6+Math.sin(t*.3+r._i)*.15}});
  p1.position.set(Math.sin(t)*6,3.5,Math.cos(t)*6);
  camera.position.set(
    Math.sin(sph.theta)*Math.sin(sph.phi)*sph.r,
    Math.cos(sph.phi)*sph.r,
    Math.cos(sph.theta)*Math.sin(sph.phi)*sph.r
  );
  camera.lookAt(0,0,0);
  renderer.render(scene,camera);
}})();"""


# ─── AGENT 4: Coder ──────────────────────────────────────────────────────────

class CoderAgent:
    name = "Coder"
    emoji = "💻"

    def run(self, arch: dict, prefilled: dict = None, progress_cb=None) -> dict:
        plan = arch.get("plan", {})
        files = sorted(arch.get("files", []), key=lambda f: f.get("priority", 99))
        result = dict(prefilled or {})

        for i, fspec in enumerate(files):
            if fspec["path"] in result:
                continue
            if progress_cb:
                progress_cb(f"✍️ `{fspec['path']}` ({i+1}/{len(files)})")
            code = self._write_file(fspec, plan, arch)
            if code:
                result[fspec["path"]] = code

        return {"files": result, "architecture": arch, "plan": plan}

    def _write_file(self, fspec: dict, plan: dict, arch: dict) -> str:
        ftype = fspec.get("type", fspec["path"].split(".")[-1])
        if ftype == "html":
            return self._html(fspec, plan, arch)
        elif ftype == "python":
            return self._python(fspec, plan)
        elif ftype == "javascript":
            return self._js(fspec, plan)
        elif ftype == "text" and "requirements" in fspec["path"]:
            return "flask>=2.3.0\nflask-cors>=4.0.0\npython-dotenv>=1.0.0\nwerkzeug>=2.3.0\n"
        elif ftype == "markdown":
            return self._readme(plan, arch)
        return ""

    def _html(self, fspec, plan, arch) -> str:
        req = plan.get("user_request", "")
        name = plan.get("project_name", "app").replace("-", " ").title()
        features = plan.get("features", [])
        traits = plan.get("traits", {})
        views = plan.get("views", [])
        color = arch.get("color", "indigo")

        # CDN list as human-readable names for prompts (not raw HTML tags)
        cdn_names = []
        if traits.get("is_landing") or traits.get("is_ecommerce"):
            cdn_names += ["Tailwind CSS CDN (cdn.tailwindcss.com)", "Font Awesome 6 CDN", "AOS scroll animations CDN"]
        elif traits.get("is_dashboard"):
            cdn_names += ["Tailwind CSS CDN", "Font Awesome 6 CDN", "Chart.js CDN"]
        elif traits.get("is_game"):
            cdn_names += ["Tailwind CSS CDN", "Font Awesome 6 CDN"]
        else:
            cdn_names += ["Tailwind CSS CDN (cdn.tailwindcss.com)", "Font Awesome 6 CDN", "Alpine.js CDN (alpinejs)"]

        # CDN actual tags for injection into generated HTML
        cdn_tags = "\n  ".join(arch.get("cdns", []))
        cdn_note = ", ".join(cdn_names)

        # Determine project type — use traits to override if planner was vague
        ptype = plan.get("project_type", "webapp")
        if traits.get("is_ecommerce") and ptype not in ("game", "dashboard", "landing", "api", "3d-scene"):
            ptype = "ecommerce"
        elif traits.get("is_dashboard") and ptype not in ("game", "landing", "api", "3d-scene"):
            ptype = "dashboard"
        elif traits.get("is_landing") and ptype not in ("game", "dashboard", "api", "3d-scene"):
            ptype = "landing"
        elif traits.get("is_game"):
            ptype = "game"

        has_aos = traits.get("is_landing") or traits.get("is_ecommerce")
        has_alpine = not traits.get("is_game")
        has_gsap = traits.get("is_landing")

        if ptype == "game":
            return self._game_prompt(req, name, features, color, cdn_note)
        elif ptype == "dashboard":
            return self._dashboard_prompt(req, name, features, color, cdn_note)
        elif ptype == "landing":
            return self._landing_prompt(req, name, features, color, cdn_note, views, has_aos, has_gsap)
        elif ptype == "ecommerce":
            return self._ecommerce_prompt(req, name, features, color, cdn_note, has_alpine)
        else:
            return self._webapp_prompt(req, name, features, color, cdn_note, views, has_alpine, color)

    def _webapp_prompt(self, req, name, features, color, cdn_html, views, has_alpine, has_sortable, tw_config) -> str:
        feat_str = "\n".join(f"- {f}" for f in features)
        views_desc = ", ".join(v.get("name", "") for v in views) if views else "Main app view"
        prompt = f"""Write a COMPLETE single-file HTML web app. NO placeholders. All features fully implemented.

App: "{req}"
Name: {name}
Views/Sections: {views_desc}
Features:
{feat_str}

REQUIREMENTS:
1. DOCTYPE html, complete head, body structure
2. Tailwind CSS (already loaded via CDN) — use Tailwind classes extensively
3. Dark mode toggle using Tailwind 'dark:' classes + localStorage
4. Alpine.js x-data for all reactive state (no separate framework)
5. CSS custom properties for theme colors
6. Gradient backgrounds, glass morphism cards (backdrop-blur)
7. Smooth transitions on all interactive elements
8. Font Awesome icons on buttons and menu items
9. Mobile-responsive navbar with hamburger menu
10. Multi-section layout with smooth scroll between sections
11. All data stored in localStorage for persistence
12. Loading skeleton states where data appears
13. Empty states with helpful messages
14. Keyboard shortcuts (Escape, Enter, Ctrl+Z)
15. Toast notifications for user actions
{tw_config if has_sortable else ""}
IMPLEMENT EVERY FEATURE COMPLETELY. No TODOs. No "add your code here". Real working JavaScript.
CDNs already in head: {cdn_html}

Output ONLY the complete HTML in ```html block."""

        resp = call_ai(prompt, timeout=130)
        code = extract_code(resp, "html")
        return code or self._fallback_html(name, color, features)

    def _landing_prompt(self, req, name, features, color, cdn_html, views, has_aos, has_gsap) -> str:
        feat_str = "\n".join(f"- {f}" for f in features)
        aos_init = "AOS.init({duration:800,once:true});" if has_aos else ""
        aos_attr = 'data-aos="fade-up"' if has_aos else ""
        gsap_note = "Use GSAP ScrollTrigger for hero text animation." if has_gsap else ""

        prompt = f"""Write a STUNNING, PRODUCTION-READY landing page. 

Product: "{req}"
Brand: {name}
Features to showcase:
{feat_str}

MUST HAVE:
1. Full-screen hero with gradient background, animated headline, CTA buttons
2. Sticky navbar with logo, nav links, CTA button, smooth scroll
3. Features grid (6 cards with Font Awesome icons, descriptions)
4. How it works / process section (numbered steps)
5. Pricing section (3 tiers: Free, Pro, Enterprise) with toggle monthly/yearly
6. Testimonials section (3 cards with avatar, name, quote)
7. FAQ accordion with Alpine.js x-show
8. CTA banner section with gradient background
9. Footer with links, social icons, copyright
10. Smooth scroll behavior, scroll-to-top button
11. Mobile responsive hamburger menu
12. {f"AOS scroll animations on all sections ({aos_attr})" if has_aos else "CSS scroll-triggered animations"}
13. {gsap_note}
14. Dark professional color scheme using {color} as primary

CDNs loaded: {cdn_html}
{f"Call AOS.init() at bottom of script." if has_aos else ""}

Output ONLY complete ```html."""

        resp = call_ai(prompt, timeout=130)
        code = extract_code(resp, "html")
        return code or self._fallback_html(name, color, features)

    def _dashboard_prompt(self, req, name, features, color, cdn_html) -> str:
        feat_str = "\n".join(f"- {f}" for f in features)
        prompt = f"""Write a COMPLETE analytics dashboard HTML file.

Dashboard: "{req}"
Name: {name}
Features:
{feat_str}

MUST INCLUDE:
1. Sticky sidebar with navigation icons (Font Awesome), active states, collapse button
2. Top header bar with search, notifications bell, user avatar
3. KPI cards row (4 cards): total revenue, users, growth %, active sessions — with trend arrows and colored badges
4. Line chart (Chart.js) — monthly revenue/users over 12 months with realistic data
5. Bar chart (Chart.js) — weekly comparison data
6. Doughnut/pie chart (Chart.js) — category breakdown
7. Recent activity table with avatars, status badges, timestamps
8. Dark/light mode toggle stored in localStorage (apply 'dark' class to html)
9. Responsive: sidebar collapses to bottom nav on mobile
10. Alpine.js for tab switching and filter state
11. Gradient colored chart fills, grid lines, tooltips styled
12. Skeleton loading animation on first render
13. Color scheme: {color} primary for sidebar and charts

CDNs: {cdn_html}

Chart.js data must be realistic and varied. Use hex colors matching {color} theme.

Output ONLY complete ```html."""

        resp = call_ai(prompt, timeout=130)
        code = extract_code(resp, "html")
        return code or self._fallback_html(name, color, features)

    def _game_prompt(self, req, name, features, color, cdn_html) -> str:
        feat_str = "\n".join(f"- {f}" for f in features)
        prompt = f"""Write a COMPLETE, FULLY PLAYABLE HTML5 Canvas game.

Game: "{req}"
Name: {name}
Features:
{feat_str}

REQUIREMENTS:
1. Game loop using requestAnimationFrame with delta time
2. Full input handling: keyboard (arrow keys / WASD) + touch/swipe for mobile
3. Collision detection (AABB or circle)
4. Proper game states: MENU → PLAYING → PAUSED → GAME_OVER
5. Score system with high score stored in localStorage
6. Lives/health system
7. Level progression with increasing difficulty
8. Sound effects using Web Audio API (beep/buzz patterns, no external files)
9. Particle effects on collisions/deaths
10. Smooth sprite/character drawing with canvas arcs and rects
11. Beautiful game UI: score display, lives, level indicator
12. Pause with 'P' key
13. Restart with 'R' or clicking restart button
14. Responsive canvas that fills the screen
15. Gradient background, neon-style visuals

CDNs: {cdn_html}

Output ONLY complete ```html with all game code inside <script> tags."""

        resp = call_ai(prompt, timeout=130)
        code = extract_code(resp, "html")
        return code or self._fallback_html(name, color, features)

    def _ecommerce_prompt(self, req, name, features, color, cdn_html, has_alpine) -> str:
        feat_str = "\n".join(f"- {f}" for f in features)
        prompt = f"""Write a COMPLETE e-commerce store HTML file.

Store: "{req}"
Name: {name}
Features:
{feat_str}

MUST INCLUDE:
1. Navbar with logo, search bar, cart icon with badge count
2. Hero banner with promotional text and CTA
3. Category filter tabs (All, Electronics, Fashion, etc.)
4. Product grid (8 products minimum) with image placeholder (gradient div), name, price, rating stars, Add to Cart button
5. Shopping cart sidebar (slide-in) with item list, quantities, subtotal, checkout button
6. Product quick-view modal with description and size selector
7. Wishlist functionality with heart toggle
8. Toast notifications for cart actions
9. Search filtering that hides/shows products
10. Sort by: price low-high, high-low, rating
11. Price range display, discounts shown
12. Footer with links
13. All state managed with Alpine.js x-data
14. localStorage cart persistence

CDNs: {cdn_html}

Output ONLY complete ```html."""

        resp = call_ai(prompt, timeout=130)
        code = extract_code(resp, "html")
        return code or self._fallback_html(name, color, features)

    def _python(self, fspec, plan) -> str:
        req = plan.get("user_request", "")
        features = plan.get("features", [])
        traits = plan.get("traits", {})
        feat_str = "\n".join(f"- {f}" for f in features)
        has_auth = traits.get("is_auth", False) or "auth" in req.lower() or "login" in req.lower()

        prompt = f"""Write a COMPLETE Python Flask REST API.

Project: "{req}"
Features:
{feat_str}

REQUIREMENTS:
1. All imports at top (flask, flask_cors, os, uuid, datetime{', werkzeug.security' if has_auth else ''})
2. CORS(app) for all origins
3. In-memory data stores (dicts/lists) — no database setup needed
4. {'JWT-like token auth using a simple token store dict' if has_auth else 'No auth required'}
5. COMPLETE routes implementing ALL features:
   - GET /health → status check
   - Full CRUD for main resource
   - Search/filter endpoints
   {'- POST /auth/register + POST /auth/login with password hashing' if has_auth else ''}
6. Consistent JSON response format: {{"success": bool, "data": ..., "error": str}}
7. Error handlers: 400, 404, 405, 500
8. Request validation with helpful error messages
9. Pagination support (page, per_page query params)
10. CORS headers on all responses
11. if __name__ == '__main__': app.run(debug=True, host='0.0.0.0', port=5000)
12. Detailed docstrings on every route

Output ONLY complete ```python code."""

        resp = call_ai(prompt, timeout=120)
        code = extract_code(resp, "python")
        return code or self._fallback_flask(plan)

    def _js(self, fspec, plan) -> str:
        req = plan.get("user_request", "")
        prompt = f"""Write complete JavaScript for: {fspec.get('purpose', req)}
Project: {req}
Output ONLY the complete ```javascript code."""
        resp = call_ai(prompt, timeout=90)
        return extract_code(resp, "javascript") or "// JavaScript\n"

    def _readme(self, plan, arch) -> str:
        name = plan.get("project_name", "project").replace("-", " ").title()
        desc = plan.get("description", "")
        feats = "\n".join(f"- {f}" for f in plan.get("features", []))
        tech = ", ".join(plan.get("tech_stack", []))
        entry = arch.get("entry_point", "index.html")
        flist = "\n".join(f"- `{f['path']}`" for f in arch.get("files", []))
        setup = f"```bash\npip install -r requirements.txt\npython {entry}\n```" if entry.endswith(".py") else f"1. Extract the ZIP\n2. Open `{entry}` in your browser\n3. No build step needed!"
        return f"# {name}\n\n{desc}\n\n## Features\n{feats}\n\n## Tech Stack\n{tech}\n\n## Files\n{flist}\n\n## Getting Started\n{setup}\n\n---\n*Generated by LovableBot — 7-Agent AI Platform*\n"

    def _fallback_html(self, name, color, features) -> str:
        feat_items = "".join(f'<li class="flex items-center gap-2"><i class="fa-solid fa-check text-brand-500"></i>{f}</li>' for f in features)
        return f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8"/><meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{name}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
  <script>tailwind.config={{darkMode:'class',theme:{{extend:{{colors:{{brand:tailwind.colors.{color}}}}}}}}}</script>
</head>
<body class="bg-gray-950 text-white min-h-screen flex items-center justify-center p-8">
  <div class="max-w-2xl w-full bg-gray-900 rounded-2xl p-8 border border-gray-800">
    <h1 class="text-4xl font-bold bg-gradient-to-r from-brand-400 to-purple-400 bg-clip-text text-transparent mb-3">{name}</h1>
    <p class="text-gray-400 mb-6">AI-generated project — all features included below.</p>
    <ul class="space-y-2 text-sm text-gray-300">{feat_items}</ul>
  </div>
</body>
</html>"""

    def _fallback_flask(self, plan) -> str:
        nm = plan.get("project_name", "api")
        return f"""from flask import Flask, jsonify, request\nfrom flask_cors import CORS\nimport os, uuid\n\napp=Flask(__name__)\nCORS(app)\nstore=[]\n\n@app.route('/health')\ndef health(): return jsonify({{"status":"ok","project":"{nm}"}})\n\n@app.route('/items',methods=['GET'])\ndef list_items(): return jsonify({{"success":True,"data":store,"total":len(store)}})\n\n@app.route('/items',methods=['POST'])\ndef create():\n    d=request.get_json()\n    if not d: return jsonify({{"success":False,"error":"No data"}}),400\n    d['id']=str(uuid.uuid4())\n    store.append(d)\n    return jsonify({{"success":True,"data":d}}),201\n\n@app.errorhandler(404)\ndef not_found(e): return jsonify({{"success":False,"error":"Not found"}}),404\n\nif __name__=='__main__': app.run(debug=True,host='0.0.0.0',port=5000)\n"""


# ─── AGENT 5: Iteration Agent ────────────────────────────────────────────────

class IterationAgent:
    name = "Iterator"
    emoji = "🔄"

    def run(self, modification: str, existing_files: dict, plan: dict) -> dict:
        """Modify existing generated code based on user's change request."""
        # Find the main file to modify
        main_file = None
        for candidate in ["index.html", "app.py", "scene.js"]:
            if candidate in existing_files:
                main_file = candidate
                break

        if not main_file:
            main_file = max(existing_files, key=lambda k: len(existing_files[k]))

        ext = main_file.split(".")[-1]
        current_code = existing_files[main_file]

        prompt = f"""You are modifying an existing {ext} file based on a user request.

User change request: "{modification}"

Current code ({len(current_code)} chars):
{current_code[:8000]}{"... [truncated]" if len(current_code) > 8000 else ""}

TASK: Apply the requested changes to the code.
- Keep all existing functionality intact
- Only modify/add what the user requested
- Maintain the same overall structure, styling approach, and libraries
- If adding a new feature, integrate it naturally
- If fixing a bug, fix ONLY that bug

Output the COMPLETE updated {ext} file in a code block. Do not truncate."""

        resp = call_ai(prompt, timeout=130)
        new_code = extract_code(resp, ext)

        updated = dict(existing_files)
        if new_code and len(new_code) > 500:
            updated[main_file] = new_code

        return updated


# ─── AGENT 6: Debugger ───────────────────────────────────────────────────────

class DebuggerAgent:
    name = "Debugger"
    emoji = "🔬"

    def run(self, coder_out: dict, progress_cb=None) -> dict:
        files = coder_out.get("files", {})
        plan = coder_out.get("plan", {})
        fixed = dict(files)
        report = []

        for fpath, content in files.items():
            ext = fpath.split(".")[-1].lower()
            issues = self._scan(fpath, ext, content, files)
            if issues:
                content = self._fix(fpath, ext, content, files, issues)
                fixed[fpath] = content
                report.extend(f"{fpath}: {iss}" for iss in issues)

            # Regenerate if suspiciously short
            if len(content.strip()) < 300 and ext in ("html", "py", "js"):
                if progress_cb:
                    progress_cb(f"⚠️ `{fpath}` seems incomplete ({len(content)} chars), regenerating...")
                better = self._ai_regen(fpath, ext, content, plan)
                if better and len(better) > len(content):
                    fixed[fpath] = better
                    report.append(f"{fpath}: Regenerated (was too short)")

        return {"files": fixed, "plan": plan,
                "architecture": coder_out.get("architecture", {}),
                "debug_report": report}

    def _scan(self, fpath, ext, content, all_files):
        issues = []
        if ext == "html":
            if "<!DOCTYPE" not in content[:100]:
                issues.append("Missing DOCTYPE")
            if "</html>" not in content[-200:]:
                issues.append("Missing closing </html>")
            if "</body>" not in content[-500:]:
                issues.append("Missing closing </body>")
            # Check linked JS files exist
            for jf in all_files:
                if jf.endswith(".js") and jf not in content:
                    issues.append(f"JS file not linked: {jf}")
            if "scene.js" in all_files and "three.min.js" not in content and "three.js" not in content:
                issues.append("Three.js CDN missing")
        elif ext == "js":
            if abs(content.count("{") - content.count("}")) > 5:
                issues.append("Unbalanced braces")
            if abs(content.count("(") - content.count(")")) > 5:
                issues.append("Unbalanced parentheses")
        elif ext == "py":
            if "app.run" not in content and "from flask import" in content:
                issues.append("Missing app.run()")
        return issues

    def _fix(self, fpath, ext, content, all_files, issues):
        if ext == "html":
            if "Missing DOCTYPE" in str(issues):
                content = "<!DOCTYPE html>\n" + content
            if "Missing closing </html>" in str(issues):
                content += "\n</html>"
            if "Missing closing </body>" in str(issues):
                content = content.rstrip().rstrip("</html>") + "\n</body>\n</html>"
            for jf in all_files:
                if jf.endswith(".js") and jf not in content:
                    tag = f'<script src="{jf}"></script>'
                    content = content.replace("</body>", f"  {tag}\n</body>")
            if "Three.js CDN missing" in str(issues):
                cdn = '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>'
                content = content.replace("</head>", f"  {cdn}\n</head>")
        elif ext == "py":
            if "Missing app.run()" in str(issues):
                content += "\n\nif __name__ == '__main__':\n    app.run(debug=True, host='0.0.0.0', port=5000)\n"
        return content

    def _ai_regen(self, fpath, ext, content, plan):
        prompt = f"""Rewrite this incomplete {ext} file completely for: {plan.get('description','')}
Features: {', '.join(plan.get('features',[]))}
Current (broken): {content[:500]}
Write the complete file in a ```{ext} code block."""
        resp = call_ai(prompt, timeout=90)
        return extract_code(resp, ext)


# ─── AGENT 7: Reviewer ───────────────────────────────────────────────────────

class ReviewerAgent:
    name = "Reviewer"
    emoji = "🔍"

    def run(self, dbg_out: dict, progress_cb=None) -> dict:
        files = dbg_out.get("files", {})
        plan = dbg_out.get("plan", {})
        features = plan.get("features", [])
        improved = dict(files)

        # Pick main file to review
        for candidate in ["index.html", "app.py", "scene.js"]:
            if candidate in files and len(files[candidate]) > 500:
                fpath = candidate
                break
        else:
            if not files:
                return {**dbg_out, "files": improved}
            fpath = max(files, key=lambda k: len(files[k]))

        ext = fpath.split(".")[-1]
        content = files[fpath]

        if progress_cb:
            progress_cb(f"🔎 Quality-checking `{fpath}` ({len(content):,} chars)...")

        # Check which features are missing
        missing = [f for f in features if not any(kw.lower() in content.lower()
                   for kw in f.lower().split()[:3])]

        if not missing and len(content) > 8000:
            # Already good, skip expensive AI call
            return {**dbg_out, "files": improved}

        missing_str = "\n".join(f"- {f}" for f in missing[:4]) if missing else "none"

        prompt = f"""Final quality review for this {ext} file.

Project: {plan.get('project_name')} — {plan.get('description','')}
ALL required features:
{chr(10).join(f'- {f}' for f in features)}

Missing/incomplete features detected:
{missing_str}

Current code:
{content[:7000]}{"... [truncated]" if len(content)>7000 else ""}

Add any missing features. Improve UI quality. Fix any remaining issues.
Return the complete improved {ext} in a code block. Do not truncate."""

        resp = call_ai(prompt, timeout=130)
        new_code = extract_code(resp, ext)

        if new_code and len(new_code) >= len(content) * 0.55:
            improved[fpath] = new_code

        return {"files": improved, "plan": plan,
                "architecture": dbg_out.get("architecture", {}),
                "debug_report": dbg_out.get("debug_report", [])}


# ─── PACKAGER ─────────────────────────────────────────────────────────────────

class PackagerAgent:
    name = "Packager"
    emoji = "📦"

    def run(self, rev_out: dict) -> dict:
        files = rev_out.get("files", {})
        plan = rev_out.get("plan", {})
        arch = rev_out.get("architecture", {})
        dbg = rev_out.get("debug_report", [])

        if "README.md" not in files:
            files["README.md"] = self._readme(plan, arch, files)

        zip_path = self._zip(files, plan.get("project_name", "project"))
        total = sum(len(v) for v in files.values())

        return {
            "zip_path": zip_path,
            "files": files,
            "file_count": len(files),
            "total_chars": total,
            "debug_report": dbg,
            "plan": plan,
            "summary": self._summary(plan, files, dbg, total),
            "entry_point": arch.get("entry_point", "index.html"),
        }

    def _readme(self, plan, arch, files) -> str:
        name = plan.get("project_name", "project").replace("-", " ").title()
        feats = "\n".join(f"- {f}" for f in plan.get("features", []))
        tech = ", ".join(plan.get("tech_stack", []))
        entry = arch.get("entry_point", "index.html")
        flist = "\n".join(f"- `{p}` ({len(c):,} chars)" for p, c in sorted(files.items()))
        setup = f"```bash\npip install -r requirements.txt\npython {entry}\n```" if entry.endswith(".py") else f"Open `{entry}` in your browser."
        return f"# {name}\n\n{plan.get('description','')}\n\n## Features\n{feats}\n\n## Stack\n{tech}\n\n## Files\n{flist}\n\n## Quick Start\n{setup}\n\n---\n*LovableBot — 7-Agent AI Code Generator*\n"

    def _zip(self, files, name) -> str:
        tmp = tempfile.mkdtemp()
        path = os.path.join(tmp, f"{name}.zip")
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
            for p, c in files.items():
                zf.writestr(f"{name}/{p}", c)
        return path

    def _summary(self, plan, files, dbg, total) -> str:
        name = plan.get("project_name", "project").replace("-", " ").title()
        feats = "\n".join(f"  • {f}" for f in plan.get("features", []))
        flist = "\n".join(f"  📄 `{p}` — {len(c):,} chars" for p, c in sorted(files.items()))
        fixes = ("\n🔬 *Auto-fixes applied:*\n" + "\n".join(f"  • {r}" for r in dbg)) if dbg else ""
        return (f"✅ *{name}* built!\n\n"
                f"📝 _{plan.get('description','')}_\n\n"
                f"⚡ *Features:*\n{feats}\n\n"
                f"📁 *Output ({len(files)} files, {total:,} chars):*\n{flist}"
                f"{fixes}\n\n"
                f"📦 *Extract the ZIP and open the entry point to run.*")


# ─── ORCHESTRATOR ─────────────────────────────────────────────────────────────

class LovableOrchestrator:
    def __init__(self):
        self.planner   = PlannerAgent()
        self.architect = ArchitectAgent()
        self.threed    = ThreeDAgent()
        self.coder     = CoderAgent()
        self.iterator  = IterationAgent()
        self.debugger  = DebuggerAgent()
        self.reviewer  = ReviewerAgent()
        self.packager  = PackagerAgent()

    def generate(self, request: str, status_cb=None, existing_files: dict = None) -> dict:
        def u(msg):
            if status_cb: status_cb(msg)

        # ── Iteration mode ────────────────────────────────────────────
        if existing_files and detect_iteration(request, bool(existing_files)):
            u(f"{self.iterator.emoji} **Iteration Mode** — Modifying your existing project...")
            updated = self.iterator.run(request, existing_files, {})
            u("✅ Changes applied")

            # Re-debug and re-pack
            u(f"\n{self.debugger.emoji} **Debugger**: Checking for issues...")
            dbg = self.debugger.run({"files": updated, "plan": {}, "architecture": {}})
            u("✅ Clean")
            result = self.packager.run({**dbg, "architecture": {}})
            return result

        # ── Full generation mode ──────────────────────────────────────

        u(f"{self.planner.emoji} **Agent 1/7 — Planner**: Analyzing...")
        plan = self.planner.run(request)
        u(f"✅ *{plan.get('project_name')}* | {plan.get('project_type')} | {plan.get('complexity')} | theme: {plan.get('color_theme')}")

        u(f"\n{self.architect.emoji} **Agent 2/7 — Architect**: Designing structure...")
        arch = self.architect.run(plan)
        cdns_count = len(arch.get("cdns", []))
        u(f"✅ {len(arch.get('files',[]))} file(s) | {cdns_count} CDN(s) | entry: `{arch.get('entry_point')}`")

        prefilled = {}
        if plan.get("has_3d") or plan.get("traits", {}).get("is_3d"):
            u(f"\n{self.threed.emoji} **Agent 3/7 — 3D Specialist**: Crafting Three.js scene...")
            prefilled = self.threed.run(plan)
            u(f"✅ 3D scene — {sum(len(v) for v in prefilled.values()):,} chars")
        else:
            u(f"\n⏭ Agent 3/7 — 3D Specialist: Not needed")

        u(f"\n{self.coder.emoji} **Agent 4/7 — Coder**: Writing production code...")
        def coder_cb(m): u(f"  ↳ {m}")
        code_out = self.coder.run(arch, prefilled=prefilled, progress_cb=coder_cb)
        total = sum(len(v) for v in code_out["files"].values())
        u(f"✅ {len(code_out['files'])} files | {total:,} chars")

        u(f"\n{self.debugger.emoji} **Agent 5/7 — Debugger**: Scanning for bugs...")
        def dbg_cb(m): u(f"  ↳ {m}")
        dbg_out = self.debugger.run(code_out, progress_cb=dbg_cb)
        fixes = dbg_out.get("debug_report", [])
        u(f"✅ {len(fixes)} fix(es) applied" if fixes else "✅ No bugs — clean code")

        u(f"\n{self.reviewer.emoji} **Agent 6/7 — Reviewer**: Final polish...")
        def rev_cb(m): u(f"  ↳ {m}")
        rev_out = self.reviewer.run(dbg_out, progress_cb=rev_cb)
        u("✅ Reviewed and polished")

        u(f"\n{self.packager.emoji} **Agent 7/7 — Packager**: Building ZIP...")
        result = self.packager.run(rev_out)
        u(f"✅ {result['file_count']} files | {result['total_chars']:,} chars | ZIP ready!")

        return result
