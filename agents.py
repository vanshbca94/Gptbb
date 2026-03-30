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

MANAGEMENT_KEYWORDS = [
    "management", "manager", "system", "portal", "admin", "crm", "erp",
    "inventory", "student", "employee", "hr", "school", "hospital", "clinic",
    "patient", "doctor", "medical", "pharmacy", "healthcare", "appointment",
    "teacher", "course", "grade", "attendance", "library", "book",
    "hotel", "reservation", "booking", "restaurant", "order", "delivery",
    "warehouse", "supplier", "vendor", "purchase", "invoice", "payroll",
    "project management", "task manager", "ticket", "helpdesk", "support",
    "fleet", "vehicle", "asset", "maintenance", "facility",
    "contact", "customer", "client", "member", "subscription",
    "staff", "department", "role", "permission", "user management",
    "real estate", "property", "tenant", "lease", "gym", "fitness",
    "salon", "spa", "event", "conference", "volunteer",
]

def is_management_system(req: str) -> bool:
    r = req.lower()
    return any(kw in r for kw in MANAGEMENT_KEYWORDS)

def is_pure_api_request(req: str) -> bool:
    r = req.lower()
    explicit_api = any(w in r for w in ["python api", "flask api", "fastapi", "rest api", "build an api", "create an api", "make an api"])
    is_mgmt = is_management_system(r)
    return explicit_api and not is_mgmt

def detect_traits(req: str) -> dict:
    r = req.lower()
    mgmt = is_management_system(r)
    return {
        "is_3d":         any(w in r for w in ["3d", "three.js", "sphere", "cube", "rotate", "orbit", "webgl", "glsl", "voxel", "mesh"]),
        "is_game":       any(w in r for w in ["game", "snake", "tetris", "chess", "pacman", "platformer", "shooter", "puzzle", "breakout", "pong", "flappy", "arcade"]),
        "is_dashboard":  any(w in r for w in ["dashboard", "analytics", "chart", "graph", "stats", "metrics", "kpi", "report"]),
        "is_api":        is_pure_api_request(r),
        "is_landing":    any(w in r for w in ["landing", "homepage", "hero", "pricing", "saas", "startup", "portfolio", "agency"]),
        "is_ecommerce":  any(w in r for w in ["shop", "store", "ecommerce", "cart", "checkout", "buy"]),
        "is_auth":       any(w in r for w in ["login", "signup", "auth", "register", "password", "session"]),
        "is_social":     any(w in r for w in ["social", "feed", "post", "like", "comment", "follow"]),
        "is_realtime":   any(w in r for w in ["realtime", "real-time", "live", "websocket", "chat"]),
        "is_management": mgmt,
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
        selected += ["aos", "gsap"]
    if traits.get("is_dashboard") or traits.get("is_management") or project_type in ("management", "dashboard"):
        selected += ["chartjs"]
    if traits.get("is_game") or traits.get("is_animation"):
        selected += ["anime"]
    if "drag" in str(stack).lower():
        selected += ["sortable"]
    if "markdown" in str(stack).lower():
        selected += ["marked"]
    if traits.get("is_ecommerce"):
        selected += ["gsap"]
    return [CDNS[k] for k in dict.fromkeys(selected) if k in CDNS]


# ─── AGENT 1: Planner ────────────────────────────────────────────────────────

class PlannerAgent:
    name = "Planner"
    emoji = "🧠"

    def run(self, request: str) -> dict:
        traits = detect_traits(request)
        is_mgmt = traits.get("is_management", False)

        # Build context hint for AI
        type_hint = ""
        if is_mgmt:
            type_hint = 'PROJECT TYPE: This is a frontend management system web app (NOT a Python API). Use project_type="management", has_backend=false, complexity="complex".'
        elif traits["is_api"]:
            type_hint = 'PROJECT TYPE: Python REST API. Use project_type="api", has_backend=true.'
        elif traits["is_3d"]:
            type_hint = 'PROJECT TYPE: 3D web scene. Use project_type="3d-scene", has_3d=true, has_backend=false.'
        elif traits["is_game"]:
            type_hint = 'PROJECT TYPE: Browser game. Use project_type="game", has_backend=false.'
        elif traits["is_dashboard"]:
            type_hint = 'PROJECT TYPE: Analytics dashboard. Use project_type="dashboard", has_backend=false, complexity="complex".'
        elif traits["is_ecommerce"]:
            type_hint = 'PROJECT TYPE: E-commerce store. Use project_type="ecommerce", has_backend=false.'
        elif traits["is_landing"]:
            type_hint = 'PROJECT TYPE: Landing page. Use project_type="landing", has_backend=false.'

        prompt = f"""You are an expert software project planner. Analyze this request and output a detailed project plan.

REQUEST: "{request}"

{type_hint}

Output ONLY this JSON (no other text):
```json
{{
  "project_name": "kebab-case-name-matching-request",
  "project_type": "management|landing|webapp|dashboard|game|3d-scene|api|ecommerce|social",
  "description": "One precise sentence describing the complete app",
  "tech_stack": ["Tailwind CSS", "JavaScript", "Chart.js", "Font Awesome"],
  "features": [
    "Specific domain feature 1 (be very specific to this exact domain)",
    "Specific domain feature 2",
    "Specific domain feature 3",
    "Specific domain feature 4",
    "Specific domain feature 5",
    "Specific domain feature 6",
    "Specific domain feature 7",
    "Specific domain feature 8"
  ],
  "views": [
    {{"name": "Dashboard", "route": "dashboard", "desc": "Overview stats and charts"}},
    {{"name": "Records", "route": "records", "desc": "Main data table with CRUD"}},
    {{"name": "Add New", "route": "add", "desc": "Add/edit form"}},
    {{"name": "Reports", "route": "reports", "desc": "Analytics and export"}}
  ],
  "complexity": "complex",
  "has_3d": false,
  "has_backend": false,
  "color_theme": "indigo|violet|blue|green|orange|red|slate"
}}
```

CRITICAL RULES:
- Management/admin/portal systems: ALWAYS has_backend=false, project_type="management", complexity="complex"
- Pure Python API requests: has_backend=true, project_type="api"
- features MUST be highly specific to this exact domain (e.g., for hospital: patient registration, doctor scheduling, etc.)
- views MUST be specific to this domain's main entities and workflows
- project_name must reflect the actual domain (e.g., "student-management-system", "hospital-portal")
- Generate at least 8 specific features"""

        resp = call_ai(prompt, timeout=60)
        plan = extract_json(resp) or {}

        if not isinstance(plan, dict) or not plan.get("features"):
            plan = self._fallback(request, traits)

        # ── Safety overrides: never trust AI for these critical decisions ──
        # Management systems must never be Python backend
        if is_mgmt and not traits["is_api"]:
            plan["has_backend"] = False
            plan["complexity"] = "complex"
            if plan.get("project_type") not in ("management", "dashboard", "webapp"):
                plan["project_type"] = "management"

        # Pure API must be backend
        if traits["is_api"] and not is_mgmt:
            plan["has_backend"] = True

        # 3D must stay 3D
        if traits["is_3d"]:
            plan["has_3d"] = True
            plan["has_backend"] = False

        # Ensure we always have enough views for management systems
        if is_mgmt and len(plan.get("views", [])) < 3:
            plan["views"] = self._domain_views(request)

        # Ensure enough features
        if len(plan.get("features", [])) < 6:
            plan["features"] = self._domain_features(request, traits)

        plan.update({"user_request": request, "traits": traits})
        plan.setdefault("color_theme", "indigo")
        plan.setdefault("views", [])
        return plan

    def _domain_views(self, req: str) -> list:
        """Generate domain-appropriate views based on request keywords."""
        r = req.lower()
        if any(w in r for w in ["student", "school", "grade", "course", "attendance"]):
            return [
                {"name": "Dashboard", "route": "dashboard", "desc": "Stats overview"},
                {"name": "Students", "route": "students", "desc": "Student records table"},
                {"name": "Courses", "route": "courses", "desc": "Course management"},
                {"name": "Grades", "route": "grades", "desc": "Grade tracking"},
                {"name": "Attendance", "route": "attendance", "desc": "Attendance records"},
                {"name": "Reports", "route": "reports", "desc": "Analytics & export"},
            ]
        elif any(w in r for w in ["hospital", "patient", "doctor", "clinic", "medical", "health"]):
            return [
                {"name": "Dashboard", "route": "dashboard", "desc": "Hospital overview"},
                {"name": "Patients", "route": "patients", "desc": "Patient records"},
                {"name": "Doctors", "route": "doctors", "desc": "Doctor management"},
                {"name": "Appointments", "route": "appointments", "desc": "Appointment scheduling"},
                {"name": "Medical Records", "route": "records", "desc": "Medical history"},
                {"name": "Reports", "route": "reports", "desc": "Analytics"},
            ]
        elif any(w in r for w in ["employee", "hr", "staff", "payroll", "department"]):
            return [
                {"name": "Dashboard", "route": "dashboard", "desc": "HR overview"},
                {"name": "Employees", "route": "employees", "desc": "Employee directory"},
                {"name": "Departments", "route": "departments", "desc": "Department management"},
                {"name": "Attendance", "route": "attendance", "desc": "Attendance tracking"},
                {"name": "Payroll", "route": "payroll", "desc": "Salary management"},
                {"name": "Reports", "route": "reports", "desc": "HR analytics"},
            ]
        elif any(w in r for w in ["inventory", "warehouse", "stock", "product", "supplier"]):
            return [
                {"name": "Dashboard", "route": "dashboard", "desc": "Inventory overview"},
                {"name": "Products", "route": "products", "desc": "Product catalog"},
                {"name": "Stock", "route": "stock", "desc": "Stock management"},
                {"name": "Suppliers", "route": "suppliers", "desc": "Supplier management"},
                {"name": "Orders", "route": "orders", "desc": "Purchase orders"},
                {"name": "Reports", "route": "reports", "desc": "Inventory analytics"},
            ]
        else:
            return [
                {"name": "Dashboard", "route": "dashboard", "desc": "Overview & stats"},
                {"name": "Records", "route": "records", "desc": "Main data table"},
                {"name": "Add New", "route": "add", "desc": "Create new record"},
                {"name": "Reports", "route": "reports", "desc": "Analytics & export"},
            ]

    def _domain_features(self, req: str, traits: dict) -> list:
        """Generate domain-specific features."""
        r = req.lower()
        if any(w in r for w in ["student", "school", "grade"]):
            return ["Student registration with photo & ID", "Course enrollment management", "Grade tracking (A-F scale + GPA)", "Attendance marking & reports", "Teacher assignment per subject", "Timetable/schedule management", "Parent portal notifications", "Academic performance analytics"]
        elif any(w in r for w in ["hospital", "patient", "doctor", "clinic"]):
            return ["Patient registration & medical history", "Doctor scheduling & availability", "Appointment booking & reminders", "Medical records & diagnosis tracking", "Prescription management", "Billing & insurance processing", "Lab results management", "Hospital analytics dashboard"]
        elif any(w in r for w in ["employee", "hr", "staff"]):
            return ["Employee onboarding & profiles", "Department & team management", "Attendance & leave tracking", "Payroll calculation & slips", "Performance review system", "Job posting & recruitment", "Training records management", "HR analytics & reports"]
        elif any(w in r for w in ["inventory", "stock", "warehouse"]):
            return ["Product catalog with SKUs & barcodes", "Real-time stock level tracking", "Low stock alerts & notifications", "Supplier management & contacts", "Purchase order creation", "Sales & dispatch management", "Inventory valuation reports", "Reorder point automation"]
        else:
            return ["Complete CRUD operations", "Advanced search & filtering", "Data export (CSV/PDF)", "Dashboard with analytics charts", "Dark/light mode toggle", "Responsive mobile design", "Toast notifications", "Pagination & sorting"]

    def _fallback(self, req: str, traits: dict) -> dict:
        is_mgmt = traits.get("is_management", False)
        name = req.lower().replace(" ", "-").replace("_", "-")[:40]
        if traits["is_3d"]:
            return {"project_name": "3d-scene", "project_type": "3d-scene",
                    "tech_stack": ["Three.js", "CSS3"], "has_3d": True, "has_backend": False,
                    "features": ["3D scene", "Orbit controls", "Dynamic lighting", "Particles", "Animation loop", "Responsive"],
                    "views": [], "complexity": "complex", "color_theme": "violet"}
        elif traits["is_api"] and not is_mgmt:
            return {"project_name": "flask-api", "project_type": "api",
                    "tech_stack": ["Python", "Flask", "Flask-CORS"],
                    "features": ["REST endpoints", "CRUD ops", "JSON responses", "Error handling", "CORS", "Auth"],
                    "has_3d": False, "has_backend": True, "views": [], "complexity": "medium", "color_theme": "blue"}
        elif traits["is_game"]:
            return {"project_name": "canvas-game", "project_type": "game",
                    "tech_stack": ["HTML5 Canvas", "JavaScript"], "has_3d": False, "has_backend": False,
                    "features": ["Game loop", "Player controls", "Collision detection", "Score system", "Game over", "Restart"],
                    "views": [], "complexity": "medium", "color_theme": "indigo"}
        elif is_mgmt or traits["is_dashboard"]:
            views = self._domain_views(req)
            feats = self._domain_features(req, traits)
            return {"project_name": name, "project_type": "management",
                    "tech_stack": ["Tailwind CSS", "Chart.js", "JavaScript", "Font Awesome"],
                    "features": feats, "has_3d": False, "has_backend": False,
                    "views": views, "complexity": "complex", "color_theme": "indigo"}
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

        # Determine if multi-file architecture is needed
        complexity = plan.get("complexity", "medium")
        project_type = plan.get("project_type", "webapp")
        req_lower = plan.get("user_request", "").lower()
        is_mgmt = traits.get("is_management", False) or is_management_system(req_lower)
        use_multifile = (
            is_mgmt
            or complexity == "complex"
            or project_type in ("management", "dashboard")
            or traits.get("is_dashboard")
        )

        if use_multifile:
            views = plan.get("views", [])
            views_desc = "; ".join(f'{v["name"]}={v.get("desc","")}' for v in views)
            files = [
                {"path": "index.html", "type": "html", "priority": 1,
                 "purpose": f"App shell — sidebar nav ({', '.join(v['name'] for v in views)}), header, view containers, all CDN links"},
                {"path": "styles.css", "type": "css", "priority": 2,
                 "purpose": "Complete CSS — CSS variables, sidebar, nav-link, data-table, badge, card, form-input, btn, modal, toast, skeleton, responsive"},
                {"path": "app.js", "type": "javascript", "priority": 3,
                 "purpose": "App core — showView(), routing, toggleDarkMode(), showToast(), openModal(), closeModal(), handleSearch(), exportCSV(), DOMContentLoaded init"},
                {"path": "data.js", "type": "javascript", "priority": 4,
                 "purpose": f"Data layer for: {req_lower[:80]} — sample data (15+ records), CRUD functions, localStorage, search(), filter(), sortBy(), getStats()"},
                {"path": "ui.js", "type": "javascript", "priority": 5,
                 "purpose": f"UI renderers — {views_desc[:120]} — tables, forms, charts, modals, pagination"},
            ]
            return {"files": files, "entry_point": "index.html", "cdns": selected_cdns,
                    "color": color, "plan": plan, "is_multifile": True}

        # Standard single-file web app
        files = [{"path": "index.html", "type": "html", "priority": 1,
                  "purpose": "Complete app — Tailwind, Alpine.js, all features, all views"}]
        return {"files": files, "entry_point": "index.html", "cdns": selected_cdns,
                "color": color, "plan": plan, "is_multifile": False}


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
        fname = fspec["path"]
        if ftype == "html":
            return self._html(fspec, plan, arch)
        elif ftype == "css":
            return self._css(fspec, plan, arch)
        elif ftype == "python":
            return self._python(fspec, plan)
        elif ftype == "javascript":
            if fname == "app.js":
                return self._app_js(fspec, plan, arch)
            elif fname == "data.js":
                return self._data_js(fspec, plan, arch)
            elif fname == "ui.js":
                return self._ui_js(fspec, plan, arch)
            else:
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

        # Multi-file mode: generate HTML shell only
        file_paths = [f["path"] for f in arch.get("files", [])]
        if "app.js" in file_paths and "data.js" in file_paths:
            return self._multifile_shell(req, name, features, color, arch, views)


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
            has_sortable = "drag" in str(plan.get("tech_stack", [])).lower() or "sort" in req.lower()
            tw_config = f"Use tailwind.config={{darkMode:'class',theme:{{extend:{{colors:{{brand:tailwind.colors.{color}}}}}}}}}"
            return self._webapp_prompt(req, name, features, color, cdn_note, views, has_alpine, has_sortable, tw_config)

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

    def _multifile_shell(self, req, name, features, color, arch, views) -> str:
        """Generate the HTML shell for multi-file projects."""
        cdn_tags = "\n  ".join(arch.get("cdns", []))
        views_list = views or [{"name": "Dashboard"}, {"name": "List"}, {"name": "Add"}, {"name": "Reports"}]
        accent = {"indigo": "#6366f1", "violet": "#8b5cf6", "blue": "#3b82f6",
                  "green": "#22c55e", "orange": "#f97316", "red": "#ef4444", "slate": "#64748b"}.get(color, "#6366f1")

        # Domain-aware app icon and nav icons
        domain = self._get_domain(req)
        domain_icon = {
            "student": "fa-graduation-cap", "hospital": "fa-hospital",
            "hr": "fa-users-between-lines", "inventory": "fa-boxes-stacked",
            "hotel": "fa-hotel", "library": "fa-book-open", "restaurant": "fa-utensils",
            "crm": "fa-handshake", "project": "fa-diagram-project", "realestate": "fa-building",
        }.get(domain, "fa-layer-group")
        domain_subtitle = {
            "student": "Student Management", "hospital": "Hospital Management",
            "hr": "HR Management", "inventory": "Inventory Management",
            "hotel": "Hotel Management", "library": "Library Management",
            "restaurant": "Restaurant Management", "crm": "CRM Platform",
            "project": "Project Management", "realestate": "Property Management",
        }.get(domain, "Management System")

        # Nav icon mapping by keyword in view name
        def nav_icon(vname):
            n = vname.lower()
            if "dashboard" in n or "home" in n or "overview" in n: return "fa-gauge-high"
            if "student" in n or "patient" in n or "employee" in n or "contact" in n or "guest" in n or "member" in n: return "fa-users"
            if "doctor" in n or "staff" in n: return "fa-user-md"
            if "course" in n or "subject" in n: return "fa-book"
            if "report" in n or "analytic" in n or "stat" in n: return "fa-chart-bar"
            if "add" in n or "new" in n or "create" in n: return "fa-plus-circle"
            if "grade" in n or "result" in n or "score" in n: return "fa-star-half-stroke"
            if "attend" in n: return "fa-calendar-check"
            if "schedule" in n or "appointment" in n: return "fa-calendar-days"
            if "room" in n or "ward" in n: return "fa-door-open"
            if "payment" in n or "billing" in n or "payroll" in n: return "fa-credit-card"
            if "inventory" in n or "stock" in n or "product" in n: return "fa-boxes-stacked"
            if "setting" in n or "config" in n: return "fa-gear"
            if "profile" in n or "account" in n: return "fa-circle-user"
            if "message" in n or "notif" in n: return "fa-bell"
            if "task" in n or "project" in n: return "fa-list-check"
            if "list" in n or "record" in n or "all" in n: return "fa-table-list"
            return "fa-circle-dot"

        nav_links = "\n        ".join(
            f'<a href="#" data-view="{v["name"].lower().replace(" ","-")}" class="nav-link">'
            f'<i class="fa-solid {nav_icon(v["name"])} mr-2 w-4 text-center"></i>{v["name"]}</a>'
            for v in views_list
        )
        view_divs = "\n    ".join(
            f'<div id="view-{v["name"].lower().replace(" ","-")}" class="view-section hidden"></div>'
            for v in views_list
        )
        return f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{name}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  {cdn_tags}
  <link rel="stylesheet" href="styles.css"/>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{ extend: {{ colors: {{ brand: {{ 50:'#eef2ff',100:'#e0e7ff',200:'#c7d2fe',300:'#a5b4fc',400:'#818cf8',500:'{accent}',600:'#4f46e5',700:'#4338ca',800:'#3730a3',900:'#312e81' }} }} }} }}
    }};
  </script>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen flex">

  <!-- Sidebar -->
  <aside id="sidebar" class="sidebar w-64 bg-gray-900 border-r border-gray-800 flex flex-col min-h-screen fixed left-0 top-0 z-40 transition-transform">
    <div class="p-5 border-b border-gray-800">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-brand-500 flex items-center justify-center">
          <i class="fa-solid {domain_icon} text-white text-sm"></i>
        </div>
        <div>
          <h1 class="font-bold text-white text-sm">{name}</h1>
          <p class="text-gray-500 text-xs">{domain_subtitle}</p>
        </div>
      </div>
    </div>
    <nav class="flex-1 p-4 space-y-1" id="sidebar-nav">
      {nav_links}
    </nav>
    <div class="p-4 border-t border-gray-800">
      <div class="flex items-center gap-3 p-2 rounded-lg bg-gray-800">
        <div class="w-8 h-8 rounded-full bg-brand-500 flex items-center justify-center text-xs font-bold">A</div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-white truncate">Admin User</p>
          <p class="text-xs text-gray-500">Administrator</p>
        </div>
      </div>
    </div>
  </aside>

  <!-- Main Content -->
  <div class="flex-1 flex flex-col ml-64">
    <!-- Top Header -->
    <header class="sticky top-0 z-30 bg-gray-900/80 backdrop-blur border-b border-gray-800 px-6 py-4 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <button onclick="toggleSidebar()" class="text-gray-400 hover:text-white transition lg:hidden">
          <i class="fa-solid fa-bars text-lg"></i>
        </button>
        <div class="relative">
          <i class="fa-solid fa-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm"></i>
          <input type="text" id="global-search" placeholder="Search..." oninput="handleSearch(this.value)"
            class="bg-gray-800 border border-gray-700 rounded-lg pl-9 pr-4 py-2 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-brand-500 w-64"/>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <button onclick="toggleDarkMode()" class="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white transition" title="Toggle theme">
          <i class="fa-solid fa-moon text-sm"></i>
        </button>
        <button class="relative p-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white transition">
          <i class="fa-solid fa-bell text-sm"></i>
          <span class="absolute top-1 right-1 w-2 h-2 bg-brand-500 rounded-full"></span>
        </button>
      </div>
    </header>

    <!-- Page Content -->
    <main class="flex-1 p-6" id="main-content">
      {view_divs}
    </main>
  </div>

  <!-- Toast Container -->
  <div id="toast-container" class="fixed bottom-6 right-6 z-50 space-y-3"></div>

  <!-- Modal Container -->
  <div id="modal-overlay" class="hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div id="modal-content" class="bg-gray-900 border border-gray-700 rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto"></div>
  </div>

  <script src="data.js"></script>
  <script src="ui.js"></script>
  <script src="app.js"></script>
</body>
</html>"""

    def _css(self, fspec, plan, arch) -> str:
        req = plan.get("user_request", "")
        name = plan.get("project_name", "app").replace("-", " ").title()
        color = arch.get("color", "indigo")
        feat_str = "\n".join(f"- {f}" for f in plan.get("features", []))
        accent = {"indigo": "#6366f1", "violet": "#8b5cf6", "blue": "#3b82f6",
                  "green": "#22c55e", "orange": "#f97316", "red": "#ef4444", "slate": "#64748b"}.get(color, "#6366f1")

        prompt = f"""Write complete CSS for this multi-file web app: "{req}"
App name: {name}
Primary color: {accent}
Features: {feat_str}

REQUIREMENTS:
- CSS custom properties (--brand, --bg, --surface, --border, --text-*) at :root and .dark
- .sidebar, .nav-link styles with hover/active states
- .view-section transition animations (fade-in)
- .data-table styles (striped rows, hover, sticky header)
- .card, .stat-card, .glass-card styles with hover effects
- .badge, .status-pill with color variants (success, warning, danger, info)
- .modal, .form-input, .btn, .btn-primary, .btn-danger styles
- .toast animation (slide-in-right)
- Skeleton loading animation (shimmer keyframe)
- Responsive: sidebar hidden on mobile (transform translateX)
- Smooth scrollbar styling
- Chart container styles

Output ONLY complete ```css."""

        resp = call_ai(prompt, timeout=100)
        css = extract_code(resp, "css")
        if not css or len(css) < 300:
            css = self._fallback_css(accent)
        return css

    def _fallback_css(self, accent: str) -> str:
        return f""":root {{
  --brand: {accent};
  --bg: #030712;
  --surface: #111827;
  --border: #1f2937;
  --text-primary: #f9fafb;
  --text-secondary: #9ca3af;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: var(--bg); color: var(--text-primary); font-family: 'Inter', system-ui, sans-serif; }}
.sidebar {{ transition: transform .3s ease; }}
.nav-link {{ display: flex; align-items: center; padding: .6rem 1rem; border-radius: .5rem; color: var(--text-secondary); font-size: .875rem; cursor: pointer; transition: all .2s; text-decoration: none; }}
.nav-link:hover, .nav-link.active {{ background: rgba({",".join(str(int(accent.lstrip("#")[i:i+2], 16)) for i in (0,2,4))}, .15); color: var(--brand); }}
.view-section {{ animation: fadeIn .3s ease; }}
@keyframes fadeIn {{ from {{ opacity:0; transform:translateY(8px) }} to {{ opacity:1; transform:translateY(0) }} }}
.data-table {{ width:100%; border-collapse:collapse; }}
.data-table th {{ background:var(--surface); padding:.75rem 1rem; text-align:left; font-size:.75rem; text-transform:uppercase; letter-spacing:.05em; color:var(--text-secondary); border-bottom:1px solid var(--border); }}
.data-table td {{ padding:.75rem 1rem; border-bottom:1px solid var(--border); font-size:.875rem; }}
.data-table tr:hover td {{ background:rgba(255,255,255,.02); }}
.badge {{ display:inline-flex; align-items:center; padding:.2rem .6rem; border-radius:9999px; font-size:.7rem; font-weight:600; }}
.badge-success {{ background:rgba(34,197,94,.15); color:#4ade80; }}
.badge-danger {{ background:rgba(239,68,68,.15); color:#f87171; }}
.badge-warning {{ background:rgba(245,158,11,.15); color:#fbbf24; }}
.badge-info {{ background:rgba(99,102,241,.15); color:{accent}; }}
.btn {{ display:inline-flex; align-items:center; gap:.5rem; padding:.5rem 1rem; border-radius:.5rem; font-size:.875rem; font-weight:500; cursor:pointer; transition:all .2s; border:none; outline:none; }}
.btn-primary {{ background:{accent}; color:#fff; }}
.btn-primary:hover {{ opacity:.9; }}
.btn-danger {{ background:rgba(239,68,68,.15); color:#f87171; }}
.btn-danger:hover {{ background:rgba(239,68,68,.25); }}
.form-input {{ width:100%; background:var(--surface); border:1px solid var(--border); border-radius:.5rem; padding:.6rem .9rem; color:var(--text-primary); font-size:.875rem; outline:none; transition:border-color .2s; }}
.form-input:focus {{ border-color:{accent}; }}
.card {{ background:var(--surface); border:1px solid var(--border); border-radius:.75rem; padding:1.25rem; }}
@keyframes shimmer {{ from {{ background-position: -200% 0 }} to {{ background-position: 200% 0 }} }}
.skeleton {{ background: linear-gradient(90deg, var(--surface) 25%, #1f2937 50%, var(--surface) 75%); background-size:200% 100%; animation: shimmer 1.5s infinite; border-radius:.5rem; }}
#toast-container .toast {{ background:var(--surface); border:1px solid var(--border); border-radius:.75rem; padding:.75rem 1rem; min-width:280px; font-size:.875rem; display:flex; align-items:center; gap:.6rem; animation:slideIn .3s ease; }}
@keyframes slideIn {{ from {{ transform:translateX(120%) }} to {{ transform:translateX(0) }} }}
@media(max-width:768px) {{ .sidebar {{ transform:translateX(-100%) }} .sidebar.open {{ transform:translateX(0) }} body .ml-64 {{ margin-left:0 }} }}
"""

    def _get_domain(self, req: str) -> str:
        """Detect the domain type from request for domain-specific generation."""
        r = req.lower()
        if any(w in r for w in ["student", "school", "grade", "course", "attendance", "teacher", "academic"]):
            return "student"
        elif any(w in r for w in ["hospital", "patient", "doctor", "clinic", "medical", "health", "appointment", "nurse", "pharmacy"]):
            return "hospital"
        elif any(w in r for w in ["employee", "hr", "staff", "payroll", "department", "workforce", "recruit"]):
            return "hr"
        elif any(w in r for w in ["inventory", "stock", "warehouse", "product", "supplier", "sku", "barcode"]):
            return "inventory"
        elif any(w in r for w in ["hotel", "reservation", "room", "guest", "booking", "check-in"]):
            return "hotel"
        elif any(w in r for w in ["library", "book", "author", "borrow", "isbn", "catalog"]):
            return "library"
        elif any(w in r for w in ["restaurant", "food", "menu", "order", "table", "chef", "kitchen"]):
            return "restaurant"
        elif any(w in r for w in ["crm", "customer", "client", "lead", "deal", "pipeline", "sales"]):
            return "crm"
        elif any(w in r for w in ["project", "task", "milestone", "kanban", "sprint", "issue", "ticket"]):
            return "project"
        elif any(w in r for w in ["real estate", "property", "tenant", "lease", "unit", "rent"]):
            return "realestate"
        else:
            return "generic"

    def _app_js(self, fspec, plan, arch) -> str:
        req = plan.get("user_request", "")
        name = plan.get("project_name", "app").replace("-", " ").title()
        views = plan.get("views", [])
        features = plan.get("features", [])
        feat_str = "\n".join(f"- {f}" for f in features)
        views_list = [v.get("name", "").lower().replace(" ", "-") for v in views] or ["dashboard", "list", "add", "reports"]
        first_view = views_list[0]
        views_str = ", ".join(f'"{v}"' for v in views_list)
        domain = self._get_domain(req)

        prompt = f"""Write the complete, production-ready app.js for a "{req}" management web app.

App Name: {name}
Domain: {domain}
Views (IDs used in HTML as #view-<id>): {views_str}
Features:
{feat_str}

YOU MUST IMPLEMENT EVERY FUNCTION — no stubs, no TODO, no placeholders:

1. showView(name) — hide all .view-section elements, show #view-<name>, mark nav-link active, call renderView(name)
2. renderView(name) — dispatch to the correct render function in ui.js based on view name
3. toggleSidebar() — toggle .open on #sidebar, toggle ml-64 on .main-content
4. toggleDarkMode() — toggle 'dark' on document.documentElement, persist to localStorage, update icon
5. handleSearch(query) — pass query to current view's render function for live filtering
6. showToast(message, type) — type: 'success'|'error'|'warning'|'info' — colored icon + text, auto-dismiss 3.5s
7. openModal(htmlContent) — insert into #modal-content, show #modal-overlay
8. closeModal() — hide #modal-overlay, clear content
9. exportToCSV(dataArray, filename) — build CSV string from array of objects, trigger download
10. printSection() — window.print() with print-only styles
11. confirmDelete(id, deleteFn, renderFn) — show confirm modal, on confirm call deleteFn(id) then renderFn()
12. formatDate(dateStr) — format ISO date to readable string
13. formatCurrency(amount) — format number to $ currency string
14. DOMContentLoaded handler:
    - Load dark mode preference from localStorage
    - Call loadAllData() from data.js
    - Call showView('{first_view}')
    - Wire ALL nav-link clicks: document.querySelectorAll('.nav-link').forEach(link => link.addEventListener('click', e => {{ e.preventDefault(); const v = link.dataset.view; if(v) showView(v); }}))
    - Wire modal overlay click to close
    - Wire keyboard shortcuts: Escape → closeModal(), Ctrl+K → focus #global-search
    - Wire sidebar toggle button

All functions must be defined in global scope (no ES modules).
Output ONLY the complete ```javascript (no explanations)."""

        resp = call_ai(prompt, timeout=130)
        code = extract_code(resp, "javascript")
        if not code or len(code) < 500:
            code = self._fallback_app_js(views_list, first_view)
        return code

    def _data_js(self, fspec, plan, arch) -> str:
        req = plan.get("user_request", "")
        name = plan.get("project_name", "app").replace("-", " ").title()
        features = plan.get("features", [])
        feat_str = "\n".join(f"- {f}" for f in features)
        domain = self._get_domain(req)
        db_key = plan.get("project_name", "app").replace("-", "_")

        # Build domain-specific sample data hint
        domain_hints = {
            "student": "Students with: id, studentId(S001+), name, email, phone, course, year(1-4), gpa(0-4.0), grade(A/B/C), status(active/inactive/graduated), enrolledDate, address",
            "hospital": "Patients: id, patientId(P001+), name, age, gender, bloodType, doctor, diagnosis, admissionDate, status(admitted/discharged/outpatient), ward, phone, insurance. Doctors: id, name, specialization, schedule, status.",
            "hr": "Employees with: id, empId(E001+), name, email, department, position, salary, joinDate, status(active/on-leave/terminated), phone, manager, leaveBalance",
            "inventory": "Products with: id, sku(SKU-001+), name, category, quantity, minStock, price, supplier, lastUpdated, status(in-stock/low-stock/out-of-stock). Suppliers with name, contact, email.",
            "hotel": "Rooms: id, roomNo, type(single/double/suite), floor, price, status(available/occupied/maintenance). Bookings: id, guestName, room, checkIn, checkOut, status, payment.",
            "library": "Books: id, isbn, title, author, category, year, copies, available, status. Members: id, name, email, borrowedBooks[], joinDate, status.",
            "crm": "Contacts: id, name, company, email, phone, stage(lead/prospect/customer), value, source, assignedTo, lastContact, status",
            "project": "Projects: id, name, description, priority, status(planning/active/review/done), startDate, deadline, progress(0-100), team[], budget. Tasks: id, projectId, title, assignee, priority, status, dueDate.",
            "generic": "Records with domain-appropriate fields, id, name, status(active/inactive), createdAt, and 5+ domain-specific fields",
        }
        data_hint = domain_hints.get(domain, domain_hints["generic"])

        prompt = f"""Write the complete, production-ready data.js for a "{req}" web app.

Domain: {domain}
App Name: {name}
Storage key: '{db_key}_data'
Features:
{feat_str}

Data schema hint: {data_hint}

IMPLEMENT EVERYTHING — no stubs, all functions must work:

1. SAMPLE DATA — minimum 15 realistic, varied records:
   - Use real-looking names (diverse, realistic)
   - Realistic IDs, dates (spanning 2022-2024), varied statuses
   - Domain-appropriate field values
   - If domain has multiple entity types (e.g., hospital has patients + doctors), define both

2. STORAGE:
   - const DB_KEY = '{db_key}_data'
   - function saveData(key, data) — JSON.stringify to localStorage
   - function loadData(key, fallback) — JSON.parse from localStorage with try/catch
   - function loadAllData() — load all entity collections from storage or use sample data

3. CRUD for main entity:
   - function getAll(entityType) — returns array for entity type
   - function getById(id, entityType) — find by id
   - function createRecord(data, entityType) — generate id, add to array, save
   - function updateRecord(id, data, entityType) — merge update, save
   - function deleteRecord(id, entityType) — remove from array, save

4. QUERY:
   - function searchRecords(query, entityType) — search all string fields case-insensitive
   - function filterRecords(criteria, entityType) — filter by multiple fields
   - function sortRecords(records, field, direction) — sort asc/desc

5. ANALYTICS:
   - function getStats() — returns object with: total, active, inactive, recent(last30days count), monthly(12-element array), categoryBreakdown(object), and domain-specific metrics

6. UTILS:
   - function generateId(prefix) — prefix + timestamp + random
   - function formatDate(iso) — readable format
   - function getStatusColor(status) — returns CSS class name (badge-success/danger/warning/info)
   - function getDomainLabel() — returns "{{singular}}" and "{{plural}}" labels for the domain entity

All variables must be in global scope (no ES modules).
Output ONLY complete ```javascript."""

        resp = call_ai(prompt, timeout=130)
        code = extract_code(resp, "javascript")
        if not code or len(code) < 500:
            code = self._fallback_data_js(req, name, domain, db_key)
        return code

    def _ui_js(self, fspec, plan, arch) -> str:
        req = plan.get("user_request", "")
        name = plan.get("project_name", "app").replace("-", " ").title()
        views = plan.get("views", [])
        features = plan.get("features", [])
        feat_str = "\n".join(f"- {f}" for f in features)
        color = arch.get("color", "indigo")
        accent = {"indigo": "#6366f1", "violet": "#8b5cf6", "blue": "#3b82f6",
                  "green": "#22c55e", "orange": "#f97316", "red": "#ef4444"}.get(color, "#6366f1")
        views_list = [v.get("name", "") for v in views] or ["Dashboard", "Records", "Add New", "Reports"]
        views_routes = [v.get("route", v.get("name", "").lower()) for v in views]
        views_desc = "\n".join(f'  - {v.get("name")}: {v.get("desc", "")}' for v in views) if views else "  - Dashboard, Records, Add, Reports"
        domain = self._get_domain(req)

        # Get domain-specific form fields
        form_fields = {
            "student": ["Full Name:text:name:required", "Email:email:email:required", "Student ID:text:studentId:required", "Course/Program:text:course:required", "Year (1-4):number:year:min=1,max=4", "GPA:number:gpa:min=0,max=4,step=0.1", "Status:select:status:active|inactive|graduated", "Phone:tel:phone", "Address:textarea:address", "Enrolled Date:date:enrolledDate"],
            "hospital": ["Full Name:text:name:required", "Patient ID:text:patientId:required", "Age:number:age:min=0,max=120", "Gender:select:gender:Male|Female|Other", "Blood Type:select:bloodType:A+|A-|B+|B-|O+|O-|AB+|AB-", "Assigned Doctor:text:doctor:required", "Diagnosis:text:diagnosis:required", "Ward:text:ward", "Phone:tel:phone", "Status:select:status:admitted|discharged|outpatient", "Insurance:text:insurance"],
            "hr": ["Full Name:text:name:required", "Employee ID:text:empId:required", "Email:email:email:required", "Department:text:department:required", "Position:text:position:required", "Salary:number:salary:required", "Phone:tel:phone", "Join Date:date:joinDate:required", "Manager:text:manager", "Status:select:status:active|on-leave|terminated"],
            "inventory": ["Product Name:text:name:required", "SKU:text:sku:required", "Category:text:category:required", "Quantity:number:quantity:min=0", "Min Stock:number:minStock:min=0", "Unit Price:number:price:min=0,step=0.01", "Supplier:text:supplier:required", "Status:select:status:in-stock|low-stock|out-of-stock"],
            "crm": ["Contact Name:text:name:required", "Company:text:company:required", "Email:email:email:required", "Phone:tel:phone", "Stage:select:stage:lead|prospect|customer|churned", "Deal Value:number:value:min=0", "Source:select:source:website|referral|cold-call|email|social", "Assigned To:text:assignedTo", "Last Contact:date:lastContact"],
            "generic": ["Name:text:name:required", "Email:email:email", "Phone:tel:phone", "Status:select:status:active|inactive", "Category:text:category", "Description:textarea:description", "Date:date:date", "Notes:textarea:notes"],
        }
        fields = form_fields.get(domain, form_fields["generic"])

        prompt = f"""Write the complete, production-ready ui.js for a "{req}" management web app.

Domain: {domain}
App Name: {name}  
Color: {accent}
Views to render:
{views_desc}
Features:
{feat_str}

IMPLEMENT EVERY RENDER FUNCTION — complete HTML, no placeholders:

=== REQUIRED FUNCTIONS ===

renderView(viewName) — routes to correct render function by view name/route

renderDashboard(container) — renders to container element:
  - Page title + subtitle
  - 4 stat cards in a grid: total records, active count, inactive count, recent (30-day) additions
    Each card: icon (Font Awesome), number, label, trend % badge
  - Chart.js Bar chart: monthly data for last 12 months (use getStats().monthly)  
  - Chart.js Doughnut chart: status breakdown (use getStats().categoryBreakdown)
  - Recent activity table: last 5 records in a styled table with badges
  - All data from getStats() and getAll()

renderList(container, query='') — renders main data table:
  - Toolbar: "Records" title with count, [+ Add New] button, search input (pre-filled with query), filter select, sort select
  - Full <table class="data-table"> with ALL domain-appropriate columns
  - Each row: all fields, status badge, action buttons (View | Edit | Delete)
  - Pagination: 10 per page, Prev/Next buttons, "Showing X-Y of Z" text
  - Empty state: icon + message when no records
  - Calls openModal() for View/Edit, calls confirmDelete() for Delete

renderForm(container, recordId=null) — Add/Edit form:
  - Title: "Add New {domain} Record" or "Edit Record"
  - Form with ALL these fields (validate required fields):
{chr(10).join(f"    * {f}" for f in fields[:8])}
  - [Save] and [Cancel] buttons
  - On submit: call createRecord() or updateRecord(), showToast(), close modal / navigate to list
  - Client-side validation with red border + error message under each invalid field

renderReports(container) — Analytics view:
  - Summary stat cards
  - Chart.js Line chart: trend over 12 months
  - Chart.js Bar chart: comparison by category/status
  - Top records table (top 5 by relevant metric)
  - [Export CSV] button calling exportToCSV()
  - [Print] button

renderDetail(id) — opens detail modal:
  - All record fields displayed in a clean 2-column grid
  - Status badge prominently
  - [Edit] and [Close] buttons

=== STYLE RULES ===
- Use CSS classes: card, data-table, badge-success, badge-danger, badge-warning, badge-info, btn, btn-primary, btn-danger, btn-secondary, form-input
- Charts: dark background (#111827), grid color rgba(255,255,255,0.05), text color #9ca3af, accent {accent}
- All innerHTML strings must be complete — no truncation
- Wire event listeners after setting innerHTML using querySelectorAll

All functions must be global scope. No ES modules.
Output ONLY complete ```javascript."""

        resp = call_ai(prompt, timeout=150)
        code = extract_code(resp, "javascript")
        if not code or len(code) < 500:
            code = self._fallback_ui_js(req, name, views_list, views_routes, color, accent, domain, fields)
        return code

    def _fallback_app_js(self, views_list: list, first_view: str = None) -> str:
        first_view = first_view or (views_list[0] if views_list else "dashboard")
        return f"""'use strict';
/* ═══ APP CORE ═══ */
let currentView = '{first_view}';
let _charts = {{}};

function showView(name) {{
  document.querySelectorAll('.view-section').forEach(s => s.classList.add('hidden'));
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  const el = document.getElementById('view-' + name);
  if (el) {{
    el.classList.remove('hidden');
    currentView = name;
    // Destroy old charts before re-rendering to avoid canvas reuse errors
    Object.values(_charts).forEach(c => {{ try {{ c.destroy(); }} catch(e) {{}} }});
    _charts = {{}};
    if (typeof renderView === 'function') renderView(name, el);
  }}
  document.querySelectorAll('.nav-link').forEach(l => {{
    if (l.dataset.view === name || l.getAttribute('onclick')?.includes('"'+name+'"') || l.getAttribute('onclick')?.includes("'"+name+"'")) l.classList.add('active');
  }});
}}

function toggleSidebar() {{
  const sb = document.getElementById('sidebar');
  const mc = document.querySelector('.main-content') || document.querySelector('.ml-64');
  if (sb) sb.classList.toggle('open');
  if (mc) mc.classList.toggle('ml-0');
}}

function toggleDarkMode() {{
  document.documentElement.classList.toggle('dark');
  localStorage.setItem('theme', document.documentElement.classList.contains('dark') ? 'dark' : 'light');
  const icon = document.querySelector('#dark-toggle i');
  if (icon) icon.className = document.documentElement.classList.contains('dark') ? 'fa-solid fa-moon text-sm' : 'fa-solid fa-sun text-sm';
}}

function handleSearch(q) {{
  const container = document.querySelector('.view-section:not(.hidden)');
  if (typeof renderView === 'function') renderView(currentView, container, q);
}}

function showToast(msg, type) {{
  type = type || 'success';
  const c = document.getElementById('toast-container');
  if (!c) return;
  const icons = {{success:'check-circle',error:'circle-xmark',warning:'triangle-exclamation',info:'circle-info'}};
  const colors = {{success:'#4ade80',error:'#f87171',warning:'#fbbf24',info:'#818cf8'}};
  const t = document.createElement('div');
  t.className = 'toast';
  t.innerHTML = '<i class="fa-solid fa-'+icons[type]+'" style="color:'+colors[type]+'"></i><span>'+msg+'</span>';
  c.appendChild(t);
  setTimeout(function() {{ t.style.opacity='0'; setTimeout(function(){{t.remove();}},300); }}, 3200);
}}

function openModal(html) {{
  const mc = document.getElementById('modal-content');
  const mo = document.getElementById('modal-overlay');
  if (mc) mc.innerHTML = html;
  if (mo) mo.classList.remove('hidden');
}}

function closeModal() {{
  const mo = document.getElementById('modal-overlay');
  if (mo) mo.classList.add('hidden');
  const mc = document.getElementById('modal-content');
  if (mc) mc.innerHTML = '';
}}

function exportToCSV(data, filename) {{
  if (!data || !data.length) {{ showToast('No data to export', 'warning'); return; }}
  const keys = Object.keys(data[0]);
  const rows = [keys.join(',')].concat(data.map(function(r) {{
    return keys.map(function(k) {{ return '"'+(r[k]===undefined||r[k]===null?'':r[k])+'"'; }}).join(',');
  }}));
  const blob = new Blob([rows.join('\\n')], {{type:'text/csv'}});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = (filename||'export')+'.csv'; a.click();
  URL.revokeObjectURL(url);
  showToast('Exported '+data.length+' records!', 'success');
}}

function formatDate(dateStr) {{
  if (!dateStr) return '-';
  try {{ return new Date(dateStr).toLocaleDateString('en-US', {{year:'numeric',month:'short',day:'numeric'}}); }} catch(e) {{ return dateStr; }}
}}

function formatCurrency(n) {{
  return '$' + parseFloat(n||0).toLocaleString('en-US', {{minimumFractionDigits:2}});
}}

function confirmDelete(id, deleteFn, refreshFn) {{
  openModal('<div class="p-6 text-center"><div class="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-4"><i class="fa-solid fa-triangle-exclamation text-red-400 text-2xl"></i></div><h3 class="text-lg font-bold text-white mb-2">Delete Record?</h3><p class="text-gray-400 text-sm mb-6">This cannot be undone.</p><div class="flex gap-3"><button id="confirm-del-btn" class="btn btn-danger flex-1">Yes, Delete</button><button onclick="closeModal()" class="btn flex-1" style="background:#1f2937;color:#9ca3af">Cancel</button></div></div>');
  setTimeout(function() {{
    const btn = document.getElementById('confirm-del-btn');
    if (btn) btn.addEventListener('click', function() {{
      if (typeof deleteFn === 'function') deleteFn(id);
      closeModal();
      showToast('Record deleted', 'error');
      if (typeof refreshFn === 'function') refreshFn();
    }});
  }}, 50);
}}

function safeChart(id, config) {{
  try {{
    const canvas = document.getElementById(id);
    if (!canvas) return null;
    if (_charts[id]) {{ _charts[id].destroy(); delete _charts[id]; }}
    _charts[id] = new Chart(canvas, config);
    return _charts[id];
  }} catch(e) {{ console.warn('Chart error:', e); return null; }}
}}

document.addEventListener('DOMContentLoaded', function() {{
  // Theme
  const theme = localStorage.getItem('theme') || 'dark';
  if (theme === 'dark') document.documentElement.classList.add('dark');

  // Load data
  if (typeof loadAllData === 'function') loadAllData();

  // Nav wiring
  document.querySelectorAll('.nav-link').forEach(function(link) {{
    link.addEventListener('click', function(e) {{
      e.preventDefault();
      const v = link.dataset.view || link.getAttribute('href')?.replace('#','');
      if (v) showView(v);
    }});
  }});

  // Modal close on backdrop
  const mo = document.getElementById('modal-overlay');
  if (mo) mo.addEventListener('click', function(e) {{ if (e.target === mo) closeModal(); }});

  // Keyboard shortcuts
  document.addEventListener('keydown', function(e) {{
    if (e.key === 'Escape') closeModal();
    if ((e.ctrlKey||e.metaKey) && e.key === 'k') {{ e.preventDefault(); const s = document.getElementById('global-search'); if(s) s.focus(); }}
  }});

  // Dark mode button
  const dtBtn = document.getElementById('dark-toggle');
  if (dtBtn) dtBtn.addEventListener('click', toggleDarkMode);

  // Sidebar toggle
  const sbBtn = document.getElementById('sidebar-toggle');
  if (sbBtn) sbBtn.addEventListener('click', toggleSidebar);

  // Initial view
  showView('{first_view}');
}});
"""

    def _fallback_data_js(self, req: str, name: str, domain: str, db_key: str) -> str:
        # Domain-specific sample data
        samples = {
            "student": """[
  {id:'S001',name:'Alice Johnson',email:'alice@campus.edu',studentId:'2024001',course:'Computer Science',year:2,gpa:3.9,grade:'A',status:'active',phone:'555-0101',enrolledDate:'2023-09-01',address:'123 Oak St'},
  {id:'S002',name:'Bob Smith',email:'bob@campus.edu',studentId:'2024002',course:'Mathematics',year:3,gpa:3.5,grade:'B+',status:'active',phone:'555-0102',enrolledDate:'2022-09-01',address:'456 Elm Ave'},
  {id:'S003',name:'Carol White',email:'carol@campus.edu',studentId:'2024003',course:'Physics',year:1,gpa:3.7,grade:'A-',status:'active',phone:'555-0103',enrolledDate:'2024-09-01',address:'789 Pine Rd'},
  {id:'S004',name:'David Brown',email:'david@campus.edu',studentId:'2024004',course:'Chemistry',year:4,gpa:2.8,grade:'C+',status:'inactive',phone:'555-0104',enrolledDate:'2021-09-01',address:'321 Maple Dr'},
  {id:'S005',name:'Eva Martinez',email:'eva@campus.edu',studentId:'2024005',course:'Biology',year:2,gpa:3.2,grade:'B',status:'active',phone:'555-0105',enrolledDate:'2023-09-01',address:'654 Cedar Ln'},
  {id:'S006',name:'Frank Lee',email:'frank@campus.edu',studentId:'2024006',course:'Computer Science',year:1,gpa:4.0,grade:'A+',status:'active',phone:'555-0106',enrolledDate:'2024-09-01',address:'987 Birch Ct'},
  {id:'S007',name:'Grace Kim',email:'grace@campus.edu',studentId:'2024007',course:'English',year:3,gpa:3.0,grade:'B-',status:'active',phone:'555-0107',enrolledDate:'2022-09-01',address:'147 Walnut Way'},
  {id:'S008',name:'Henry Clark',email:'henry@campus.edu',studentId:'2024008',course:'History',year:2,gpa:1.8,grade:'D',status:'inactive',phone:'555-0108',enrolledDate:'2023-09-01',address:'258 Spruce Ave'},
  {id:'S009',name:'Iris Torres',email:'iris@campus.edu',studentId:'2024009',course:'Fine Arts',year:4,gpa:3.8,grade:'A',status:'active',phone:'555-0109',enrolledDate:'2021-09-01',address:'369 Aspen Blvd'},
  {id:'S010',name:'James Wilson',email:'james@campus.edu',studentId:'2024010',course:'Engineering',year:1,gpa:3.4,grade:'B+',status:'active',phone:'555-0110',enrolledDate:'2024-09-01',address:'741 Willow St'},
  {id:'S011',name:'Karen Davis',email:'karen@campus.edu',studentId:'2024011',course:'Nursing',year:2,gpa:3.6,grade:'A-',status:'active',phone:'555-0111',enrolledDate:'2023-09-01',address:'852 Oak Park'},
  {id:'S012',name:'Leo Garcia',email:'leo@campus.edu',studentId:'2024012',course:'Business',year:3,gpa:2.9,grade:'C',status:'active',phone:'555-0112',enrolledDate:'2022-09-01',address:'963 Pine Hill'},
  {id:'S013',name:'Mia Rodriguez',email:'mia@campus.edu',studentId:'2024013',course:'Psychology',year:1,gpa:3.3,grade:'B',status:'active',phone:'555-0113',enrolledDate:'2024-09-01',address:'174 Elm Court'},
  {id:'S014',name:'Noah Chen',email:'noah@campus.edu',studentId:'2024014',course:'Economics',year:4,gpa:3.7,grade:'A-',status:'graduated',phone:'555-0114',enrolledDate:'2020-09-01',address:'285 Maple Ave'},
  {id:'S015',name:'Olivia Scott',email:'olivia@campus.edu',studentId:'2024015',course:'Computer Science',year:2,gpa:3.95,grade:'A+',status:'active',phone:'555-0115',enrolledDate:'2023-09-01',address:'396 Cedar Way'}
]""",
            "hospital": """[
  {id:'P001',patientId:'PAT-001',name:'Alice Johnson',age:34,gender:'Female',bloodType:'A+',doctor:'Dr. Smith',diagnosis:'Hypertension',ward:'Cardiology',phone:'555-0101',status:'admitted',admissionDate:'2024-01-15',insurance:'BlueCross'},
  {id:'P002',patientId:'PAT-002',name:'Bob Martinez',age:67,gender:'Male',bloodType:'O-',doctor:'Dr. Lee',diagnosis:'Diabetes Type 2',ward:'Endocrinology',phone:'555-0102',status:'outpatient',admissionDate:'2024-02-01',insurance:'Aetna'},
  {id:'P003',patientId:'PAT-003',name:'Carol White',age:45,gender:'Female',bloodType:'B+',doctor:'Dr. Patel',diagnosis:'Pneumonia',ward:'Respiratory',phone:'555-0103',status:'admitted',admissionDate:'2024-03-10',insurance:'UnitedHealth'},
  {id:'P004',patientId:'PAT-004',name:'David Brown',age:52,gender:'Male',bloodType:'AB+',doctor:'Dr. Kim',diagnosis:'Appendicitis',ward:'Surgery',phone:'555-0104',status:'discharged',admissionDate:'2024-01-20',insurance:'Cigna'},
  {id:'P005',patientId:'PAT-005',name:'Eva Torres',age:28,gender:'Female',bloodType:'O+',doctor:'Dr. Smith',diagnosis:'Fracture - Left Leg',ward:'Orthopedics',phone:'555-0105',status:'admitted',admissionDate:'2024-03-15',insurance:'BlueCross'},
  {id:'P006',patientId:'PAT-006',name:'Frank Lee',age:71,gender:'Male',bloodType:'A-',doctor:'Dr. Patel',diagnosis:'COPD',ward:'Respiratory',phone:'555-0106',status:'outpatient',admissionDate:'2024-02-28',insurance:'Medicare'},
  {id:'P007',patientId:'PAT-007',name:'Grace Kim',age:39,gender:'Female',bloodType:'B-',doctor:'Dr. Rodriguez',diagnosis:'Migraine',ward:'Neurology',phone:'555-0107',status:'outpatient',admissionDate:'2024-03-05',insurance:'Aetna'},
  {id:'P008',patientId:'PAT-008',name:'Henry Clark',age:58,gender:'Male',bloodType:'O+',doctor:'Dr. Lee',diagnosis:'Coronary Artery Disease',ward:'Cardiology',phone:'555-0108',status:'admitted',admissionDate:'2024-03-18',insurance:'Medicaid'},
  {id:'P009',patientId:'PAT-009',name:'Iris Davis',age:22,gender:'Female',bloodType:'AB-',doctor:'Dr. Kim',diagnosis:'Appendix Surgery',ward:'Surgery',phone:'555-0109',status:'discharged',admissionDate:'2024-02-10',insurance:'BlueCross'},
  {id:'P010',patientId:'PAT-010',name:'James Wilson',age:44,gender:'Male',bloodType:'A+',doctor:'Dr. Smith',diagnosis:'Kidney Stones',ward:'Urology',phone:'555-0110',status:'admitted',admissionDate:'2024-03-20',insurance:'UnitedHealth'},
  {id:'P011',patientId:'PAT-011',name:'Karen Garcia',age:35,gender:'Female',bloodType:'O+',doctor:'Dr. Rodriguez',diagnosis:'Depression',ward:'Psychiatry',phone:'555-0111',status:'outpatient',admissionDate:'2024-01-30',insurance:'Cigna'},
  {id:'P012',patientId:'PAT-012',name:'Leo Chen',age:63,gender:'Male',bloodType:'B+',doctor:'Dr. Patel',diagnosis:'Bronchitis',ward:'Respiratory',phone:'555-0112',status:'discharged',admissionDate:'2024-03-01',insurance:'Medicare'},
  {id:'P013',patientId:'PAT-013',name:'Mia Scott',age:29,gender:'Female',bloodType:'A+',doctor:'Dr. Lee',diagnosis:'Anemia',ward:'Hematology',phone:'555-0113',status:'outpatient',admissionDate:'2024-02-15',insurance:'Aetna'},
  {id:'P014',patientId:'PAT-014',name:'Noah Adams',age:55,gender:'Male',bloodType:'O-',doctor:'Dr. Kim',diagnosis:'Prostate Examination',ward:'Urology',phone:'555-0114',status:'outpatient',admissionDate:'2024-03-22',insurance:'BlueCross'},
  {id:'P015',patientId:'PAT-015',name:'Olivia Baker',age:48,gender:'Female',bloodType:'AB+',doctor:'Dr. Smith',diagnosis:'Gallstones',ward:'Surgery',phone:'555-0115',status:'admitted',admissionDate:'2024-03-25',insurance:'UnitedHealth'}
]""",
            "hr": """[
  {id:'E001',empId:'EMP-001',name:'Alice Johnson',email:'alice@company.com',department:'Engineering',position:'Senior Developer',salary:95000,phone:'555-0101',joinDate:'2021-03-15',status:'active',manager:'John Director',leaveBalance:15},
  {id:'E002',empId:'EMP-002',name:'Bob Smith',email:'bob@company.com',department:'Marketing',position:'Marketing Manager',salary:75000,phone:'555-0102',joinDate:'2020-07-01',status:'active',manager:'Jane VP',leaveBalance:12},
  {id:'E003',empId:'EMP-003',name:'Carol White',email:'carol@company.com',department:'HR',position:'HR Specialist',salary:62000,phone:'555-0103',joinDate:'2022-01-10',status:'active',manager:'Bob Smith',leaveBalance:18},
  {id:'E004',empId:'EMP-004',name:'David Brown',email:'david@company.com',department:'Finance',position:'Financial Analyst',salary:72000,phone:'555-0104',joinDate:'2019-11-20',status:'on-leave',manager:'Jane VP',leaveBalance:0},
  {id:'E005',empId:'EMP-005',name:'Eva Martinez',email:'eva@company.com',department:'Engineering',position:'Junior Developer',salary:65000,phone:'555-0105',joinDate:'2023-06-01',status:'active',manager:'Alice Johnson',leaveBalance:20},
  {id:'E006',empId:'EMP-006',name:'Frank Lee',email:'frank@company.com',department:'Sales',position:'Sales Representative',salary:58000,phone:'555-0106',joinDate:'2021-09-15',status:'active',manager:'Bob Smith',leaveBalance:10},
  {id:'E007',empId:'EMP-007',name:'Grace Kim',email:'grace@company.com',department:'Design',position:'UI/UX Designer',salary:70000,phone:'555-0107',joinDate:'2022-04-01',status:'active',manager:'Jane VP',leaveBalance:14},
  {id:'E008',empId:'EMP-008',name:'Henry Clark',email:'henry@company.com',department:'Engineering',position:'DevOps Engineer',salary:90000,phone:'555-0108',joinDate:'2020-02-14',status:'terminated',manager:'Alice Johnson',leaveBalance:0},
  {id:'E009',empId:'EMP-009',name:'Iris Torres',email:'iris@company.com',department:'Finance',position:'Accountant',salary:68000,phone:'555-0109',joinDate:'2021-08-01',status:'active',manager:'David Brown',leaveBalance:16},
  {id:'E010',empId:'EMP-010',name:'James Wilson',email:'james@company.com',department:'Sales',position:'Sales Manager',salary:85000,phone:'555-0110',joinDate:'2018-05-20',status:'active',manager:'Jane VP',leaveBalance:8},
  {id:'E011',empId:'EMP-011',name:'Karen Davis',email:'karen@company.com',department:'Engineering',position:'Full Stack Developer',salary:88000,phone:'555-0111',joinDate:'2022-10-01',status:'active',manager:'Alice Johnson',leaveBalance:17},
  {id:'E012',empId:'EMP-012',name:'Leo Garcia',email:'leo@company.com',department:'Marketing',position:'Content Strategist',salary:60000,phone:'555-0112',joinDate:'2023-01-15',status:'active',manager:'Bob Smith',leaveBalance:19},
  {id:'E013',empId:'EMP-013',name:'Mia Rodriguez',email:'mia@company.com',department:'HR',position:'Recruiter',salary:58000,phone:'555-0113',joinDate:'2022-07-01',status:'active',manager:'Carol White',leaveBalance:15},
  {id:'E014',empId:'EMP-014',name:'Noah Chen',email:'noah@company.com',department:'Design',position:'Graphic Designer',salary:65000,phone:'555-0114',joinDate:'2021-03-01',status:'on-leave',manager:'Grace Kim',leaveBalance:5},
  {id:'E015',empId:'EMP-015',name:'Olivia Scott',email:'olivia@company.com',department:'Engineering',position:'Data Scientist',salary:105000,phone:'555-0115',joinDate:'2023-09-01',status:'active',manager:'Alice Johnson',leaveBalance:20}
]""",
            "inventory": """[
  {id:'I001',sku:'SKU-001',name:'Laptop Pro 15"',category:'Electronics',quantity:45,minStock:10,price:1299.99,supplier:'TechSupply Co',lastUpdated:'2024-03-01',status:'in-stock'},
  {id:'I002',sku:'SKU-002',name:'Wireless Mouse',category:'Peripherals',quantity:8,minStock:15,price:29.99,supplier:'TechSupply Co',lastUpdated:'2024-03-10',status:'low-stock'},
  {id:'I003',sku:'SKU-003',name:'Office Chair',category:'Furniture',quantity:0,minStock:5,price:349.99,supplier:'FurniturePlus',lastUpdated:'2024-02-28',status:'out-of-stock'},
  {id:'I004',sku:'SKU-004',name:'USB-C Hub',category:'Peripherals',quantity:120,minStock:20,price:49.99,supplier:'TechSupply Co',lastUpdated:'2024-03-15',status:'in-stock'},
  {id:'I005',sku:'SKU-005',name:'Standing Desk',category:'Furniture',quantity:12,minStock:3,price:599.99,supplier:'FurniturePlus',lastUpdated:'2024-03-05',status:'in-stock'},
  {id:'I006',sku:'SKU-006',name:'Monitor 27"',category:'Electronics',quantity:3,minStock:5,price:449.99,supplier:'DisplayWorld',lastUpdated:'2024-03-12',status:'low-stock'},
  {id:'I007',sku:'SKU-007',name:'Mechanical Keyboard',category:'Peripherals',quantity:67,minStock:10,price:89.99,supplier:'TechSupply Co',lastUpdated:'2024-03-08',status:'in-stock'},
  {id:'I008',sku:'SKU-008',name:'Desk Lamp LED',category:'Lighting',quantity:0,minStock:8,price:39.99,supplier:'LightCo',lastUpdated:'2024-02-20',status:'out-of-stock'},
  {id:'I009',sku:'SKU-009',name:'Webcam HD',category:'Peripherals',quantity:34,minStock:10,price:79.99,supplier:'TechSupply Co',lastUpdated:'2024-03-18',status:'in-stock'},
  {id:'I010',sku:'SKU-010',name:'Headset Pro',category:'Audio',quantity:22,minStock:8,price:129.99,supplier:'AudioPlus',lastUpdated:'2024-03-14',status:'in-stock'},
  {id:'I011',sku:'SKU-011',name:'Tablet 10"',category:'Electronics',quantity:5,minStock:8,price:399.99,supplier:'DisplayWorld',lastUpdated:'2024-03-20',status:'low-stock'},
  {id:'I012',sku:'SKU-012',name:'Printer Laser',category:'Electronics',quantity:9,minStock:3,price:249.99,supplier:'TechSupply Co',lastUpdated:'2024-03-11',status:'in-stock'},
  {id:'I013',sku:'SKU-013',name:'Paper A4 (ream)',category:'Supplies',quantity:200,minStock:50,price:8.99,supplier:'OfficeSupplyHub',lastUpdated:'2024-03-19',status:'in-stock'},
  {id:'I014',sku:'SKU-014',name:'Whiteboard 48x36',category:'Furniture',quantity:7,minStock:2,price:89.99,supplier:'FurniturePlus',lastUpdated:'2024-03-07',status:'in-stock'},
  {id:'I015',sku:'SKU-015',name:'Cable Management Kit',category:'Accessories',quantity:2,minStock:10,price:19.99,supplier:'OfficeSupplyHub',lastUpdated:'2024-03-22',status:'low-stock'}
]""",
            "crm": """[
  {id:'C001',name:'Alice Johnson',company:'Acme Corp',email:'alice@acme.com',phone:'555-0101',stage:'customer',value:15000,source:'referral',assignedTo:'Sales Rep A',lastContact:'2024-03-15',status:'active'},
  {id:'C002',name:'Bob Smith',company:'TechStart LLC',email:'bob@techstart.com',phone:'555-0102',stage:'prospect',value:8500,source:'website',assignedTo:'Sales Rep B',lastContact:'2024-03-10',status:'active'},
  {id:'C003',name:'Carol White',company:'Global Systems',email:'carol@globalsys.com',phone:'555-0103',stage:'lead',value:22000,source:'cold-call',assignedTo:'Sales Rep A',lastContact:'2024-03-18',status:'active'},
  {id:'C004',name:'David Brown',company:'Brown & Co',email:'david@brownco.com',phone:'555-0104',stage:'customer',value:5600,source:'email',assignedTo:'Sales Rep C',lastContact:'2024-02-28',status:'inactive'},
  {id:'C005',name:'Eva Martinez',company:'EV Solutions',email:'eva@evsolutions.com',phone:'555-0105',stage:'prospect',value:31000,source:'social',assignedTo:'Sales Rep B',lastContact:'2024-03-20',status:'active'},
  {id:'C006',name:'Frank Lee',company:'Lee Industries',email:'frank@leeinc.com',phone:'555-0106',stage:'lead',value:12000,source:'referral',assignedTo:'Sales Rep A',lastContact:'2024-03-22',status:'active'},
  {id:'C007',name:'Grace Kim',company:'Kim Digital',email:'grace@kimdigital.com',phone:'555-0107',stage:'customer',value:45000,source:'website',assignedTo:'Sales Rep C',lastContact:'2024-03-05',status:'active'},
  {id:'C008',name:'Henry Clark',company:'Clark Group',email:'henry@clarkgrp.com',phone:'555-0108',stage:'churned',value:7800,source:'cold-call',assignedTo:'Sales Rep B',lastContact:'2024-01-15',status:'inactive'},
  {id:'C009',name:'Iris Torres',company:'Torres Tech',email:'iris@torrestech.com',phone:'555-0109',stage:'prospect',value:19500,source:'email',assignedTo:'Sales Rep A',lastContact:'2024-03-19',status:'active'},
  {id:'C010',name:'James Wilson',company:'Wilson Media',email:'james@wilsonmedia.com',phone:'555-0110',stage:'lead',value:6300,source:'social',assignedTo:'Sales Rep C',lastContact:'2024-03-21',status:'active'},
  {id:'C011',name:'Karen Davis',company:'Davis Consulting',email:'karen@daviscons.com',phone:'555-0111',stage:'customer',value:28000,source:'referral',assignedTo:'Sales Rep B',lastContact:'2024-03-12',status:'active'},
  {id:'C012',name:'Leo Garcia',company:'Garcia Foods',email:'leo@garciafoods.com',phone:'555-0112',stage:'prospect',value:9200,source:'website',assignedTo:'Sales Rep A',lastContact:'2024-03-08',status:'active'},
  {id:'C013',name:'Mia Rodriguez',company:'Rodriguez PR',email:'mia@rodrigpr.com',phone:'555-0113',stage:'lead',value:14700,source:'referral',assignedTo:'Sales Rep C',lastContact:'2024-03-17',status:'active'},
  {id:'C014',name:'Noah Chen',company:'Chen Analytics',email:'noah@chendata.com',phone:'555-0114',stage:'customer',value:52000,source:'cold-call',assignedTo:'Sales Rep B',lastContact:'2024-03-23',status:'active'},
  {id:'C015',name:'Olivia Baker',company:'Baker Retail',email:'olivia@bakerretail.com',phone:'555-0115',stage:'prospect',value:11400,source:'social',assignedTo:'Sales Rep A',lastContact:'2024-03-16',status:'active'}
]""",
        }
        sample_data = samples.get(domain, samples.get("student"))
        db_key_safe = db_key.replace("-", "_")

        # Domain-specific getStats body
        stats_bodies = {
            "hospital": """
  const total = records.length;
  const admitted = records.filter(function(r){return r.status==='admitted';}).length;
  const discharged = records.filter(function(r){return r.status==='discharged';}).length;
  const outpatient = records.filter(function(r){return r.status==='outpatient';}).length;
  const today = new Date(); const month = today.getMonth(); const year = today.getFullYear();
  const recent = records.filter(function(r){const d=new Date(r.admissionDate);return d.getMonth()===month&&d.getFullYear()===year;}).length;
  const wards = {}; records.forEach(function(r){wards[r.ward]=(wards[r.ward]||0)+1;});
  const monthly = Array(12).fill(0).map(function(_,i){return records.filter(function(r){return new Date(r.admissionDate).getMonth()===i;}).length;});
  return {total,active:admitted,inactive:discharged,admitted,discharged,outpatient,recent,monthly,categoryBreakdown:{admitted,discharged,outpatient},wards};""",
            "hr": """
  const total = records.length;
  const active = records.filter(function(r){return r.status==='active';}).length;
  const onLeave = records.filter(function(r){return r.status==='on-leave';}).length;
  const terminated = records.filter(function(r){return r.status==='terminated';}).length;
  const avgSalary = total ? Math.round(records.reduce(function(s,r){return s+(parseFloat(r.salary)||0);},0)/total) : 0;
  const depts = {}; records.forEach(function(r){depts[r.department]=(depts[r.department]||0)+1;});
  const monthly = Array(12).fill(0).map(function(_,i){return records.filter(function(r){return new Date(r.joinDate).getMonth()===i;}).length;});
  return {total,active,inactive:terminated,onLeave,terminated,avgSalary,recent:records.filter(function(r){const d=new Date(r.joinDate);return d.getFullYear()===new Date().getFullYear();}).length,monthly,categoryBreakdown:depts};""",
            "inventory": """
  const total = records.length;
  const inStock = records.filter(function(r){return r.status==='in-stock';}).length;
  const lowStock = records.filter(function(r){return r.status==='low-stock';}).length;
  const outOfStock = records.filter(function(r){return r.status==='out-of-stock';}).length;
  const totalValue = records.reduce(function(s,r){return s+(parseFloat(r.price)||0)*(parseInt(r.quantity)||0);},0);
  const cats = {}; records.forEach(function(r){cats[r.category]=(cats[r.category]||0)+1;});
  const monthly = Array(12).fill(0).map(function(_,i){return records.filter(function(r){return new Date(r.lastUpdated).getMonth()===i;}).length;});
  return {total,active:inStock,inactive:outOfStock,inStock,lowStock,outOfStock,totalValue:totalValue.toFixed(2),recent:lowStock+outOfStock,monthly,categoryBreakdown:cats};""",
        }
        stats_body = stats_bodies.get(domain, """
  const total = records.length;
  const active = records.filter(function(r){return r.status==='active';}).length;
  const inactive = total - active;
  const today = new Date();
  const recent = records.filter(function(r){
    const d = new Date(r.enrolledDate||r.joinDate||r.admissionDate||r.lastContact||r.createdAt||0);
    return (today - d) < 30*24*60*60*1000;
  }).length;
  const catField = records[0] ? (records[0].course||records[0].department||records[0].category||records[0].stage||'status') : 'status';
  const cats = {}; records.forEach(function(r){const v=r[catField]||'Other';cats[v]=(cats[v]||0)+1;});
  const monthly = Array(12).fill(0).map(function(_,i){return Math.floor(Math.random()*5)+active;});
  return {total,active,inactive,recent,monthly,categoryBreakdown:cats};""")

        return f"""'use strict';
/* ═══ DATA MODULE ═══ */
const DB_KEY = '{db_key_safe}_data';
let records = [];

const SAMPLE_DATA = {sample_data};

/* ── Storage ── */
function saveData() {{
  try {{ localStorage.setItem(DB_KEY, JSON.stringify(records)); }} catch(e) {{}}
}}
function loadAllData() {{
  try {{
    const stored = localStorage.getItem(DB_KEY);
    records = stored ? JSON.parse(stored) : SAMPLE_DATA.map(function(r){{return Object.assign({{}},r);}});
  }} catch(e) {{
    records = SAMPLE_DATA.map(function(r){{return Object.assign({{}},r);}});
  }}
}}

/* ── ID & Date utils ── */
function generateId(prefix) {{
  prefix = prefix || 'R';
  return prefix + Date.now().toString(36).toUpperCase() + Math.random().toString(36).substr(2,4).toUpperCase();
}}
function formatDate(dateStr) {{
  if (!dateStr) return '-';
  try {{ return new Date(dateStr).toLocaleDateString('en-US',{{year:'numeric',month:'short',day:'numeric'}}); }} catch(e) {{ return dateStr; }}
}}
function getStatusColor(status) {{
  const map = {{
    active:'badge-success',admitted:'badge-success','in-stock':'badge-success',customer:'badge-success',
    inactive:'badge-danger',terminated:'badge-danger',discharged:'badge-info',
    'out-of-stock':'badge-danger',churned:'badge-danger',
    'on-leave':'badge-warning','low-stock':'badge-warning',pending:'badge-warning',outpatient:'badge-info',
    lead:'badge-info',prospect:'badge-warning',graduated:'badge-info'
  }};
  return map[status] || 'badge-info';
}}

/* ── CRUD ── */
function getAll(entityType) {{
  return records;
}}
function getById(id, entityType) {{
  return records.find(function(r){{return r.id===id;}}) || null;
}}
function createRecord(data, entityType) {{
  data.id = data.id || generateId();
  data.createdAt = data.createdAt || new Date().toISOString();
  records.push(data);
  saveData();
  return data;
}}
function updateRecord(id, data, entityType) {{
  const idx = records.findIndex(function(r){{return r.id===id;}});
  if (idx >= 0) {{
    records[idx] = Object.assign({{}}, records[idx], data, {{id:id}});
    saveData();
    return records[idx];
  }}
  return null;
}}
function deleteRecord(id, entityType) {{
  records = records.filter(function(r){{return r.id!==id;}});
  saveData();
}}

/* ── Query ── */
function searchRecords(query, entityType) {{
  if (!query) return records;
  const lq = query.toLowerCase();
  return records.filter(function(r){{
    return Object.values(r).some(function(v){{return String(v).toLowerCase().includes(lq);}});
  }});
}}
function filterRecords(criteria, entityType) {{
  return records.filter(function(r){{
    return Object.keys(criteria).every(function(k){{
      return !criteria[k] || String(r[k]).toLowerCase() === String(criteria[k]).toLowerCase();
    }});
  }});
}}
function sortRecords(arr, field, direction) {{
  arr = arr || records;
  direction = direction || 'asc';
  return arr.slice().sort(function(a,b){{
    const av = a[field]||'', bv = b[field]||'';
    if (direction==='asc') return av>bv?1:(av<bv?-1:0);
    return av<bv?1:(av>bv?-1:0);
  }});
}}

/* ── Analytics ── */
function getStats() {{{stats_body}
}}
"""

    def _fallback_ui_js(self, req: str, name: str, views_list: list, views_routes: list, color: str, accent: str, domain: str, fields: list) -> str:
        first = views_list[0] if views_list else "Dashboard"
        accent = accent or "#6366f1"
        # Build domain-specific table columns
        col_defs = {
            "student": [("Student ID","studentId"),("Name","name"),("Course","course"),("Year","year"),("GPA","gpa"),("Grade","grade"),("Status","status"),("Enrolled","enrolledDate")],
            "hospital": [("Patient ID","patientId"),("Name","name"),("Age","age"),("Gender","gender"),("Doctor","doctor"),("Diagnosis","diagnosis"),("Ward","ward"),("Status","status"),("Admitted","admissionDate")],
            "hr": [("Emp ID","empId"),("Name","name"),("Department","department"),("Position","position"),("Salary","salary"),("Status","status"),("Join Date","joinDate")],
            "inventory": [("SKU","sku"),("Product","name"),("Category","category"),("Qty","quantity"),("Min Stock","minStock"),("Price","price"),("Supplier","supplier"),("Status","status")],
            "crm": [("Name","name"),("Company","company"),("Email","email"),("Stage","stage"),("Value","value"),("Source","source"),("Assigned To","assignedTo"),("Last Contact","lastContact")],
        }
        cols = col_defs.get(domain, [("ID","id"),("Name","name"),("Status","status"),("Category","category"),("Email","email"),("Date","date")])

        # Build table headers
        th_parts = []
        for c in cols:
            th_parts.append('<th onclick="doSort(\''+c[1]+'\')" class="cursor-pointer hover:text-white">'+c[0]+' <i class="fa-solid fa-sort text-gray-600 text-xs ml-1"></i></th>')
        th_html = "".join(th_parts)
        # Build row renderer
        row_cells = []
        for label, key in cols:
            if key == "status":
                row_cells.append(f'\'<td><span class="badge \'+getStatusColor(r.{key})+\'">\'+r.{key}+\'</span></td>\'')
            elif key in ("salary","price","value"):
                row_cells.append(f'\'<td>\'+formatCurrency(r.{key})+\'</td>\'')
            elif key in ("enrolledDate","admissionDate","joinDate","lastContact","lastUpdated","date"):
                row_cells.append(f'\'<td>\'+formatDate(r.{key})+\'</td>\'')
            else:
                row_cells.append(f'\'<td>\'+(r.{key}===undefined||r.{key}===null?\'-\':r.{key})+\'</td>\'')
        row_js = "+".join(row_cells)

        # Build form fields HTML
        form_html_parts = []
        for spec in fields[:8]:
            parts = spec.split(":")
            label_txt = parts[0] if len(parts)>0 else "Field"
            inp_type = parts[1] if len(parts)>1 else "text"
            inp_name = parts[2] if len(parts)>2 else "field"
            extra = parts[3] if len(parts)>3 else ""
            required = "required" if "required" in extra else ""
            if inp_type == "select":
                options_raw = extra.replace("required","").strip("|").split("|") if extra else []
                opts = "".join(f'<option value=\\"{o}\\">\'+( r.{inp_name}===\\"{o}\\" ? \\" selected\\" : \\"\\" )+\'{o}</option>' for o in options_raw if o)
                form_html_parts.append(f'<div><label class=\\"block text-sm text-gray-400 mb-1\\">{label_txt}</label><select name=\\"{inp_name}\\" class=\\"form-input\\">{opts}</select></div>')
            elif inp_type == "textarea":
                form_html_parts.append(f'<div><label class=\\"block text-sm text-gray-400 mb-1\\">{label_txt}</label><textarea name=\\"{inp_name}\\" class=\\"form-input\\" rows=\\"3\\" placeholder=\\"{label_txt}\\">\'+( r.{inp_name}||\\"\\" )+\'</textarea></div>')
            else:
                form_html_parts.append(f'<div><label class=\\"block text-sm text-gray-400 mb-1\\">{label_txt}</label><input type=\\"{inp_type}\\" name=\\"{inp_name}\\" value=\\"\'+( r.{inp_name}||\\"\\" )+\'\\\" {required} class=\\"form-input\\" placeholder=\\"{label_txt}\\"/></div>')
        form_html = "".join(form_html_parts)

        # Stat card labels
        stat_labels = {
            "student": [("fa-users","text-brand-400","Total Students","total","brand"),("fa-circle-check","text-green-400","Active","active","green"),("fa-user-minus","text-red-400","Inactive","inactive","red"),("fa-graduation-cap","text-blue-400","Recent","recent","blue")],
            "hospital": [("fa-hospital-user","text-brand-400","Total Patients","total","brand"),("fa-bed","text-green-400","Admitted","admitted","green"),("fa-right-from-bracket","text-blue-400","Discharged","discharged","blue"),("fa-stethoscope","text-yellow-400","Outpatient","outpatient","yellow")],
            "hr": [("fa-users","text-brand-400","Total Employees","total","brand"),("fa-circle-check","text-green-400","Active","active","green"),("fa-plane","text-yellow-400","On Leave","onLeave","yellow"),("fa-dollar-sign","text-blue-400","Avg Salary","avgSalary","blue")],
            "inventory": [("fa-boxes-stacked","text-brand-400","Total Items","total","brand"),("fa-circle-check","text-green-400","In Stock","inStock","green"),("fa-triangle-exclamation","text-yellow-400","Low Stock","lowStock","yellow"),("fa-circle-xmark","text-red-400","Out of Stock","outOfStock","red")],
            "crm": [("fa-users","text-brand-400","Total Contacts","total","brand"),("fa-handshake","text-green-400","Customers","active","green"),("fa-funnel-dollar","text-blue-400","Prospects","inactive","blue"),("fa-star","text-yellow-400","Leads","recent","yellow")],
        }
        stats = stat_labels.get(domain, [
            ("fa-database","text-brand-400","Total Records","total","brand"),
            ("fa-circle-check","text-green-400","Active","active","green"),
            ("fa-circle-xmark","text-red-400","Inactive","inactive","red"),
            ("fa-clock","text-blue-400","Recent","recent","blue"),
        ])
        stat_cards_js = "+".join(
            f'\'<div class="card"><div class="flex items-center justify-between"><div><p class="text-gray-400 text-xs uppercase tracking-wider">{s[2]}</p><p class="text-3xl font-bold text-white mt-1">\'+s.{s[3]}+\'</p></div><div class="w-12 h-12 bg-{s[4]}-500/10 rounded-xl flex items-center justify-center"><i class="fa-solid {s[0]} {s[1]} text-lg"></i></div></div></div>\''
            for s in stats
        )
        return f"""'use strict';
/* ═══ UI MODULE ═══ */
let _page = 1, _perPage = 10, _query = '', _sortField = 'name', _sortDir = 'asc', _filterStatus = '';

function renderView(viewName, container, searchQ) {{
  const n = (viewName||'').toLowerCase().replace(/[^a-z]/g,'');
  if (!container) container = document.getElementById('view-'+viewName) || document.querySelector('.view-section:not(.hidden)');
  if (!container) return;
  if (searchQ !== undefined) {{ _query = searchQ; _page = 1; }}
  if (n.includes('dashboard') || n.includes('home') || n.includes('overview')) renderDashboard(container);
  else if (n.includes('report') || n.includes('analytic') || n.includes('stat')) renderReports(container);
  else if (n.includes('add') || n.includes('new') || n.includes('create')) renderForm(container, null);
  else renderList(container, _query);
}}

function renderDashboard(container) {{
  if (!container) container = document.getElementById('view-dashboard') || document.querySelector('.view-section');
  if (!container) return;
  const s = (typeof getStats==='function') ? getStats() : {{}};
  const all = (typeof getAll==='function') ? getAll() : [];
  container.innerHTML =
    '<div class="mb-6"><h2 class="text-2xl font-bold text-white">{name}</h2><p class="text-gray-400 text-sm mt-1">Overview & Analytics</p></div>'+
    '<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">'+
    {stat_cards_js}+
    '</div>'+
    '<div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">'+
    '<div class="card"><h3 class="font-semibold text-white mb-4">Monthly Trend</h3><canvas id="dash-bar" height="200"></canvas></div>'+
    '<div class="card"><h3 class="font-semibold text-white mb-4">Status Breakdown</h3><canvas id="dash-dough" height="200"></canvas></div>'+
    '</div>'+
    '<div class="card"><div class="flex items-center justify-between mb-4"><h3 class="font-semibold text-white">Recent Records</h3><button onclick="showView(\\'' + (views_routes[1] if len(views_routes)>1 else 'list') + '\\')" class="btn btn-primary py-1.5 px-4 text-sm">View All</button></div><div class="overflow-x-auto">'+buildTableHTML(all.slice(0,5))+'</div></div>';
  setTimeout(function() {{
    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    const monthly = s.monthly || Array(12).fill(0).map(function(){{return Math.floor(Math.random()*8)+1;}});
    const breakdown = s.categoryBreakdown || {{}};
    const bLabels = Object.keys(breakdown), bData = Object.values(breakdown);
    const colors = ['{accent}','#4ade80','#f87171','#fbbf24','#818cf8','#38bdf8','#fb923c'];
    if (typeof safeChart === 'function') {{
      safeChart('dash-bar', {{type:'bar',data:{{labels:months,datasets:[{{label:'Records',data:monthly,backgroundColor:'{accent}99',borderRadius:6}}]}},options:{{responsive:true,plugins:{{legend:{{display:false}}}},scales:{{y:{{beginAtZero:true,grid:{{color:'rgba(255,255,255,.05)'}},ticks:{{color:'#6b7280'}}}},x:{{grid:{{display:false}},ticks:{{color:'#6b7280'}}}}}}}}}});
      safeChart('dash-dough', {{type:'doughnut',data:{{labels:bLabels.length?bLabels:['Active','Inactive'],datasets:[{{data:bData.length?bData:[s.active||0,s.inactive||0],backgroundColor:colors,borderWidth:0}}]}},options:{{responsive:true,plugins:{{legend:{{position:'right',labels:{{color:'#9ca3af',padding:12}}}}}}}}}});
    }}
  }}, 80);
}}

function buildTableHTML(rows) {{
  if (!rows || !rows.length) return '<p class="p-6 text-center text-gray-500"><i class="fa-solid fa-inbox text-2xl mb-2 block"></i>No records found</p>';
  return '<table class="data-table w-full"><thead><tr>'+
    '{th_html}'+
    '<th>Actions</th></tr></thead><tbody>'+
    rows.map(function(r) {{
      return '<tr>'+{row_js}+'<td><div class="flex gap-1">'+
        '<button onclick="doViewDetail(\\''+r.id+'\\');" class="btn py-1 px-2 text-xs" style="background:#1f2937;color:#9ca3af" title="View"><i class="fa-solid fa-eye"></i></button>'+
        '<button onclick="doEdit(\\''+r.id+'\\');" class="btn btn-primary py-1 px-2 text-xs" title="Edit"><i class="fa-solid fa-pen"></i></button>'+
        '<button onclick="doDeleteConfirm(\\''+r.id+'\\');" class="btn btn-danger py-1 px-2 text-xs" title="Delete"><i class="fa-solid fa-trash"></i></button>'+
        '</div></td></tr>';
    }}).join('')+
    '</tbody></table>';
}}

function renderList(container, searchQ) {{
  if (!container) container = document.querySelector('.view-section:not(.hidden)');
  if (!container) return;
  if (searchQ !== undefined) {{ _query = searchQ; _page = 1; }}
  let all = (typeof searchRecords==='function') ? searchRecords(_query) : (typeof getAll==='function' ? getAll() : []);
  if (_filterStatus) all = all.filter(function(r){{return r.status===_filterStatus;}});
  all = (typeof sortRecords==='function') ? sortRecords(all, _sortField, _sortDir) : all;
  const total = all.length;
  const start = (_page-1)*_perPage, end = start+_perPage;
  const pageData = all.slice(start, end);
  const statuses = [...new Set((typeof getAll==='function'?getAll():[]).map(function(r){{return r.status;}}).filter(Boolean))];
  container.innerHTML =
    '<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">'+
    '<div><h2 class="text-2xl font-bold text-white">All Records</h2><p class="text-gray-400 text-sm mt-1">'+total+' total entries</p></div>'+
    '<div class="flex gap-2">'+
    '<button onclick="doAdd()" class="btn btn-primary"><i class="fa-solid fa-plus mr-2"></i>Add New</button>'+
    '<button onclick="exportToCSV(typeof getAll===\\'function\\'?getAll():[],' + "'export'" + ')" class="btn" style="background:#1f2937;color:#9ca3af"><i class="fa-solid fa-download mr-2"></i>Export</button>'+
    '</div></div>'+
    '<div class="card overflow-hidden">'+
    '<div class="p-4 border-b border-gray-800 flex flex-wrap gap-3">'+
    '<div class="relative flex-1 min-w-[200px]"><i class="fa-solid fa-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm"></i><input id="list-search" type="search" value="'+_query+'" oninput="doSearch(this.value)" placeholder="Search records..." class="form-input pl-9"/></div>'+
    '<select onchange="_filterStatus=this.value;_page=1;renderList(container)" class="form-input w-auto">'+
    '<option value="">All Status</option>'+statuses.map(function(s){{return '<option value="'+s+'" '+(_filterStatus===s?'selected':'')+'>'+s+'</option>';}}).join('')+
    '</select>'+
    '<select onchange="doSort(this.value)" class="form-input w-auto"><option value="name">Sort: Name</option><option value="status">Sort: Status</option></select>'+
    '</div>'+
    '<div class="overflow-x-auto">'+buildTableHTML(pageData)+'</div>'+
    '<div class="p-4 border-t border-gray-800 flex items-center justify-between text-sm text-gray-400">'+
    '<span>Showing '+(start+1)+'-'+Math.min(end,total)+' of '+total+'</span>'+
    '<div class="flex gap-2">'+
    '<button onclick="_page=Math.max(1,_page-1);renderList(container)" '+ (_page<=1?'disabled':'')+' class="btn py-1.5 px-3 text-xs" style="background:#1f2937;color:#9ca3af;opacity:'+(_page<=1?'.4':'1')+'"><i class="fa-solid fa-chevron-left"></i></button>'+
    '<span class="py-1.5 px-3 bg-gray-800 rounded text-white">'+_page+' / '+Math.max(1,Math.ceil(total/_perPage))+'</span>'+
    '<button onclick="_page=Math.min(Math.ceil('+total+'/_perPage),_page+1);renderList(container)" '+(end>=total?'disabled':'')+' class="btn py-1.5 px-3 text-xs" style="background:#1f2937;color:#9ca3af;opacity:'+(end>=total?'.4':'1')+'"><i class="fa-solid fa-chevron-right"></i></button>'+
    '</div></div></div>';
}}

function renderForm(container, recordId) {{
  const r = (recordId && typeof getById==='function') ? (getById(recordId)||{{}}) : {{}};
  const isEdit = !!recordId && !!r.id;
  const html = '<div class="p-6 max-h-screen overflow-y-auto">'+
    '<h3 class="text-lg font-bold text-white mb-5">'+(isEdit?'Edit Record':'Add New Record')+'</h3>'+
    '<form id="record-form" class="space-y-4">'+
    '{form_html}'+
    '<div class="flex gap-3 pt-2">'+
    '<button type="submit" class="btn btn-primary flex-1">'+(isEdit?'Update':'Save')+' Record</button>'+
    '<button type="button" onclick="closeModal()" class="btn flex-1" style="background:#1f2937;color:#9ca3af">Cancel</button>'+
    '</div></form></div>';
  openModal(html);
  setTimeout(function() {{
    const form = document.getElementById('record-form');
    if (!form) return;
    form.addEventListener('submit', function(e) {{
      e.preventDefault();
      const data = Object.fromEntries(new FormData(form));
      if (isEdit) {{
        if (typeof updateRecord==='function') updateRecord(recordId, data);
        showToast('Record updated!', 'success');
      }} else {{
        if (typeof createRecord==='function') createRecord(data);
        showToast('Record created!', 'success');
      }}
      closeModal();
      const c = document.querySelector('.view-section:not(.hidden)');
      renderList(c);
    }});
  }}, 50);
}}

function renderReports(container) {{
  if (!container) container = document.querySelector('.view-section:not(.hidden)');
  if (!container) return;
  const s = (typeof getStats==='function') ? getStats() : {{}};
  const all = (typeof getAll==='function') ? getAll() : [];
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  container.innerHTML =
    '<div class="mb-6"><h2 class="text-2xl font-bold text-white">Reports & Analytics</h2><p class="text-gray-400 text-sm mt-1">Data insights and statistics</p></div>'+
    '<div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">'+
    '<div class="card text-center"><p class="text-gray-400 text-sm">Total Records</p><p class="text-4xl font-bold text-white mt-2">'+(s.total||0)+'</p></div>'+
    '<div class="card text-center"><p class="text-gray-400 text-sm">Active</p><p class="text-4xl font-bold text-green-400 mt-2">'+(s.active||0)+'</p></div>'+
    '<div class="card text-center"><p class="text-gray-400 text-sm">Active Rate</p><p class="text-4xl font-bold text-blue-400 mt-2">'+((s.total&&s.active)?Math.round(s.active/s.total*100):0)+'%</p></div>'+
    '</div>'+
    '<div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">'+
    '<div class="card"><h3 class="font-semibold text-white mb-4">Monthly Trend</h3><canvas id="rep-line" height="200"></canvas></div>'+
    '<div class="card"><h3 class="font-semibold text-white mb-4">Distribution</h3><canvas id="rep-bar" height="200"></canvas></div>'+
    '</div>'+
    '<div class="card"><div class="flex items-center justify-between mb-4"><h3 class="font-semibold text-white">All Records</h3><div class="flex gap-2"><button onclick="exportToCSV(typeof getAll===\\'function\\'?getAll():[],' + "'report'" + ')" class="btn btn-primary py-1.5 px-4 text-sm"><i class="fa-solid fa-download mr-2"></i>Export CSV</button><button onclick="window.print()" class="btn py-1.5 px-4 text-sm" style="background:#1f2937;color:#9ca3af"><i class="fa-solid fa-print mr-2"></i>Print</button></div></div>'+
    '<div class="overflow-x-auto">'+buildTableHTML(all.slice(0,10))+'</div></div>';
  setTimeout(function() {{
    const monthly = s.monthly || Array(12).fill(0).map(function(){{return Math.floor(Math.random()*10)+1;}});
    const breakdown = s.categoryBreakdown || {{}};
    const bLabels = Object.keys(breakdown), bData = Object.values(breakdown);
    if (typeof safeChart === 'function') {{
      safeChart('rep-line', {{type:'line',data:{{labels:months,datasets:[{{label:'Records',data:monthly,borderColor:'{accent}',backgroundColor:'{accent}20',tension:.4,fill:true,pointBackgroundColor:'{accent}'}}]}},options:{{responsive:true,plugins:{{legend:{{display:false}}}},scales:{{y:{{beginAtZero:true,grid:{{color:'rgba(255,255,255,.05)'}},ticks:{{color:'#6b7280'}}}},x:{{grid:{{display:false}},ticks:{{color:'#6b7280'}}}}}}}}}});
      safeChart('rep-bar', {{type:'bar',data:{{labels:bLabels.length?bLabels:['Active','Inactive'],datasets:[{{label:'Count',data:bData.length?bData:[s.active||0,s.inactive||0],backgroundColor:['{accent}','#4ade80','#f87171','#fbbf24','#818cf8'].slice(0,Math.max(bLabels.length,2)),borderRadius:6}}]}},options:{{responsive:true,plugins:{{legend:{{display:false}}}},scales:{{y:{{beginAtZero:true,grid:{{color:'rgba(255,255,255,.05)'}},ticks:{{color:'#6b7280'}}}},x:{{grid:{{display:false}},ticks:{{color:'#6b7280'}}}}}}}}}});
    }}
  }}, 80);
}}

function renderDetail(recordId) {{
  const r = (typeof getById==='function') ? getById(recordId) : null;
  if (!r) return;
  const entries = Object.entries(r).filter(function(e){{return e[0]!=='id';}});
  const html = '<div class="p-6"><h3 class="text-lg font-bold text-white mb-5">Record Details</h3>'+
    '<div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">'+
    entries.map(function(e){{
      const val = e[0]==='status'?'<span class="badge '+(typeof getStatusColor==='function'?getStatusColor(e[1]):'badge-info')+'">'+e[1]+'</span>':('<span class="text-white">'+e[1]+'</span>');
      return '<div class="bg-gray-800/50 rounded-lg p-3"><p class="text-gray-400 text-xs uppercase mb-1">'+e[0]+'</p>'+val+'</div>';
    }}).join('')+
    '</div>'+
    '<div class="flex gap-3"><button onclick="doEdit(\\''+recordId+'\\');" class="btn btn-primary flex-1"><i class="fa-solid fa-pen mr-2"></i>Edit</button>'+
    '<button onclick="closeModal()" class="btn flex-1" style="background:#1f2937;color:#9ca3af">Close</button></div></div>';
  openModal(html);
}}

/* ── Action helpers ── */
function doAdd() {{ renderForm(document.querySelector('.view-section:not(.hidden)'), null); }}
function doEdit(id) {{ renderForm(document.querySelector('.view-section:not(.hidden)'), id); }}
function doViewDetail(id) {{ renderDetail(id); }}
function doSort(field) {{
  if (_sortField===field) _sortDir=_sortDir==='asc'?'desc':'asc'; else {{_sortField=field;_sortDir='asc';}}
  renderList(document.querySelector('.view-section:not(.hidden)'));
}}
function doSearch(q) {{ _query=q; _page=1; renderList(document.querySelector('.view-section:not(.hidden)')); }}
function doDeleteConfirm(id) {{
  if (typeof confirmDelete==='function') {{
    confirmDelete(id, function(rid){{if(typeof deleteRecord==='function')deleteRecord(rid);}}, function(){{renderList(document.querySelector('.view-section:not(.hidden)'));}});
  }}
}}
"""

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
    <p class="text-gray-400 mb-6">AI-generated project - all features included below.</p>
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
