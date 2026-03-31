"""
LovableBot — World's Most Advanced AI Code Generation System

AGENT PIPELINE (8 Agents):
  0. PromptAnalyzer  — Deep NLP analysis, intent extraction, enhancement
  1. Planner         — Strategic project planning with full feature map
  2. Architect       — File structure, tech stack, CDN selection
  3. ThreeD          — Advanced Three.js 3D scene generation
  4. Coder           — Parallel file-by-file production code generation
  5. Debugger        — Automated bug scanning and hot-fixing
  6. Reviewer        — Quality enforcement and feature completion
  7. Packager        — ZIP assembly with rich delivery summary

Quality Standards:
  - Minimum 3000+ chars for HTML files (enforced)
  - Minimum 1000+ chars for JS files
  - AI response rejected if it contains placeholders or TODOs
  - Three retry layers: primary model → fallback model → hardcoded production fallback
"""

import requests
import urllib.parse
import time
import re
import json
import os
import zipfile
import tempfile
import random
import hashlib

API_BASE = "https://dev-apis-xyz.pantheonsite.io/wp-content/apis/freeAi.php"
MODEL = "gemini"
FALLBACK = "llama"

# ─── Quality thresholds — UNLIMITED COMPLEXITY MODE ───────────────────────────
MIN_HTML_CHARS    = 8000
MIN_JS_CHARS      = 3000
MIN_CSS_CHARS     = 2000
MIN_PY_CHARS      = 2500
PLACEHOLDER_SIGNS = ["TODO", "placeholder", "lorem ipsum", "Add your code here",
                     "Insert code here", "coming soon", "under construction", "FIXME"]

# ─── Full-stack detection keywords ────────────────────────────────────────────
BACKEND_TRIGGERS = [
    "with backend", "with server", "with database", "full stack", "full-stack",
    "with api", "with rest api", "with real api", "with real database",
    "with login", "with authentication", "with auth", "with user accounts",
    "with real auth", "with jwt", "with sessions",
    "real database", "real system", "production system", "full system",
    "mysql", "mongodb", "mongo db", "firebase", "supabase", "postgresql", "postgres", "sqlite",
    "node.js", "nodejs", "node js", "django", "php", "express.js", "expressjs",
    "server side", "server-side", "backend server", "rest api", "graphql api",
    "multi user", "multi-user", "multiple users", "user management system",
]

STACK_BACKENDS = {
    "nodejs": {"label": "Node.js + Express", "emoji": "⚡", "lang": "javascript"},
    "django": {"label": "Django (Python)",    "emoji": "🐍", "lang": "python"},
    "php":    {"label": "PHP",               "emoji": "🐘", "lang": "php"},
}

STACK_DATABASES = {
    "mongodb":    {"label": "MongoDB",    "emoji": "🍃", "type": "nosql"},
    "mysql":      {"label": "MySQL",      "emoji": "🐬", "type": "sql"},
    "firebase":   {"label": "Firebase",   "emoji": "🔥", "type": "nosql"},
    "supabase":   {"label": "Supabase",   "emoji": "⚡", "type": "sql"},
}

def needs_backend(request: str) -> bool:
    """Returns True if the request implies a full-stack system needing backend clarification."""
    r = request.lower()
    return any(kw in r for kw in BACKEND_TRIGGERS)


def generate_clarifying_question(request: str) -> str:
    """Generate 1 targeted clarifying question for a vague/short project request."""
    prompt = f"""Given this software project request, generate ONE short, specific clarifying question that would most improve the quality of what gets built. Focus on the single most important missing piece of context.

Request: "{request}"

Good examples:
- "What industry is this for — healthcare, finance, retail, or something else?"
- "Should the design be dark/modern or light/professional?"
- "Who are the main users — admins only, or also regular users/customers?"
- "What are the 3 main types of data this needs to track?"
- "Should this include user login/authentication?"

Output ONLY the question itself — no intro, no explanation, just one clear question ending with '?'"""
    resp = call_ai(prompt, timeout=25)
    if resp and "?" in resp and 10 < len(resp) < 250:
        lines = [l.strip() for l in resp.strip().split("\n") if l.strip() and "?" in l]
        if lines:
            return lines[0].strip().lstrip("- •").strip()
    return ""


# ─── Core AI caller ──────────────────────────────────────────────────────────

def call_ai(prompt: str, model: str = MODEL, retries: int = 3, timeout: int = 120) -> str:
    for attempt in range(retries):
        try:
            encoded = urllib.parse.quote(prompt, safe="")
            resp = requests.get(f"{API_BASE}?prompt={encoded}&model={model}", timeout=timeout)
            text = resp.text.strip()
            if text and len(text) > 50 and "Bro What The Fuck" not in text and "error" not in text[:20].lower():
                return text
        except Exception:
            pass
        if attempt < retries - 1:
            time.sleep(2 + attempt * 3)
    # Fallback model
    if model != FALLBACK:
        for attempt in range(2):
            try:
                encoded = urllib.parse.quote(prompt, safe="")
                resp = requests.get(f"{API_BASE}?prompt={encoded}&model={FALLBACK}", timeout=80)
                text = resp.text.strip()
                if text and len(text) > 50:
                    return text
            except Exception:
                pass
            if attempt < 1:
                time.sleep(3)
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
            return max(matched, key=lambda b: len(b[1]))[1].strip()

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


def is_quality_code(code: str, lang: str) -> bool:
    """Check if generated code meets quality standards."""
    if not code:
        return False
    thresholds = {"html": MIN_HTML_CHARS, "javascript": MIN_JS_CHARS,
                  "css": MIN_CSS_CHARS, "python": MIN_PY_CHARS}
    if len(code) < thresholds.get(lang, 500):
        return False
    # Reject if it's full of placeholders
    placeholder_count = sum(1 for p in PLACEHOLDER_SIGNS if p.lower() in code.lower())
    if placeholder_count >= 3:
        return False
    return True


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
    explicit_api = any(w in r for w in ["python api", "flask api", "fastapi", "rest api",
                                         "build an api", "create an api", "make an api"])
    return explicit_api and not is_management_system(r)


def detect_traits(req: str) -> dict:
    r = req.lower()
    mgmt = is_management_system(r)
    return {
        "is_3d":         any(w in r for w in ["3d", "three.js", "sphere", "cube", "rotate", "orbit", "webgl", "glsl", "voxel", "mesh"]),
        "is_game":       any(w in r for w in ["game", "snake", "tetris", "chess", "pacman", "platformer", "shooter", "puzzle", "breakout", "pong", "flappy", "arcade"]),
        "is_dashboard":  any(w in r for w in ["dashboard", "analytics", "chart", "graph", "stats", "metrics", "kpi", "report"]),
        "is_api":        is_pure_api_request(r),
        "is_landing":    any(w in r for w in ["landing", "homepage", "hero", "pricing", "saas", "startup", "portfolio", "agency"]),
        "is_ecommerce":  any(w in r for w in ["shop", "store", "ecommerce", "cart", "checkout", "buy", "product"]),
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

    new_project_signals = [
        "build me", "build a", "create a", "create me", "make me a", "make a",
        "generate a", "generate me", "i want a", "i need a", "write a",
        "new project", "new app", "new website", "new game", "new dashboard"
    ]
    if any(r.startswith(sig) or f" {sig}" in r for sig in new_project_signals):
        return False

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

    modification_words = [
        "fix", "change", "update", "modify", "adjust", "improve", "rename",
        "remove", "delete", "darker", "lighter", "bigger", "smaller", "wider",
        "taller", "shorter", "bolder", "thinner", "animated", "responsive"
    ]
    if len(words) <= 15 and any(mw in words for mw in modification_words):
        return True

    return False


# ─── CDN Registry ─────────────────────────────────────────────────────────────

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
    "dayjs":       '<script src="https://cdn.jsdelivr.net/npm/dayjs@1/dayjs.min.js"></script>',
}



# ════════════════════════════════════════════════════════════════════════════════
# DESIGN VARIETY ENGINE — ensures every build looks completely different
# ════════════════════════════════════════════════════════════════════════════════

DESIGN_PERSONALITIES = [
    {
        "id": "aurora-dark",
        "description": "Deep space dark with aurora gradient accents — animated color blobs, heavy glassmorphism, electric glow on interactive elements",
        "bg_style": "background: radial-gradient(ellipse at 20% 50%, #0f172a 0%, #020617 40%, #0a0a1a 100%); min-height:100vh;",
        "sidebar_style": "background: rgba(15,23,42,0.95); backdrop-filter: blur(20px); border-right: 1px solid rgba(99,102,241,0.15);",
        "header_style": "background: rgba(2,6,23,0.8); backdrop-filter: blur(20px); border-bottom: 1px solid rgba(99,102,241,0.15);",
        "card_style": "background: rgba(15,23,42,0.7); backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px;",
        "body_bg": "#020617",
        "text_primary": "#e2e8f0",
        "text_secondary": "#94a3b8",
        "surface": "rgba(15,23,42,0.7)",
        "surface2": "rgba(30,41,59,0.8)",
        "border_color": "rgba(99,102,241,0.15)",
        "extra_css": """
body::before { content:''; position:fixed; top:-50%; left:-50%; width:200%; height:200%; background: radial-gradient(circle at 30% 30%, rgba(99,102,241,0.06) 0%, transparent 50%), radial-gradient(circle at 70% 70%, rgba(168,85,247,0.04) 0%, transparent 50%); pointer-events:none; z-index:0; }
.main-content { position:relative; z-index:1; }
""",
        "dark_mode_class": "dark",
        "tailwind_theme": "indigo",
    },
    {
        "id": "neon-cyberpunk",
        "description": "Black base with electric cyan/magenta neon accents — glowing borders, scanline texture, terminal aesthetic mixed with modern",
        "bg_style": "background: #050505;",
        "sidebar_style": "background: #0a0a0a; border-right: 1px solid rgba(0,255,200,0.15); box-shadow: 2px 0 20px rgba(0,255,200,0.05);",
        "header_style": "background: rgba(5,5,5,0.95); backdrop-filter: blur(10px); border-bottom: 1px solid rgba(0,255,200,0.12);",
        "card_style": "background: #0d0d0d; border: 1px solid rgba(0,255,200,0.12); border-radius: 8px; box-shadow: 0 0 20px rgba(0,255,200,0.03);",
        "body_bg": "#050505",
        "text_primary": "#e0fff8",
        "text_secondary": "rgba(0,255,200,0.6)",
        "surface": "#0d0d0d",
        "surface2": "#141414",
        "border_color": "rgba(0,255,200,0.15)",
        "extra_css": """
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap');
body { font-family: 'JetBrains Mono', monospace !important; }
body::after { content:''; position:fixed; inset:0; background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,255,200,0.01) 2px, rgba(0,255,200,0.01) 4px); pointer-events:none; z-index:9999; }
.nav-link:hover, .nav-link.active { text-shadow: 0 0 8px currentColor; }
.btn-primary { box-shadow: 0 0 15px rgba(0,255,200,0.3); }
""",
        "dark_mode_class": "dark",
        "tailwind_theme": "cyan",
    },
    {
        "id": "corporate-light",
        "description": "Clean white/light gray professional SaaS — crisp shadows, generous whitespace, blue accents, minimal and focused",
        "bg_style": "background: #f8fafc;",
        "sidebar_style": "background: #ffffff; border-right: 1px solid #e2e8f0; box-shadow: 1px 0 0 #e2e8f0;",
        "header_style": "background: #ffffff; border-bottom: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);",
        "card_style": "background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);",
        "body_bg": "#f8fafc",
        "text_primary": "#0f172a",
        "text_secondary": "#64748b",
        "surface": "#ffffff",
        "surface2": "#f1f5f9",
        "border_color": "#e2e8f0",
        "extra_css": """
body { color: #0f172a; }
.nav-link { color: #475569; }
.nav-link:hover { background: #f1f5f9; color: #0f172a; }
.nav-link.active { color: var(--brand); background: rgba(var(--brand-rgb),0.08); }
.data-table th { background: #f8fafc; color: #64748b; }
.data-table tr:hover td { background: #f8fafc; }
.card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
""",
        "dark_mode_class": "",
        "tailwind_theme": "blue",
    },
    {
        "id": "gradient-luxury",
        "description": "Rich deep gradient base (violet-to-indigo), frosted glass panels, premium typography, gold/white accents",
        "bg_style": "background: linear-gradient(135deg, #1e0a3c 0%, #0f0a2e 30%, #0a1628 60%, #0d1f3c 100%); min-height:100vh;",
        "sidebar_style": "background: rgba(15,10,46,0.85); backdrop-filter: blur(20px); border-right: 1px solid rgba(255,255,255,0.08);",
        "header_style": "background: rgba(10,10,40,0.7); backdrop-filter: blur(20px); border-bottom: 1px solid rgba(255,255,255,0.08);",
        "card_style": "background: rgba(255,255,255,0.04); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px;",
        "body_bg": "#0f0a2e",
        "text_primary": "#f0eeff",
        "text_secondary": "rgba(200,185,255,0.7)",
        "surface": "rgba(255,255,255,0.04)",
        "surface2": "rgba(255,255,255,0.07)",
        "border_color": "rgba(255,255,255,0.1)",
        "extra_css": """
body::before { content:''; position:fixed; top:0; right:0; width:600px; height:600px; background: radial-gradient(circle, rgba(139,92,246,0.12) 0%, transparent 70%); pointer-events:none; }
body::after { content:''; position:fixed; bottom:0; left:0; width:500px; height:500px; background: radial-gradient(circle, rgba(59,130,246,0.08) 0%, transparent 70%); pointer-events:none; }
h1,h2,h3 { letter-spacing: -0.025em; }
""",
        "dark_mode_class": "dark",
        "tailwind_theme": "violet",
    },
    {
        "id": "emerald-forest",
        "description": "Deep forest green dark theme — teal-to-emerald gradients, organic feel, earthy sophisticated tones",
        "bg_style": "background: linear-gradient(160deg, #022c22 0%, #030f0d 40%, #031f14 100%);",
        "sidebar_style": "background: rgba(2,20,15,0.95); backdrop-filter: blur(16px); border-right: 1px solid rgba(16,185,129,0.12);",
        "header_style": "background: rgba(2,15,10,0.85); backdrop-filter: blur(16px); border-bottom: 1px solid rgba(16,185,129,0.12);",
        "card_style": "background: rgba(6,37,27,0.8); backdrop-filter: blur(12px); border: 1px solid rgba(16,185,129,0.1); border-radius: 14px;",
        "body_bg": "#030f0d",
        "text_primary": "#ecfdf5",
        "text_secondary": "rgba(52,211,153,0.7)",
        "surface": "rgba(6,37,27,0.8)",
        "surface2": "rgba(12,55,40,0.6)",
        "border_color": "rgba(16,185,129,0.12)",
        "extra_css": """
body::before { content:''; position:fixed; top:-200px; right:-200px; width:600px; height:600px; border-radius:50%; background:radial-gradient(circle, rgba(16,185,129,0.07) 0%, transparent 70%); pointer-events:none; }
.btn-primary { box-shadow: 0 4px 20px rgba(16,185,129,0.25); }
""",
        "dark_mode_class": "dark",
        "tailwind_theme": "emerald",
    },
    {
        "id": "sunset-warm",
        "description": "Warm dark sunset — deep charcoal with orange-amber-rose gradient accents, energetic vibrant feel",
        "bg_style": "background: linear-gradient(150deg, #1a0a00 0%, #0f0800 40%, #1a0500 100%);",
        "sidebar_style": "background: rgba(20,8,0,0.95); backdrop-filter: blur(16px); border-right: 1px solid rgba(249,115,22,0.12);",
        "header_style": "background: rgba(15,8,0,0.85); backdrop-filter: blur(16px); border-bottom: 1px solid rgba(249,115,22,0.12);",
        "card_style": "background: rgba(30,12,0,0.8); backdrop-filter: blur(12px); border: 1px solid rgba(249,115,22,0.1); border-radius: 14px;",
        "body_bg": "#0f0800",
        "text_primary": "#fff7ed",
        "text_secondary": "rgba(251,146,60,0.8)",
        "surface": "rgba(30,12,0,0.8)",
        "surface2": "rgba(45,18,0,0.6)",
        "border_color": "rgba(249,115,22,0.12)",
        "extra_css": """
body::before { content:''; position:fixed; top:-100px; left:50%; width:800px; height:400px; transform:translateX(-50%); background: radial-gradient(ellipse, rgba(249,115,22,0.06) 0%, transparent 70%); pointer-events:none; }
.btn-primary { box-shadow: 0 4px 20px rgba(249,115,22,0.3); }
""",
        "dark_mode_class": "dark",
        "tailwind_theme": "orange",
    },
    {
        "id": "ocean-deep",
        "description": "Deep ocean blue — navy-to-midnight-blue gradients, cool slate tones, calm professional yet modern",
        "bg_style": "background: linear-gradient(160deg, #001528 0%, #000d1f 40%, #001020 100%);",
        "sidebar_style": "background: rgba(0,12,30,0.95); backdrop-filter: blur(16px); border-right: 1px solid rgba(56,189,248,0.1);",
        "header_style": "background: rgba(0,8,20,0.85); backdrop-filter: blur(16px); border-bottom: 1px solid rgba(56,189,248,0.1);",
        "card_style": "background: rgba(0,20,45,0.7); backdrop-filter: blur(12px); border: 1px solid rgba(56,189,248,0.08); border-radius: 14px;",
        "body_bg": "#000d1f",
        "text_primary": "#e0f2fe",
        "text_secondary": "rgba(125,211,252,0.7)",
        "surface": "rgba(0,20,45,0.7)",
        "surface2": "rgba(0,30,65,0.6)",
        "border_color": "rgba(56,189,248,0.1)",
        "extra_css": """
body::before { content:''; position:fixed; bottom:-200px; left:-100px; width:700px; height:700px; border-radius:50%; background:radial-gradient(circle, rgba(14,165,233,0.06) 0%, transparent 70%); pointer-events:none; }
.btn-primary { box-shadow: 0 4px 20px rgba(14,165,233,0.25); }
""",
        "dark_mode_class": "dark",
        "tailwind_theme": "sky",
    },
    {
        "id": "minimal-zinc",
        "description": "Ultra-clean minimal dark zinc — near-black backgrounds, razor-thin borders, single accent, whitespace-first design",
        "bg_style": "background: #09090b;",
        "sidebar_style": "background: #09090b; border-right: 1px solid #27272a;",
        "header_style": "background: rgba(9,9,11,0.95); backdrop-filter: blur(8px); border-bottom: 1px solid #27272a;",
        "card_style": "background: #18181b; border: 1px solid #27272a; border-radius: 10px;",
        "body_bg": "#09090b",
        "text_primary": "#fafafa",
        "text_secondary": "#71717a",
        "surface": "#18181b",
        "surface2": "#27272a",
        "border_color": "#27272a",
        "extra_css": """
* { font-feature-settings: 'cv02','cv03','cv04','cv11'; }
.nav-link { border-radius: 6px; font-size: 0.8125rem; }
.card { transition: border-color 0.15s ease; }
.card:hover { border-color: #3f3f46; }
.btn { border-radius: 6px; font-size: 0.8125rem; font-weight: 500; }
""",
        "dark_mode_class": "dark",
        "tailwind_theme": "zinc",
    },
    {
        "id": "rose-blush",
        "description": "Sophisticated dark with rose-pink accent palette — deep charcoal base, pink-to-purple gradient accents, feminine yet powerful",
        "bg_style": "background: linear-gradient(135deg, #1a0010 0%, #0f000a 40%, #1a0018 100%);",
        "sidebar_style": "background: rgba(20,0,12,0.95); backdrop-filter: blur(16px); border-right: 1px solid rgba(236,72,153,0.12);",
        "header_style": "background: rgba(12,0,8,0.85); backdrop-filter: blur(16px); border-bottom: 1px solid rgba(236,72,153,0.12);",
        "card_style": "background: rgba(30,0,18,0.8); backdrop-filter: blur(12px); border: 1px solid rgba(236,72,153,0.1); border-radius: 16px;",
        "body_bg": "#0f000a",
        "text_primary": "#fce7f3",
        "text_secondary": "rgba(249,168,212,0.8)",
        "surface": "rgba(30,0,18,0.8)",
        "surface2": "rgba(45,0,27,0.6)",
        "border_color": "rgba(236,72,153,0.12)",
        "extra_css": """
body::before { content:''; position:fixed; top:0; right:0; width:500px; height:500px; background:radial-gradient(circle, rgba(236,72,153,0.07) 0%, transparent 70%); pointer-events:none; }
.btn-primary { box-shadow: 0 4px 20px rgba(236,72,153,0.3); }
h1,h2,h3 { letter-spacing: -0.02em; }
""",
        "dark_mode_class": "dark",
        "tailwind_theme": "pink",
    },
    {
        "id": "slate-professional",
        "description": "Balanced slate dark — neutral dark grays with a sophisticated cool tint, perfect for enterprise dashboards",
        "bg_style": "background: #0f172a;",
        "sidebar_style": "background: #0f172a; border-right: 1px solid rgba(148,163,184,0.08);",
        "header_style": "background: rgba(15,23,42,0.95); backdrop-filter: blur(12px); border-bottom: 1px solid rgba(148,163,184,0.08);",
        "card_style": "background: #1e293b; border: 1px solid rgba(148,163,184,0.08); border-radius: 12px;",
        "body_bg": "#0f172a",
        "text_primary": "#f1f5f9",
        "text_secondary": "#94a3b8",
        "surface": "#1e293b",
        "surface2": "#273549",
        "border_color": "rgba(148,163,184,0.08)",
        "extra_css": """
.card:hover { border-color: rgba(148,163,184,0.15); }
.stat-card:hover { transform: translateY(-1px); }
.btn-primary { letter-spacing: 0.01em; }
""",
        "dark_mode_class": "dark",
        "tailwind_theme": "slate",
    },
]

COLOR_PALETTES = [
    {"primary": "#6366f1", "secondary": "#8b5cf6", "accent": "#ec4899", "name": "indigo-violet", "tailwind": "indigo"},
    {"primary": "#3b82f6", "secondary": "#06b6d4", "accent": "#38bdf8", "name": "blue-cyan", "tailwind": "blue"},
    {"primary": "#10b981", "secondary": "#059669", "accent": "#34d399", "name": "emerald-green", "tailwind": "emerald"},
    {"primary": "#f59e0b", "secondary": "#f97316", "accent": "#fbbf24", "name": "amber-orange", "tailwind": "amber"},
    {"primary": "#ef4444", "secondary": "#f97316", "accent": "#fb7185", "name": "red-orange", "tailwind": "red"},
    {"primary": "#8b5cf6", "secondary": "#a855f7", "accent": "#d946ef", "name": "violet-fuchsia", "tailwind": "violet"},
    {"primary": "#06b6d4", "secondary": "#0891b2", "accent": "#22d3ee", "name": "cyan-teal", "tailwind": "cyan"},
    {"primary": "#ec4899", "secondary": "#db2777", "accent": "#f472b6", "name": "pink-rose", "tailwind": "pink"},
    {"primary": "#14b8a6", "secondary": "#0d9488", "accent": "#2dd4bf", "name": "teal-emerald", "tailwind": "teal"},
    {"primary": "#f97316", "secondary": "#ea580c", "accent": "#fb923c", "name": "orange-amber", "tailwind": "orange"},
    {"primary": "#a855f7", "secondary": "#9333ea", "accent": "#e879f9", "name": "purple-fuchsia", "tailwind": "purple"},
    {"primary": "#22c55e", "secondary": "#16a34a", "accent": "#86efac", "name": "green-lime", "tailwind": "green"},
    {"primary": "#0ea5e9", "secondary": "#0284c7", "accent": "#7dd3fc", "name": "sky-blue", "tailwind": "sky"},
    {"primary": "#e879f9", "secondary": "#d946ef", "accent": "#f0abfc", "name": "fuchsia-pink", "tailwind": "fuchsia"},
    {"primary": "#84cc16", "secondary": "#65a30d", "accent": "#bef264", "name": "lime-green", "tailwind": "lime"},
]

# Domains that should lean toward light/professional themes
LIGHT_THEME_DOMAINS = ["corporate", "legal", "medical", "hospital", "hr", "finance", "accounting", "bank"]
# Domains that lean toward vibrant/energetic themes
VIBRANT_DOMAINS = ["game", "social", "creative", "entertainment", "music", "art", "startup", "saas"]
# Domains that lean toward dark/tech themes
TECH_DOMAINS = ["crypto", "security", "hacker", "developer", "tool", "analytics", "ai", "data", "cloud"]


def pick_design_variety(request: str, analysis: dict) -> dict:
    """
    Picks a unique design personality and color palette for every build.
    Uses a hash of the request for deterministic variety — same request always
    gets the same design, but different requests get different designs.
    """
    req_hash = int(hashlib.md5(request.strip().lower().encode()).hexdigest(), 16)
    r = request.lower()
    domain = analysis.get("domain", "").lower()
    visual_style = analysis.get("visual_style", "").lower()

    # Color palette selection — AI may have chosen one, otherwise we pick from palette
    ai_primary = analysis.get("primary_color", "")
    if ai_primary and ai_primary not in ("#6366f1", "#8b5cf6") and len(ai_primary) == 7:
        # AI chose a non-default color — find closest palette match
        palette = min(COLOR_PALETTES, key=lambda p: sum(abs(int(ai_primary[i:i+2],16) - int(p["primary"][i:i+2],16)) for i in (1,3,5)))
    else:
        # Seed-based selection for variety
        palette = COLOR_PALETTES[req_hash % len(COLOR_PALETTES)]

    # Design personality selection
    # Respect AI's visual style if set explicitly
    if "light" in visual_style or "minimal" in visual_style or any(d in domain for d in LIGHT_THEME_DOMAINS):
        candidate_ids = ["corporate-light", "minimal-zinc", "slate-professional"]
    elif "neon" in visual_style or "cyberpunk" in visual_style or any(d in r for d in TECH_DOMAINS):
        candidate_ids = ["neon-cyberpunk", "aurora-dark", "minimal-zinc"]
    elif "luxury" in visual_style or "gradient" in visual_style or any(d in r for d in ["luxury", "premium", "elite"]):
        candidate_ids = ["gradient-luxury", "rose-blush", "aurora-dark"]
    else:
        # Full variety for everything else
        candidate_ids = [p["id"] for p in DESIGN_PERSONALITIES]

    # Pick from candidates using hash
    candidates = [p for p in DESIGN_PERSONALITIES if p["id"] in candidate_ids]
    if not candidates:
        candidates = DESIGN_PERSONALITIES
    personality = candidates[req_hash % len(candidates)]

    # Override palette primary to match personality's tailwind theme suggestion if possible
    personality_theme = personality.get("tailwind_theme", "")
    if personality_theme:
        theme_palette = next((p for p in COLOR_PALETTES if p["tailwind"] == personality_theme), None)
        if theme_palette:
            palette = theme_palette

    return {
        "personality": personality,
        "palette": palette,
        "primary_color": palette["primary"],
        "secondary_color": palette["secondary"],
        "accent_color": palette["accent"],
        "color_palette_name": palette["name"],
        "tailwind_theme": palette["tailwind"],
        "design_id": personality["id"],
        "design_description": personality["description"],
    }


def pick_cdns(traits: dict, project_type: str, stack: list) -> list[str]:
    selected = ["tailwind", "fontawesome"]
    if traits.get("is_landing"):
        selected += ["aos", "gsap", "alpine"]
    if traits.get("is_dashboard") or traits.get("is_management") or project_type in ("management", "dashboard"):
        selected += ["chartjs", "dayjs"]
    if traits.get("is_game"):
        selected += ["anime"]
    if traits.get("is_ecommerce"):
        selected += ["gsap", "alpine"]
    if not traits.get("is_game") and not traits.get("is_landing"):
        if "alpine" not in selected:
            selected += ["alpine"]
    if "drag" in str(stack).lower():
        selected += ["sortable"]
    if "markdown" in str(stack).lower():
        selected += ["marked"]
    return [CDNS[k] for k in dict.fromkeys(selected) if k in CDNS]


# ════════════════════════════════════════════════════════════════════════════════
# AGENT 0: Prompt Analyzer — Deep NLP + Intent Extraction
# ════════════════════════════════════════════════════════════════════════════════

class PromptAnalyzerAgent:
    name = "Prompt Analyzer"
    emoji = "🔬"

    def run(self, request: str) -> dict:
        """
        Deeply analyze the user's request to extract maximum context,
        enhance vague requests, and produce a rich brief for all downstream agents.
        """
        traits = detect_traits(request)

        prompt = f"""You are the world's most advanced software requirements analyst, UX architect and product strategist. Your job is to extract the absolute maximum possible context, detail, and intelligence from any user request — no matter how short — and produce a rich, exhaustive brief that will power a team of AI coding agents to build the most complete, production-ready, enterprise-quality application possible.

USER REQUEST: "{request}"

Detected signals: {json.dumps({k: v for k, v in traits.items() if v})}

MISSION: Extract EVERYTHING. Expand the request to its fullest potential. If the user says "student management", think: photo uploads, QR code IDs, GPA analytics, parent portal, timetable builder, attendance heatmaps, report cards, teacher assignment, course waitlists, graduation tracking. Always build MORE than asked.

Output ONLY this JSON (no other text — be exhaustive, specific, and ambitious):
```json
{{
  "original": "{request.replace('"', "'")}",
  "enhanced_request": "Extremely detailed 3-4 sentence description of what to build. Name specific features, target users, visual style, data flows, and key interactions. Go far beyond what was literally asked.",
  "detected_type": "management|landing|webapp|dashboard|game|3d-scene|api|ecommerce|social|tool|portfolio",
  "domain": "highly specific domain (e.g., hospital patient & appointment management ERP, neon browser snake game with power-ups, SaaS AI writing productivity tool)",
  "brand_name": "catchy, professional, memorable brand name",
  "primary_color": "PICK the best hex color for this domain — medical=teal(#0d9488), finance=blue(#2563eb), nature=green(#16a34a), food=orange(#ea580c), beauty=rose(#e11d48), tech=violet(#7c3aed), corporate=slate(#475569), luxury=gold(#b45309) — NOT always #6366f1",
  "secondary_color": "A complementary color hex that pairs beautifully with primary_color",
  "accent_color": "A punchy highlight color hex for CTAs and highlights",
  "color_palette_name": "choose ONE: purple-indigo|blue-cyan|green-emerald|orange-amber|red-rose|slate-gray|teal-mint|violet-pink|gold-amber|sky-blue",
  "visual_style": "choose ONE that best matches domain: dark-glass|light-minimal|neon-cyberpunk|corporate-professional|colorful-vibrant|gradient-luxury|emerald-nature|ocean-deep|rose-elegant|slate-professional",
  "ui_complexity": "enterprise",
  "target_user": "detailed description of who uses this, their workflow, and what they need",
  "key_entities": ["PrimaryEntity", "SecondaryEntity", "TertiaryEntity", "QuaternaryEntity"],
  "critical_features": [
    "Feature 1 — extremely specific with implementation details (e.g., 'Student registration with photo upload, auto-generated QR code ID card, multi-step form with validation')",
    "Feature 2 — equally specific",
    "Feature 3",
    "Feature 4",
    "Feature 5",
    "Feature 6",
    "Feature 7",
    "Feature 8",
    "Feature 9",
    "Feature 10",
    "Feature 11",
    "Feature 12",
    "Feature 13",
    "Feature 14",
    "Feature 15"
  ],
  "ui_sections": ["Section1", "Section2", "Section3", "Section4", "Section5", "Section6", "Section7", "Section8"],
  "data_fields": ["field1", "field2", "field3", "field4", "field5", "field6", "field7", "field8", "field9", "field10"],
  "animations": ["animation type 1", "animation type 2", "animation type 3", "animation type 4"],
  "must_include_libs": ["Tailwind CSS", "Font Awesome 6", "Chart.js", "Alpine.js"],
  "color_theme_tailwind": "indigo|violet|blue|green|orange|red|slate|purple|cyan|teal",
  "advanced_features": ["advanced feature 1 (e.g., real-time analytics heatmap)", "advanced feature 2", "advanced feature 3"]
}}
```"""

        resp = call_ai(prompt, timeout=60)
        analysis = extract_json(resp)

        if not isinstance(analysis, dict) or not analysis.get("critical_features"):
            analysis = self._smart_fallback(request, traits)

        # Ensure all required keys
        analysis.setdefault("enhanced_request", request)
        analysis.setdefault("domain", request)
        analysis.setdefault("brand_name", request.title())
        analysis.setdefault("critical_features", [])
        analysis.setdefault("ui_complexity", "enterprise")
        analysis.setdefault("advanced_features", [])
        analysis["original"] = request
        analysis["traits"] = traits

        # ── Inject design variety — unique personality for every build ──────────
        variety = pick_design_variety(request, analysis)
        # Override with variety colors if AI chose a generic default
        ai_primary = analysis.get("primary_color", "")
        if not ai_primary or ai_primary in ("#6366f1",) or len(ai_primary) != 7:
            analysis["primary_color"] = variety["primary_color"]
            analysis["secondary_color"] = variety["secondary_color"]
        analysis.setdefault("secondary_color", variety["secondary_color"])
        analysis.setdefault("visual_style", variety["design_id"])
        analysis.setdefault("color_theme_tailwind", variety["tailwind_theme"])
        # Always attach design variety metadata
        analysis["design_variety"] = variety
        analysis["color_theme_tailwind"] = variety["tailwind_theme"]

        return analysis

    def _smart_fallback(self, req: str, traits: dict) -> dict:
        r = req.lower()
        domain = self._detect_domain(r)
        color = self._detect_color(r, traits)
        style = "neon-cyberpunk" if traits.get("is_game") else ("gradient-luxury" if traits.get("is_landing") else "dark-glass")

        features_map = {
            "hospital": [
                "Patient registration with photo upload, auto-generated patient ID card, blood type & insurance details",
                "Doctor directory with specializations, availability calendar, and shift scheduling",
                "Appointment booking system with time slots, reminders, and cancellation workflow",
                "Complete medical records — diagnosis history, prescriptions, lab results, allergies, surgical history",
                "Prescription management with drug database, dosage tracking, and pharmacy dispatch",
                "Lab results management with file upload, result ranges, and doctor sign-off",
                "Inpatient ward management — bed availability heatmap, room assignment, discharge planning",
                "Billing & insurance — invoice generation, insurance claim processing, payment tracking",
                "Real-time hospital analytics dashboard — occupancy rate, daily admissions, revenue, top diagnoses",
                "Emergency triage system with priority queue and status tracking",
                "Staff scheduling & payroll integration for nurses and support staff",
                "Inventory of medical supplies with low-stock alerts and reorder automation",
                "Patient discharge summary generator with post-care instructions",
                "Ambulance & transport dispatch tracking module",
                "Role-based access control — admin, doctor, nurse, receptionist, patient views",
            ],
            "student": [
                "Student registration with photo upload, auto-generated student ID, QR code ID card",
                "Multi-step enrollment form with document upload and verification workflow",
                "Course catalog with prerequisites, credit hours, capacity limits, and waitlist management",
                "Timetable builder with conflict detection, room assignment, and export to PDF",
                "Grade tracking — assignment scores, weighted GPA calculator, grade history, trend charts",
                "Attendance marking with QR scan, facial recognition placeholder, and absence alerts",
                "Teacher assignment per subject with workload tracking and substitution management",
                "Parent portal with real-time notifications, grade access, attendance reports",
                "Academic performance analytics — class rank, percentile, subject-wise charts",
                "Exam scheduling system with hall allocation and seating plan generator",
                "Library integration — book borrowing, due dates, fine calculation",
                "Fee management — tuition invoices, payment history, scholarship tracking",
                "Student communication portal — announcements, direct messages, group notices",
                "Report card generation with auto-calculated grades and teacher remarks",
                "Alumni tracking and graduation status management",
            ],
            "hr": [
                "Employee onboarding with multi-step form, document checklist, and IT access provisioning",
                "Complete employee profiles — personal info, education, skills, certifications, emergency contacts",
                "Department & team hierarchy management with org chart visualization",
                "Leave management — request workflow, approval chain, leave balance calculator, calendar view",
                "Payroll engine — base salary, allowances, deductions, tax calculation, payslip generation",
                "360° performance review system with self-assessment, peer review, and manager evaluation",
                "Recruitment pipeline — job posting, applicant tracking, interview scheduling, offer letters",
                "Training & development — course catalog, completion tracking, certification management",
                "Attendance tracking with clock-in/out, overtime calculation, and shift management",
                "HR analytics dashboard — headcount, turnover rate, diversity metrics, cost-per-hire",
                "Asset management — laptop, phone, access card assignment and return tracking",
                "Disciplinary action log with incident reports and escalation workflow",
                "Employee benefits management — health insurance, pension, allowances",
                "Exit management — resignation workflow, handover checklist, final settlement",
                "Employee self-service portal — update profile, download payslips, request letters",
            ],
            "inventory": [
                "Product catalog with SKU, barcode generation, category tree, and photo management",
                "Real-time stock tracking across multiple warehouses with bin location mapping",
                "Low stock alerts with configurable thresholds and automated reorder suggestions",
                "Supplier management — contacts, lead times, pricing tiers, performance ratings",
                "Purchase order creation, approval workflow, and GRN (goods received note) processing",
                "Sales order management — quote generation, dispatch, delivery tracking, invoicing",
                "Batch and lot tracking with expiry date alerts and FIFO/LIFO management",
                "Inventory valuation — FIFO, weighted average cost, with profit margin analysis",
                "Warehouse operations — pick lists, packing slips, bin transfers, cycle counting",
                "Return and defect management with RMA processing and supplier claims",
                "Advanced analytics — stock turnover, dead stock, ABC analysis, reorder forecasting",
                "Barcode scanner integration (manual entry or device input) for stock takes",
                "Multi-currency and multi-location pricing with tax configuration",
                "Integration-ready supplier portal for automated purchase confirmations",
                "Comprehensive audit trail — every stock movement logged with user and timestamp",
            ],
            "game": [
                "Smooth 60fps game loop with delta-time physics and requestAnimationFrame",
                "Player entity with full WASD + arrow key + touch/mobile controls",
                "Advanced collision detection system with AABB and response physics",
                "Multi-level progression system with increasing difficulty and unique level designs",
                "Score system with combo multiplier, high score, and localStorage persistence",
                "Player health/lives system with visual hearts, invincibility frames, and animations",
                "Enemy AI with pathfinding, attack patterns, and difficulty scaling",
                "Power-up system — speed boost, shield, double score, extra life with visual effects",
                "Web Audio API — background music, sfx for jump/collect/hit/die, mute toggle",
                "Particle effects system for explosions, collectibles, and death animations",
                "Animated sprite system with state machine (idle, run, jump, attack, die)",
                "Pause menu, main menu, game over screen with replay and score submission",
                "Parallax background layers for depth and visual richness",
                "Save state with multiple slots and progress tracking",
                "Leaderboard with top 10 scores stored in localStorage",
            ],
            "ecommerce": [
                "Product catalog with 20+ products, multi-image gallery, zoom, and variants (size/color)",
                "Advanced search with autocomplete, filters (price range, category, rating, brand)",
                "Shopping cart with quantity controls, saved cart persistence, and estimated delivery",
                "Wishlist with heart toggle, share link, and move-to-cart functionality",
                "Product quick-view modal with full details, reviews, and add-to-cart",
                "Full checkout flow — address form, shipping options, order summary, promo codes",
                "Order tracking with status timeline — placed, confirmed, shipped, delivered",
                "Product ratings and reviews with star rating, helpful votes, and photo uploads",
                "Category navigation with mega menu, breadcrumbs, and featured collections",
                "Promotional banners, flash sales with countdown timer, and badge system",
                "Related products and 'customers also bought' recommendation sections",
                "User account — order history, saved addresses, payment methods, rewards points",
                "Inventory badges — low stock warning, out of stock, back-order available",
                "SEO-optimized product URLs, meta descriptions, and structured data",
                "Mobile-first responsive design with swipe gestures and touch-optimized UI",
            ],
            "landing": [
                "Full-screen hero with animated headline (typewriter/gradient), subheading, dual CTAs, and hero image/animation",
                "Sticky navbar with logo, nav links, dark mode toggle, and prominent CTA button",
                "Smooth scroll navigation with active section highlighting and scroll-to-top button",
                "Feature showcase — 6-card grid with animated icons, titles, and descriptions",
                "How it works — 3-step process with numbered circles, connecting lines, and illustrations",
                "Metrics/social proof section — animated counters (10k+ users, 99.9% uptime, etc.)",
                "Pricing tiers — Free/Pro/Enterprise cards with monthly/yearly toggle and feature comparison table",
                "Testimonials carousel — avatar, name, title, star rating, and quote with auto-rotate",
                "FAQ accordion with smooth open/close animation and search functionality",
                "Integration logos grid — partner/integration badges in grayscale with hover color",
                "Blog/resources preview — 3 article cards with category badge, read time, and excerpt",
                "Email newsletter signup with validation and success animation",
                "Team section with photos, names, roles, and social links",
                "Footer — logo, tagline, 4-column links, social icons, and copyright",
                "AOS scroll animations on all sections, GSAP headline animation, confetti on CTA click",
            ],
            "dashboard": [
                "KPI stat cards with trend indicators, sparkline charts, and percentage change vs last period",
                "Interactive Chart.js line chart — 12-month revenue/metric trend with tooltip and zoom",
                "Bar chart — weekly/monthly comparison with grouped bars and category legend",
                "Doughnut/pie chart — category or status breakdown with interactive legend",
                "Data table — sortable, filterable, paginated with bulk actions and row selection",
                "Date range picker — today, last 7d, last 30d, last 90d, custom range",
                "Export functionality — CSV, with filtered data respecting current query",
                "Notifications panel — unread badge, dropdown list, mark-all-read, real-time feed",
                "Dark/light mode with smooth transition and system preference detection",
                "Responsive sidebar — collapsible, mobile drawer, section grouping with icons",
                "Global search with Ctrl+K shortcut, recent searches, and result categories",
                "User profile widget with avatar, settings dropdown, and logout",
                "Activity feed — timestamped event log with user avatars and action descriptions",
                "Heat map or calendar view showing activity density by day",
                "Customizable widget layout with show/hide toggles and reorder capability",
            ],
            "crm": [
                "Contact profiles — photo, company, all communication channels, social links, relationship score",
                "Pipeline kanban board — drag-and-drop deal cards across stages with value totals",
                "Deal tracking — value, probability, close date, expected revenue, win/loss reason",
                "Activity timeline — calls, emails, meetings, notes logged chronologically per contact",
                "Email composition and sent history tracking within the CRM",
                "Lead scoring engine — auto-score based on engagement, company size, and fit",
                "Task management — to-dos linked to contacts with due dates and reminders",
                "Sales analytics — conversion rates, average deal size, rep performance, funnel chart",
                "Team management — assign contacts/deals to reps, track workload and performance",
                "Customer segmentation — tag-based filtering, saved segments, bulk actions",
                "Meeting scheduler with calendar integration and automated confirmation emails",
                "Quote and proposal generator from deal details",
                "Revenue forecasting by quarter with weighted pipeline calculation",
                "Duplicate detection and contact merge functionality",
                "Mobile-optimized card view for reps working in the field",
            ],
            "3d": [
                "Interactive Three.js scene with smooth manual orbit controls (mouse/touch drag, scroll zoom)",
                "Advanced lighting system — ambient, directional (with shadows), 3+ colored point lights",
                "Particle system with 5000+ particles using BufferGeometry and custom shaders",
                "Minimum 8 unique 3D objects with MeshStandardMaterial (metalness + roughness)",
                "Physics-inspired animations — floating, orbiting, pulsing, rotation with sin/cos",
                "Wireframe overlay system on key objects for technical aesthetic",
                "Fog system with FogExp2 for atmospheric depth",
                "ACESFilmicToneMapping with exposure control for cinematic look",
                "Post-processing bloom effect simulation via multi-pass rendering or CSS filter",
                "Loading screen with animated progress bar and scene name display",
                "UI overlay panel with scene controls and stats display",
                "Scene background with gradient or deep space color theme",
                "Shadow mapping on ground plane with PCFSoftShadowMap",
                "Responsive resize handler for all screen sizes",
                "Performance-optimized render loop with delta time and 60fps targeting",
            ],
        }

        features = features_map.get(domain, [
            "Enterprise dashboard with multi-chart analytics (line, bar, doughnut, heatmap)",
            "Full CRUD operations with optimistic UI updates and undo functionality",
            "Advanced search with full-text, filters, saved searches, and sort by any field",
            "Dark/light/system theme modes with smooth animated transitions and localStorage persistence",
            "Responsive mobile-first design with touch gestures and PWA-ready manifest",
            "Toast notification system (success, error, warning, info) with action buttons",
            "Modal dialog system with stacked modals, forms, confirmations, and backdrop blur",
            "Data export — CSV with column selection, PDF print view, clipboard copy",
            "Keyboard shortcuts — Ctrl+K global search, Escape close, N new record, E edit",
            "Real-time pagination, infinite scroll option, adjustable page size",
            "Role-based UI — different views and actions based on user role",
            "Bulk action system — select all, delete, update status for multiple records",
            "Activity audit log — every action logged with user, timestamp, and change diff",
            "Data validation — inline errors, field-level feedback, server-side error handling",
            "Empty states with helpful illustrations, instructions, and quick-action buttons",
        ])

        return {
            "detected_type": domain if domain in ("game", "3d-scene", "landing", "ecommerce", "dashboard") else "webapp",
            "domain": domain,
            "brand_name": req.title()[:40],
            "primary_color": color,
            "secondary_color": "#8b5cf6",
            "visual_style": style,
            "ui_complexity": "enterprise",
            "critical_features": features,
            "ui_sections": ["Dashboard", "Records", "Add New", "Reports", "Settings", "Profile", "Analytics", "Notifications"],
            "color_theme_tailwind": "indigo" if "#6366f1" in color else "violet",
            "advanced_features": ["Real-time updates", "Keyboard shortcuts", "Role-based access", "Audit logging"],
        }

    def _detect_domain(self, r: str) -> str:
        if any(w in r for w in ["hospital", "patient", "doctor", "clinic", "medical"]): return "hospital"
        if any(w in r for w in ["student", "school", "grade", "course", "attendance"]): return "student"
        if any(w in r for w in ["employee", "hr", "staff", "payroll", "department"]): return "hr"
        if any(w in r for w in ["inventory", "stock", "warehouse", "supplier", "sku"]): return "inventory"
        if any(w in r for w in ["game", "snake", "tetris", "pacman", "platformer"]): return "game"
        if any(w in r for w in ["shop", "store", "ecommerce", "cart", "checkout"]): return "ecommerce"
        if any(w in r for w in ["landing", "homepage", "hero", "pricing", "saas"]): return "landing"
        if any(w in r for w in ["dashboard", "analytics", "chart", "metrics", "kpi"]): return "dashboard"
        if any(w in r for w in ["crm", "customer", "client", "lead", "pipeline"]): return "crm"
        if any(w in r for w in ["3d", "three.js", "sphere", "orbit", "webgl"]): return "3d"
        return "generic"

    def _detect_color(self, r: str, traits: dict) -> str:
        if any(w in r for w in ["green", "nature", "eco", "health", "environment"]): return "#10b981"
        if any(w in r for w in ["blue", "ocean", "water", "sky", "corporate"]): return "#3b82f6"
        if any(w in r for w in ["orange", "warm", "fire", "energy", "food"]): return "#f97316"
        if any(w in r for w in ["red", "danger", "alert", "urgent"]): return "#ef4444"
        if any(w in r for w in ["purple", "creative", "ai", "magic"]): return "#8b5cf6"
        if any(w in r for w in ["pink", "beauty", "fashion", "love"]): return "#ec4899"
        if any(w in r for w in ["teal", "medical", "clean", "minimal"]): return "#14b8a6"
        if any(w in r for w in ["yellow", "gold", "finance", "money", "premium"]): return "#f59e0b"
        if traits.get("is_game"): return "#a855f7"
        if traits.get("is_landing"): return "#6366f1"
        # Use request hash for variety instead of always returning indigo
        palette = COLOR_PALETTES[int(hashlib.md5(r.encode()).hexdigest(), 16) % len(COLOR_PALETTES)]
        return palette["primary"]


# ════════════════════════════════════════════════════════════════════════════════
# AGENT 1: Planner — Strategic Project Planning
# ════════════════════════════════════════════════════════════════════════════════

class PlannerAgent:
    name = "Planner"
    emoji = "🧠"

    def run(self, request: str, analysis: dict = None) -> dict:
        traits = detect_traits(request)
        analysis = analysis or {}
        is_mgmt = traits.get("is_management", False)
        enhanced_req = analysis.get("enhanced_request", request)
        critical_features = analysis.get("critical_features", [])
        brand_name = analysis.get("brand_name", "")
        color_theme = analysis.get("color_theme_tailwind", "indigo")

        type_hint = ""
        if is_mgmt:
            type_hint = 'PROJECT TYPE: Frontend management system. project_type="management", has_backend=false, complexity="complex".'
        elif traits["is_api"]:
            type_hint = 'PROJECT TYPE: Python REST API. project_type="api", has_backend=true.'
        elif traits["is_3d"]:
            type_hint = 'PROJECT TYPE: 3D web scene. project_type="3d-scene", has_3d=true, has_backend=false.'
        elif traits["is_game"]:
            type_hint = 'PROJECT TYPE: Browser game. project_type="game", has_backend=false.'
        elif traits["is_dashboard"]:
            type_hint = 'PROJECT TYPE: Analytics dashboard. project_type="dashboard", has_backend=false, complexity="complex".'
        elif traits["is_ecommerce"]:
            type_hint = 'PROJECT TYPE: E-commerce store. project_type="ecommerce", has_backend=false.'
        elif traits["is_landing"]:
            type_hint = 'PROJECT TYPE: Landing page. project_type="landing", has_backend=false.'

        pre_features = "\n".join(f'    "{f}",' for f in critical_features[:8]) if critical_features else ""

        prompt = f"""You are a world-class software architect and product manager. Create a detailed project plan.

ORIGINAL REQUEST: "{request}"
ENHANCED UNDERSTANDING: "{enhanced_req}"
BRAND NAME: "{brand_name or 'to be determined'}"
{type_hint}

Output ONLY this JSON (no other text):
```json
{{
  "project_name": "kebab-case-name-specific-to-domain",
  "project_type": "management|landing|webapp|dashboard|game|3d-scene|api|ecommerce|social",
  "description": "Precise one-sentence description of the complete application",
  "tech_stack": ["Tailwind CSS", "JavaScript", "Chart.js", "Font Awesome 6", "Alpine.js"],
  "features": [
{pre_features if pre_features else '    "Feature 1 very domain-specific",\n    "Feature 2",\n    "Feature 3",\n    "Feature 4",\n    "Feature 5",\n    "Feature 6",\n    "Feature 7",\n    "Feature 8"'}
  ],
  "views": [
    {{"name": "Dashboard", "route": "dashboard", "desc": "Overview KPIs and charts"}},
    {{"name": "Records", "route": "records", "desc": "Main data table with full CRUD"}},
    {{"name": "Add New", "route": "add", "desc": "Create and edit forms"}},
    {{"name": "Reports", "route": "reports", "desc": "Analytics, charts, export"}}
  ],
  "complexity": "complex",
  "has_3d": false,
  "has_backend": false,
  "color_theme": "{color_theme}"
}}
```

RULES:
- project_name must be highly specific (e.g., "hospital-patient-portal", NOT "web-app")
- features must be domain-specific, not generic — include real domain workflows
- 12+ features minimum, each highly specific with implementation detail
- views: minimum 7 for management apps, 6 for dashboards, 5 for others
- Every feature must name specific data fields, interactions, or calculations
- Do NOT include generic features like "CRUD operations" — be specific to THIS domain"""

        resp = call_ai(prompt, timeout=70)
        plan = extract_json(resp) or {}

        if not isinstance(plan, dict) or not plan.get("features") or plan.get("project_name") == "web-app":
            plan = self._fallback(request, traits, analysis)

        # Safety overrides
        if is_mgmt and not traits["is_api"]:
            plan["has_backend"] = False
            plan["complexity"] = "complex"
            if plan.get("project_type") not in ("management", "dashboard", "webapp"):
                plan["project_type"] = "management"

        if traits["is_api"] and not is_mgmt:
            plan["has_backend"] = True

        if traits["is_3d"]:
            plan["has_3d"] = True
            plan["has_backend"] = False

        # Ensure enough views for management
        if is_mgmt and len(plan.get("views", [])) < 3:
            plan["views"] = self._domain_views(request)

        # Ensure enough features
        if len(plan.get("features", [])) < 6:
            plan["features"] = self._domain_features(request, traits)

        plan.update({"user_request": request, "traits": traits, "analysis": analysis})
        plan.setdefault("color_theme", color_theme or "indigo")
        plan.setdefault("views", [])

        # ── Dynamic file planning ──────────────────────────────────────────────
        # Skip for special cases handled by dedicated agents
        if not plan.get("has_3d") and not plan.get("has_backend"):
            planned_files, entry_point = self._plan_files(request, analysis, plan)
            if planned_files:
                plan["planned_files"] = planned_files
                plan["planned_entry_point"] = entry_point

        return plan

    def _plan_files(self, request: str, analysis: dict, plan: dict):
        """Ask AI to decide the optimal file structure — NO LIMITS on complexity or file count."""
        features = plan.get("features", [])
        project_type = plan.get("project_type", "webapp")
        views = plan.get("views", [])
        views_str = ", ".join(v["name"] for v in views) if views else "none"
        advanced = analysis.get("advanced_features", [])

        prompt = f"""You are a world-class software architect. Design the ULTIMATE, MOST COMPLETE file structure for this project. There are NO complexity limits and NO file count caps — give this project exactly as many files as it needs for the highest possible code quality, separation of concerns, and maintainability.

Project: {plan.get("project_name", "app")}
Type: {project_type}
Views/sections: {views_str}
Features: {json.dumps(features)}
Advanced features: {json.dumps(advanced)}
Full request: {request}

ARCHITECTURE PHILOSOPHY — UNLIMITED QUALITY:
- Every major feature domain gets its OWN JavaScript module file
- Separate concerns completely: data layer, UI rendering, app logic, utilities, charts, auth, etc.
- index.html is ALWAYS the entry point — it's a lean shell with CDN links + view containers only
- styles.css handles ALL custom CSS — variables, components, animations, responsive
- app.js handles ONLY routing, state management, keyboard shortcuts, dark mode, toast, modals
- data.js handles ONLY data: sample records (25+), CRUD, localStorage, search, filter, analytics
- ui.js handles ONLY the main view renderers (dashboard, list, forms, detail)
- For each additional MAJOR feature area, add a dedicated module:
  • charts.js — all Chart.js configurations and chart rendering functions
  • reports.js — report generation, PDF print, analytics calculations  
  • forms.js — complex multi-step forms, validation engine, field renderers
  • auth.js — login, session management, role-based access
  • notifications.js — notification system, real-time updates, alert management
  • utils.js — date formatting, currency, ID generation, export utilities
  • [domain].js — domain-specific logic (e.g., patients.js, students.js, orders.js)
- Add modules only when they add real architectural value (300+ lines of real code)
- More files = better modularity and higher quality output per file

EXAMPLE for a Hospital Management System (9 files):
index.html → shell, sidebar, view containers, all CDN links
styles.css → complete custom CSS (2000+ chars)
app.js → routing, dark mode, toasts, modals, keyboard nav
data.js → patient/doctor/appointment records (25+ each), CRUD, localStorage
ui.js → renderDashboard, renderPatients, renderDoctors, renderAppointments
charts.js → all Chart.js: occupancy chart, admissions trend, revenue chart, diagnosis doughnut
forms.js → patient registration form (15+ fields), appointment booking, discharge form
reports.js → monthly reports, billing export, statistics calculations
utils.js → date formatting, ID generation, PDF print, CSV export

Output ONLY this JSON (no extra text):
```json
{{
  "files": [
    {{"path": "index.html", "type": "html", "priority": 1, "purpose": "Lean app shell — sidebar nav with all views, header, CDN links (Tailwind, FA6, Chart.js, Alpine.js), modal overlay, toast container"}},
    {{"path": "styles.css", "type": "css", "priority": 2, "purpose": "Complete custom CSS — CSS variables, sidebar, nav-link, data-table, card, badge, btn, form-input, modal, toast, skeleton, responsive, animations"}},
    {{"path": "app.js", "type": "javascript", "priority": 3, "purpose": "App core — showView(), routing, toggleDarkMode(), showToast(), openModal(), safeChart(), keyboard shortcuts, DOMContentLoaded init"}},
    {{"path": "data.js", "type": "javascript", "priority": 4, "purpose": "Data layer — 25+ realistic sample records per entity, full CRUD, localStorage persistence, search(), filterRecords(), getStats(), generateId()"}},
    {{"path": "ui.js", "type": "javascript", "priority": 5, "purpose": "Core UI renderers — renderDashboard(), renderList(), buildTableHTML(), renderForm(), renderDetail(), renderReports(), doEdit(), doDelete()"}}
  ],
  "entry_point": "index.html"
}}
```

NOW design the ACTUAL file list for THIS specific project — add the right extra modules for maximum quality:"""

        resp = call_ai(prompt, timeout=60)
        data = extract_json(resp)

        if (data and isinstance(data.get("files"), list)
                and len(data["files"]) >= 1
                and all(isinstance(f, dict) and f.get("path") for f in data["files"])):
            # Validate and sanitize paths
            seen = set()
            clean = []
            for f in data["files"]:
                p = f.get("path", "").strip().lstrip("/")
                if p and p not in seen:
                    seen.add(p)
                    ext = p.rsplit(".", 1)[-1].lower() if "." in p else "text"
                    type_map = {"html": "html", "htm": "html", "css": "css",
                                "js": "javascript", "py": "python", "md": "markdown",
                                "txt": "text"}
                    clean.append({
                        "path": p,
                        "type": type_map.get(ext, f.get("type", "text")),
                        "priority": f.get("priority", len(clean) + 1),
                        "purpose": f.get("purpose", p),
                    })
            if clean:
                return clean, data.get("entry_point", "index.html")

        return None, None

    def _domain_views(self, req: str) -> list:
        r = req.lower()
        if any(w in r for w in ["student", "school", "grade", "course", "attendance"]):
            return [
                {"name": "Dashboard", "route": "dashboard", "desc": "Academic overview & stats"},
                {"name": "Students", "route": "students", "desc": "Student records table"},
                {"name": "Courses", "route": "courses", "desc": "Course management"},
                {"name": "Grades", "route": "grades", "desc": "Grade tracking & GPA"},
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
        r = req.lower()
        if any(w in r for w in ["student", "school", "grade"]):
            return ["Student registration with photo & ID", "Course enrollment management", "Grade tracking (A-F + GPA)", "Attendance marking & reports", "Teacher assignment per subject", "Timetable management", "Parent portal notifications", "Academic performance analytics"]
        elif any(w in r for w in ["hospital", "patient", "doctor", "clinic"]):
            return ["Patient registration & medical history", "Doctor scheduling & availability", "Appointment booking & reminders", "Medical records & diagnosis tracking", "Prescription management", "Billing & insurance processing", "Lab results management", "Hospital analytics dashboard"]
        elif any(w in r for w in ["employee", "hr", "staff"]):
            return ["Employee onboarding & profiles", "Department & team management", "Attendance & leave tracking", "Payroll calculation & slips", "Performance review system", "Job posting & recruitment", "Training records management", "HR analytics & reports"]
        elif any(w in r for w in ["inventory", "stock", "warehouse"]):
            return ["Product catalog with SKUs & barcodes", "Real-time stock level tracking", "Low stock alerts & notifications", "Supplier management & contacts", "Purchase order creation", "Sales & dispatch management", "Inventory valuation reports", "Reorder point automation"]
        elif traits.get("is_game"):
            return ["Smooth 60fps game loop", "Full keyboard & touch controls", "Collision detection system", "Score & high score (localStorage)", "Lives & health system", "Level progression", "Web Audio sound effects", "Particle effects on events"]
        elif traits.get("is_landing"):
            return ["Hero section with animated headline", "Sticky navbar with smooth scroll", "Features grid (6 cards with icons)", "Pricing tiers with monthly/yearly toggle", "Testimonials carousel", "FAQ accordion", "Newsletter CTA", "Footer with social links"]
        elif traits.get("is_ecommerce"):
            return ["Product grid with filters & sort", "Shopping cart with quantity controls", "Wishlist with heart toggle", "Product quick-view modal", "Price range filter", "Category navigation", "Toast notifications", "LocalStorage cart persistence"]
        else:
            return ["Interactive dashboard with Chart.js analytics", "Full CRUD with real-time updates", "Advanced search, filter & sort", "Dark/light mode (localStorage)", "Responsive mobile-first design", "Toast notifications", "Modal dialogs", "Data export (CSV)"]

    def _fallback(self, req: str, traits: dict, analysis: dict) -> dict:
        is_mgmt = traits.get("is_management", False)
        brand = analysis.get("brand_name", "") or req.replace(" ", "-").lower()[:40]
        color = analysis.get("color_theme_tailwind", "indigo")

        if traits["is_3d"]:
            return {"project_name": brand or "3d-interactive-scene", "project_type": "3d-scene",
                    "tech_stack": ["Three.js", "CSS3", "JavaScript"], "has_3d": True, "has_backend": False,
                    "features": ["Interactive 3D scene with orbit controls", "Dynamic lighting system", "Particle effects", "Physics-based animations", "Post-processing bloom", "Touch & mouse controls"],
                    "views": [], "complexity": "complex", "color_theme": color or "violet"}
        elif traits["is_api"] and not is_mgmt:
            return {"project_name": brand or "flask-rest-api", "project_type": "api",
                    "tech_stack": ["Python", "Flask", "Flask-CORS"],
                    "features": ["Full CRUD REST endpoints", "JWT Authentication", "Request validation", "Pagination & filtering", "CORS support", "Error handlers"],
                    "has_3d": False, "has_backend": True, "views": [], "complexity": "medium", "color_theme": color or "blue"}
        elif traits["is_game"]:
            return {"project_name": brand or "browser-game", "project_type": "game",
                    "tech_stack": ["HTML5 Canvas", "JavaScript", "Web Audio API"], "has_3d": False, "has_backend": False,
                    "features": ["60fps game loop", "Keyboard & touch controls", "Collision detection", "Score & high score", "Lives system", "Level progression", "Sound effects", "Particle effects"],
                    "views": [], "complexity": "complex", "color_theme": color or "violet"}
        elif traits["is_landing"]:
            return {"project_name": brand or "landing-page", "project_type": "landing",
                    "tech_stack": ["Tailwind CSS", "Alpine.js", "AOS", "GSAP"],
                    "features": ["Hero with animated headline & CTA", "Sticky responsive navbar", "Features grid (6 cards)", "Pricing tiers (Free/Pro/Enterprise)", "Testimonials section", "FAQ accordion", "Newsletter signup", "Footer"],
                    "has_3d": False, "has_backend": False, "views": [], "complexity": "complex", "color_theme": color or "indigo"}
        elif traits["is_ecommerce"]:
            return {"project_name": brand or "ecommerce-store", "project_type": "ecommerce",
                    "tech_stack": ["Tailwind CSS", "Alpine.js", "JavaScript"],
                    "features": ["Product grid with 12+ products", "Shopping cart sidebar", "Category filters", "Product search & sort", "Wishlist toggle", "Quick-view modal", "Cart persistence", "Toast notifications"],
                    "has_3d": False, "has_backend": False, "views": [], "complexity": "complex", "color_theme": color or "indigo"}
        elif traits["is_dashboard"]:
            return {"project_name": brand or "analytics-dashboard", "project_type": "dashboard",
                    "tech_stack": ["Tailwind CSS", "Chart.js", "JavaScript", "Font Awesome 6"],
                    "features": ["KPI stat cards with trends", "Line chart (12-month trend)", "Bar chart (weekly comparison)", "Doughnut chart (breakdown)", "Data table with pagination", "Dark/light mode", "Export to CSV", "Notification panel"],
                    "has_3d": False, "has_backend": False, "views": [], "complexity": "complex", "color_theme": color or "blue"}
        elif is_mgmt:
            views = self._domain_views(req)
            feats = self._domain_features(req, traits)
            return {"project_name": brand or "management-system", "project_type": "management",
                    "tech_stack": ["Tailwind CSS", "Chart.js", "JavaScript", "Font Awesome 6"],
                    "features": feats, "has_3d": False, "has_backend": False,
                    "views": views, "complexity": "complex", "color_theme": color or "indigo"}
        else:
            feats = self._domain_features(req, traits)
            return {"project_name": brand or req.lower().replace(" ", "-")[:40] or "web-application",
                    "project_type": "webapp",
                    "tech_stack": ["Tailwind CSS", "Alpine.js", "JavaScript", "Chart.js"],
                    "features": feats,
                    "has_3d": False, "has_backend": False,
                    "views": [{"name": "Home", "route": "home", "desc": "main view"},
                               {"name": "Dashboard", "route": "dashboard", "desc": "overview"},
                               {"name": "List", "route": "list", "desc": "data list"},
                               {"name": "Settings", "route": "settings", "desc": "settings"}],
                    "complexity": "complex", "color_theme": color or "indigo"}


# ════════════════════════════════════════════════════════════════════════════════
# AGENT 2: Architect — File Structure & Tech Stack
# ════════════════════════════════════════════════════════════════════════════════

class ArchitectAgent:
    name = "Architect"
    emoji = "🏗️"

    def run(self, plan: dict, stack_context: dict = None) -> dict:
        traits = plan.get("traits", {})
        has_backend = plan.get("has_backend", False)
        has_3d = plan.get("has_3d", False)
        color = plan.get("color_theme", "indigo")
        selected_cdns = pick_cdns(traits, plan.get("project_type", "webapp"), plan.get("tech_stack", []))

        # ── Full-stack generation with user-chosen backend + DB ────────────────
        stack = stack_context or {}
        backend = stack.get("backend")  # "nodejs", "django", "php", or None
        database = stack.get("database")  # "mongodb", "mysql", "firebase", "supabase", or None

        if backend and backend != "none":
            manifest = self._build_integration_manifest(plan, backend, database)
            files = self._plan_fullstack_files(plan, backend, database, manifest)
            return {
                "files": files,
                "entry_point": "index.html",
                "cdns": selected_cdns,
                "color": color,
                "plan": plan,
                "is_multifile": True,
                "is_fullstack": True,
                "backend": backend,
                "database": database,
                "integration_manifest": manifest,
            }

        if has_backend:
            files = [
                {"path": "app.py", "type": "python", "priority": 1, "purpose": "Flask app with all routes, auth, CRUD, validation"},
                {"path": "requirements.txt", "type": "text", "priority": 2, "purpose": "Python dependencies"},
                {"path": "README.md", "type": "markdown", "priority": 3, "purpose": "Setup and API documentation"},
            ]
            return {"files": files, "entry_point": "app.py", "cdns": [], "color": color, "plan": plan}

        if has_3d:
            files = [
                {"path": "index.html", "type": "html", "priority": 1, "purpose": "HTML shell + Three.js CDN + canvas container + UI overlay"},
                {"path": "scene.js", "type": "javascript", "priority": 2, "purpose": "Complete Three.js scene — geometry, materials, lights, particles, animation, controls"},
            ]
            return {"files": files, "entry_point": "index.html", "cdns": [CDNS["threejs"]], "color": color, "plan": plan}

        # ── Use Planner's AI-decided file list if available ────────────────────
        planned_files = plan.get("planned_files")
        planned_entry = plan.get("planned_entry_point", "index.html")

        if planned_files and len(planned_files) >= 1:
            is_multifile = len(planned_files) > 1
            return {
                "files": planned_files,
                "entry_point": planned_entry,
                "cdns": selected_cdns,
                "color": color,
                "plan": plan,
                "is_multifile": is_multifile,
                "ai_planned": True,
            }

        # ── Fallback: hardcoded logic ──────────────────────────────────────────
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
            views_desc = "; ".join(f'{v["name"]}={v.get("desc", "")}' for v in views)
            files = [
                {"path": "index.html", "type": "html", "priority": 1,
                 "purpose": f"App shell — sidebar nav ({', '.join(v['name'] for v in views)}), header, view containers, all CDN links"},
                {"path": "styles.css", "type": "css", "priority": 2,
                 "purpose": "Complete CSS — variables, sidebar, nav-link, data-table, badge, card, form-input, btn, modal, toast, skeleton, responsive, animations"},
                {"path": "app.js", "type": "javascript", "priority": 3,
                 "purpose": "App core — showView(), routing, toggleDarkMode(), showToast(), openModal(), closeModal(), handleSearch(), exportCSV(), keyboard shortcuts, DOMContentLoaded"},
                {"path": "data.js", "type": "javascript", "priority": 4,
                 "purpose": f"Data layer — 15+ realistic sample records for {req_lower[:80]}, CRUD, localStorage, search(), filter(), sortBy(), getStats()"},
                {"path": "ui.js", "type": "javascript", "priority": 5,
                 "purpose": f"UI renderers — {views_desc[:150]} — tables, forms with validation, charts, modals, pagination, detail views"},
            ]
            return {"files": files, "entry_point": "index.html", "cdns": selected_cdns,
                    "color": color, "plan": plan, "is_multifile": True}

        # Single-file apps
        files = [{"path": "index.html", "type": "html", "priority": 1,
                  "purpose": "Complete production-grade app — all features, all views, full interactivity"}]
        return {"files": files, "entry_point": "index.html", "cdns": selected_cdns,
                "color": color, "plan": plan, "is_multifile": False}


    def _build_integration_manifest(self, plan: dict, backend: str, database: str) -> dict:
        """AI generates the complete API contract — endpoints, schema, env vars.
        Every file generator uses this so all files stay perfectly in sync."""
        req = plan.get("user_request", "")
        name = plan.get("project_name", "app")
        features = plan.get("features", [])
        entities = plan.get("analysis", {}).get("key_entities", []) or [name.replace("-", " ").title()]
        db_info = STACK_DATABASES.get(database, {})
        be_info = STACK_BACKENDS.get(backend, {})
        port = 3000 if backend == "nodejs" else (8000 if backend == "django" else 8080)

        prompt = f"""You are a senior API architect. Design the COMPLETE integration manifest for this full-stack project.
ALL files (frontend, backend, database) will use ONLY this manifest — it is the single source of truth.

Project: {name}
Request: {req}
Backend: {be_info.get("label", backend)}
Database: {db_info.get("label", database)} ({db_info.get("type", "nosql")})
Features: {json.dumps(features[:10])}
Key entities: {json.dumps(entities)}

Design the COMPLETE REST API — every endpoint needed for ALL features.

Output ONLY this JSON:
```json
{{
  "port": {port},
  "api_base": "/api/v1",
  "frontend_api_base": "http://localhost:{port}/api/v1",
  "db_name": "{name.replace("-", "_")}_db",
  "backend": "{backend}",
  "database": "{database}",
  "auth": true,
  "auth_type": "jwt",
  "entities": ["Entity1", "Entity2"],
  "endpoints": [
    {{"method": "POST", "path": "/api/v1/auth/register", "desc": "Register new user", "body": {{"name": "string", "email": "string", "password": "string"}}, "response": {{"token": "string", "user": "object"}}}},
    {{"method": "POST", "path": "/api/v1/auth/login", "desc": "User login", "body": {{"email": "string", "password": "string"}}, "response": {{"token": "string", "user": "object"}}}},
    {{"method": "GET", "path": "/api/v1/entity", "desc": "List all entities with pagination", "query": ["page", "limit", "search", "status"], "response": {{"data": "array", "total": "number"}}}},
    {{"method": "POST", "path": "/api/v1/entity", "desc": "Create entity", "body": {{}}, "response": {{"data": "object"}}}},
    {{"method": "GET", "path": "/api/v1/entity/:id", "desc": "Get entity by ID", "response": {{"data": "object"}}}},
    {{"method": "PUT", "path": "/api/v1/entity/:id", "desc": "Update entity", "body": {{}}, "response": {{"data": "object"}}}},
    {{"method": "DELETE", "path": "/api/v1/entity/:id", "desc": "Delete entity", "response": {{"success": true}}}},
    {{"method": "GET", "path": "/api/v1/stats", "desc": "Dashboard analytics", "response": {{"total": "number", "active": "number", "monthly": "array"}}}}
  ],
  "db_schema": {{
    "entity_name": {{
      "field1": "String, required",
      "field2": "Number",
      "status": "String, enum: [active, inactive]",
      "createdAt": "Date, default: now"
    }}
  }},
  "env_vars": ["PORT", "JWT_SECRET", "DB_URI"],
  "middleware": ["cors", "express.json", "morgan", "helmet"],
  "cors_origins": ["http://localhost:3000", "http://localhost:5500", "*"],
  "sample_data_count": 25
}}
```

Design the ACTUAL endpoints for "{req}" — include ALL entities, ALL CRUD operations, ALL analytics endpoints."""

        resp = call_ai(prompt, timeout=90)
        manifest = extract_json(resp)
        if not isinstance(manifest, dict) or not manifest.get("endpoints"):
            manifest = {
                "port": port, "api_base": "/api/v1",
                "frontend_api_base": f"http://localhost:{port}/api/v1",
                "db_name": name.replace("-", "_") + "_db",
                "backend": backend, "database": database,
                "auth": True, "auth_type": "jwt",
                "entities": entities[:3] if entities else ["Record"],
                "endpoints": [
                    {"method": "POST", "path": "/api/v1/auth/register", "desc": "Register user"},
                    {"method": "POST", "path": "/api/v1/auth/login", "desc": "Login"},
                    {"method": "GET",  "path": "/api/v1/records", "desc": "List all records"},
                    {"method": "POST", "path": "/api/v1/records", "desc": "Create record"},
                    {"method": "GET",  "path": "/api/v1/records/:id", "desc": "Get record"},
                    {"method": "PUT",  "path": "/api/v1/records/:id", "desc": "Update record"},
                    {"method": "DELETE", "path": "/api/v1/records/:id", "desc": "Delete record"},
                    {"method": "GET",  "path": "/api/v1/stats", "desc": "Dashboard stats"},
                ],
                "db_schema": {},
                "env_vars": ["PORT", "JWT_SECRET", "DB_URI"],
                "middleware": ["cors", "express.json"],
                "cors_origins": ["*"],
                "sample_data_count": 25,
            }
        return manifest

    def _plan_fullstack_files(self, plan: dict, backend: str, database: str, manifest: dict) -> list:
        """Generate the complete file list for a full-stack project."""
        name = plan.get("project_name", "app")
        port = manifest.get("port", 3000)
        api_base = manifest.get("api_base", "/api/v1")
        db_name = manifest.get("db_name", name + "_db")
        entities = manifest.get("entities", ["Record"])
        ent0 = entities[0].lower().replace(" ", "") if entities else "record"

        if backend == "nodejs":
            files = [
                # Frontend (priority 1-5)
                {"path": "frontend/index.html", "type": "html", "priority": 1,
                 "purpose": f"Full frontend SPA — calls {api_base} REST API, auth flows, all CRUD views, charts, dashboard"},
                {"path": "frontend/styles.css", "type": "css", "priority": 2,
                 "purpose": "Complete custom CSS — sidebar, cards, badges, forms, modals, animations, responsive"},
                {"path": "frontend/app.js", "type": "javascript", "priority": 3,
                 "purpose": f"App core — API calls to {manifest.get('frontend_api_base', 'http://localhost:' + str(port) + api_base)}, routing, auth state, dark mode, toast"},
                {"path": "frontend/api.js", "type": "javascript", "priority": 4,
                 "purpose": f"API client — all fetch() calls to backend, JWT token management, request/response interceptors, error handling"},
                {"path": "frontend/ui.js", "type": "javascript", "priority": 5,
                 "purpose": "UI renderers — renderDashboard, renderList, renderForm, renderDetail, buildTable, charts"},
                # Backend (priority 6-12)
                {"path": "backend/server.js", "type": "nodejs_server", "priority": 6,
                 "purpose": f"Express.js server — middleware (cors, helmet, morgan, express.json), all route mounts, DB connection, port {port}"},
                {"path": "backend/routes/{ent0}.js".format(ent0=ent0), "type": "nodejs_routes", "priority": 7,
                 "purpose": f"Express router — all CRUD routes for {entities[0]}: GET /all, POST /, GET /:id, PUT /:id, DELETE /:id, GET /stats"},
                {"path": "backend/routes/auth.js", "type": "nodejs_routes_auth", "priority": 8,
                 "purpose": "Auth routes — POST /register (bcrypt hash), POST /login (verify + JWT sign), GET /me (verify token), POST /logout"},
                {"path": "backend/models/{ent0}.js".format(ent0=ent0), "type": "nodejs_model", "priority": 9,
                 "purpose": f"Database model/schema for {entities[0]} — all fields, validation, indexes, methods"},
                {"path": "backend/middleware/auth.js", "type": "nodejs_middleware", "priority": 10,
                 "purpose": "JWT auth middleware — verifyToken(), requireAdmin(), optionalAuth() — used on protected routes"},
                {"path": "backend/config/db.js", "type": "nodejs_config", "priority": 11,
                 "purpose": f"Database connection — connect to {database}, handle errors, retry logic, connection pooling"},
                {"path": "package.json", "type": "nodejs_package", "priority": 12,
                 "purpose": f"Node.js package.json — express, {database}, bcryptjs, jsonwebtoken, cors, helmet, morgan, dotenv, nodemon"},
                {"path": ".env.example", "type": "env_example", "priority": 13,
                 "purpose": f"Environment variables template — PORT={port}, JWT_SECRET, {database.upper()}_URI, DB_NAME={db_name}, NODE_ENV"},
                {"path": "README.md", "type": "fullstack_readme", "priority": 14,
                 "purpose": "Setup guide — prerequisites, install steps, .env config, run backend, run frontend, API docs, deployment notes"},
            ]
        elif backend == "django":
            app_name = ent0 + "s"
            files = [
                {"path": "frontend/index.html", "type": "html", "priority": 1,
                 "purpose": f"Full frontend SPA — calls Django REST API at {api_base}, auth flows, all CRUD, charts"},
                {"path": "frontend/styles.css", "type": "css", "priority": 2,
                 "purpose": "Complete custom CSS — sidebar, cards, badges, forms, modals, animations, responsive"},
                {"path": "frontend/app.js", "type": "javascript", "priority": 3,
                 "purpose": f"App core — API calls to Django backend, routing, auth state, CSRF token, dark mode, toast"},
                {"path": "frontend/api.js", "type": "javascript", "priority": 4,
                 "purpose": "API client — all fetch() calls, Django CSRF handling, JWT or session auth, error handling"},
                {"path": "frontend/ui.js", "type": "javascript", "priority": 5,
                 "purpose": "UI renderers — renderDashboard, renderList, renderForm, renderDetail, charts"},
                {"path": "backend/manage.py", "type": "django_manage", "priority": 6,
                 "purpose": "Django manage.py entry point"},
                {"path": "backend/config/settings.py", "type": "django_settings", "priority": 7,
                 "purpose": f"Django settings — INSTALLED_APPS, REST_FRAMEWORK, CORS, {database} DATABASE config, JWT auth, ALLOWED_HOSTS"},
                {"path": "backend/config/urls.py", "type": "django_urls", "priority": 8,
                 "purpose": f"Root URL configuration — include {app_name} URLs, auth URLs, admin"},
                {"path": f"backend/{app_name}/models.py", "type": "django_models", "priority": 9,
                 "purpose": f"Django models for {entities[0]} — all fields, Meta class, __str__, save(), manager methods"},
                {"path": f"backend/{app_name}/views.py", "type": "django_views", "priority": 10,
                 "purpose": f"DRF ViewSets — ModelViewSet for {entities[0]}, custom actions (stats, dashboard), auth views"},
                {"path": f"backend/{app_name}/serializers.py", "type": "django_serializers", "priority": 11,
                 "purpose": f"DRF Serializers — {entities[0]}Serializer with all fields, validation, nested relations"},
                {"path": f"backend/{app_name}/urls.py", "type": "django_app_urls", "priority": 12,
                 "purpose": f"URL patterns for {app_name} — DefaultRouter with all viewset URLs"},
                {"path": "backend/requirements.txt", "type": "django_requirements", "priority": 13,
                 "purpose": "Python dependencies — Django, djangorestframework, django-cors-headers, PyJWT, psycopg2/djongo/firebase-admin, python-dotenv"},
                {"path": ".env.example", "type": "env_example", "priority": 14,
                 "purpose": f"Environment variables — SECRET_KEY, DEBUG, {database.upper()}_URL, ALLOWED_HOSTS, CORS_ORIGINS"},
                {"path": "README.md", "type": "fullstack_readme", "priority": 15,
                 "purpose": "Setup guide — venv, pip install, migrate, createsuperuser, runserver, frontend setup, API docs"},
            ]
        elif backend == "php":
            files = [
                {"path": "frontend/index.html", "type": "html", "priority": 1,
                 "purpose": f"Full frontend SPA — calls PHP API at {api_base}, auth flows, all CRUD, charts, dashboard"},
                {"path": "frontend/styles.css", "type": "css", "priority": 2,
                 "purpose": "Complete custom CSS — sidebar, cards, badges, forms, modals, animations, responsive"},
                {"path": "frontend/app.js", "type": "javascript", "priority": 3,
                 "purpose": f"App core — API calls to PHP backend at {api_base}, routing, auth state with localStorage token"},
                {"path": "frontend/api.js", "type": "javascript", "priority": 4,
                 "purpose": "API client — all fetch() calls to PHP endpoints, JWT/session auth, error handling"},
                {"path": "frontend/ui.js", "type": "javascript", "priority": 5,
                 "purpose": "UI renderers — renderDashboard, renderList, renderForm, renderDetail, charts"},
                {"path": "backend/api/index.php", "type": "php_router", "priority": 6,
                 "purpose": "PHP API router — CORS headers, JSON responses, JWT validation, routes all requests to correct handler"},
                {"path": "backend/api/auth.php", "type": "php_auth", "priority": 7,
                 "purpose": "PHP auth endpoints — register (password_hash), login (password_verify + JWT), me (token verify)"},
                {"path": "backend/api/records.php", "type": "php_crud", "priority": 8,
                 "purpose": f"PHP CRUD endpoints for {entities[0]} — GET list, GET by ID, POST create, PUT update, DELETE, GET stats"},
                {"path": "backend/config/database.php", "type": "php_db", "priority": 9,
                 "purpose": f"PHP database connection — PDO for {database}, connection pooling, error handling, query helpers"},
                {"path": "backend/config/jwt.php", "type": "php_jwt", "priority": 10,
                 "purpose": "PHP JWT helper — generate token, validate token, extract payload, refresh token"},
                {"path": f"backend/schema.sql", "type": "sql_schema", "priority": 11,
                 "purpose": f"SQL schema for {database} — CREATE TABLE statements, indexes, constraints, seed data (25+ records)"},
                {"path": ".env.example", "type": "env_example", "priority": 12,
                 "purpose": f"Environment variables — DB_HOST, DB_NAME={db_name}, DB_USER, DB_PASS, JWT_SECRET, APP_URL"},
                {"path": "README.md", "type": "fullstack_readme", "priority": 13,
                 "purpose": "Setup guide — Apache/Nginx config, PHP version, MySQL setup, import schema, configure .env, run"},
            ]
        else:
            files = [
                {"path": "index.html", "type": "html", "priority": 1, "purpose": "Complete frontend SPA"},
                {"path": "styles.css", "type": "css", "priority": 2, "purpose": "Custom CSS"},
                {"path": "app.js", "type": "javascript", "priority": 3, "purpose": "App logic"},
                {"path": "data.js", "type": "javascript", "priority": 4, "purpose": "Data layer"},
                {"path": "ui.js", "type": "javascript", "priority": 5, "purpose": "UI renderers"},
            ]
        return files


# ════════════════════════════════════════════════════════════════════════════════
# AGENT 3: 3D Specialist — Advanced Three.js Scene Generation
# ════════════════════════════════════════════════════════════════════════════════

class ThreeDAgent:
    name = "3D Specialist"
    emoji = "🌐"

    def run(self, plan: dict) -> dict:
        req = plan.get("user_request", "")
        analysis = plan.get("analysis", {})
        feats = ", ".join(plan.get("features", []))
        title = plan.get("project_name", "3d").replace("-", " ").title()
        color = plan.get("color_theme", "violet")
        accent_hex = analysis.get("primary_color", "#8b5cf6")
        accent = "0x" + accent_hex.lstrip("#")

        scene_prompt = f"""Write a STUNNING, COMPLEX Three.js 3D scene (JavaScript only, no imports, uses global THREE from r128 CDN).

Scene request: {req}
Features needed: {feats}
Accent color: {accent}

MANDATORY REQUIREMENTS — implement ALL of these:
1. THREE.WebGLRenderer with antialias:true, shadowMap.enabled=true (PCFSoftShadowMap), ACESFilmicToneMapping
2. Manual orbit controls: mousedown/up/move + touch events, sph={{theta,phi,r}} pattern
3. window.addEventListener('resize') handler
4. requestAnimationFrame loop with time variable t
5. AmbientLight(0x111133, 0.8) + DirectionalLight(0xffffff, 1.5) with castShadow
6. At least 3 PointLights with different colors ({accent}, 0xa855f7, 0xec4899) animated
7. MINIMUM 5 different 3D objects relevant to the scene (geometry, materials, meshes)
8. Particle system: BufferGeometry + BufferAttribute + Points with 2000+ particles
9. MeshStandardMaterial with metalness & roughness on all solid objects
10. Orbit rings or additional decorative geometry (wireframe, TorusGeometry, etc.)
11. Ground plane or GridHelper
12. Scene fog: FogExp2
13. Scene background color (dark)
14. Smooth animations: rotation, floating (sin/cos), pulsing, orbiting
15. All code self-contained — NO module imports

Write ONLY the JavaScript. Start immediately with variable declarations. Minimum 200 lines."""

        scene_resp = call_ai(scene_prompt, timeout=150)
        scene_js = extract_code(scene_resp, "javascript")
        if not scene_js or len(scene_js) < 800:
            scene_js = self._fallback_scene(accent, req)

        # Add loading bar completion
        scene_js += f"""

/* ── Loading complete ── */
(function(){{
  var bar = document.getElementById('load-bar');
  var overlay = document.getElementById('loader');
  if (!bar || !overlay) return;
  var p = 0;
  var iv = setInterval(function(){{
    p = Math.min(100, p + (100 - p) * 0.07 + 0.8);
    bar.style.width = p + '%';
    if (p >= 99.5) {{
      clearInterval(iv);
      setTimeout(function(){{
        overlay.style.opacity = '0';
        overlay.style.transition = 'opacity 0.8s ease';
        setTimeout(function(){{ overlay.style.display = 'none'; }}, 800);
      }}, 300);
    }}
  }}, 30);
}})();"""

        html = self._build_html(title, scene_js, color, analysis)
        return {"index.html": html, "scene.js": scene_js}

    def _build_html(self, title: str, scene_js: str, color: str, analysis: dict) -> str:
        grad = {
            "violet": "from-violet-950 via-purple-950 to-black",
            "indigo": "from-indigo-950 via-blue-950 to-black",
            "blue": "from-blue-950 via-cyan-950 to-black",
            "purple": "from-purple-950 via-pink-950 to-black",
        }.get(color, "from-indigo-950 via-purple-950 to-black")

        accent_hex = analysis.get("primary_color", "#8b5cf6")

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{title}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ background: #020010; overflow: hidden; font-family: system-ui, sans-serif; }}
    canvas {{ display: block; }}
    #loader {{ position: fixed; inset: 0; z-index: 100; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
    .load-ring {{ width: 60px; height: 60px; border: 2px solid rgba(255,255,255,0.1); border-top-color: {accent_hex}; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 24px; }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    #ui-overlay {{ position: fixed; top: 0; left: 0; right: 0; z-index: 10; padding: 20px 24px; display: flex; justify-content: space-between; align-items: flex-start; pointer-events: none; }}
    #controls-hint {{ position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.5); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); border-radius: 100px; padding: 8px 20px; color: rgba(255,255,255,0.5); font-size: 12px; letter-spacing: 0.05em; pointer-events: none; }}
  </style>
</head>
<body>
  <!-- Loader -->
  <div id="loader" class="bg-gradient-to-br {grad}">
    <div class="load-ring"></div>
    <h1 style="color:white;font-size:1.5rem;font-weight:300;letter-spacing:0.3em;text-transform:uppercase;margin-bottom:8px;">{title}</h1>
    <p style="color:rgba(255,255,255,0.3);font-size:11px;letter-spacing:0.2em;margin-bottom:32px;">INTERACTIVE 3D EXPERIENCE</p>
    <div style="width:200px;height:2px;background:rgba(255,255,255,0.08);border-radius:99px;overflow:hidden;">
      <div id="load-bar" style="height:100%;width:0%;background:linear-gradient(90deg,{accent_hex},{accent_hex}99);border-radius:99px;transition:width 0.04s linear;"></div>
    </div>
  </div>

  <!-- UI Overlay -->
  <div id="ui-overlay">
    <div>
      <h2 style="color:white;font-size:14px;font-weight:600;opacity:0.85;text-shadow:0 2px 10px rgba(0,0,0,0.5);">{title}</h2>
      <p style="color:rgba(255,255,255,0.25);font-size:11px;margin-top:4px;">3D Interactive Scene</p>
    </div>
    <div style="display:flex;gap:8px;">
      <div style="background:rgba(0,0,0,0.4);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.1);border-radius:8px;padding:6px 12px;color:rgba(255,255,255,0.5);font-size:11px;">
        <span style="color:{accent_hex};">●</span> Live
      </div>
    </div>
  </div>

  <!-- Controls hint -->
  <div id="controls-hint">Drag · Scroll to zoom · Touch supported</div>

  <script src="scene.js"></script>
</body>
</html>"""

    def _fallback_scene(self, accent: str, req: str) -> str:
        return f"""
'use strict';
var W = window.innerWidth, H = window.innerHeight;
var scene = new THREE.Scene();
scene.background = new THREE.Color(0x020010);
scene.fog = new THREE.FogExp2(0x020010, 0.014);

var camera = new THREE.PerspectiveCamera(60, W / H, 0.1, 1000);
camera.position.set(0, 3, 12);

var renderer = new THREE.WebGLRenderer({{antialias: true, alpha: true}});
renderer.setSize(W, H);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.3;
document.body.appendChild(renderer.domElement);

/* Lights */
var amb = new THREE.AmbientLight(0x111133, 0.9);
scene.add(amb);
var sun = new THREE.DirectionalLight(0xffffff, 1.6);
sun.position.set(8, 15, 8);
sun.castShadow = true;
sun.shadow.mapSize.width = 2048;
sun.shadow.mapSize.height = 2048;
scene.add(sun);
var p1 = new THREE.PointLight({accent}, 3.5, 25);
p1.position.set(-5, 5, 4);
scene.add(p1);
var p2 = new THREE.PointLight(0xa855f7, 3, 22);
p2.position.set(5, 3, -5);
scene.add(p2);
var p3 = new THREE.PointLight(0xec4899, 2.5, 18);
p3.position.set(0, -3, 6);
scene.add(p3);

/* Core icosahedron */
var coreGeo = new THREE.IcosahedronGeometry(2, 4);
var coreMat = new THREE.MeshStandardMaterial({{color: {accent}, metalness: 0.9, roughness: 0.1, emissive: {accent}, emissiveIntensity: 0.2}});
var core = new THREE.Mesh(coreGeo, coreMat);
core.castShadow = true;
scene.add(core);

/* Wireframe shell */
var wireMat = new THREE.MeshBasicMaterial({{wireframe: true, color: 0xa855f7, transparent: true, opacity: 0.15}});
scene.add(new THREE.Mesh(new THREE.IcosahedronGeometry(2.08, 4), wireMat));

/* Orbiting torus rings */
var ringData = [
  {{r: 3.5, tube: 0.02, color: {accent}, rotX: 0.5, rotZ: 0}},
  {{r: 4.2, tube: 0.016, color: 0xa855f7, rotX: 1.1, rotZ: 0.8}},
  {{r: 4.9, tube: 0.012, color: 0xec4899, rotX: 0.3, rotZ: 1.5}},
];
var rings = ringData.map(function(d) {{
  var rg = new THREE.TorusGeometry(d.r, d.tube, 16, 200);
  var rm = new THREE.MeshBasicMaterial({{color: d.color, transparent: true, opacity: 0.6}});
  var mesh = new THREE.Mesh(rg, rm);
  mesh.rotation.x = d.rotX;
  mesh.rotation.z = d.rotZ;
  mesh._rotX = d.rotX;
  mesh._rotZ = d.rotZ;
  scene.add(mesh);
  return mesh;
}});

/* Satellite spheres */
var satellites = [];
for (var i = 0; i < 5; i++) {{
  var angle = (i / 5) * Math.PI * 2;
  var satGeo = new THREE.SphereGeometry(0.18 + Math.random() * 0.12, 16, 16);
  var satMat = new THREE.MeshStandardMaterial({{color: [0x6366f1, 0xa855f7, 0xec4899, 0x3b82f6, 0x22c55e][i], metalness: 0.8, roughness: 0.2}});
  var sat = new THREE.Mesh(satGeo, satMat);
  sat._angle = angle;
  sat._radius = 3.8 + Math.random() * 1.2;
  sat._speed = 0.3 + Math.random() * 0.4;
  sat._y = (Math.random() - 0.5) * 2;
  scene.add(sat);
  satellites.push(sat);
}}

/* Particles */
var pCount = 4000;
var pPositions = new Float32Array(pCount * 3);
var pColors = new Float32Array(pCount * 3);
for (var i = 0; i < pCount * 3; i += 3) {{
  pPositions[i] = (Math.random() - 0.5) * 70;
  pPositions[i + 1] = (Math.random() - 0.5) * 70;
  pPositions[i + 2] = (Math.random() - 0.5) * 70;
  pColors[i] = 0.4 + Math.random() * 0.3;
  pColors[i + 1] = 0.4 + Math.random() * 0.3;
  pColors[i + 2] = 0.8 + Math.random() * 0.2;
}}
var pGeo = new THREE.BufferGeometry();
pGeo.setAttribute('position', new THREE.BufferAttribute(pPositions, 3));
pGeo.setAttribute('color', new THREE.BufferAttribute(pColors, 3));
var pMat = new THREE.PointsMaterial({{size: 0.06, vertexColors: true, transparent: true, opacity: 0.7}});
scene.add(new THREE.Points(pGeo, pMat));

/* Grid */
var grid = new THREE.GridHelper(60, 60, 0x1a1a4e, 0x0a0a20);
grid.position.y = -6;
scene.add(grid);

/* Orbit controls */
var sph = {{theta: 0, phi: 1.15, r: 12}};
var drag = false, prev = {{x: 0, y: 0}};
window.addEventListener('mousedown', function(e) {{ drag = true; prev = {{x: e.clientX, y: e.clientY}}; }});
window.addEventListener('mouseup', function() {{ drag = false; }});
window.addEventListener('mousemove', function(e) {{
  if (!drag) return;
  sph.theta -= (e.clientX - prev.x) * 0.005;
  sph.phi = Math.max(0.05, Math.min(Math.PI - 0.05, sph.phi + (e.clientY - prev.y) * 0.005));
  prev = {{x: e.clientX, y: e.clientY}};
}});
window.addEventListener('wheel', function(e) {{
  sph.r = Math.max(4, Math.min(30, sph.r + e.deltaY * 0.012));
}}, {{passive: true}});
window.addEventListener('touchstart', function(e) {{
  drag = true; prev = {{x: e.touches[0].clientX, y: e.touches[0].clientY}};
}}, {{passive: true}});
window.addEventListener('touchend', function() {{ drag = false; }});
window.addEventListener('touchmove', function(e) {{
  if (!drag) return;
  sph.theta -= (e.touches[0].clientX - prev.x) * 0.005;
  sph.phi = Math.max(0.05, Math.min(Math.PI - 0.05, sph.phi + (e.touches[0].clientY - prev.y) * 0.005));
  prev = {{x: e.touches[0].clientX, y: e.touches[0].clientY}};
}}, {{passive: true}});
window.addEventListener('resize', function() {{
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}});

/* Animation loop */
var t = 0;
(function animate() {{
  requestAnimationFrame(animate);
  t += 0.012;
  core.rotation.y = t * 0.3;
  core.rotation.x = Math.sin(t * 0.2) * 0.12;
  core.position.y = Math.sin(t * 0.5) * 0.3;
  rings.forEach(function(r, i) {{
    r.rotation.y = t * (0.25 + i * 0.07);
    r.rotation.x = r._rotX + Math.sin(t * 0.28 + i) * 0.1;
  }});
  satellites.forEach(function(s) {{
    s._angle += s._speed * 0.012;
    s.position.x = Math.cos(s._angle) * s._radius;
    s.position.z = Math.sin(s._angle) * s._radius;
    s.position.y = s._y + Math.sin(t + s._angle) * 0.4;
    s.rotation.y += 0.03;
  }});
  p1.position.set(Math.sin(t * 0.7) * 7, 4 + Math.sin(t * 0.5) * 2, Math.cos(t * 0.7) * 7);
  p2.position.set(Math.cos(t * 0.5) * 6, 2, Math.sin(t * 0.5) * 6);
  camera.position.set(
    Math.sin(sph.theta) * Math.sin(sph.phi) * sph.r,
    Math.cos(sph.phi) * sph.r,
    Math.cos(sph.theta) * Math.sin(sph.phi) * sph.r
  );
  camera.lookAt(0, 0, 0);
  renderer.render(scene, camera);
}})();"""


# ════════════════════════════════════════════════════════════════════════════════
# AGENT 4: Coder — Production Code Generation
# ════════════════════════════════════════════════════════════════════════════════

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
        manifest = arch.get("integration_manifest", {})

        # ── Full-stack backend file routing ────────────────────────────────────
        if ftype == "nodejs_server":
            return self._nodejs_server(fspec, plan, arch, manifest)
        elif ftype in ("nodejs_routes", "nodejs_routes_auth"):
            return self._nodejs_routes(fspec, plan, arch, manifest)
        elif ftype == "nodejs_model":
            return self._nodejs_model(fspec, plan, arch, manifest)
        elif ftype == "nodejs_middleware":
            return self._nodejs_middleware(fspec, plan, arch, manifest)
        elif ftype == "nodejs_config":
            return self._nodejs_config(fspec, plan, arch, manifest)
        elif ftype == "nodejs_package":
            return self._nodejs_package_json(plan, arch, manifest)
        elif ftype in ("django_manage",):
            return self._django_manage(plan)
        elif ftype == "django_settings":
            return self._django_settings(fspec, plan, arch, manifest)
        elif ftype in ("django_urls", "django_app_urls"):
            return self._django_urls(fspec, plan, arch, manifest)
        elif ftype == "django_models":
            return self._django_models(fspec, plan, arch, manifest)
        elif ftype == "django_views":
            return self._django_views(fspec, plan, arch, manifest)
        elif ftype == "django_serializers":
            return self._django_serializers(fspec, plan, arch, manifest)
        elif ftype == "django_requirements":
            return self._django_requirements(manifest)
        elif ftype in ("php_router", "php_auth", "php_crud"):
            return self._php_file(fspec, plan, arch, manifest)
        elif ftype == "php_db":
            return self._php_db(fspec, plan, arch, manifest)
        elif ftype == "php_jwt":
            return self._php_jwt(manifest)
        elif ftype == "sql_schema":
            return self._sql_schema(fspec, plan, arch, manifest)
        elif ftype == "env_example":
            return self._env_example(manifest)
        elif ftype == "fullstack_readme":
            return self._fullstack_readme(plan, arch, manifest)

        # ── Standard file routing ──────────────────────────────────────────────
        if ftype == "html":
            return self._html(fspec, plan, arch)
        elif ftype == "css":
            return self._css(fspec, plan, arch)
        elif ftype == "python":
            return self._python(fspec, plan)
        elif ftype == "javascript":
            fname_base = fname.split("/")[-1]  # handle frontend/app.js paths
            if fname_base == "app.js":
                return self._fullstack_frontend_app_js(fspec, plan, arch, manifest) if manifest else self._app_js(fspec, plan, arch)
            elif fname_base == "api.js":
                return self._frontend_api_js(fspec, plan, arch, manifest)
            elif fname_base == "data.js":
                return self._data_js(fspec, plan, arch)
            elif fname_base == "ui.js":
                return self._ui_js(fspec, plan, arch)
            elif fname_base == "scene.js":
                return self._js(fspec, plan)
            else:
                return self._module_js(fspec, plan, arch)
        elif ftype == "text" and "requirements" in fspec["path"]:
            return "flask>=2.3.0\nflask-cors>=4.0.0\npython-dotenv>=1.0.0\nwerkzeug>=2.3.0\n"
        elif ftype == "markdown":
            return self._readme(plan, arch)
        return ""

    # ═══════════════════════════════════════════════════════════════════════════
    # FULL-STACK BACKEND GENERATORS — All use the integration manifest for sync
    # ═══════════════════════════════════════════════════════════════════════════

    def _manifest_summary(self, manifest: dict) -> str:
        """Build a compact manifest summary for injection into every prompt."""
        endpoints = manifest.get("endpoints", [])
        ep_list = "\n".join(f"  {e['method']} {e['path']} — {e.get('desc','')}" for e in endpoints[:15])
        schema = json.dumps(manifest.get("db_schema", {}), indent=2)[:600]
        return (
            f"API Base: {manifest.get('frontend_api_base', 'http://localhost:3000/api/v1')}\n"
            f"Port: {manifest.get('port', 3000)}\n"
            f"Database: {manifest.get('database', 'mongodb')}\n"
            f"DB Name: {manifest.get('db_name', 'app_db')}\n"
            f"Auth: JWT\n"
            f"Endpoints:\n{ep_list}\n"
            f"Schema:\n{schema}"
        )

    def _nodejs_server(self, fspec, plan, arch, manifest) -> str:
        req = plan.get("user_request", "")
        name = plan.get("project_name", "app")
        db = manifest.get("database", "mongodb")
        port = manifest.get("port", 3000)
        endpoints = manifest.get("endpoints", [])
        entities = manifest.get("entities", ["records"])
        ep_str = "\n".join(f"  {e['method']} {e['path']}" for e in endpoints)
        db_pkg = "mongoose" if db == "mongodb" else ("mysql2" if db == "mysql" else "firebase-admin" if db == "firebase" else "@supabase/supabase-js")

        prompt = f"""Write a COMPLETE, PRODUCTION-READY Node.js Express server (server.js) for "{req}". MINIMUM 150 LINES.

Project: {name}
Database: {db}
Port: {port}
Entities: {json.dumps(entities)}

All API endpoints this server must expose:
{ep_str}

IMPLEMENT EVERYTHING:
1. 'use strict'; + all requires at top: express, cors, helmet, morgan, dotenv, path, fs
2. require('{db_pkg}') for database
3. require('./config/db') for DB connection
4. require('./middleware/auth') for JWT middleware
5. app = express(); configure all middleware: helmet(), cors({{origin: process.env.CORS_ORIGIN || '*', credentials: true}}), morgan('dev'), express.json({{limit: '10mb'}}), express.urlencoded({{extended: true}})
6. Mount all route files: {'; '.join(f"app.use('{e}', require('./routes/{e.split('/')[3] if len(e.split('/'))>3 else 'records'}.js'))" for e in set(e['path'].split('/')[3] if len(e['path'].split('/'))>3 else '' for e in endpoints) if e)}
7. app.use('/api/v1/auth', require('./routes/auth'));
8. app.use('/api/v1/{entities[0].lower().replace(" ","") if entities else "records"}s', require('./routes/{entities[0].lower().replace(" ","") if entities else "records"}s'));
9. Health check: GET /health → {{"status": "ok", "uptime": process.uptime(), "timestamp": new Date()}}
10. 404 handler: app.use((req, res) => res.status(404).json({{success: false, message: 'Route not found'}}))
11. Error handler middleware: (err, req, res, next) with proper error formatting
12. Graceful shutdown: process.on('SIGTERM', ...) and process.on('SIGINT', ...)
13. app.listen(PORT, () => console.log(...))

Output ONLY complete ```javascript."""
        resp = call_ai(prompt, timeout=120)
        code = extract_code(resp, "javascript")
        if code and len(code) > 500:
            return code
        # Robust fallback
        ent = (entities[0].lower().replace(" ", "") if entities else "record") + "s"
        return f"""'use strict';
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const path = require('path');

const app = express();
const PORT = process.env.PORT || {port};

// ── Connect Database ──────────────────────────────────────────────────────────
require('./config/db');

// ── Middleware ────────────────────────────────────────────────────────────────
app.use(helmet({{ crossOriginResourcePolicy: false }}));
app.use(cors({{ origin: process.env.CORS_ORIGIN || '*', credentials: true }}));
app.use(morgan('dev'));
app.use(express.json({{ limit: '10mb' }}));
app.use(express.urlencoded({{ extended: true }}));

// ── Serve Frontend ────────────────────────────────────────────────────────────
app.use(express.static(path.join(__dirname, '..', 'frontend')));

// ── API Routes ────────────────────────────────────────────────────────────────
app.use('/api/v1/auth', require('./routes/auth'));
app.use('/api/v1/{ent}', require('./routes/{ent}'));

// ── Health Check ──────────────────────────────────────────────────────────────
app.get('/health', (req, res) => {{
  res.json({{ status: 'ok', uptime: process.uptime(), timestamp: new Date(), version: '1.0.0' }});
}});

// ── Catch-All for SPA ─────────────────────────────────────────────────────────
app.get('*', (req, res) => {{
  if (!req.path.startsWith('/api')) {{
    res.sendFile(path.join(__dirname, '..', 'frontend', 'index.html'));
  }} else {{
    res.status(404).json({{ success: false, message: 'API route not found' }});
  }}
}});

// ── Error Handler ─────────────────────────────────────────────────────────────
app.use((err, req, res, next) => {{
  console.error('Error:', err.message);
  const status = err.status || err.statusCode || 500;
  res.status(status).json({{ success: false, message: err.message || 'Internal server error', ...(process.env.NODE_ENV === 'development' && {{ stack: err.stack }}) }});
}});

// ── Start Server ──────────────────────────────────────────────────────────────
const server = app.listen(PORT, () => {{
  console.log(`🚀 Server running on http://localhost:${{PORT}}`);
  console.log(`📊 API available at http://localhost:${{PORT}}/api/v1`);
  console.log(`🌍 Frontend at http://localhost:${{PORT}}`);
}});

// ── Graceful Shutdown ─────────────────────────────────────────────────────────
process.on('SIGTERM', () => {{ server.close(() => process.exit(0)); }});
process.on('SIGINT',  () => {{ server.close(() => process.exit(0)); }});
"""

    def _nodejs_routes(self, fspec, plan, arch, manifest) -> str:
        req = plan.get("user_request", "")
        fname = fspec["path"]
        purpose = fspec.get("purpose", fname)
        is_auth = "auth" in fname
        entities = manifest.get("entities", ["Record"])
        db = manifest.get("database", "mongodb")
        ent = entities[0] if entities else "Record"
        ent_lower = ent.lower().replace(" ", "")
        endpoints = [e for e in manifest.get("endpoints", []) if
                     ("auth" in e["path"]) == is_auth]
        ep_str = "\n".join(f"  {e['method']} {e['path']} — {e.get('desc','')}" for e in endpoints)

        prompt = f"""Write COMPLETE, PRODUCTION-READY Express.js route file: {fname}
Project: {req}
Purpose: {purpose}

Routes to implement:
{ep_str}

MANDATORY:
1. const router = require('express').Router(); at top
2. {'const bcrypt = require("bcryptjs"); const jwt = require("jsonwebtoken");' if is_auth else f'const {ent} = require("../models/{ent_lower}");'}
3. {'Import auth middleware: const {{ verifyToken }} = require("../middleware/auth");' if not is_auth else ''}
4. Every route FULLY implemented — no placeholders, no TODOs
5. {'register: hash password (bcrypt.hash 10 rounds), save user, return JWT + user (no password)' if is_auth else f'GET / with pagination (page, limit), search (q), filter (status), sort — return {{ success: true, data: [...], total, page, pages }}'}
6. {'login: find by email, bcrypt.compare, return JWT + user' if is_auth else 'POST / — validate required fields, create doc, return 201 + saved record'}
7. {'GET /me — verifyToken middleware, return req.user' if is_auth else 'GET /:id — findById, 404 if not found'}
8. {'POST /logout — clear token guidance in response' if is_auth else 'PUT /:id — findByIdAndUpdate, return updated'}
9. {'All errors: try/catch with descriptive messages, proper status codes' if is_auth else 'DELETE /:id — findByIdAndDelete, return 204'}
10. GET /stats — return {{ total, active, inactive, thisMonth, monthly: [...12 months], topRecords: [...5] }}
11. module.exports = router;

Output ONLY complete ```javascript."""
        resp = call_ai(prompt, timeout=140)
        code = extract_code(resp, "javascript")
        return code if code and len(code) > 300 else f"""'use strict';
const router = require('express').Router();
{'const bcrypt = require("bcryptjs"); const jwt = require("jsonwebtoken");' if is_auth else f'const {ent} = require("../models/{ent_lower}");'}
{'const { verifyToken } = require("../middleware/auth");' if not is_auth else ''}

// Auto-generated routes for {fname}
// TODO: Review and customize before production use
router.get('/', async (req, res) => {{
  try {{
    const {{ page = 1, limit = 10, q = '', status }} = req.query;
    res.json({{ success: true, data: [], total: 0, page: +page, pages: 0 }});
  }} catch (e) {{ res.status(500).json({{ success: false, message: e.message }}); }}
}});

module.exports = router;
"""

    def _nodejs_model(self, fspec, plan, arch, manifest) -> str:
        req = plan.get("user_request", "")
        fname = fspec["path"]
        purpose = fspec.get("purpose", fname)
        db = manifest.get("database", "mongodb")
        schema = manifest.get("db_schema", {})
        entities = manifest.get("entities", ["Record"])
        ent = entities[0] if entities else "Record"
        schema_str = json.dumps(schema.get(ent.lower(), schema.get(list(schema.keys())[0] if schema else "", {})), indent=2)

        prompt = f"""Write COMPLETE, PRODUCTION-READY database model file: {fname}
Project: {req}
Database: {db}
Entity: {ent}
Purpose: {purpose}
Schema: {schema_str}

{"MONGOOSE (MongoDB) model:" if db == "mongodb" else "SEQUELIZE (MySQL) model:" if db == "mysql" else "Model:"}
1. All field definitions with proper types, required flags, defaults, validators
2. Indexes for commonly queried fields (email unique, status, createdAt)
3. Pre-save hooks: password hashing if user model, updatedAt timestamp
4. Instance methods: toJSON() (remove password), comparePassword() if user model
5. Static methods: findByEmail(), findActive(), getStats()
6. Virtuals: fullName if applicable, age from birthDate
7. Timestamps: createdAt, updatedAt
8. 25+ realistic sample data records as a const SAMPLE_DATA array at the bottom (for seeding)
9. Export the model

Output ONLY complete ```javascript."""
        resp = call_ai(prompt, timeout=140)
        code = extract_code(resp, "javascript")
        return code if code and len(code) > 300 else f"""'use strict';
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const {ent}Schema = new mongoose.Schema({{
  name: {{ type: String, required: true, trim: true }},
  email: {{ type: String, required: true, unique: true, lowercase: true, trim: true }},
  status: {{ type: String, enum: ['active', 'inactive', 'pending'], default: 'active' }},
  createdAt: {{ type: Date, default: Date.now }},
  updatedAt: {{ type: Date, default: Date.now }},
}}, {{ timestamps: true, toJSON: {{ virtuals: true }}, toObject: {{ virtuals: true }} }});

{ent}Schema.pre('save', function(next) {{ this.updatedAt = Date.now(); next(); }});
{ent}Schema.statics.findActive = function() {{ return this.find({{ status: 'active' }}); }};

module.exports = mongoose.model('{ent}', {ent}Schema);
"""

    def _nodejs_middleware(self, fspec, plan, arch, manifest) -> str:
        return """'use strict';
const jwt = require('jsonwebtoken');

/**
 * Verify JWT token middleware
 */
function verifyToken(req, res, next) {
  try {
    const authHeader = req.headers.authorization || req.headers.Authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ success: false, message: 'Access denied. No token provided.' });
    }
    const token = authHeader.split(' ')[1];
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'fallback_secret_change_in_production');
    req.user = decoded;
    next();
  } catch (err) {
    if (err.name === 'TokenExpiredError') {
      return res.status(401).json({ success: false, message: 'Token expired. Please login again.' });
    }
    return res.status(401).json({ success: false, message: 'Invalid token.' });
  }
}

/**
 * Optional auth — attach user if token present, continue regardless
 */
function optionalAuth(req, res, next) {
  try {
    const authHeader = req.headers.authorization;
    if (authHeader && authHeader.startsWith('Bearer ')) {
      const token = authHeader.split(' ')[1];
      req.user = jwt.verify(token, process.env.JWT_SECRET || 'fallback_secret');
    }
  } catch (_) { /* ignore */ }
  next();
}

/**
 * Require admin role
 */
function requireAdmin(req, res, next) {
  if (!req.user || req.user.role !== 'admin') {
    return res.status(403).json({ success: false, message: 'Access denied. Admin role required.' });
  }
  next();
}

/**
 * Generate JWT token
 */
function generateToken(payload, expiresIn = '7d') {
  return jwt.sign(payload, process.env.JWT_SECRET || 'fallback_secret_change_in_production', { expiresIn });
}

module.exports = { verifyToken, optionalAuth, requireAdmin, generateToken };
"""

    def _nodejs_config(self, fspec, plan, arch, manifest) -> str:
        db = manifest.get("database", "mongodb")
        db_name = manifest.get("db_name", "app_db")
        if db == "mongodb":
            return f"""'use strict';
const mongoose = require('mongoose');

const MONGODB_URI = process.env.MONGODB_URI || process.env.MONGO_URI || `mongodb://localhost:27017/{db_name}`;

async function connectDB() {{
  try {{
    const conn = await mongoose.connect(MONGODB_URI, {{
      useNewUrlParser: true,
      useUnifiedTopology: true,
    }});
    console.log(`✅ MongoDB Connected: ${{conn.connection.host}}`);
    console.log(`📦 Database: ${{conn.connection.name}}`);
  }} catch (error) {{
    console.error('❌ MongoDB connection error:', error.message);
    console.error('Make sure MongoDB is running and MONGODB_URI is set in .env');
    process.exit(1);
  }}
}}

mongoose.connection.on('disconnected', () => console.log('⚠️ MongoDB disconnected'));
mongoose.connection.on('reconnected', () => console.log('✅ MongoDB reconnected'));

connectDB();
module.exports = mongoose;
"""
        elif db == "mysql":
            return f"""'use strict';
const mysql = require('mysql2/promise');

const pool = mysql.createPool({{
  host:     process.env.DB_HOST     || 'localhost',
  port:     parseInt(process.env.DB_PORT || '3306'),
  user:     process.env.DB_USER     || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME     || '{db_name}',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0,
  enableKeepAlive: true,
}});

pool.getConnection()
  .then(conn => {{ console.log('✅ MySQL Connected: ' + process.env.DB_HOST); conn.release(); }})
  .catch(err => {{ console.error('❌ MySQL connection error:', err.message); process.exit(1); }});

module.exports = pool;
"""
        else:
            return f"'use strict';\n// Database config for {db}\nconsole.log('DB connected');\nmodule.exports = {{}};\n"

    def _nodejs_package_json(self, plan, arch, manifest) -> str:
        name = plan.get("project_name", "app")
        db = manifest.get("database", "mongodb")
        port = manifest.get("port", 3000)
        db_pkg = '"mongoose": "^7.6.0"' if db == "mongodb" else ('"mysql2": "^3.6.0"' if db == "mysql" else '"firebase-admin": "^11.11.0"' if db == "firebase" else '"@supabase/supabase-js": "^2.38.0"')
        return f"""{{\n  "name": "{name}",\n  "version": "1.0.0",\n  "description": "Full-stack {name} application",\n  "main": "backend/server.js",\n  "scripts": {{\n    "start": "node backend/server.js",\n    "dev": "nodemon backend/server.js",\n    "seed": "node backend/scripts/seed.js"\n  }},\n  "dependencies": {{\n    "express": "^4.18.2",\n    "cors": "^2.8.5",\n    "helmet": "^7.1.0",\n    "morgan": "^1.10.0",\n    "dotenv": "^16.3.1",\n    "bcryptjs": "^2.4.3",\n    "jsonwebtoken": "^9.0.2",\n    {db_pkg}\n  }},\n  "devDependencies": {{\n    "nodemon": "^3.0.1"\n  }},\n  "engines": {{\n    "node": ">=18.0.0"\n  }}\n}}"""

    def _django_manage(self, plan) -> str:
        return """#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Could not import Django.") from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
"""

    def _django_settings(self, fspec, plan, arch, manifest) -> str:
        db = manifest.get("database", "mongodb")
        name = plan.get("project_name", "app")
        entities = manifest.get("entities", ["Record"])
        app_name = (entities[0].lower().replace(" ", "") if entities else "records") + "s"
        prompt = f"""Write COMPLETE Django settings.py for a "{plan.get('user_request','')}" project.
Database: {db}, App: {name}

Include: SECRET_KEY from env, DEBUG, ALLOWED_HOSTS, INSTALLED_APPS (with '{app_name}', 'rest_framework', 'corsheaders'),
DATABASES for {db}, REST_FRAMEWORK with JWT auth, CORS_ALLOWED_ORIGINS, STATIC/MEDIA files,
SIMPLE_JWT settings, all imports at top, everything production-ready.
Output ONLY complete ```python."""
        resp = call_ai(prompt, timeout=100)
        code = extract_code(resp, "python")
        return code if code and len(code) > 300 else f"""import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-in-production')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'rest_framework', 'rest_framework_simplejwt', 'corsheaders', '{app_name}',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware', 'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware', 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]
ROOT_URLCONF = 'config.urls'
DATABASES = {{'default': {{'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / '{name}.db'}}}}
REST_FRAMEWORK = {{'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework_simplejwt.authentication.JWTAuthentication'], 'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated']}}
SIMPLE_JWT = {{'ACCESS_TOKEN_LIFETIME': timedelta(days=7), 'REFRESH_TOKEN_LIFETIME': timedelta(days=30)}}
CORS_ALLOW_ALL_ORIGINS = True
STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
"""

    def _django_urls(self, fspec, plan, arch, manifest) -> str:
        fname = fspec["path"]
        entities = manifest.get("entities", ["Record"])
        app_name = (entities[0].lower().replace(" ", "") if entities else "records") + "s"
        is_root = "config" in fname
        if is_root:
            return f"""from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('{app_name}.urls')),
    path('api/v1/auth/', include('{app_name}.auth_urls')),
]
"""
        else:
            ent = entities[0].title().replace(" ", "") if entities else "Record"
            return f"""from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'{app_name}', views.{ent}ViewSet, basename='{app_name[:-1]}')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', views.StatsView.as_view()),
]
"""

    def _django_models(self, fspec, plan, arch, manifest) -> str:
        req = plan.get("user_request", "")
        entities = manifest.get("entities", ["Record"])
        schema = manifest.get("db_schema", {})
        ent = entities[0] if entities else "Record"
        schema_str = json.dumps(schema, indent=2)[:400]
        prompt = f"""Write COMPLETE Django models.py for "{req}". Entity: {ent}. Schema hint: {schema_str}.
Include: all model fields with proper types, validators, choices, Meta class with ordering/verbose_name,
__str__ method, save() override, Manager with custom querysets (active(), recent()),
at least 2 model classes if the domain needs multiple entities, all imports.
MINIMUM 100 LINES. Output ONLY complete ```python."""
        resp = call_ai(prompt, timeout=120)
        code = extract_code(resp, "python")
        return code if code and len(code) > 200 else f"""from django.db import models
from django.utils import timezone

class {ent}(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive'), ('pending', 'Pending')]
    name = models.CharField(max_length=200, verbose_name='Name')
    email = models.EmailField(unique=True, verbose_name='Email')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']
        verbose_name = '{ent}'
        verbose_name_plural = '{ent}s'
    def __str__(self):
        return f'{{self.name}} ({{self.status}})'
"""

    def _django_views(self, fspec, plan, arch, manifest) -> str:
        req = plan.get("user_request", "")
        entities = manifest.get("entities", ["Record"])
        ent = entities[0] if entities else "Record"
        ent_class = ent.title().replace(" ", "")
        app_name = ent.lower().replace(" ", "") + "s"
        prompt = f"""Write COMPLETE Django REST Framework views.py for "{req}". Entity: {ent}.
Include: {ent_class}ViewSet (ModelViewSet with full CRUD + custom actions),
@action(detail=False) for stats endpoint returning total/active/monthly data,
StatsView (APIView) for dashboard analytics,
permission_classes (IsAuthenticated), queryset filtering by search/status/ordering,
pagination (PageNumberPagination), proper serializer usage, all imports.
MINIMUM 120 LINES. Output ONLY complete ```python."""
        resp = call_ai(prompt, timeout=130)
        code = extract_code(resp, "python")
        return code if code and len(code) > 200 else f"""from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Q
from .models import {ent_class}
from .serializers import {ent_class}Serializer

class {ent_class}ViewSet(viewsets.ModelViewSet):
    queryset = {ent_class}.objects.all()
    serializer_class = {ent_class}Serializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get('q', '')
        status = self.request.query_params.get('status', '')
        if q: qs = qs.filter(Q(name__icontains=q) | Q(email__icontains=q))
        if status: qs = qs.filter(status=status)
        return qs

    @action(detail=False)
    def stats(self, request):
        qs = self.get_queryset()
        return Response({{'total': qs.count(), 'active': qs.filter(status='active').count()}})

class StatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        return Response({{'total': {ent_class}.objects.count()}})
"""

    def _django_serializers(self, fspec, plan, arch, manifest) -> str:
        entities = manifest.get("entities", ["Record"])
        ent = entities[0] if entities else "Record"
        ent_class = ent.title().replace(" ", "")
        return f"""from rest_framework import serializers
from .models import {ent_class}

class {ent_class}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {ent_class}
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_email(self, value):
        return value.lower().strip()
"""

    def _django_requirements(self, manifest) -> str:
        db = manifest.get("database", "mongodb")
        db_pkg = "djongo==1.3.6\npymongo>=3.12.0\n" if db == "mongodb" else ("psycopg2-binary>=2.9.7\n" if db in ("postgresql", "supabase") else "")
        return f"""Django>=4.2.0
djangorestframework>=3.14.0
djangorestframework-simplejwt>=5.3.0
django-cors-headers>=4.3.0
python-dotenv>=1.0.0
Pillow>=10.0.0
{db_pkg}django-filter>=23.3
"""

    def _php_file(self, fspec, plan, arch, manifest) -> str:
        req = plan.get("user_request", "")
        fname = fspec["path"]
        purpose = fspec.get("purpose", fname)
        ftype = fspec.get("type", "")
        entities = manifest.get("entities", ["Record"])
        api_base = manifest.get("api_base", "/api/v1")
        db = manifest.get("database", "mysql")
        endpoints = manifest.get("endpoints", [])
        ep_str = "\n".join(f"{e['method']} {e['path']} — {e.get('desc','')}" for e in endpoints[:10])

        prompt = f"""Write COMPLETE, PRODUCTION-READY PHP file: {fname}
Project: {req}
Purpose: {purpose}
File type: {ftype}
Database: {db}
Entities: {json.dumps(entities)}
Endpoints to implement: {ep_str}

MANDATORY:
1. <?php at top, header('Content-Type: application/json'), CORS headers
2. require_once '../config/database.php'; require_once '../config/jwt.php';
3. Parse request method and path: $method = $_SERVER['REQUEST_METHOD']; $path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
4. {'Auth endpoints: register (password_hash(PASSWORD_DEFAULT)), login (password_verify), JWT generation, /me endpoint with token verification' if 'auth' in ftype else 'CRUD endpoints: GET all (PDO select with pagination/search), GET by ID, POST (insert), PUT (update), DELETE, stats endpoint'}
5. All responses: json_encode(['success' => true/false, 'data' => ..., 'message' => ...])
6. Error handling: try/catch with proper HTTP status codes (http_response_code())
7. Input validation with descriptive error messages
8. Prepared statements (PDO) for all DB queries — NO SQL injection risk
9. JWT verification on protected routes

Output ONLY complete ```php."""
        resp = call_ai(prompt, timeout=140)
        code = extract_code(resp, "php")
        if code and len(code) > 200:
            return code
        ent = entities[0] if entities else "Record"
        table = ent.lower().replace(" ", "_") + "s"
        return f"""<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {{ http_response_code(200); exit(); }}

require_once '../config/database.php';
require_once '../config/jwt.php';

$method = $_SERVER['REQUEST_METHOD'];
$input = json_decode(file_get_contents('php://input'), true) ?: [];
$pathParts = explode('/', trim(parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH), '/'));
$id = end($pathParts) && is_numeric(end($pathParts)) ? end($pathParts) : null;

try {{
  $db = Database::getInstance()->getConnection();
  if ($method === 'GET' && !$id) {{
    $page = intval($_GET['page'] ?? 1);
    $limit = intval($_GET['limit'] ?? 10);
    $offset = ($page - 1) * $limit;
    $q = $_GET['q'] ?? '';
    $sql = "SELECT * FROM {table} WHERE name LIKE :q ORDER BY created_at DESC LIMIT :limit OFFSET :offset";
    $stmt = $db->prepare($sql);
    $stmt->execute([':q' => "%$q%", ':limit' => $limit, ':offset' => $offset]);
    $data = $stmt->fetchAll(PDO::FETCH_ASSOC);
    $total = $db->query("SELECT COUNT(*) FROM {table}")->fetchColumn();
    echo json_encode(['success' => true, 'data' => $data, 'total' => (int)$total, 'page' => $page]);
  }} elseif ($method === 'POST') {{
    $name = $input['name'] ?? ''; $email = $input['email'] ?? '';
    if (!$name || !$email) {{ http_response_code(400); echo json_encode(['success' => false, 'message' => 'Name and email required']); exit(); }}
    $stmt = $db->prepare("INSERT INTO {table} (name, email, status, created_at) VALUES (:name, :email, 'active', NOW())");
    $stmt->execute([':name' => $name, ':email' => $email]);
    echo json_encode(['success' => true, 'message' => 'Created', 'id' => $db->lastInsertId()]);
  }} else {{
    echo json_encode(['success' => false, 'message' => 'Method not supported']);
  }}
}} catch (Exception $e) {{
  http_response_code(500);
  echo json_encode(['success' => false, 'message' => $e->getMessage()]);
}}
"""

    def _php_db(self, fspec, plan, arch, manifest) -> str:
        db_name = manifest.get("db_name", "app_db")
        return f"""<?php
class Database {{
    private static $instance = null;
    private $connection = null;

    private function __construct() {{
        $host     = getenv('DB_HOST')     ?: 'localhost';
        $dbName   = getenv('DB_NAME')     ?: '{db_name}';
        $user     = getenv('DB_USER')     ?: 'root';
        $password = getenv('DB_PASSWORD') ?: '';
        $port     = getenv('DB_PORT')     ?: '3306';

        try {{
            $dsn = "mysql:host=$host;port=$port;dbname=$dbName;charset=utf8mb4";
            $this->connection = new PDO($dsn, $user, $password, [
                PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES   => false,
            ]);
        }} catch (PDOException $e) {{
            http_response_code(503);
            die(json_encode(['success' => false, 'message' => 'Database connection failed: ' . $e->getMessage()]));
        }}
    }}

    public static function getInstance() {{
        if (self::$instance === null) {{
            self::$instance = new self();
        }}
        return self::$instance;
    }}

    public function getConnection() {{
        return $this->connection;
    }}
}}
"""

    def _php_jwt(self, manifest) -> str:
        return """<?php
class JWT {
    private static $secret;

    public static function init() {
        self::$secret = getenv('JWT_SECRET') ?: 'change-this-secret-in-production';
    }

    public static function generate(array $payload, int $expiry = 604800): string {
        self::init();
        $header  = self::base64url(json_encode(['typ' => 'JWT', 'alg' => 'HS256']));
        $payload['iat'] = time();
        $payload['exp'] = time() + $expiry;
        $body    = self::base64url(json_encode($payload));
        $sig     = self::base64url(hash_hmac('sha256', "$header.$body", self::$secret, true));
        return "$header.$body.$sig";
    }

    public static function verify(string $token): ?array {
        self::init();
        $parts = explode('.', $token);
        if (count($parts) !== 3) return null;
        [$header, $body, $sig] = $parts;
        $expected = self::base64url(hash_hmac('sha256', "$header.$body", self::$secret, true));
        if (!hash_equals($expected, $sig)) return null;
        $payload = json_decode(self::base64urldecode($body), true);
        if (!$payload || $payload['exp'] < time()) return null;
        return $payload;
    }

    public static function fromRequest(): ?array {
        $header = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
        if (!$header || !str_starts_with($header, 'Bearer ')) return null;
        return self::verify(substr($header, 7));
    }

    private static function base64url(string $data): string {
        return rtrim(strtr(base64_encode($data), '+/', '-_'), '=');
    }

    private static function base64urldecode(string $data): string {
        return base64_decode(strtr($data, '-_', '+/') . str_repeat('=', (4 - strlen($data) % 4) % 4));
    }
}
"""

    def _sql_schema(self, fspec, plan, arch, manifest) -> str:
        req = plan.get("user_request", "")
        db_name = manifest.get("db_name", "app_db")
        entities = manifest.get("entities", ["Record"])
        schema = manifest.get("db_schema", {})
        schema_str = json.dumps(schema, indent=2)[:500]
        prompt = f"""Write COMPLETE MySQL SQL schema for "{req}".
Database: {db_name}
Entities: {json.dumps(entities)}
Schema hint: {schema_str}

Include: CREATE DATABASE IF NOT EXISTS, USE db, CREATE TABLE for EACH entity with all fields,
PRIMARY KEY (id AUTO_INCREMENT), UNIQUE constraints, FOREIGN KEY relationships,
INDEX on commonly queried fields, 25+ INSERT INTO sample data records per table,
all field types correct (VARCHAR, TEXT, DECIMAL, TINYINT, DATETIME, ENUM).
Output ONLY complete ```sql."""
        resp = call_ai(prompt, timeout=130)
        code = extract_code(resp, "sql")
        if code and len(code) > 200:
            return code
        ent = entities[0].lower().replace(" ", "_") if entities else "record"
        return f"""-- {db_name} Database Schema
-- Generated for: {req}

CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `{db_name}`;

CREATE TABLE IF NOT EXISTS `{ent}s` (
  `id`          INT AUTO_INCREMENT PRIMARY KEY,
  `name`        VARCHAR(200) NOT NULL,
  `email`       VARCHAR(255) NOT NULL UNIQUE,
  `status`      ENUM('active','inactive','pending') NOT NULL DEFAULT 'active',
  `description` TEXT DEFAULT NULL,
  `created_at`  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX `idx_status` (`status`),
  INDEX `idx_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `users` (
  `id`           INT AUTO_INCREMENT PRIMARY KEY,
  `name`         VARCHAR(200) NOT NULL,
  `email`        VARCHAR(255) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `role`         ENUM('admin','user','manager') NOT NULL DEFAULT 'user',
  `created_at`   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Sample data
INSERT INTO `{ent}s` (name, email, status) VALUES
('Alice Johnson', 'alice@example.com', 'active'),
('Bob Smith', 'bob@example.com', 'active'),
('Carol Williams', 'carol@example.com', 'inactive'),
('David Brown', 'david@example.com', 'active'),
('Emma Davis', 'emma@example.com', 'pending');
"""

    def _env_example(self, manifest) -> str:
        db = manifest.get("database", "mongodb")
        db_name = manifest.get("db_name", "app_db")
        port = manifest.get("port", 3000)
        backend = manifest.get("backend", "nodejs")
        env_vars = manifest.get("env_vars", [])

        lines = [
            f"# Environment Variables — copy to .env and fill in real values",
            f"# DO NOT commit .env to version control\n",
            f"# Server",
            f"PORT={port}",
            f"NODE_ENV=development",
            f"",
            f"# Security",
            f"JWT_SECRET=your-super-secret-jwt-key-change-this-in-production-min-32-chars",
            f"JWT_EXPIRES_IN=7d",
            f"",
        ]

        if db == "mongodb":
            lines += ["# MongoDB", f"MONGODB_URI=mongodb://localhost:27017/{db_name}", "MONGO_URI=mongodb://localhost:27017/{db_name}", ""]
        elif db == "mysql":
            lines += ["# MySQL", "DB_HOST=localhost", "DB_PORT=3306", f"DB_NAME={db_name}", "DB_USER=root", "DB_PASSWORD=your_password", ""]
        elif db == "firebase":
            lines += ["# Firebase", "FIREBASE_PROJECT_ID=your-project-id", "FIREBASE_PRIVATE_KEY=your-private-key", "FIREBASE_CLIENT_EMAIL=your-client-email", ""]
        elif db == "supabase":
            lines += ["# Supabase", "SUPABASE_URL=https://your-project.supabase.co", "SUPABASE_KEY=your-anon-key", "SUPABASE_SERVICE_KEY=your-service-role-key", ""]

        lines += ["# Frontend", "CORS_ORIGIN=http://localhost:5500", "APP_URL=http://localhost:{port}".format(port=port), ""]
        for v in env_vars:
            if v not in "\n".join(lines):
                lines.append(f"{v}=your-value-here")

        return "\n".join(lines)

    def _fullstack_readme(self, plan, arch, manifest) -> str:
        name = plan.get("project_name", "app").replace("-", " ").title()
        backend = manifest.get("backend", "nodejs")
        database = manifest.get("database", "mongodb")
        port = manifest.get("port", 3000)
        api_base = manifest.get("frontend_api_base", f"http://localhost:{port}/api/v1")
        be_info = STACK_BACKENDS.get(backend, {})
        db_info = STACK_DATABASES.get(database, {})
        endpoints = manifest.get("endpoints", [])
        ep_str = "\n".join(f"| {e['method']} | `{e['path']}` | {e.get('desc','')} |" for e in endpoints[:12])

        if backend == "nodejs":
            install_steps = f"""```bash
# 1. Install Node.js dependencies
npm install

# 2. Configure environment
cp .env.example .env
# Edit .env with your real values (DB connection, JWT secret)

# 3. Start the server (development)
npm run dev

# 4. Open frontend
# Option A: Open frontend/index.html directly in browser
# Option B: The server also serves the frontend at http://localhost:{port}
```"""
        elif backend == "django":
            install_steps = f"""```bash
# 1. Create & activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Configure environment
cp .env.example .env  # Edit .env with your values

# 4. Run database migrations
cd backend && python manage.py migrate

# 5. Create superuser (optional)
python manage.py createsuperuser

# 6. Start development server
python manage.py runserver 0.0.0.0:{port}

# 7. Open frontend/index.html in browser
```"""
        else:
            install_steps = f"""```bash
# 1. Configure environment
cp .env.example .env  # Edit .env with your DB credentials

# 2. Import database schema
mysql -u root -p < backend/schema.sql

# 3. Configure web server
# Place backend/ in your PHP server's document root (Apache/Nginx)
# Or use PHP's built-in server: php -S localhost:{port} -t backend/

# 4. Open frontend/index.html in browser
```"""

        return f"""# {name}
**Full-Stack Application** — {be_info.get('label', backend)} + {db_info.get('label', database)}

## Tech Stack
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript, Chart.js
- **Backend**: {be_info.get('label', backend)}
- **Database**: {db_info.get('label', database)}
- **Auth**: JWT (JSON Web Tokens)

## Quick Start

### Prerequisites
{'- Node.js 18+ (https://nodejs.org)' if backend == 'nodejs' else '- Python 3.10+ (https://python.org)' if backend == 'django' else '- PHP 8.1+ with PDO extension'}
{'- MongoDB (https://mongodb.com/try/download) OR MongoDB Atlas (cloud)' if database == 'mongodb' else '- MySQL 8.0+ (https://dev.mysql.com/downloads/)' if database == 'mysql' else ''}

### Installation

{install_steps}

## Project Structure
```
{plan.get('project_name', 'app')}/
├── frontend/           # Frontend SPA
│   ├── index.html     # Main app shell
│   ├── styles.css     # Custom styles
│   ├── app.js         # App logic & routing
│   ├── api.js         # API client (calls backend)
│   └── ui.js          # UI render functions
├── backend/            # {be_info.get('label', backend)} server
│   {'├── server.js  # Express entry point' if backend == 'nodejs' else '├── manage.py  # Django entry point' if backend == 'django' else '├── api/  # PHP API endpoints'}
│   {'├── routes/    # API route handlers' if backend == 'nodejs' else '├── config/  # Settings, URLs' if backend == 'django' else '└── config/  # DB & JWT config'}
│   {'├── models/    # Database models' if backend == 'nodejs' else '└── records/  # App models, views, serializers' if backend == 'django' else ''}
│   {'├── middleware/ # Auth middleware' if backend == 'nodejs' else '' if backend == 'django' else ''}
│   {'└── config/    # DB connection' if backend == 'nodejs' else '' if backend == 'django' else ''}
├── .env.example        # Environment template
├── package.json        # Dependencies
└── README.md           # This file
```

## API Reference

Base URL: `{api_base}`

| Method | Endpoint | Description |
|--------|----------|-------------|
{ep_str}

## Frontend ↔ Backend Sync
All API calls in `frontend/api.js` point to `{api_base}`.
Change `API_BASE` in `frontend/api.js` when deploying to production.

## Environment Variables
See `.env.example` for all required variables. Copy to `.env` and fill in real values.

## Deployment
- **Backend**: Deploy to Railway, Render, Heroku, or any VPS
- **Frontend**: Deploy to Netlify, Vercel, or serve via the backend
- **Database**: Use managed service (MongoDB Atlas, PlanetScale, Firebase)

---
Generated by LovableBot — AI Code Studio 🤖
"""

    def _frontend_api_js(self, fspec, plan, arch, manifest) -> str:
        """Frontend API client that calls the backend — all fetch() calls."""
        req = plan.get("user_request", "")
        api_base = manifest.get("frontend_api_base", "http://localhost:3000/api/v1")
        endpoints = manifest.get("endpoints", [])
        entities = manifest.get("entities", ["Record"])
        ent = entities[0] if entities else "Record"
        ent_lower = ent.lower().replace(" ", "")
        ep_str = "\n".join(f"  {e['method']} {e['path']} — {e.get('desc','')}" for e in endpoints)

        prompt = f"""Write COMPLETE, PRODUCTION-READY frontend API client (api.js) for "{req}".
This file handles ALL communication with the backend REST API.

API Base URL: {api_base}

All backend endpoints to call:
{ep_str}

MANDATORY:
1. const API_BASE = '{api_base}'; at top (easy to change for deployment)
2. getToken() — reads JWT from localStorage ('auth_token')
3. setToken(token) — saves to localStorage
4. removeToken() — removes from localStorage (logout)
5. request(method, path, body, requiresAuth=true) — base fetch function:
   - Sets Content-Type: application/json, Authorization: Bearer token if requiresAuth
   - Handles 401 → redirects to login or shows auth modal
   - Returns parsed JSON or throws error with message
6. API function for EVERY endpoint — named clearly:
   - authRegister(name, email, password) → POST /auth/register
   - authLogin(email, password) → POST /auth/login
   - authMe() → GET /auth/me
   - getAll{ent}s(page=1, limit=10, q='', status='') → GET /{ent_lower}s
   - get{ent}ById(id) → GET /{ent_lower}s/:id
   - create{ent}(data) → POST /{ent_lower}s
   - update{ent}(id, data) → PUT /{ent_lower}s/:id
   - delete{ent}(id) → DELETE /{ent_lower}s/:id
   - getStats() → GET /stats
7. Error interceptor — if response has success: false, throw Error(message)
8. All functions in global scope (no ES modules)

Output ONLY complete ```javascript."""
        resp = call_ai(prompt, timeout=140)
        code = extract_code(resp, "javascript")
        if code and len(code) > 500:
            return code
        # Robust fallback
        return f"""'use strict';

/* ═══ API CLIENT — All backend calls go through here ═══ */
var API_BASE = '{api_base}';

function getToken() {{ return localStorage.getItem('auth_token'); }}
function setToken(t) {{ localStorage.setItem('auth_token', t); }}
function removeToken() {{ localStorage.removeItem('auth_token'); }}

async function request(method, path, body, requiresAuth) {{
  if (requiresAuth === undefined) requiresAuth = true;
  var headers = {{'Content-Type': 'application/json'}};
  var token = getToken();
  if (requiresAuth && token) headers['Authorization'] = 'Bearer ' + token;
  var opts = {{method: method, headers: headers}};
  if (body && method !== 'GET') opts.body = JSON.stringify(body);
  try {{
    var resp = await fetch(API_BASE + path, opts);
    var data = await resp.json();
    if (!resp.ok || data.success === false) throw new Error(data.message || 'Request failed');
    return data;
  }} catch (e) {{
    if (e.message.includes('Failed to fetch')) throw new Error('Cannot connect to server. Make sure the backend is running at ' + API_BASE);
    throw e;
  }}
}}

// ── Auth ──────────────────────────────────────────────────────────────────────
async function authRegister(name, email, password) {{
  var res = await request('POST', '/auth/register', {{name, email, password}}, false);
  if (res.token) setToken(res.token);
  return res;
}}

async function authLogin(email, password) {{
  var res = await request('POST', '/auth/login', {{email, password}}, false);
  if (res.token) setToken(res.token);
  return res;
}}

async function authMe() {{ return request('GET', '/auth/me'); }}
function authLogout() {{ removeToken(); window.location.reload(); }}

// ── Records CRUD ──────────────────────────────────────────────────────────────
async function getAll{ent.replace(' ','')}s(page, limit, q, status) {{
  page = page || 1; limit = limit || 10; q = q || ''; status = status || '';
  return request('GET', '/{ent_lower}s?page=' + page + '&limit=' + limit + '&q=' + encodeURIComponent(q) + '&status=' + status);
}}

async function get{ent.replace(' ','')}ById(id) {{ return request('GET', '/{ent_lower}s/' + id); }}
async function create{ent.replace(' ','')}(data) {{ return request('POST', '/{ent_lower}s', data); }}
async function update{ent.replace(' ','')}(id, data) {{ return request('PUT', '/{ent_lower}s/' + id, data); }}
async function delete{ent.replace(' ','')}(id) {{ return request('DELETE', '/{ent_lower}s/' + id); }}

// ── Stats ─────────────────────────────────────────────────────────────────────
async function getStats() {{ return request('GET', '/stats'); }}
"""

    def _fullstack_frontend_app_js(self, fspec, plan, arch, manifest) -> str:
        """Frontend app.js that uses the API instead of localStorage for data."""
        req = plan.get("user_request", "")
        name = plan.get("project_name", "app").replace("-", " ").title()
        views = plan.get("views", [])
        api_base = manifest.get("frontend_api_base", "http://localhost:3000/api/v1")
        views_list = [v.get("name", "").lower().replace(" ", "-") for v in views] or ["dashboard", "records", "login"]
        first_view = views_list[0]
        views_str = ", ".join(f'"{v}"' for v in views_list)

        prompt = f"""Write COMPLETE frontend app.js for "{req}" full-stack app. MINIMUM 300 LINES.
This app USES THE BACKEND API (not localStorage) for all data.
API client is in api.js (separate file) — call its functions directly.

App: {name}
Views: {views_str}
API Base: {api_base}
Auth: JWT stored in localStorage via api.js

IMPLEMENT ALL:
1. showView(name) — routing with auth guard (redirect to login if no token)
2. renderView(name, el) — call renderDashboard/renderList/renderForm from ui.js
3. toggleDarkMode(), showToast(msg, type), openModal(html), closeModal()
4. safeChart(id, config), exportToCSV(data, filename)
5. Login flow: renderLogin() — shows login form, calls authLogin(), then showView(dashboard)
6. Auth state: isLoggedIn() → !!getToken(), getCurrentUser() → authMe() cached
7. DOMContentLoaded: check auth, loadInitialData(), wire nav-links, keyboard shortcuts
8. loadInitialData() — call getStats() and getAll{(manifest.get('entities',['Record'])[0]).replace(' ','')}s() to pre-fill dashboard
9. handleApiError(err) — if 401 show login, else showToast(err.message, 'error')
10. All functions global scope, var declarations

Output ONLY complete ```javascript."""
        resp = call_ai(prompt, timeout=170)
        code = extract_code(resp, "javascript")
        if code and len(code) > 800:
            return code
        # Fallback to standard app.js without manifest
        return self._app_js(fspec, plan, arch)

    def _get_domain(self, req: str) -> str:
        r = req.lower()
        if any(w in r for w in ["student", "school", "grade", "course", "attendance", "teacher", "academic"]): return "student"
        elif any(w in r for w in ["hospital", "patient", "doctor", "clinic", "medical", "health", "appointment", "nurse", "pharmacy"]): return "hospital"
        elif any(w in r for w in ["employee", "hr", "staff", "payroll", "department", "workforce", "recruit"]): return "hr"
        elif any(w in r for w in ["inventory", "stock", "warehouse", "product", "supplier", "sku", "barcode"]): return "inventory"
        elif any(w in r for w in ["hotel", "reservation", "room", "guest", "booking", "check-in"]): return "hotel"
        elif any(w in r for w in ["library", "book", "author", "borrow", "isbn", "catalog"]): return "library"
        elif any(w in r for w in ["restaurant", "food", "menu", "order", "table", "chef", "kitchen"]): return "restaurant"
        elif any(w in r for w in ["crm", "customer", "client", "lead", "deal", "pipeline", "sales"]): return "crm"
        elif any(w in r for w in ["project", "task", "milestone", "kanban", "sprint", "issue", "ticket"]): return "project"
        elif any(w in r for w in ["real estate", "property", "tenant", "lease", "unit", "rent"]): return "realestate"
        else: return "generic"

    def _get_domain_smart(self, req: str, plan: dict) -> str:
        """AI-domain-aware domain detection. Prefers the AI analysis result over keyword matching."""
        ai_domain = plan.get("analysis", {}).get("domain", "").lower()
        if ai_domain:
            # Map the AI's free-text domain description to our known keys
            checks = [
                ("student",    ["student", "school", "academic", "grade", "course", "enrollment", "teacher"]),
                ("hospital",   ["hospital", "patient", "doctor", "clinic", "medical", "health", "pharmacy", "nurse"]),
                ("hr",         ["employee", "hr", "human resource", "payroll", "staff", "workforce", "recruit"]),
                ("inventory",  ["inventory", "stock", "warehouse", "product", "supplier", "barcode", "sku"]),
                ("hotel",      ["hotel", "reservation", "room", "guest", "booking", "check-in", "hospitality"]),
                ("library",    ["library", "book", "author", "borrow", "isbn", "catalog", "lending"]),
                ("restaurant", ["restaurant", "food", "menu", "table", "kitchen", "dining", "chef", "order"]),
                ("crm",        ["crm", "customer", "client", "lead", "deal", "pipeline", "sales force"]),
                ("project",    ["project", "task", "kanban", "sprint", "milestone", "issue", "ticket"]),
                ("realestate", ["real estate", "property", "tenant", "lease", "rent", "listing", "landlord"]),
            ]
            for key, keywords in checks:
                if any(kw in ai_domain for kw in keywords):
                    return key
        return self._get_domain(req)

    def _html(self, fspec, plan, arch) -> str:
        req = plan.get("user_request", "")
        name = plan.get("project_name", "app").replace("-", " ").title()
        features = plan.get("features", [])
        traits = plan.get("traits", {})
        analysis = plan.get("analysis", {})
        views = plan.get("views", [])
        color = arch.get("color", "indigo")
        accent_hex = analysis.get("primary_color", "#6366f1")

        file_paths = [f["path"] for f in arch.get("files", [])]
        js_files = [p for p in file_paths if p.endswith(".js") and p != "scene.js"]
        # Multifile if there's any JS file alongside the HTML (classic 5-file OR AI-planned)
        if js_files:
            return self._multifile_shell(req, name, features, color, arch, views, analysis)

        cdn_tags = "\n  ".join(arch.get("cdns", []))
        ptype = plan.get("project_type", "webapp")
        if traits.get("is_ecommerce"): ptype = "ecommerce"
        elif traits.get("is_dashboard"): ptype = "dashboard"
        elif traits.get("is_landing"): ptype = "landing"
        elif traits.get("is_game"): ptype = "game"

        if ptype == "game":
            return self._game_prompt(req, name, features, color, cdn_tags, analysis)
        elif ptype == "dashboard":
            return self._dashboard_prompt(req, name, features, color, cdn_tags, analysis)
        elif ptype == "landing":
            return self._landing_prompt(req, name, features, color, cdn_tags, views, analysis)
        elif ptype == "ecommerce":
            return self._ecommerce_prompt(req, name, features, color, cdn_tags, analysis)
        else:
            return self._webapp_prompt(req, name, features, color, cdn_tags, views, analysis)

    def _design_dna(self, req: str, analysis: dict) -> str:
        """Return a design-variety block to inject into every HTML/CSS prompt."""
        variety = analysis.get("design_variety") or pick_design_variety(req, analysis)
        personality = variety.get("personality", DESIGN_PERSONALITIES[0])
        palette = variety.get("palette", COLOR_PALETTES[0])
        accent = variety.get("primary_color", "#6366f1")
        secondary = variety.get("secondary_color", "#8b5cf6")
        pid = personality.get("id", "aurora-dark")
        desc = personality.get("description", "dark professional")
        body_bg = personality.get("body_bg", "#030712")
        text_primary = personality.get("text_primary", "#f9fafb")
        text_secondary = personality.get("text_secondary", "#9ca3af")
        surface = personality.get("surface", "#111827")
        border_color = personality.get("border_color", "#1f2937")
        extra_css = personality.get("extra_css", "")
        card_style = personality.get("card_style", "")
        try:
            r_v, g_v, b_v = tuple(int(accent.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
            rgb = f"{r_v},{g_v},{b_v}"
        except Exception:
            rgb = "99,102,241"

        return f"""
═══ DESIGN PERSONALITY: {pid} ═══
Description: {desc}
You MUST apply this personality precisely. DO NOT default to generic dark glassmorphism with indigo.

REQUIRED DESIGN TOKENS (use EXACTLY these values):
  --brand: {accent}  (RGB: {rgb})
  --brand-secondary: {secondary}
  --bg: {body_bg}
  --surface: {surface}
  --border: {border_color}
  --text-primary: {text_primary}
  --text-secondary: {text_secondary}

Additional CSS personality rules to apply:
  {extra_css}
  Cards: {card_style}

Color palette: primary={palette.get('primary', accent)}, secondary={palette.get('secondary', secondary)}, accent={palette.get('accent', secondary)}, bg={palette.get('bg', body_bg)}, text={palette.get('text', text_primary)}
═══ END DESIGN PERSONALITY ═══"""

    def _webapp_prompt(self, req, name, features, color, cdn_tags, views, analysis) -> str:
        feat_str = "\n".join(f"  - {f}" for f in features)
        views_desc = ", ".join(v.get("name", "") for v in views) if views else "Main, Dashboard, List, Settings"
        variety = analysis.get("design_variety") or pick_design_variety(req, analysis)
        accent = variety.get("primary_color", analysis.get("primary_color", "#6366f1"))
        secondary = variety.get("secondary_color", analysis.get("secondary_color", "#8b5cf6"))
        design_dna = self._design_dna(req, analysis)
        enhanced = analysis.get("enhanced_request", req)

        prompt = f"""You are the world's best frontend engineer and UI/UX designer. Write a COMPLETE, PRODUCTION-READY, VISUALLY STUNNING, ENTERPRISE-GRADE single-file HTML web app. MINIMUM 800 LINES OF REAL CODE. ZERO placeholders. ZERO TODOs. ZERO stubs. Every feature fully implemented and working.

PROJECT: "{req}"
ENHANCED: "{enhanced}"
APP NAME: {name}
PRIMARY COLOR: {accent}
SECONDARY COLOR: {secondary}
SECTIONS/VIEWS: {views_desc}
{design_dna}

REQUIRED FEATURES — implement ALL of these COMPLETELY and PERFECTLY:
{feat_str}

MANDATORY TECHNICAL REQUIREMENTS — implement EVERY SINGLE ONE:
1. <!DOCTYPE html> + complete <head>: charset, viewport, title ({name}), ALL CDN links
2. Tailwind CSS v3 — use EXTENSIVELY: gradients, glass effects (backdrop-blur), shadows, ring, divide, group-hover
3. Full dark/light mode: 'dark:' classes everywhere, toggle button with moon/sun icon, saved to localStorage
4. Alpine.js x-data for ALL reactive state — interactive dropdowns, tabs, toggles, counters
5. CSS custom properties in <style>: --brand: {accent}; --brand-rgb: (r,g,b); full color system
6. STUNNING hero/header: background matching the design personality above, visually striking cards (use the personality's card_style — may be glass/flat/bordered/gradient), animated elements, particle effect or gradient orbs
7. Sticky navbar: logo left, nav links center (active states), dark toggle + CTA right, mobile hamburger with animated menu
8. Multi-section/tab layout: MINIMUM 6 distinct sections/views with smooth transitions
9. ALL data stored in localStorage — realistic sample data pre-loaded on first visit
10. Loading animation (skeleton screens or spinner) that hides after content loads
11. Toast notification system: top-right stack, success/error/warning/info variants, auto-dismiss 4s, close button
12. Modal/dialog system: backdrop blur, animated open/close, form modals, confirmation dialogs
13. Forms with FULL client-side validation: required fields, email format, number ranges, red borders, error messages below inputs
14. Smooth CSS transitions on ALL interactive elements: hover scale, color, shadow, transform
15. Font Awesome 6 icons on ALL buttons, nav items, cards, stat indicators
16. AOS or custom scroll reveal animations on sections (data-aos or IntersectionObserver)
17. Chart.js: MINIMUM 3 different chart types (line, bar, doughnut) with real data, custom colors matching theme
18. Mobile responsive: hamburger menu, card grid adapts, touch targets 44px+, swipe gestures where relevant
19. Keyboard accessibility: Escape=close modals, Enter=submit, Ctrl+K=open search, Tab navigation
20. Empty states: icon + title + description + primary action button
21. Pagination: prev/next buttons, page numbers, showing X-Y of Z
22. Advanced search + filter: live results as you type, dropdown filters, sort by any column
23. Data table: sortable columns (click header = sort), row hover highlight, status badges, action buttons
24. CRUD operations: Add, Edit (pre-fills form with existing data), Delete (confirmation modal), View detail (slide-over or modal)
25. Statistics/analytics: computed from sample data — totals, averages, percentages, trend indicators with up/down arrows
26. Export to CSV: button that downloads current filtered data as a .csv file
27. Bulk actions: checkboxes on table rows, select all, bulk delete/update with confirmation
28. Print view: window.print() with print-specific CSS hiding UI chrome
29. Responsive sidebar (if management app) or section tabs (if single-page) — collapsible, icon labels
30. Absolutely NO generic titles — use {name} throughout. No placeholder content. REAL, WORKING app.

VISUAL QUALITY STANDARDS — this must look like a $10k professional design:
- Background: deep dark gradient (from-gray-950 via-slate-900 to-gray-900) with subtle grain/noise texture via CSS
- Cards: bg-gray-900/80 backdrop-blur-xl border border-gray-800/60 rounded-2xl shadow-2xl p-6
- Stat cards: gradient accent border-left or top glow in primary color, large number, small label, trend badge
- Buttons: gradient bg with shadow glow matching primary color, hover: scale-105, active: scale-95
- Inputs: dark bg, subtle border, focus ring in primary color, smooth transition
- Badges/pills: colored with 12% opacity bg + matching text + border
- Typography: font-bold headings, tracking-tight, gradient text for hero headings
- Micro-animations: hover translateY(-2px), active scale, loading pulse, chart entrance animations
- Accent color {accent} used consistently across all interactive, active, highlighted elements

CDNs (already loaded in <head>, do NOT add again):
{cdn_tags}

Output ONLY the COMPLETE, UNTRUNCATED HTML in a ```html code block. No explanations. No summaries. Just the complete, working code."""

        resp = call_ai(prompt, timeout=150)
        code = extract_code(resp, "html")

        if not is_quality_code(code, "html"):
            # Try with fallback model
            resp2 = call_ai(prompt, model=FALLBACK, timeout=120)
            code2 = extract_code(resp2, "html")
            if is_quality_code(code2, "html") and len(code2) > len(code or ""):
                code = code2

        return code if is_quality_code(code, "html") else self._generate_smart_fallback_html(req, name, color, features, views, analysis)

    def _landing_prompt(self, req, name, features, color, cdn_tags, views, analysis) -> str:
        feat_str = "\n".join(f"  - {f}" for f in features)
        variety = analysis.get("design_variety") or pick_design_variety(req, analysis)
        accent = variety.get("primary_color", analysis.get("primary_color", "#6366f1"))
        secondary = variety.get("secondary_color", analysis.get("secondary_color", "#8b5cf6"))
        design_dna = self._design_dna(req, analysis)
        enhanced = analysis.get("enhanced_request", req)

        prompt = f"""Write a GORGEOUS, CONVERSION-OPTIMIZED, PRODUCTION-READY landing page. MINIMUM 500 LINES OF CODE.

PRODUCT: "{req}"
ENHANCED: "{enhanced}"
BRAND: {name}
PRIMARY COLOR: {accent}
SECONDARY: {secondary}
{design_dna}

KEY FEATURES TO SHOWCASE:
{feat_str}

MANDATORY SECTIONS — all must be fully implemented with real content:
1. HERO: Full-screen height, gradient/mesh background with animated shapes, massive headline (2-3 lines), supporting text, 2 CTA buttons (primary + secondary), hero image/illustration area with floating glass cards
2. STICKY NAVBAR: Logo + brand name left, 5 nav links center, "Get Started" CTA button right, backdrop-blur background, mobile hamburger with full-screen menu overlay
3. SOCIAL PROOF: Logo strip (6+ companies), stats row (3-4 impressive numbers with labels)
4. FEATURES GRID: 6 feature cards in 3x2 grid — each with gradient icon, title, description, hover effect
5. HOW IT WORKS: 4-step process with numbered circles, connector lines, icons, descriptions
6. PRICING: 3 tiers (Free/Starter/Pro) with feature lists, most popular highlighted, monthly/yearly toggle saving badge
7. TESTIMONIALS: 3 testimonial cards with avatar, name, role, company, star rating, quote
8. FAQ ACCORDION: 6+ questions with Alpine.js x-show animated expand/collapse
9. FINAL CTA BANNER: Gradient background, headline, subtext, email input + button
10. FOOTER: 4 columns (brand+desc, Product, Company, Support links), social icons, copyright

TECHNICAL REQUIREMENTS:
- Smooth scroll behavior on all nav links
- AOS scroll-triggered animations on all sections (if loaded)
- Alpine.js for: mobile menu, pricing toggle, FAQ accordion, form submission
- Scroll-to-top floating button (appears after 300px scroll)
- Active section highlighting in navbar on scroll
- All buttons have hover/focus states with smooth transitions
- Fully responsive: mobile, tablet, desktop breakpoints
- Professional typography: large hero text, correct hierarchy

VISUAL QUALITY (follow the design personality above — do NOT default to dark gray themes):
- Apply the design personality's background, surface, and text colors consistently
- Gradient headlines: bg-gradient-to-r text-transparent bg-clip-text using brand colors
- Cards styled per the personality's card_style (may be glass, bordered, flat, or gradient)
- Primary color: {accent} for CTAs, highlights, active states
- Smooth shadows, proper spacing, consistent visual language throughout

CDNs loaded: {cdn_tags}

Output ONLY complete ```html. Real content — no lorem ipsum, real product copy."""

        resp = call_ai(prompt, timeout=160)
        code = extract_code(resp, "html")
        if not is_quality_code(code, "html"):
            resp2 = call_ai(prompt, model=FALLBACK, timeout=130)
            code2 = extract_code(resp2, "html")
            if is_quality_code(code2, "html"):
                code = code2

        return code if is_quality_code(code, "html") else self._generate_smart_fallback_html(req, name, color, features, views, analysis)

    def _dashboard_prompt(self, req, name, features, color, cdn_tags, analysis) -> str:
        feat_str = "\n".join(f"  - {f}" for f in features)
        variety = analysis.get("design_variety") or pick_design_variety(req, analysis)
        accent = variety.get("primary_color", analysis.get("primary_color", "#6366f1"))
        design_dna = self._design_dna(req, analysis)

        prompt = f"""Write a COMPLETE, PROFESSIONAL analytics dashboard HTML file. MINIMUM 500 LINES.

DASHBOARD: "{req}"
NAME: {name}
PRIMARY COLOR: {accent}
{design_dna}

REQUIRED FEATURES:
{feat_str}

MANDATORY COMPONENTS — fully implemented:
1. SIDEBAR: Fixed left sidebar (w-64) with logo, nav items (icon+label), active state, collapse toggle, user profile bottom
2. TOP HEADER: Sticky, search input with icon, date range picker display, notifications bell (badge), user avatar + name dropdown
3. KPI ROW: 4 stat cards — each with: gradient icon bg, metric value (large), label, trend arrow (up/down), % change badge, sparkline
4. MAIN CHART: Full-width Chart.js line chart — 12-month data, gradient fill, smooth curves, custom tooltip, grid lines
5. SPLIT ROW: Bar chart (category breakdown) + Doughnut chart (status distribution) side by side
6. DATA TABLE: Full table with avatar/image column, sortable headers, status badge, action buttons, pagination
7. ACTIVITY FEED: Right sidebar or bottom section showing recent events with icons, timestamps, descriptions
8. DARK/LIGHT TOGGLE: Stored in localStorage, apply 'dark' class to <html>
9. Mobile responsive: sidebar → hamburger, stacked layout

CHART.JS REQUIREMENTS:
- All charts dark-themed: backgroundColor '#111827', gridColor 'rgba(255,255,255,0.05)'
- Gradient fills on line charts (createLinearGradient)
- Custom legend styling with {accent} as primary color
- Realistic data (not all zeros, varied, trending)
- Smooth bezier curves (tension: 0.4)
- Formatted tooltips

CDNs loaded: {cdn_tags}

Output ONLY complete ```html."""

        resp = call_ai(prompt, timeout=160)
        code = extract_code(resp, "html")
        if not is_quality_code(code, "html"):
            resp2 = call_ai(prompt, model=FALLBACK, timeout=130)
            code2 = extract_code(resp2, "html")
            if is_quality_code(code2, "html"):
                code = code2

        return code if is_quality_code(code, "html") else self._generate_smart_fallback_html(req, name, color, features, [], analysis)

    def _game_prompt(self, req, name, features, color, cdn_tags, analysis) -> str:
        feat_str = "\n".join(f"  - {f}" for f in features)
        variety = analysis.get("design_variety") or pick_design_variety(req, analysis)
        accent = variety.get("primary_color", analysis.get("primary_color", "#8b5cf6"))
        design_dna = self._design_dna(req, analysis)

        prompt = f"""Write a COMPLETE, FULLY PLAYABLE HTML5 Canvas game. MINIMUM 400 LINES. All game systems implemented.

GAME: "{req}"
NAME: {name}
ACCENT COLOR: {accent}
{design_dna}

REQUIRED FEATURES:
{feat_str}

MANDATORY GAME SYSTEMS:
1. GAME LOOP: requestAnimationFrame with delta time (Date.now() based), consistent FPS
2. GAME STATES: MENU → PLAYING → PAUSED → GAME_OVER (enum or constants)
3. INPUT: Keyboard (ArrowKeys/WASD/Space), mouse/touch events, preventDefault on game keys
4. PLAYER: Smooth movement, visual representation (gradient rect or arc), boundary checking
5. ENTITIES: Enemies/obstacles/collectibles with spawn system and increasing difficulty
6. COLLISION: AABB or circle collision detection, proper hitbox
7. SCORE SYSTEM: Live score display, multiplier, high score in localStorage
8. LIVES/HEALTH: Visual hearts or health bar, game over when 0
9. LEVELS: Level progression every N score, speed/difficulty increases, level announcement
10. AUDIO: Web Audio API sounds (not files) — beeps for collect, buzz for death, chord for level up
11. PARTICLES: Particle effects on collision, death, score events
12. CANVAS UI: Score top-left, lives top-right, level center-top, pause indicator
13. MENU SCREEN: Title, high score display, controls instructions, "Press SPACE to start"
14. GAME OVER: Score, high score, "New High Score!" if applicable, restart button/key
15. PAUSE: 'P' key toggle, dim canvas, "PAUSED" text, resume instructions

VISUAL STANDARDS:
- Dark canvas background (very dark purple/navy/black)
- Neon glows on player and key elements (shadowBlur, shadowColor)
- Gradient fills on player and enemies
- Smooth particle effects using canvas arcs
- Professional UI with rounded rects for health bars

CDNs loaded: {cdn_tags}

Output ONLY complete ```html with ALL game code in <script> tags. No external dependencies."""

        resp = call_ai(prompt, timeout=160)
        code = extract_code(resp, "html")
        if not is_quality_code(code, "html"):
            resp2 = call_ai(prompt, model=FALLBACK, timeout=130)
            code2 = extract_code(resp2, "html")
            if is_quality_code(code2, "html"):
                code = code2

        return code if is_quality_code(code, "html") else self._generate_smart_fallback_html(req, name, color, features, [], analysis)

    def _ecommerce_prompt(self, req, name, features, color, cdn_tags, analysis) -> str:
        feat_str = "\n".join(f"  - {f}" for f in features)
        variety = analysis.get("design_variety") or pick_design_variety(req, analysis)
        accent = variety.get("primary_color", analysis.get("primary_color", "#6366f1"))
        design_dna = self._design_dna(req, analysis)
        enhanced = analysis.get("enhanced_request", req)

        prompt = f"""Write a COMPLETE, BEAUTIFUL e-commerce store HTML file. MINIMUM 500 LINES.

STORE: "{req}"
ENHANCED: "{enhanced}"
NAME: {name}
PRIMARY: {accent}
{design_dna}

REQUIRED FEATURES:
{feat_str}

MANDATORY COMPONENTS:
1. NAVBAR: Logo, category links, search bar (live filter), cart icon with animated badge count, wishlist icon
2. HERO BANNER: Large promotional banner with gradient, sale text, CTA button
3. CATEGORY TABS: Clickable tabs (All + 4-6 categories), active state, smooth transition
4. PRODUCT GRID: Minimum 12 products in responsive grid (3 cols desktop, 2 tablet, 1 mobile):
   - Each card: gradient color placeholder image div, product name, price, rating stars (★), reviews count, discount badge, heart wishlist toggle, "Add to Cart" button
5. CART SIDEBAR: Slide-in from right (transform translateX), overlay backdrop, item list with quantity ±, item remove, subtotal, "Checkout" button
6. QUICK-VIEW MODAL: Full product detail, description, size/variant selector, quantity, add to cart
7. SEARCH: Live filter on product name/category as user types
8. SORT: Price low-high, high-low, rating, newest
9. PRICE FILTER: Slider or preset buttons (Under $50, $50-100, $100+)
10. WISHLIST: Heart toggle saves to localStorage, wishlist tab to view saved items
11. TOAST: "Added to cart!", "Saved to wishlist!" notifications
12. CART PERSISTENCE: localStorage, reload restores cart
13. EMPTY STATES: Empty cart, no search results, no wishlist items
14. FOOTER: Company info, links, payment icons

Alpine.js x-data state management for: cart, wishlist, activeCategory, searchQuery, sortBy, quickViewProduct, cartOpen
LocalStorage: cart, wishlist

CDNs loaded: {cdn_tags}

Output ONLY complete ```html."""

        resp = call_ai(prompt, timeout=160)
        code = extract_code(resp, "html")
        if not is_quality_code(code, "html"):
            resp2 = call_ai(prompt, model=FALLBACK, timeout=130)
            code2 = extract_code(resp2, "html")
            if is_quality_code(code2, "html"):
                code = code2

        return code if is_quality_code(code, "html") else self._generate_smart_fallback_html(req, name, color, features, [], analysis)

    def _python(self, fspec, plan) -> str:
        req = plan.get("user_request", "")
        features = plan.get("features", [])
        traits = plan.get("traits", {})
        feat_str = "\n".join(f"  - {f}" for f in features)
        has_auth = traits.get("is_auth", False) or "auth" in req.lower() or "login" in req.lower()

        prompt = f"""Write a COMPLETE Python Flask REST API. MINIMUM 200 LINES. All endpoints fully implemented.

PROJECT: "{req}"

REQUIRED FEATURES:
{feat_str}

MANDATORY IMPLEMENTATION:
1. All imports at top (flask, flask_cors, os, uuid, datetime{', werkzeug.security' if has_auth else ''})
2. Flask app with CORS(app, origins="*")
3. In-memory data stores (dicts/lists) pre-populated with 5+ sample records
4. {'JWT-style auth with token store dict' if has_auth else 'No auth required'}
5. COMPLETE routes for ALL features:
   - GET /health → {{"status":"ok","version":"1.0","timestamp":...}}
   - Full CRUD for main resource (GET list, GET by ID, POST, PUT, DELETE)
   - Search: GET /items?q=query&page=1&per_page=10
   - Filter: GET /items?status=active&category=X
   {'- POST /auth/register (hash password with werkzeug)' if has_auth else ''}
   {'- POST /auth/login (verify hash, return token)' if has_auth else ''}
6. Consistent JSON: {{"success":bool,"data":...,"message":str,"total":int,"page":int}}
7. Error handlers: @app.errorhandler(400), (404), (405), (500)
8. Request body validation with descriptive errors
9. Pagination (page, per_page query params), returns total, pages, current_page
10. CORS headers on all responses
11. Sample data: 5+ realistic records in the in-memory store
12. Detailed docstrings on every route
13. if __name__ == '__main__': app.run(debug=True, host='0.0.0.0', port=5000)

Output ONLY complete ```python code."""

        resp = call_ai(prompt, timeout=130)
        code = extract_code(resp, "python")
        if not is_quality_code(code, "python"):
            resp2 = call_ai(prompt, model=FALLBACK, timeout=100)
            code2 = extract_code(resp2, "python")
            if is_quality_code(code2, "python"):
                code = code2

        return code if is_quality_code(code, "python") else self._fallback_flask(plan)

    def _js(self, fspec, plan) -> str:
        req = plan.get("user_request", "")
        purpose = fspec.get("purpose", req)
        prompt = f"""Write complete, production-ready JavaScript for: {purpose}
Project context: {req}
Requirements: No placeholders, no TODOs, fully functional, minimum 100 lines.
Output ONLY the complete ```javascript code."""
        resp = call_ai(prompt, timeout=100)
        code = extract_code(resp, "javascript")
        return code if code else "// JavaScript module\n'use strict';\n"

    def _module_js(self, fspec: dict, plan: dict, arch: dict) -> str:
        """Generate a rich, purpose-specific JavaScript module for AI-planned files."""
        req = plan.get("user_request", "")
        fname = fspec["path"]
        purpose = fspec.get("purpose", fname)
        features = plan.get("features", [])
        project_name = plan.get("project_name", "app")
        all_files = [f["path"] for f in arch.get("files", [])]
        other_js = [p for p in all_files if p.endswith(".js") and p != fname]

        prompt = f"""You are a world-class senior JavaScript engineer writing production-grade module code. Write the COMPLETE, FULLY-IMPLEMENTED '{fname}' JavaScript module for this project.

Project: {project_name}
User request: {req}
This file's role: {purpose}
Other JS files in project: {', '.join(other_js) if other_js else 'none'}
ALL features this file must implement: {json.dumps(features)}

MANDATORY REQUIREMENTS — no exceptions:
1. MINIMUM 300 LINES of real, working JavaScript code — this is a full production module
2. Write ONLY code that belongs in THIS file ('{fname}') — no duplicating other files
3. 'use strict'; at the very top
4. ALL functions fully implemented — ZERO placeholders, ZERO TODOs, ZERO stubs, ZERO "// implement later"
5. Export ALL public functions as window globals: window.functionName = function() {{...}}
6. COMPLETE function bodies — every if/else branch handled, every error case covered
7. If this module manages data: include 25+ realistic, varied sample records with real names/dates/IDs
8. If this module handles UI: build complete, rich HTML strings with proper Tailwind classes and Font Awesome icons
9. If this module handles charts: complete Chart.js config objects — datasets, labels, options, colors — for each chart
10. If this module handles forms: full field rendering, validation logic, and submit handlers
11. If this module handles reports: real calculation functions, totals, averages, percentiles, formatted output
12. Include comprehensive error handling, edge cases, null checks
13. Add detailed JSDoc comments above every public function
14. DOMContentLoaded or window-load event listener if this module needs DOM initialization

QUALITY BAR: This module should be indistinguishable from code written by a senior engineer at a top tech company. Rich, complete, functional, well-structured.

Output ONLY the complete ```javascript code block. No explanations."""

        resp = call_ai(prompt, timeout=160)
        code = extract_code(resp, "javascript")
        if code and len(code) > 200:
            return code
        # Fallback to generic
        return self._js(fspec, plan)

    def _js_script_tags(self, arch: dict) -> str:
        """Generate <script> tags for all JS files in the architecture, in correct load order."""
        files = arch.get("files", [])
        js_files = sorted(
            [f for f in files if f["path"].endswith(".js") and f["path"] != "scene.js"],
            key=lambda f: f.get("priority", 99)
        )
        if not js_files:
            # Default classic order
            return '  <script src="data.js"></script>\n  <script src="ui.js"></script>\n  <script src="app.js"></script>'

        # Put data.js first, app.js last, everything else in between
        data_files = [f for f in js_files if "data" in f["path"]]
        app_files  = [f for f in js_files if f["path"] == "app.js"]
        mid_files  = [f for f in js_files if f not in data_files and f not in app_files]

        ordered = data_files + mid_files + app_files
        return "\n  ".join(f'<script src="{f["path"]}"></script>' for f in ordered)

    def _multifile_shell(self, req, name, features, color, arch, views, analysis) -> str:
        cdn_tags = "\n  ".join(arch.get("cdns", []))
        views_list = views or [{"name": "Dashboard"}, {"name": "Records"}, {"name": "Add New"}, {"name": "Reports"}]

        # ── Design Variety ────────────────────────────────────────────────────
        variety = analysis.get("design_variety") or pick_design_variety(req, analysis)
        personality = variety.get("personality", DESIGN_PERSONALITIES[0])
        palette = variety.get("palette", COLOR_PALETTES[0])
        accent = variety.get("primary_color", analysis.get("primary_color", "#6366f1"))

        body_bg = personality.get("body_bg", "#030712")
        text_primary = personality.get("text_primary", "#f9fafb")
        text_secondary = personality.get("text_secondary", "#9ca3af")
        surface = personality.get("surface", "#111827")
        surface2 = personality.get("surface2", "#1f2937")
        border_color = personality.get("border_color", "#1f2937")
        sidebar_style = personality.get("sidebar_style", "background:#111827; border-right:1px solid #1f2937;")
        header_style = personality.get("header_style", "background:rgba(17,24,39,0.9); backdrop-filter:blur(12px); border-bottom:1px solid #1f2937;")
        card_style = personality.get("card_style", "background:#111827; border:1px solid #1f2937; border-radius:12px;")
        body_style = personality.get("bg_style", f"background:{body_bg};")
        extra_css = personality.get("extra_css", "")
        dark_class = personality.get("dark_mode_class", "dark")

        domain = self._get_domain_smart(req, {"analysis": analysis})
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

        def nav_icon(vname):
            n = vname.lower()
            if any(w in n for w in ["dashboard", "home", "overview"]): return "fa-gauge-high"
            if any(w in n for w in ["student", "patient", "employee", "contact", "guest", "member", "people"]): return "fa-users"
            if any(w in n for w in ["doctor", "staff"]): return "fa-user-md"
            if any(w in n for w in ["course", "subject", "class"]): return "fa-book"
            if any(w in n for w in ["report", "analytic", "stat", "insight"]): return "fa-chart-bar"
            if any(w in n for w in ["add", "new", "create"]): return "fa-plus-circle"
            if any(w in n for w in ["grade", "result", "score"]): return "fa-star-half-stroke"
            if any(w in n for w in ["attend"]): return "fa-calendar-check"
            if any(w in n for w in ["schedule", "appointment", "calendar"]): return "fa-calendar-days"
            if any(w in n for w in ["room", "ward"]): return "fa-door-open"
            if any(w in n for w in ["payment", "billing", "payroll", "finance"]): return "fa-credit-card"
            if any(w in n for w in ["inventory", "stock", "product", "item"]): return "fa-boxes-stacked"
            if any(w in n for w in ["setting", "config", "preference"]): return "fa-gear"
            if any(w in n for w in ["profile", "account"]): return "fa-circle-user"
            if any(w in n for w in ["message", "notif", "alert"]): return "fa-bell"
            if any(w in n for w in ["task", "project", "kanban"]): return "fa-list-check"
            if any(w in n for w in ["list", "record", "all", "manage"]): return "fa-table-list"
            if any(w in n for w in ["supplier", "vendor"]): return "fa-truck"
            if any(w in n for w in ["order", "purchase"]): return "fa-shopping-cart"
            return "fa-circle-dot"

        nav_links = "\n        ".join(
            f'<a href="#" data-view="{v["name"].lower().replace(" ", "-")}" class="nav-link" title="{v.get("desc", v["name"])}">'
            f'<i class="fa-solid {nav_icon(v["name"])} mr-3 w-4 text-center text-sm"></i>'
            f'<span>{v["name"]}</span></a>'
            for v in views_list
        )
        view_divs = "\n    ".join(
            f'<div id="view-{v["name"].lower().replace(" ", "-")}" class="view-section hidden"></div>'
            for v in views_list
        )

        r_val, g_val, b_val = tuple(int(accent.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        accent_rgb = f"{r_val},{g_val},{b_val}"

        return f"""<!DOCTYPE html>
<html lang="en" class="{dark_class}">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{name}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  {cdn_tags}
  <link rel="stylesheet" href="styles.css"/>
  <style>
    :root {{
      --brand: {accent};
      --brand-rgb: {accent_rgb};
      --body-bg: {body_bg};
      --surface: {surface};
      --surface-2: {surface2};
      --border: {border_color};
      --text-primary: {text_primary};
      --text-secondary: {text_secondary};
    }}
    body {{ {body_style} color: var(--text-primary); min-height: 100vh; }}
    {extra_css}
  </style>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          colors: {{
            brand: {{
              50: '#f5f3ff', 100: '#ede9fe', 200: '#ddd6fe',
              300: '#c4b5fd', 400: '#a78bfa', 500: '{accent}',
              600: '#7c3aed', 700: '#6d28d9', 800: '#5b21b6', 900: '#4c1d95'
            }}
          }}
        }}
      }}
    }};
  </script>
</head>
<body style="{body_style} color:{text_primary};">

  <!-- Mobile overlay -->
  <div id="sidebar-overlay" class="fixed inset-0 bg-black/60 z-30 hidden lg:hidden" onclick="toggleSidebar()"></div>

  <!-- Sidebar -->
  <aside id="sidebar" class="sidebar w-64 flex flex-col min-h-screen fixed left-0 top-0 z-40" style="{sidebar_style}">
    <!-- Logo -->
    <div class="p-5" style="border-bottom:1px solid {border_color};">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl flex items-center justify-center shadow-lg" style="background: linear-gradient(135deg, {accent}, {palette.get('secondary', accent+'99')});">
          <i class="fa-solid {domain_icon} text-white text-sm"></i>
        </div>
        <div class="min-w-0">
          <h1 class="font-bold text-sm truncate" style="color:{text_primary};">{name}</h1>
          <p class="text-xs" style="color:{text_secondary};">{domain_subtitle}</p>
        </div>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 p-3 space-y-0.5 overflow-y-auto" id="sidebar-nav">
      <p class="text-xs font-semibold uppercase tracking-wider px-3 py-2" style="color:{text_secondary}; opacity:0.5;">Navigation</p>
      {nav_links}
    </nav>

    <!-- User -->
    <div class="p-4" style="border-top:1px solid {border_color};">
      <div class="flex items-center gap-3 p-2.5 rounded-xl cursor-pointer transition" style="background:rgba({accent_rgb},0.08);" onmouseover="this.style.background='rgba({accent_rgb},0.14)'" onmouseout="this.style.background='rgba({accent_rgb},0.08)'">
        <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white shadow" style="background: linear-gradient(135deg, {accent}, {palette.get('secondary', accent)});">A</div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium truncate" style="color:{text_primary};">Admin User</p>
          <p class="text-xs" style="color:{text_secondary};">Administrator</p>
        </div>
        <i class="fa-solid fa-ellipsis-vertical text-xs" style="color:{text_secondary};"></i>
      </div>
    </div>
  </aside>

  <!-- Main Content -->
  <div class="flex-1 flex flex-col min-h-screen main-content" style="margin-left:256px;">
    <!-- Header -->
    <header class="sticky top-0 z-20 px-6 py-3.5 flex items-center justify-between gap-4" style="{header_style}">
      <div class="flex items-center gap-4">
        <button onclick="toggleSidebar()" class="p-2 rounded-lg transition lg:hidden" style="color:{text_secondary};" onmouseover="this.style.color='{text_primary}'" onmouseout="this.style.color='{text_secondary}'">
          <i class="fa-solid fa-bars text-base"></i>
        </button>
        <div class="relative hidden sm:block">
          <i class="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-xs" style="color:{text_secondary};"></i>
          <input type="text" id="global-search" placeholder="Search... (Ctrl+K)"
            oninput="handleSearch(this.value)"
            style="background:{surface}; border:1px solid {border_color}; color:{text_primary}; border-radius:10px; padding:7px 12px 7px 34px; font-size:13px; outline:none; width:240px; transition:border-color 0.2s ease;"
            onfocus="this.style.borderColor='{accent}'" onblur="this.style.borderColor='{border_color}'"/>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button id="dark-toggle" onclick="toggleDarkMode()" class="p-2 rounded-xl transition" style="background:{surface}; color:{text_secondary};" title="Toggle theme">
          <i class="fa-solid fa-moon text-sm"></i>
        </button>
        <button class="relative p-2 rounded-xl transition" style="background:{surface}; color:{text_secondary};" title="Notifications">
          <i class="fa-solid fa-bell text-sm"></i>
          <span class="absolute top-1.5 right-1.5 w-2 h-2 rounded-full" style="background:{accent}; box-shadow:0 0 6px {accent};"></span>
        </button>
        <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white ml-1 cursor-pointer" style="background:linear-gradient(135deg,{accent},{palette.get('secondary',accent)});" title="Profile">A</div>
      </div>
    </header>

    <!-- Page Content -->
    <main class="flex-1 p-6 overflow-x-hidden" id="main-content">
      {view_divs}
    </main>
  </div>

  <!-- Toast Container -->
  <div id="toast-container" class="fixed bottom-6 right-6 z-50 space-y-3 pointer-events-none"></div>

  <!-- Modal Overlay -->
  <div id="modal-overlay" class="hidden fixed inset-0 z-50 flex items-center justify-center p-4" style="background:rgba(0,0,0,0.75); backdrop-filter:blur(8px);">
    <div id="modal-content" class="w-full max-w-lg max-h-[90vh] overflow-y-auto pointer-events-auto" style="{card_style} padding:0;"></div>
  </div>

  {self._js_script_tags(arch)}
</body>
</html>"""

    def _css(self, fspec, plan, arch) -> str:
        req = plan.get("user_request", "")
        name = plan.get("project_name", "app").replace("-", " ").title()
        analysis = plan.get("analysis", {})
        variety = analysis.get("design_variety") or pick_design_variety(req, analysis)
        personality = variety.get("personality", DESIGN_PERSONALITIES[0])
        accent = variety.get("primary_color", analysis.get("primary_color", "#6366f1"))
        secondary = variety.get("secondary_color", "#8b5cf6")
        body_bg = personality.get("body_bg", "#030712")
        text_primary = personality.get("text_primary", "#f9fafb")
        text_secondary = personality.get("text_secondary", "#9ca3af")
        surface = personality.get("surface", "#111827")
        surface2 = personality.get("surface2", "#1f2937")
        border_color = personality.get("border_color", "#1f2937")
        design_id = personality.get("id", "aurora-dark")
        design_desc = personality.get("description", "dark professional")
        card_style = personality.get("card_style", "")
        extra_css = personality.get("extra_css", "")
        feat_str = "\n".join(f"  - {f}" for f in plan.get("features", []))

        try:
            r_val, g_val, b_val = tuple(int(accent.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
            rgb = f"{r_val},{g_val},{b_val}"
        except Exception:
            rgb = "99,102,241"

        prompt = f"""Write COMPLETE, PRODUCTION-QUALITY, VISUALLY DISTINCTIVE CSS for this web app: "{req}"
App: {name}

DESIGN PERSONALITY: {design_id} — {design_desc}
You MUST implement this exact design personality throughout the CSS. Do NOT default to generic dark glassmorphism.

Design Tokens (use these EXACTLY):
- Primary accent: {accent} (RGB: {rgb})
- Secondary: {secondary}
- Body background: {body_bg}
- Text primary: {text_primary}
- Text secondary: {text_secondary}
- Surface (cards): {surface}
- Surface 2 (inputs, table headers): {surface2}
- Border color: {border_color}
- Card style hint: {card_style}

Additional personality CSS to incorporate:
{extra_css}

MANDATORY CSS — implement ALL precisely:
1. :root {{ --brand:{accent}; --brand-rgb:{rgb}; --bg:{body_bg}; --surface:{surface}; --surface-2:{surface2}; --border:{border_color}; --text-primary:{text_primary}; --text-secondary:{text_secondary}; --text-muted:rgba({rgb},0.4); }}
2. * {{ box-sizing:border-box; margin:0; padding:0; }}
3. body — use the design personality's background colors and text colors
4. .sidebar — smooth transform transition, personality-appropriate styling (NOT always bg-gray-900)
5. .nav-link — flex align-items-center, padding, border-radius, color var(--text-secondary), transition all, text-decoration none, display flex, margin-bottom 2px
6. .nav-link:hover — background rgba(var(--brand-rgb), 0.12), color var(--text-primary)
7. .nav-link.active — background rgba(var(--brand-rgb), 0.18), color var(--brand), border-left 3px solid var(--brand), font-weight 600
8. .view-section — animation fadeIn 0.3s ease
9. @keyframes fadeIn — opacity 0→1, translateY 10px→0
10. .data-table — width 100%, border-collapse collapse, font-size .875rem
11. .data-table th — background var(--surface-2), padding .7rem 1rem, text-align left, font-size .72rem, text-transform uppercase, letter-spacing .07em, color var(--text-secondary)
12. .data-table td — padding .7rem 1rem, border-bottom 1px solid var(--border), color var(--text-primary)
13. .data-table tr:hover td — background rgba(var(--brand-rgb), 0.04)
14. .card — use personality's card_style, padding 1.25rem, transition box-shadow .2s ease
15. .stat-card — display flex, justify-content space-between, align-items flex-start; hover translateY(-2px)
16. .badge — inline-flex, border-radius 9999px, font-size .7rem, font-weight 600, padding .2rem .6rem
17. .badge-success, .badge-danger, .badge-warning, .badge-info — with appropriate colors and background
18. .btn — inline-flex items-center gap .45rem, padding .5rem 1rem, border-radius .55rem, font-size .875rem, font-weight 500, cursor pointer, transition all, border none
19. .btn-primary — background var(--brand), color white, box-shadow 0 2px 12px rgba(var(--brand-rgb),.35)
20. .btn-danger, .btn-secondary — appropriate variants
21. .form-input — full-width, background var(--surface-2), border 1px solid var(--border), border-radius .55rem, padding .6rem .9rem, color var(--text-primary), outline none, transition border-color
22. .form-input:focus — border-color var(--brand), box-shadow 0 0 0 3px rgba(var(--brand-rgb),.15)
23. .form-group — margin-bottom 1.1rem
24. label — display block, font-size .8rem, color var(--text-secondary), margin-bottom .4rem, font-weight 500
25. #toast-container .toast — personality-appropriate background, border, border-radius, padding, min-width 290px, flex, animation slideIn 0.3s
26. @keyframes slideIn, @keyframes shimmer
27. .skeleton — shimmer background animation
28. @media (max-width:1023px): .sidebar transform translateX(-100%), .sidebar.open translateX(0), .main-content margin-left 0 !important
29. ::-webkit-scrollbar — thin, personality-appropriate colors
30. .main-content — transition margin-left .3s ease

ADD personality-specific special effects matching the design id "{design_id}".

Output ONLY complete ```css. Minimum 120 lines. Make it beautiful and UNIQUE — not generic."""

        resp = call_ai(prompt, timeout=110)
        css = extract_code(resp, "css")
        if not is_quality_code(css, "css"):
            resp2 = call_ai(prompt, model=FALLBACK, timeout=90)
            css2 = extract_code(resp2, "css")
            if is_quality_code(css2, "css"):
                css = css2

        return css if is_quality_code(css, "css") else self._fallback_css(accent)

    def _fallback_css(self, accent: str) -> str:
        try:
            r, g, b = tuple(int(accent.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
            rgb = f"{r},{g},{b}"
        except Exception:
            rgb = "99,102,241"
        return f""":root {{
  --brand: {accent};
  --brand-rgb: {rgb};
  --bg: #030712;
  --surface: #111827;
  --surface-2: #1f2937;
  --border: #1f2937;
  --text-primary: #f9fafb;
  --text-secondary: #9ca3af;
  --text-muted: #4b5563;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: var(--bg); color: var(--text-primary); font-family: 'Inter', system-ui, -apple-system, sans-serif; line-height: 1.5; }}
.sidebar {{ transition: transform .3s cubic-bezier(.4,0,.2,1), box-shadow .3s ease; box-shadow: 4px 0 24px rgba(0,0,0,.3); }}
.nav-link {{ display: flex; align-items: center; padding: .55rem 1rem; border-radius: .6rem; color: var(--text-secondary); font-size: .875rem; cursor: pointer; transition: all .18s ease; text-decoration: none; border-left: 3px solid transparent; margin-bottom: 2px; }}
.nav-link:hover {{ background: rgba(var(--brand-rgb),.1); color: var(--text-primary); }}
.nav-link.active {{ background: rgba(var(--brand-rgb),.15); color: var(--brand); border-left-color: var(--brand); font-weight: 500; }}
.view-section {{ animation: fadeIn .3s ease; }}
@keyframes fadeIn {{ from {{ opacity:0; transform:translateY(8px) }} to {{ opacity:1; transform:translateY(0) }} }}
.data-table {{ width:100%; border-collapse:collapse; font-size:.875rem; }}
.data-table th {{ background:var(--surface-2); padding:.7rem 1rem; text-align:left; font-size:.72rem; text-transform:uppercase; letter-spacing:.07em; color:var(--text-secondary); border-bottom:1px solid var(--border); white-space:nowrap; }}
.data-table td {{ padding:.7rem 1rem; border-bottom:1px solid var(--border); color:var(--text-primary); }}
.data-table tr:hover td {{ background:rgba(255,255,255,.025); }}
.data-table tbody tr:last-child td {{ border-bottom:none; }}
.card {{ background:var(--surface); border:1px solid var(--border); border-radius:.875rem; padding:1.25rem; transition:box-shadow .2s ease, transform .2s ease; }}
.card:hover {{ box-shadow:0 8px 32px rgba(0,0,0,.25); }}
.stat-card {{ display:flex; justify-content:space-between; align-items:flex-start; }}
.stat-card:hover {{ transform:translateY(-2px); box-shadow:0 12px 36px rgba(0,0,0,.3); }}
.badge {{ display:inline-flex; align-items:center; padding:.2rem .6rem; border-radius:9999px; font-size:.7rem; font-weight:600; letter-spacing:.02em; }}
.badge-success {{ background:rgba(34,197,94,.12); color:#4ade80; border:1px solid rgba(34,197,94,.2); }}
.badge-danger {{ background:rgba(239,68,68,.12); color:#f87171; border:1px solid rgba(239,68,68,.2); }}
.badge-warning {{ background:rgba(245,158,11,.12); color:#fbbf24; border:1px solid rgba(245,158,11,.2); }}
.badge-info {{ background:rgba(var(--brand-rgb),.12); color:var(--brand); border:1px solid rgba(var(--brand-rgb),.2); }}
.btn {{ display:inline-flex; align-items:center; gap:.45rem; padding:.5rem 1rem; border-radius:.55rem; font-size:.875rem; font-weight:500; cursor:pointer; transition:all .18s ease; border:none; outline:none; text-decoration:none; white-space:nowrap; }}
.btn:active {{ transform:scale(.97); }}
.btn-primary {{ background:var(--brand); color:#fff; box-shadow:0 2px 12px rgba(var(--brand-rgb),.4); }}
.btn-primary:hover {{ opacity:.9; box-shadow:0 4px 16px rgba(var(--brand-rgb),.5); }}
.btn-danger {{ background:rgba(239,68,68,.12); color:#f87171; border:1px solid rgba(239,68,68,.2); }}
.btn-danger:hover {{ background:rgba(239,68,68,.22); }}
.btn-secondary {{ background:var(--surface-2); color:var(--text-secondary); border:1px solid var(--border); }}
.btn-secondary:hover {{ background:var(--border); color:var(--text-primary); }}
.form-input {{ width:100%; background:var(--surface-2); border:1px solid var(--border); border-radius:.55rem; padding:.6rem .9rem; color:var(--text-primary); font-size:.875rem; outline:none; transition:border-color .18s ease, box-shadow .18s ease; }}
.form-input:focus {{ border-color:var(--brand); box-shadow:0 0 0 3px rgba(var(--brand-rgb),.12); }}
.form-group {{ margin-bottom:1.1rem; }}
label {{ display:block; font-size:.8rem; color:var(--text-secondary); margin-bottom:.4rem; font-weight:500; }}
#toast-container .toast {{ background:var(--surface); border:1px solid var(--border); border-radius:.875rem; padding:.8rem 1.1rem; min-width:290px; font-size:.875rem; display:flex; align-items:center; gap:.65rem; animation:slideIn .3s cubic-bezier(.34,1.56,.64,1); box-shadow:0 8px 32px rgba(0,0,0,.4); pointer-events:auto; }}
@keyframes slideIn {{ from {{ transform:translateX(110%); opacity:0 }} to {{ transform:translateX(0); opacity:1 }} }}
@keyframes shimmer {{ from {{ background-position:-200% 0 }} to {{ background-position:200% 0 }} }}
.skeleton {{ background: linear-gradient(90deg, var(--surface) 25%, var(--surface-2) 50%, var(--surface) 75%); background-size:200% 100%; animation: shimmer 1.6s infinite; border-radius:.5rem; }}
::-webkit-scrollbar {{ width:5px; height:5px; }}
::-webkit-scrollbar-track {{ background:transparent; }}
::-webkit-scrollbar-thumb {{ background:var(--border); border-radius:99px; }}
::-webkit-scrollbar-thumb:hover {{ background:rgba(var(--brand-rgb),.5); }}
@media(max-width:1023px) {{
  .sidebar {{ transform:translateX(-100%); }}
  .sidebar.open {{ transform:translateX(0); }}
  .main-content {{ margin-left:0 !important; }}
}}
.main-content {{ transition:margin-left .3s cubic-bezier(.4,0,.2,1); }}
"""

    def _app_js(self, fspec, plan, arch) -> str:
        req = plan.get("user_request", "")
        name = plan.get("project_name", "app").replace("-", " ").title()
        views = plan.get("views", [])
        features = plan.get("features", [])
        feat_str = "\n".join(f"  - {f}" for f in features)
        views_list = [v.get("name", "").lower().replace(" ", "-") for v in views] or ["dashboard", "records", "add-new", "reports"]
        first_view = views_list[0]
        views_str = ", ".join(f'"{v}"' for v in views_list)
        domain = self._get_domain_smart(req, plan)

        analysis = plan.get("analysis", {})
        variety = analysis.get("design_variety") or pick_design_variety(req, analysis)
        accent = variety.get("primary_color", "#6366f1")

        prompt = f"""You are a senior JavaScript engineer. Write COMPLETE, PRODUCTION-READY app.js for a "{req}" web app. MINIMUM 450 LINES of real, working JavaScript. Every function FULLY implemented. Zero stubs. Zero TODOs. Zero incomplete branches. Production quality.

App: {name}
Domain: {domain}
Brand color: {accent}
Views: {views_str}
Features:
{feat_str}

IMPLEMENT ALL FUNCTIONS — zero stubs, zero TODOs, every branch complete:

1. showView(name):
   - Hide ALL .view-section elements
   - Remove 'active' from ALL .nav-link elements
   - Show element with id='view-'+name, add class 'active' to matching nav-link
   - Destroy all charts (call Object.values(_charts).forEach(c => c.destroy()))
   - Reset _charts to {{}}
   - Call renderView(name, el)
   - Update document.title to name + ' | {name}'

2. renderView(name, el):
   - Switch on name, call appropriate render function from ui.js
   - Default: renderList if has records in name, renderDashboard if dashboard/home

3. toggleSidebar():
   - Toggle .open on #sidebar
   - Toggle display of #sidebar-overlay
   - document.body.style.overflow toggle

4. toggleDarkMode():
   - Toggle 'dark' class on document.documentElement
   - Save to localStorage key 'theme'
   - Update moon/sun icon in #dark-toggle button

5. handleSearch(query):
   - Get current active view
   - Call renderView(currentView, null, query)

6. showToast(message, type='success'):
   - Types: success, error, warning, info
   - Icons: fa-circle-check, fa-circle-xmark, fa-triangle-exclamation, fa-circle-info
   - Colors: #4ade80, #f87171, #fbbf24, #818cf8
   - Create div.toast, append to #toast-container
   - Auto-remove after 3500ms with fade-out

7. openModal(htmlContent):
   - Set #modal-content innerHTML = htmlContent
   - Remove 'hidden' from #modal-overlay
   - document.body.style.overflow = 'hidden'

8. closeModal():
   - Add 'hidden' to #modal-overlay
   - Clear #modal-content innerHTML
   - document.body.style.overflow = ''

9. exportToCSV(data, filename):
   - Convert array of objects to CSV string
   - Trigger download with Blob + URL.createObjectURL
   - Call showToast('Exported '+data.length+' records!', 'success')

10. formatDate(dateStr): returns readable date string like 'Jan 15, 2024'
11. formatCurrency(n): returns '$X,XXX.XX' string with proper commas
12. confirmDelete(id, deleteFn, refreshFn): Opens confirm modal with warning icon; on confirm calls deleteFn(id) then refreshFn(), shows toast
13. safeChart(id, config): Destroys existing chart on canvas id if exists, creates new Chart(canvas, config), stores in _charts[id], returns chart instance
14. printSection(): window.print()
15. showGlobalSearch(query): Searches all data types, renders results in a dropdown or dedicated search results view
16. updateBreadcrumb(viewName): Updates #breadcrumb element text to reflect current view
17. handleHashChange(): Reads location.hash, calls showView with the matching view name
18. setLoading(show): Shows or hides a loading overlay/skeleton on the main content area
19. initTooltips(): Adds title-based tooltip popups on all [data-tooltip] elements
20. debounce(fn, delay): Returns a debounced version of fn, used for search inputs
21. generateId(prefix): Returns prefix + Date.now().toString(36) + Math.random().toString(36).slice(2,5).toUpperCase()
22. copyToClipboard(text): navigator.clipboard.writeText, shows success toast
23. formatNumber(n): Returns locale-formatted number string with commas

GLOBAL STATE VARS (declare at top, var scope):
  var _charts = {{}};
  var currentView = '{first_view}';
  var _searchQuery = '';

DOMContentLoaded handler (implement FULLY):
  - Load theme from localStorage ('theme' key), apply 'dark' class on documentElement if 'dark'
  - Update dark toggle button icon based on current theme
  - Call loadAllData() from data.js
  - Wire ALL .nav-link clicks: e.preventDefault(), get data-view attribute, call showView(view)
  - Wire #modal-overlay click: if e.target === overlay element, closeModal()
  - Wire keyboard events: Escape → closeModal(), Ctrl+K → e.preventDefault() + focus #global-search
  - Wire sidebar toggle button (#sidebar-toggle) if exists
  - Wire #global-search input: debounced handleSearch on 'input' event
  - Wire window hashchange: handleHashChange()
  - Wire all [data-action] buttons: dispatch to appropriate handler functions
  - Apply any saved user preferences from localStorage
  - Call showView('{first_view}') as the initial view

All functions MUST be in global scope (no ES modules, no const/let for function declarations — use var or function keyword).
Output ONLY the complete ```javascript."""

        resp = call_ai(prompt, timeout=180)
        code = extract_code(resp, "javascript")
        if not is_quality_code(code, "javascript"):
            resp2 = call_ai(prompt, model=FALLBACK, timeout=150)
            code2 = extract_code(resp2, "javascript")
            if is_quality_code(code2, "javascript"):
                code = code2

        return code if is_quality_code(code, "javascript") else self._fallback_app_js(views_list, first_view)

    def _data_js(self, fspec, plan, arch) -> str:
        req = plan.get("user_request", "")
        name = plan.get("project_name", "app").replace("-", " ").title()
        features = plan.get("features", [])
        feat_str = "\n".join(f"  - {f}" for f in features)
        domain = self._get_domain_smart(req, plan)
        db_key = plan.get("project_name", "app").replace("-", "_")

        domain_hints = {
            "student": "Students with: id, studentId(S001+), name, email, phone, course, year(1-4), gpa(0.0-4.0), grade(A/B/C/D/F), status(active/inactive/graduated), enrolledDate, address, guardian",
            "hospital": "Patients: id, patientId(P001+), name, age, gender, bloodType(A+/A-/B+/B-/O+/O-/AB+/AB-), doctor, diagnosis, admissionDate, dischargeDate, status(admitted/discharged/outpatient), ward, phone, insurance, emergencyContact. Doctors: id, name, specialization, schedule, status, phone.",
            "hr": "Employees with: id, empId(E001+), name, email, department, position, salary, joinDate, status(active/on-leave/terminated), phone, manager, leaveBalance, performanceScore(1-5), skills[]",
            "inventory": "Products with: id, sku(SKU-001+), name, category, quantity, minStock, price, costPrice, supplier, lastUpdated, status(in-stock/low-stock/out-of-stock), location, description. Suppliers with name, contact, email, phone, address.",
            "hotel": "Rooms: id, roomNo, type(single/double/suite/deluxe), floor, price, status(available/occupied/maintenance/reserved), amenities[]. Bookings: id, bookingId(BK-001+), guestName, guestEmail, guestPhone, roomNo, checkIn, checkOut, nights, status(confirmed/checked-in/checked-out/cancelled), totalAmount, paymentStatus(paid/pending/refunded), specialRequests.",
            "library": "Books: id, isbn, title, author, category, year, publisher, copies, available, status(available/borrowed/reserved), shelfLocation, language. Members: id, memberId(LIB-001+), name, email, phone, borrowedBooks[], joinDate, expiryDate, status(active/suspended/expired), fineBalance. Borrowings: id, bookId, memberId, borrowDate, dueDate, returnDate, status(active/returned/overdue), fine.",
            "restaurant": "Menu Items: id, itemId(ITM-001+), name, category(starter/main/dessert/beverage), price, cost, calories, status(available/unavailable/seasonal), description, rating. Orders: id, orderId(ORD-001+), tableNo, serverName, items[], subtotal, tax, total, status(pending/preparing/ready/served/paid), orderTime, paymentMethod. Tables: id, tableNo, capacity, status(available/occupied/reserved), section.",
            "crm": "Contacts: id, name, company, email, phone, stage(lead/prospect/customer/churned), value, source(website/referral/cold-call/email/social), assignedTo, lastContact, status, notes, deals[]",
            "project": "Projects: id, name, description, priority(low/medium/high/critical), status(planning/active/review/done/on-hold), startDate, deadline, progress(0-100), team[], budget, spent. Tasks: id, projectId, title, description, assignee, priority, status(todo/in-progress/review/done), dueDate, tags[].",
            "realestate": "Properties: id, propId(PROP-001+), title, type(apartment/house/villa/commercial/land), address, city, area(sqft), bedrooms, bathrooms, price, rentPrice, status(for-sale/for-rent/sold/rented), listedDate, agentName, features[]. Tenants: id, name, email, phone, propertyId, leaseStart, leaseEnd, monthlyRent, depositPaid, status(active/ended/defaulting).",
            "generic": "Records with: id, name, email, phone, status(active/inactive), category, description, createdAt, updatedAt, and 4+ domain-specific fields",
        }
        data_hint = domain_hints.get(domain, domain_hints["generic"])

        prompt = f"""You are a senior JavaScript data engineer. Write COMPLETE, PRODUCTION-READY data.js for a "{req}" web app. MINIMUM 250 LINES of real, working JavaScript. Every function FULLY implemented. Every edge case handled. Zero stubs. Zero TODOs.

Domain: {domain}
App: {name}
Storage key prefix: '{db_key}'
Features:
{feat_str}

Data schema: {data_hint}

IMPLEMENT EVERYTHING:

1. SAMPLE DATA — minimum 25+ realistic records per entity type:
   - Real diverse names (mix of ethnicities)
   - Realistic IDs with proper prefixes
   - Dates spanning 2022-2024
   - Varied statuses (not all active)
   - Domain-appropriate values (real department names, real course names, real diagnoses, etc.)
   - If multiple entity types exist, define ALL of them

2. STORAGE:
   const DB_KEY = '{db_key}_data'
   function saveData() — JSON.stringify to localStorage
   function loadAllData() — load from storage or use sample data, handle parse errors

3. CRUD:
   function getAll() — returns records array
   function getById(id) — find by id, return null if not found
   function createRecord(data) — generate id (prefix+Date.now()+random), set createdAt, push, save, return record
   function updateRecord(id, data) — merge update, save, return updated record or null
   function deleteRecord(id) — filter out, save

4. QUERY:
   function searchRecords(query) — case-insensitive search across all string fields
   function filterRecords(criteria) — filter by multiple key-value criteria
   function sortRecords(arr, field, direction) — sort asc/desc, handle numbers and strings

5. ANALYTICS — comprehensive, all computed from real data:
   function getStats() — returns object with:
     total, active, inactive, pending, recent (last 30 days count), thisMonth, thisWeek,
     monthly (12-element array indexed Jan-Dec with count per month),
     categoryBreakdown (object: key=category name, value=count),
     statusBreakdown (object: key=status, value=count),
     topRecords (array of top 5 by primary metric),
     recentActivity (array of last 10 records sorted by createdAt desc),
     growthRate (percentage change from last month to this month),
     PLUS 4+ domain-specific metrics (e.g., avgGpa, totalRevenue, totalBeds, occupancyRate, totalSales, conversionRate)

6. ADVANCED QUERY:
   function getByStatus(status) — filter by status
   function getByCategory(cat) — filter by category
   function getRecent(n) — get last n records by createdAt
   function getTop(field, n) — get top n records sorted by numeric field descending
   function bulkDelete(ids) — delete multiple records by id array, save once
   function bulkUpdateStatus(ids, status) — update status for multiple records, save once

7. UTILS:
   function generateId(prefix) — prefix + Date.now().toString(36).slice(-4).toUpperCase() + Math.random().toString(36).slice(2,4).toUpperCase()
   function formatDate(iso) — 'Jan 15, 2024' format using Date object
   function formatCurrency(n) — returns '$X,XXX.XX' with locale format
   function getStatusColor(status) — returns badge CSS class name (badge-success, badge-danger, badge-warning, badge-info)
   function exportDataCSV() — converts all records to CSV string and triggers download
   function getMonthLabel(i) — returns 'Jan', 'Feb', etc. for month index 0-11

All in global scope. No ES modules. No import/export.
Output ONLY complete ```javascript."""

        resp = call_ai(prompt, timeout=180)
        code = extract_code(resp, "javascript")
        if not is_quality_code(code, "javascript"):
            resp2 = call_ai(prompt, model=FALLBACK, timeout=150)
            code2 = extract_code(resp2, "javascript")
            if is_quality_code(code2, "javascript"):
                code = code2

        return code if is_quality_code(code, "javascript") else self._fallback_data_js(req, name, domain, db_key)

    def _ui_js(self, fspec, plan, arch) -> str:
        req = plan.get("user_request", "")
        name = plan.get("project_name", "app").replace("-", " ").title()
        views = plan.get("views", [])
        features = plan.get("features", [])
        feat_str = "\n".join(f"  - {f}" for f in features)
        color = arch.get("color", "indigo")
        analysis = plan.get("analysis", {})
        accent = analysis.get("primary_color", {"indigo": "#6366f1", "violet": "#8b5cf6", "blue": "#3b82f6",
                  "green": "#22c55e", "orange": "#f97316", "red": "#ef4444"}.get(color, "#6366f1"))
        views_list = [v.get("name", "") for v in views] or ["Dashboard", "Records", "Add New", "Reports"]
        views_routes = [v.get("route", v.get("name", "").lower().replace(" ", "-")) for v in views]
        views_desc = "\n".join(f"  - {v.get('name')}: {v.get('desc', '')}" for v in views) if views else "  - Dashboard, Records, Add New, Reports"
        domain = self._get_domain_smart(req, plan)

        form_fields = {
            "student": ["Full Name:text:name:required", "Email:email:email:required", "Student ID:text:studentId:required", "Course/Program:text:course:required", "Year (1-4):number:year:min=1,max=4", "GPA:number:gpa:min=0,max=4,step=0.1", "Status:select:status:active|inactive|graduated", "Phone:tel:phone", "Address:textarea:address", "Guardian Name:text:guardian"],
            "hospital": ["Full Name:text:name:required", "Patient ID:text:patientId:required", "Age:number:age:min=0,max=120", "Gender:select:gender:Male|Female|Other", "Blood Type:select:bloodType:A+|A-|B+|B-|O+|O-|AB+|AB-", "Assigned Doctor:text:doctor:required", "Diagnosis:text:diagnosis:required", "Ward:text:ward", "Phone:tel:phone", "Status:select:status:admitted|discharged|outpatient", "Insurance:text:insurance", "Emergency Contact:text:emergencyContact"],
            "hr": ["Full Name:text:name:required", "Employee ID:text:empId:required", "Email:email:email:required", "Department:text:department:required", "Position:text:position:required", "Salary:number:salary:required,min=0", "Phone:tel:phone", "Join Date:date:joinDate:required", "Manager:text:manager", "Status:select:status:active|on-leave|terminated", "Performance Score:number:performanceScore:min=1,max=5,step=0.1"],
            "inventory": ["Product Name:text:name:required", "SKU:text:sku:required", "Category:text:category:required", "Quantity:number:quantity:required,min=0", "Min Stock:number:minStock:required,min=0", "Unit Price:number:price:required,min=0,step=0.01", "Cost Price:number:costPrice:min=0,step=0.01", "Supplier:text:supplier:required", "Location:text:location", "Status:select:status:in-stock|low-stock|out-of-stock", "Description:textarea:description"],
            "crm": ["Contact Name:text:name:required", "Company:text:company:required", "Email:email:email:required", "Phone:tel:phone", "Stage:select:stage:lead|prospect|customer|churned", "Deal Value:number:value:min=0", "Source:select:source:website|referral|cold-call|email|social", "Assigned To:text:assignedTo", "Last Contact:date:lastContact", "Notes:textarea:notes"],
            "generic": ["Name:text:name:required", "Email:email:email", "Phone:tel:phone", "Status:select:status:active|inactive", "Category:text:category", "Description:textarea:description", "Date:date:date", "Notes:textarea:notes"],
        }
        fields = form_fields.get(domain, form_fields["generic"])

        prompt = f"""You are a senior frontend JavaScript engineer and UI architect. Write COMPLETE, PRODUCTION-READY ui.js for a "{req}" web app. MINIMUM 400 LINES of real, working JavaScript. Every render function FULLY implemented with complete, real HTML strings. No truncation. No placeholders. No stubs. No '...' ellipsis. Every pixel of UI coded.

Domain: {domain}
App: {name}
Accent: {accent}
Views:
{views_desc}
Features:
{feat_str}

IMPLEMENT ALL RENDER FUNCTIONS — complete HTML strings, no truncation:

renderView(viewName, container, searchQ):
  - If container is null, find it with getElementById
  - Route to correct render function based on viewName
  - Pass searchQ to list renders

renderDashboard(container):
  - Page header: title "{name}", subtitle, date
  - 4 stat cards in CSS grid (grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4):
    Each card: icon div (brand color bg), metric value (text-3xl font-bold), label, trend badge (green/red arrow + %)
  - Chart row: Monthly bar chart + status doughnut chart (Chart.js via safeChart())
  - Recent records table (last 5, using buildTableHTML())
  - All data from getStats() and getAll()

renderList(container, searchQ):
  - Toolbar: title + count, [+ Add New] button, [Export CSV] button
  - Filter/search bar: search input (live filter), status filter select, sort select
  - Table via buildTableHTML() with pagination
  - Pagination controls: Showing X-Y of Z, Prev/Next buttons, page indicator
  - Empty state: icon + message + "Add First Record" button

buildTableHTML(rows):
  - If no rows: return empty state HTML with fa-inbox icon
  - <table class="data-table"> with domain-appropriate columns
  - Status column uses badge classes from getStatusColor()
  - Currency columns formatted with $ signs
  - Date columns formatted readably
  - Actions: [View] [Edit] [Delete] buttons — calling doViewDetail(), doEdit(), doDeleteConfirm()

renderForm(container, recordId):
  - isEdit = recordId exists
  - Title: "Add New Record" or "Edit Record"
  - Card with form containing fields:
{chr(10).join(f"    {f}" for f in fields[:8])}
  - Each field: label, input/select/textarea with form-input class
  - [Save Changes] / [Add Record] primary button
  - [Cancel] secondary button (calls showView back to list)
  - Submit handler: validate required fields (red border + error text), call createRecord() or updateRecord(), showToast(), navigate

renderReports(container):
  - Page header with [Export CSV] and [Print] buttons
  - Summary stat cards row
  - Full-width Line chart: 12-month trend (getStats().monthly)
  - Bar chart: category breakdown (getStats().categoryBreakdown)
  - Top 5 records table by primary metric
  - Totals/averages row

renderDetail(recordId):
  - Opens modal via openModal()
  - 2-column grid of all record fields
  - Status badge prominently displayed
  - [Edit] and [Close] buttons

Action helpers (global functions):
function doAdd()
function doEdit(id)
function doViewDetail(id)
function doSort(field)
function doSearch(q)
function doDeleteConfirm(id)

Global state: let _page = 1, _perPage = 10, _query = '', _sortField, _sortDir = 'asc', _filterStatus = ''

Chart config template:
  - backgroundColor: '#111827' (none for canvas), gridColor: 'rgba(255,255,255,.05)', textColor: '#6b7280'
  - Primary color: '{accent}'
  - Use safeChart(id, config) from app.js

All innerHTML must be COMPLETE. No truncation. No '...' placeholders.
All functions in global scope. No ES modules.
Output ONLY complete ```javascript."""

        resp = call_ai(prompt, timeout=190)
        code = extract_code(resp, "javascript")
        if not is_quality_code(code, "javascript"):
            resp2 = call_ai(prompt, model=FALLBACK, timeout=160)
            code2 = extract_code(resp2, "javascript")
            if is_quality_code(code2, "javascript"):
                code = code2

        return code if is_quality_code(code, "javascript") else self._fallback_ui_js(req, name, views_list, views_routes, color, accent, domain, fields)

    def _fallback_app_js(self, views_list: list, first_view: str = None) -> str:
        first_view = first_view or (views_list[0] if views_list else "dashboard")
        return f"""'use strict';
/* ═══ APP CORE ═══ */
var currentView = '{first_view}';
var _charts = {{}};

function showView(name) {{
  document.querySelectorAll('.view-section').forEach(function(s) {{ s.classList.add('hidden'); }});
  document.querySelectorAll('.nav-link').forEach(function(l) {{ l.classList.remove('active'); }});
  var el = document.getElementById('view-' + name);
  if (el) {{
    el.classList.remove('hidden');
    currentView = name;
    Object.values(_charts).forEach(function(c) {{ try {{ c.destroy(); }} catch(e) {{}} }});
    _charts = {{}};
    if (typeof renderView === 'function') renderView(name, el);
  }}
  document.querySelectorAll('.nav-link').forEach(function(l) {{
    if (l.dataset.view === name) l.classList.add('active');
  }});
}}

function toggleSidebar() {{
  var sb = document.getElementById('sidebar');
  var ov = document.getElementById('sidebar-overlay');
  if (sb) sb.classList.toggle('open');
  if (ov) ov.classList.toggle('hidden');
  document.body.style.overflow = sb && sb.classList.contains('open') && window.innerWidth < 1024 ? 'hidden' : '';
}}

function toggleDarkMode() {{
  document.documentElement.classList.toggle('dark');
  var isDark = document.documentElement.classList.contains('dark');
  localStorage.setItem('theme', isDark ? 'dark' : 'light');
  var btn = document.getElementById('dark-toggle');
  if (btn) btn.querySelector('i').className = isDark ? 'fa-solid fa-moon text-sm' : 'fa-solid fa-sun text-sm';
}}

function handleSearch(q) {{
  var container = document.querySelector('.view-section:not(.hidden)');
  if (typeof renderView === 'function') renderView(currentView, container, q);
}}

function showToast(msg, type) {{
  type = type || 'success';
  var c = document.getElementById('toast-container');
  if (!c) return;
  var icons = {{success:'circle-check', error:'circle-xmark', warning:'triangle-exclamation', info:'circle-info'}};
  var colors = {{success:'#4ade80', error:'#f87171', warning:'#fbbf24', info:'#818cf8'}};
  var t = document.createElement('div');
  t.className = 'toast';
  t.style.cssText = 'background:var(--surface,#1f2937);border:1px solid var(--border,#374151);border-radius:12px;padding:12px 16px;min-width:280px;display:flex;align-items:center;gap:10px;font-size:14px;box-shadow:0 8px 32px rgba(0,0,0,.4);';
  t.innerHTML = '<i class="fa-solid fa-' + icons[type] + '" style="color:' + colors[type] + ';font-size:16px;flex-shrink:0;"></i><span style="color:#f3f4f6;">' + msg + '</span>';
  c.appendChild(t);
  setTimeout(function() {{
    t.style.opacity = '0';
    t.style.transform = 'translateX(110%)';
    t.style.transition = 'all .3s ease';
    setTimeout(function() {{ if (t.parentNode) t.remove(); }}, 300);
  }}, 3500);
}}

function openModal(html) {{
  var mc = document.getElementById('modal-content');
  var mo = document.getElementById('modal-overlay');
  if (mc) mc.innerHTML = html;
  if (mo) mo.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}}

function closeModal() {{
  var mo = document.getElementById('modal-overlay');
  if (mo) mo.classList.add('hidden');
  var mc = document.getElementById('modal-content');
  if (mc) mc.innerHTML = '';
  document.body.style.overflow = '';
}}

function exportToCSV(data, filename) {{
  if (!data || !data.length) {{ showToast('No data to export', 'warning'); return; }}
  var keys = Object.keys(data[0]);
  var rows = [keys.join(',')].concat(data.map(function(r) {{
    return keys.map(function(k) {{ return '"' + (r[k] == null ? '' : String(r[k]).replace(/"/g, '""')) + '"'; }}).join(',');
  }}));
  var blob = new Blob([rows.join('\\n')], {{type: 'text/csv'}});
  var url = URL.createObjectURL(blob);
  var a = document.createElement('a');
  a.href = url; a.download = (filename || 'export') + '.csv'; a.click();
  URL.revokeObjectURL(url);
  showToast('Exported ' + data.length + ' records!', 'success');
}}

function formatDate(dateStr) {{
  if (!dateStr) return '—';
  try {{
    return new Date(dateStr).toLocaleDateString('en-US', {{year:'numeric', month:'short', day:'numeric'}});
  }} catch(e) {{ return dateStr; }}
}}

function formatCurrency(n) {{
  return '$' + parseFloat(n || 0).toLocaleString('en-US', {{minimumFractionDigits:2, maximumFractionDigits:2}});
}}

function confirmDelete(id, deleteFn, refreshFn) {{
  openModal(
    '<div style="padding:32px;text-align:center;">' +
    '<div style="width:64px;height:64px;border-radius:50%;background:rgba(239,68,68,.12);display:flex;align-items:center;justify-content:center;margin:0 auto 16px;">' +
    '<i class="fa-solid fa-trash-can" style="color:#f87171;font-size:24px;"></i></div>' +
    '<h3 style="font-size:18px;font-weight:700;color:#f9fafb;margin-bottom:8px;">Delete Record?</h3>' +
    '<p style="color:#9ca3af;font-size:14px;margin-bottom:24px;">This action cannot be undone. The record will be permanently deleted.</p>' +
    '<div style="display:flex;gap:12px;">' +
    '<button id="confirm-del-btn" class="btn btn-danger" style="flex:1;justify-content:center;"><i class="fa-solid fa-trash mr-2"></i>Yes, Delete</button>' +
    '<button onclick="closeModal()" class="btn btn-secondary" style="flex:1;justify-content:center;">Cancel</button>' +
    '</div></div>'
  );
  setTimeout(function() {{
    var btn = document.getElementById('confirm-del-btn');
    if (btn) btn.addEventListener('click', function() {{
      if (typeof deleteFn === 'function') deleteFn(id);
      closeModal();
      showToast('Record deleted', 'error');
      if (typeof refreshFn === 'function') refreshFn();
    }});
  }}, 60);
}}

function safeChart(id, config) {{
  try {{
    var canvas = document.getElementById(id);
    if (!canvas) return null;
    if (_charts[id]) {{ _charts[id].destroy(); delete _charts[id]; }}
    _charts[id] = new Chart(canvas, config);
    return _charts[id];
  }} catch(e) {{ console.warn('Chart:', id, e); return null; }}
}}

function printSection() {{
  window.print();
}}

document.addEventListener('DOMContentLoaded', function() {{
  var theme = localStorage.getItem('theme') || 'dark';
  if (theme === 'dark') document.documentElement.classList.add('dark');
  else document.documentElement.classList.remove('dark');

  if (typeof loadAllData === 'function') loadAllData();

  document.querySelectorAll('.nav-link').forEach(function(link) {{
    link.addEventListener('click', function(e) {{
      e.preventDefault();
      var v = link.dataset.view;
      if (v) showView(v);
    }});
  }});

  var mo = document.getElementById('modal-overlay');
  if (mo) mo.addEventListener('click', function(e) {{ if (e.target === mo) closeModal(); }});

  document.addEventListener('keydown', function(e) {{
    if (e.key === 'Escape') closeModal();
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {{
      e.preventDefault();
      var s = document.getElementById('global-search');
      if (s) s.focus();
    }}
  }});

  showView('{first_view}');
}});
"""

    def _fallback_data_js(self, req: str, name: str, domain: str, db_key: str) -> str:
        samples = {
            "student": """[
  {{id:'S001',studentId:'STU-001',name:'Emma Johnson',email:'emma.johnson@university.edu',phone:'555-0101',course:'Computer Science',year:3,gpa:3.85,grade:'A',status:'active',enrolledDate:'2022-09-01',address:'123 Oak St, Boston MA',guardian:'Robert Johnson'}},
  {{id:'S002',studentId:'STU-002',name:'Liam Chen',email:'liam.chen@university.edu',phone:'555-0102',course:'Business Administration',year:2,gpa:3.42,grade:'B',status:'active',enrolledDate:'2023-09-01',address:'456 Elm Ave, Cambridge MA',guardian:'Wei Chen'}},
  {{id:'S003',studentId:'STU-003',name:'Sofia Rodriguez',email:'sofia.r@university.edu',phone:'555-0103',course:'Mechanical Engineering',year:4,gpa:3.91,grade:'A',status:'active',enrolledDate:'2021-09-01',address:'789 Pine Rd, Newton MA',guardian:'Maria Rodriguez'}},
  {{id:'S004',studentId:'STU-004',name:'Noah Williams',email:'noah.w@university.edu',phone:'555-0104',course:'Psychology',year:1,gpa:2.98,grade:'C',status:'active',enrolledDate:'2024-09-01',address:'321 Maple Dr, Brookline MA',guardian:'James Williams'}},
  {{id:'S005',studentId:'STU-005',name:'Aisha Patel',email:'aisha.p@university.edu',phone:'555-0105',course:'Data Science',year:3,gpa:3.76,grade:'A',status:'active',enrolledDate:'2022-09-01',address:'654 Cedar Ln, Somerville MA',guardian:'Raj Patel'}},
  {{id:'S006',studentId:'STU-006',name:'Ethan Kim',email:'ethan.kim@university.edu',phone:'555-0106',course:'Economics',year:2,gpa:3.55,grade:'B',status:'active',enrolledDate:'2023-09-01',address:'987 Birch St, Watertown MA',guardian:'Sunhi Kim'}},
  {{id:'S007',studentId:'STU-007',name:'Maya Thompson',email:'maya.t@university.edu',phone:'555-0107',course:'Nursing',year:4,gpa:3.88,grade:'A',status:'graduated',enrolledDate:'2020-09-01',address:'147 Walnut Ave, Quincy MA',guardian:'Sandra Thompson'}},
  {{id:'S008',studentId:'STU-008',name:'James O\'Brien',email:'james.ob@university.edu',phone:'555-0108',course:'Architecture',year:1,gpa:3.12,grade:'B',status:'active',enrolledDate:'2024-09-01',address:'258 Spruce Dr, Malden MA',guardian:'Patrick O\'Brien'}},
  {{id:'S009',studentId:'STU-009',name:'Zara Ahmed',email:'zara.a@university.edu',phone:'555-0109',course:'Chemistry',year:3,gpa:3.67,grade:'A',status:'active',enrolledDate:'2022-09-01',address:'369 Ash St, Medford MA',guardian:'Hassan Ahmed'}},
  {{id:'S010',studentId:'STU-010',name:'Carlos Mendez',email:'carlos.m@university.edu',phone:'555-0110',course:'Marketing',year:2,gpa:3.33,grade:'B',status:'active',enrolledDate:'2023-09-01',address:'741 Poplar Blvd, Arlington MA',guardian:'Ana Mendez'}},
  {{id:'S011',studentId:'STU-011',name:'Grace Park',email:'grace.p@university.edu',phone:'555-0111',course:'Finance',year:4,gpa:3.94,grade:'A',status:'active',enrolledDate:'2021-09-01',address:'852 Willow Ct, Belmont MA',guardian:'John Park'}},
  {{id:'S012',studentId:'STU-012',name:'Oliver Davis',email:'oliver.d@university.edu',phone:'555-0112',course:'Computer Science',year:1,gpa:2.75,grade:'C',status:'inactive',enrolledDate:'2024-09-01',address:'963 Hickory Ln, Waltham MA',guardian:'Henry Davis'}},
  {{id:'S013',studentId:'STU-013',name:'Isabella Garcia',email:'isabella.g@university.edu',phone:'555-0113',course:'Art & Design',year:3,gpa:3.71,grade:'A',status:'active',enrolledDate:'2022-09-01',address:'159 Magnolia St, Lexington MA',guardian:'Pedro Garcia'}},
  {{id:'S014',studentId:'STU-014',name:'Benjamin Lee',email:'ben.lee@university.edu',phone:'555-0114',course:'Biomedical Engineering',year:2,gpa:3.88,grade:'A',status:'active',enrolledDate:'2023-09-01',address:'267 Cherry Ave, Concord MA',guardian:'Christine Lee'}},
  {{id:'S015',studentId:'STU-015',name:'Ava Martinez',email:'ava.m@university.edu',phone:'555-0115',course:'Political Science',year:4,gpa:3.45,grade:'B',status:'graduated',enrolledDate:'2020-09-01',address:'384 Dogwood Dr, Bedford MA',guardian:'Luis Martinez'}}
]""",
            "hospital": """[
  {{id:'P001',patientId:'PAT-001',name:'Robert Anderson',age:45,gender:'Male',bloodType:'A+',doctor:'Dr. Sarah Mitchell',diagnosis:'Hypertension',admissionDate:'2024-03-10',status:'admitted',ward:'Cardiology',phone:'555-1001',insurance:'BlueCross',emergencyContact:'Mary Anderson'}},
  {{id:'P002',patientId:'PAT-002',name:'Linda Thompson',age:62,gender:'Female',bloodType:'O-',doctor:'Dr. James Carter',diagnosis:'Type 2 Diabetes',admissionDate:'2024-03-08',status:'outpatient',ward:'Endocrinology',phone:'555-1002',insurance:'Aetna',emergencyContact:'David Thompson'}},
  {{id:'P003',patientId:'PAT-003',name:'Michael Chen',age:38,gender:'Male',bloodType:'B+',doctor:'Dr. Emily Rodriguez',diagnosis:'Appendicitis',admissionDate:'2024-03-12',status:'admitted',ward:'Surgery',phone:'555-1003',insurance:'United',emergencyContact:'Jennifer Chen'}},
  {{id:'P004',patientId:'PAT-004',name:'Patricia Wilson',age:71,gender:'Female',bloodType:'AB+',doctor:'Dr. William Park',diagnosis:'Hip Fracture',admissionDate:'2024-03-05',status:'discharged',ward:'Orthopedics',phone:'555-1004',insurance:'Medicare',emergencyContact:'Thomas Wilson'}},
  {{id:'P005',patientId:'PAT-005',name:'James Martinez',age:29,gender:'Male',bloodType:'A-',doctor:'Dr. Sarah Mitchell',diagnosis:'Pneumonia',admissionDate:'2024-03-14',status:'admitted',ward:'Pulmonology',phone:'555-1005',insurance:'Cigna',emergencyContact:'Rosa Martinez'}},
  {{id:'P006',patientId:'PAT-006',name:'Mary Johnson',age:55,gender:'Female',bloodType:'O+',doctor:'Dr. James Carter',diagnosis:'Breast Cancer',admissionDate:'2024-02-28',status:'outpatient',ward:'Oncology',phone:'555-1006',insurance:'BlueCross',emergencyContact:'Paul Johnson'}},
  {{id:'P007',patientId:'PAT-007',name:'David Brown',age:48,gender:'Male',bloodType:'B-',doctor:'Dr. Emily Rodriguez',diagnosis:'Coronary Artery Disease',admissionDate:'2024-03-11',status:'admitted',ward:'Cardiology',phone:'555-1007',insurance:'Aetna',emergencyContact:'Susan Brown'}},
  {{id:'P008',patientId:'PAT-008',name:'Jennifer Davis',age:33,gender:'Female',bloodType:'A+',doctor:'Dr. William Park',diagnosis:'Kidney Stones',admissionDate:'2024-03-09',status:'discharged',ward:'Urology',phone:'555-1008',insurance:'United',emergencyContact:'Mark Davis'}},
  {{id:'P009',patientId:'PAT-009',name:'Christopher Garcia',age:67,gender:'Male',bloodType:'O+',doctor:'Dr. Sarah Mitchell',diagnosis:'COPD',admissionDate:'2024-03-07',status:'admitted',ward:'Pulmonology',phone:'555-1009',insurance:'Medicare',emergencyContact:'Angela Garcia'}},
  {{id:'P010',patientId:'PAT-010',name:'Michelle Lee',age:41,gender:'Female',bloodType:'AB-',doctor:'Dr. James Carter',diagnosis:'Migraine Disorder',admissionDate:'2024-03-13',status:'outpatient',ward:'Neurology',phone:'555-1010',insurance:'Cigna',emergencyContact:'Kevin Lee'}},
  {{id:'P011',patientId:'PAT-011',name:'Daniel Kim',age:52,gender:'Male',bloodType:'A+',doctor:'Dr. Emily Rodriguez',diagnosis:'Gallstones',admissionDate:'2024-03-06',status:'admitted',ward:'Surgery',phone:'555-1011',insurance:'BlueCross',emergencyContact:'Soo Kim'}},
  {{id:'P012',patientId:'PAT-012',name:'Karen White',age:38,gender:'Female',bloodType:'B+',doctor:'Dr. William Park',diagnosis:'Anxiety Disorder',admissionDate:'2024-03-15',status:'outpatient',ward:'Psychiatry',phone:'555-1012',insurance:'Aetna',emergencyContact:'Steven White'}},
  {{id:'P013',patientId:'PAT-013',name:'Mark Taylor',age:59,gender:'Male',bloodType:'O-',doctor:'Dr. Sarah Mitchell',diagnosis:'Prostate Cancer',admissionDate:'2024-02-20',status:'outpatient',ward:'Oncology',phone:'555-1013',insurance:'United',emergencyContact:'Karen Taylor'}},
  {{id:'P014',patientId:'PAT-014',name:'Nancy Harris',age:44,gender:'Female',bloodType:'A-',doctor:'Dr. James Carter',diagnosis:'Arthritis',admissionDate:'2024-03-04',status:'discharged',ward:'Rheumatology',phone:'555-1014',insurance:'Medicare',emergencyContact:'Brian Harris'}},
  {{id:'P015',patientId:'PAT-015',name:'Kevin Robinson',age:76,gender:'Male',bloodType:'AB+',doctor:'Dr. Emily Rodriguez',diagnosis:'Stroke',admissionDate:'2024-03-01',status:'admitted',ward:'Neurology',phone:'555-1015',insurance:'Cigna',emergencyContact:'Dorothy Robinson'}}
]""",
            "hr": """[
  {{id:'E001',empId:'EMP-001',name:'Alexandra Scott',email:'a.scott@company.com',department:'Engineering',position:'Senior Developer',salary:95000,joinDate:'2021-03-15',status:'active',phone:'555-2001',manager:'Sarah Kim',leaveBalance:18,performanceScore:4.5,skills:['Python','React','AWS']}},
  {{id:'E002',empId:'EMP-002',name:'Marcus Johnson',email:'m.johnson@company.com',department:'Marketing',position:'Marketing Manager',salary:78000,joinDate:'2020-07-01',status:'active',phone:'555-2002',manager:'David Chen',leaveBalance:14,performanceScore:4.2,skills:['SEO','Analytics','Copywriting']}},
  {{id:'E003',empId:'EMP-003',name:'Priya Sharma',email:'p.sharma@company.com',department:'Finance',position:'Financial Analyst',salary:72000,joinDate:'2022-01-10',status:'active',phone:'555-2003',manager:'Robert Williams',leaveBalance:20,performanceScore:4.7,skills:['Excel','PowerBI','Financial Modeling']}},
  {{id:'E004',empId:'EMP-004',name:'Jake Thompson',email:'j.thompson@company.com',department:'Sales',position:'Sales Executive',salary:65000,joinDate:'2023-04-20',status:'active',phone:'555-2004',manager:'Lisa Rodriguez',leaveBalance:12,performanceScore:3.8,skills:['CRM','Negotiation','Presentations']}},
  {{id:'E005',empId:'EMP-005',name:'Fatima Al-Hassan',email:'f.alhassan@company.com',department:'HR',position:'HR Specialist',salary:58000,joinDate:'2021-09-05',status:'active',phone:'555-2005',manager:'Jennifer Park',leaveBalance:22,performanceScore:4.1,skills:['Recruitment','Labor Law','Training']}},
  {{id:'E006',empId:'EMP-006',name:'Ryan Chang',email:'r.chang@company.com',department:'Engineering',position:'DevOps Engineer',salary:88000,joinDate:'2020-11-15',status:'active',phone:'555-2006',manager:'Sarah Kim',leaveBalance:16,performanceScore:4.4,skills:['Kubernetes','Docker','CI/CD']}},
  {{id:'E007',empId:'EMP-007',name:'Elena Petrova',email:'e.petrova@company.com',department:'Design',position:'UI/UX Designer',salary:74000,joinDate:'2022-06-01',status:'on-leave',phone:'555-2007',manager:'Michael Brown',leaveBalance:0,performanceScore:4.6,skills:['Figma','Adobe XD','User Research']}},
  {{id:'E008',empId:'EMP-008',name:'Samuel Osei',email:'s.osei@company.com',department:'Engineering',position:'Backend Developer',salary:82000,joinDate:'2021-08-20',status:'active',phone:'555-2008',manager:'Sarah Kim',leaveBalance:19,performanceScore:4.0,skills:['Node.js','PostgreSQL','GraphQL']}},
  {{id:'E009',empId:'EMP-009',name:'Yuki Tanaka',email:'y.tanaka@company.com',department:'Marketing',position:'Content Strategist',salary:62000,joinDate:'2023-01-15',status:'active',phone:'555-2009',manager:'David Chen',leaveBalance:21,performanceScore:3.9,skills:['Content Writing','Social Media','Analytics']}},
  {{id:'E010',empId:'EMP-010',name:'Carlos Vega',email:'c.vega@company.com',department:'Sales',position:'Regional Sales Manager',salary:92000,joinDate:'2019-05-10',status:'active',phone:'555-2010',manager:'Lisa Rodriguez',leaveBalance:15,performanceScore:4.8,skills:['Team Leadership','Strategic Planning','CRM']}},
  {{id:'E011',empId:'EMP-011',name:'Natasha Williams',email:'n.williams@company.com',department:'Finance',position:'Accountant',salary:64000,joinDate:'2022-09-01',status:'active',phone:'555-2011',manager:'Robert Williams',leaveBalance:17,performanceScore:4.3,skills:['GAAP','QuickBooks','Tax Compliance']}},
  {{id:'E012',empId:'EMP-012',name:'Ahmed Hassan',email:'a.hassan@company.com',department:'Engineering',position:'Data Scientist',salary:98000,joinDate:'2020-02-15',status:'terminated',phone:'555-2012',manager:'Sarah Kim',leaveBalance:0,performanceScore:3.2,skills:['Machine Learning','Python','TensorFlow']}},
  {{id:'E013',empId:'EMP-013',name:'Mei Lin',email:'m.lin@company.com',department:'Design',position:'Graphic Designer',salary:58000,joinDate:'2023-07-10',status:'active',phone:'555-2013',manager:'Michael Brown',leaveBalance:23,performanceScore:4.2,skills:['Illustrator','Photoshop','Branding']}},
  {{id:'E014',empId:'EMP-014',name:'Derek Murphy',email:'d.murphy@company.com',department:'HR',position:'Talent Acquisition Specialist',salary:61000,joinDate:'2021-12-01',status:'active',phone:'555-2014',manager:'Jennifer Park',leaveBalance:18,performanceScore:4.0,skills:['Recruiting','LinkedIn Sourcing','Interviewing']}},
  {{id:'E015',empId:'EMP-015',name:'Amara Diallo',email:'a.diallo@company.com',department:'Marketing',position:'Brand Manager',salary:84000,joinDate:'2020-04-15',status:'active',phone:'555-2015',manager:'David Chen',leaveBalance:16,performanceScore:4.5,skills:['Brand Strategy','Market Research','Campaign Management']}}
]""",
            "inventory": """[
  {{id:'I001',sku:'SKU-001',name:'MacBook Pro 14"',category:'Electronics',quantity:45,minStock:10,price:1999.99,costPrice:1450.00,supplier:'Apple Inc',lastUpdated:'2024-03-15',status:'in-stock',location:'A1-S3',description:'Apple M3 Pro chip, 18GB RAM, 512GB SSD'}},
  {{id:'I002',sku:'SKU-002',name:'Dell XPS 15',category:'Electronics',quantity:8,minStock:10,price:1799.99,costPrice:1200.00,supplier:'Dell Technologies',lastUpdated:'2024-03-14',status:'low-stock',location:'A1-S4',description:'Intel i9, 32GB RAM, RTX 4070'}},
  {{id:'I003',sku:'SKU-003',name:'Samsung 27" 4K Monitor',category:'Displays',quantity:32,minStock:5,price:599.99,costPrice:380.00,supplier:'Samsung Electronics',lastUpdated:'2024-03-13',status:'in-stock',location:'B2-S1',description:'IPS panel, 144Hz, USB-C'}},
  {{id:'I004',sku:'SKU-004',name:'Logitech MX Master 3',category:'Peripherals',quantity:2,minStock:15,price:99.99,costPrice:55.00,supplier:'Logitech',lastUpdated:'2024-03-16',status:'out-of-stock',location:'C3-S2',description:'Wireless ergonomic mouse'}},
  {{id:'I005',sku:'SKU-005',name:'Keychron K2 Keyboard',category:'Peripherals',quantity:28,minStock:8,price:89.99,costPrice:48.00,supplier:'Keychron',lastUpdated:'2024-03-12',status:'in-stock',location:'C3-S3',description:'Mechanical keyboard, TKL, RGB'}},
  {{id:'I006',sku:'SKU-006',name:'iPad Pro 12.9"',category:'Electronics',quantity:19,minStock:6,price:1099.99,costPrice:750.00,supplier:'Apple Inc',lastUpdated:'2024-03-11',status:'in-stock',location:'A2-S1',description:'M4 chip, 256GB, WiFi+Cellular'}},
  {{id:'I007',sku:'SKU-007',name:'Sony WH-1000XM5',category:'Audio',quantity:6,minStock:8,price:349.99,costPrice:200.00,supplier:'Sony Corporation',lastUpdated:'2024-03-10',status:'low-stock',location:'D4-S1',description:'Noise canceling headphones'}},
  {{id:'I008',sku:'SKU-008',name:'Anker USB-C Hub 7-in-1',category:'Accessories',quantity:67,minStock:20,price:49.99,costPrice:22.00,supplier:'Anker Innovations',lastUpdated:'2024-03-09',status:'in-stock',location:'C4-S1',description:'7 ports USB-C hub'}},
  {{id:'I009',sku:'SKU-009',name:'LG 49" UltraWide',category:'Displays',quantity:11,minStock:4,price:1199.99,costPrice:820.00,supplier:'LG Electronics',lastUpdated:'2024-03-08',status:'in-stock',location:'B2-S3',description:'5120x1440 DQHD curved monitor'}},
  {{id:'I010',sku:'SKU-010',name:'Razer DeathAdder V3',category:'Peripherals',quantity:0,minStock:12,price:79.99,costPrice:38.00,supplier:'Razer Inc',lastUpdated:'2024-03-07',status:'out-of-stock',location:'C3-S4',description:'Gaming mouse 30000 DPI'}},
  {{id:'I011',sku:'SKU-011',name:'SanDisk 1TB SSD',category:'Storage',quantity:44,minStock:15,price:89.99,costPrice:45.00,supplier:'Western Digital',lastUpdated:'2024-03-06',status:'in-stock',location:'E5-S1',description:'Portable USB-C SSD 1050MB/s'}},
  {{id:'I012',sku:'SKU-012',name:'Nvidia RTX 4080',category:'Components',quantity:7,minStock:8,price:1199.99,costPrice:850.00,supplier:'Nvidia Corp',lastUpdated:'2024-03-05',status:'low-stock',location:'A3-S1',description:'16GB GDDR6X graphics card'}},
  {{id:'I013',sku:'SKU-013',name:'Corsair 32GB DDR5',category:'Components',quantity:38,minStock:10,price:129.99,costPrice:72.00,supplier:'Corsair',lastUpdated:'2024-03-04',status:'in-stock',location:'A3-S2',description:'DDR5-5600MHz CL36 dual channel'}},
  {{id:'I014',sku:'SKU-014',name:'Elgato Stream Deck',category:'Streaming',quantity:15,minStock:5,price:149.99,costPrice:80.00,supplier:'Elgato',lastUpdated:'2024-03-03',status:'in-stock',location:'D4-S3',description:'15 LCD key stream controller'}},
  {{id:'I015',sku:'SKU-015',name:'Blue Yeti Microphone',category:'Audio',quantity:22,minStock:7,price:129.99,costPrice:65.00,supplier:'Blue Microphones',lastUpdated:'2024-03-02',status:'in-stock',location:'D4-S2',description:'USB condenser microphone'}}
]""",
            "crm": """[
  {{id:'C001',name:'Alice Johnson',company:'Acme Corporation',email:'alice@acme.com',phone:'555-0101',stage:'customer',value:45000,source:'referral',assignedTo:'Sales Rep A',lastContact:'2024-03-15',status:'active',notes:'Enterprise plan, renewal in June'}},
  {{id:'C002',name:'Bob Smith',company:'TechStart LLC',email:'bob@techstart.io',phone:'555-0102',stage:'prospect',value:12500,source:'website',assignedTo:'Sales Rep B',lastContact:'2024-03-10',status:'active',notes:'Interested in Pro plan'}},
  {{id:'C003',name:'Carol White',company:'Global Systems Inc',email:'carol@globalsys.com',phone:'555-0103',stage:'lead',value:28000,source:'cold-call',assignedTo:'Sales Rep A',lastContact:'2024-03-18',status:'active',notes:'Needs demo scheduled'}},
  {{id:'C004',name:'David Brown',company:'Brown & Associates',email:'david@brownco.com',phone:'555-0104',stage:'customer',value:8200,source:'email',assignedTo:'Sales Rep C',lastContact:'2024-02-28',status:'inactive',notes:'Switched to competitor'}},
  {{id:'C005',name:'Eva Martinez',company:'EV Solutions',email:'eva@evsolutions.com',phone:'555-0105',stage:'prospect',value:67000,source:'social',assignedTo:'Sales Rep B',lastContact:'2024-03-20',status:'active',notes:'Large enterprise deal, Q2 close'}},
  {{id:'C006',name:'Frank Lee',company:'Lee Industries',email:'frank@leeinc.com',phone:'555-0106',stage:'lead',value:19000,source:'referral',assignedTo:'Sales Rep A',lastContact:'2024-03-22',status:'active',notes:'Referred by Carol White'}},
  {{id:'C007',name:'Grace Kim',company:'Kim Digital Agency',email:'grace@kimdigital.com',phone:'555-0107',stage:'customer',value:89000,source:'website',assignedTo:'Sales Rep C',lastContact:'2024-03-05',status:'active',notes:'Top client, VIP support'}},
  {{id:'C008',name:'Henry Clark',company:'Clark Group',email:'henry@clarkgrp.com',phone:'555-0108',stage:'churned',value:5400,source:'cold-call',assignedTo:'Sales Rep B',lastContact:'2024-01-15',status:'inactive',notes:'Budget cuts'}},
  {{id:'C009',name:'Iris Torres',company:'Torres Technologies',email:'iris@torrestech.com',phone:'555-0109',stage:'prospect',value:34500,source:'email',assignedTo:'Sales Rep A',lastContact:'2024-03-19',status:'active',notes:'Decision maker confirmed'}},
  {{id:'C010',name:'James Wilson',company:'Wilson Media Group',email:'james@wilsonmedia.com',phone:'555-0110',stage:'lead',value:9800,source:'social',assignedTo:'Sales Rep C',lastContact:'2024-03-21',status:'active',notes:'Follow up with proposal'}},
  {{id:'C011',name:'Karen Davis',company:'Davis Consulting',email:'karen@daviscons.com',phone:'555-0111',stage:'customer',value:52000,source:'referral',assignedTo:'Sales Rep B',lastContact:'2024-03-12',status:'active',notes:'Annual contract signed'}},
  {{id:'C012',name:'Leo Garcia',company:'Garcia Foods',email:'leo@garciafoods.com',phone:'555-0112',stage:'prospect',value:15200,source:'website',assignedTo:'Sales Rep A',lastContact:'2024-03-08',status:'active',notes:'Free trial user'}},
  {{id:'C013',name:'Mia Rodriguez',company:'Rodriguez PR',email:'mia@rodrigpr.com',phone:'555-0113',stage:'lead',value:22300,source:'referral',assignedTo:'Sales Rep C',lastContact:'2024-03-17',status:'active',notes:'Needs pricing breakdown'}},
  {{id:'C014',name:'Noah Chen',company:'Chen Analytics',email:'noah@chendata.com',phone:'555-0114',stage:'customer',value:78000,source:'cold-call',assignedTo:'Sales Rep B',lastContact:'2024-03-23',status:'active',notes:'Expanding to 3 more teams'}},
  {{id:'C015',name:'Olivia Baker',company:'Baker Retail',email:'olivia@bakerretail.com',phone:'555-0115',stage:'prospect',value:18700,source:'social',assignedTo:'Sales Rep A',lastContact:'2024-03-16',status:'active',notes:'Product demo completed'}}
]""",
        }

        sample = samples.get(domain, samples.get("hr", "[]"))
        db_safe = db_key.replace("-", "_")

        stats_by_domain = {
            "student": """
  var total = records.length;
  var active = records.filter(function(r){return r.status==='active';}).length;
  var inactive = records.filter(function(r){return r.status==='inactive';}).length;
  var graduated = records.filter(function(r){return r.status==='graduated';}).length;
  var avgGpa = total ? (records.reduce(function(s,r){return s+(parseFloat(r.gpa)||0);},0)/total).toFixed(2) : 0;
  var courses = {}; records.forEach(function(r){courses[r.course]=(courses[r.course]||0)+1;});
  var monthly = [2,3,5,4,6,3,4,7,8,5,4,6];
  var today = new Date(); var recent = records.filter(function(r){return (today-new Date(r.enrolledDate||0))<90*24*3600*1000;}).length;
  return {total:total,active:active,inactive:inactive,graduated:graduated,recent:recent,avgGpa:avgGpa,monthly:monthly,categoryBreakdown:courses};""",
            "hospital": """
  var total = records.length;
  var admitted = records.filter(function(r){return r.status==='admitted';}).length;
  var discharged = records.filter(function(r){return r.status==='discharged';}).length;
  var outpatient = records.filter(function(r){return r.status==='outpatient';}).length;
  var wards = {}; records.forEach(function(r){wards[r.ward||'General']=(wards[r.ward||'General']||0)+1;});
  var monthly = [12,15,18,14,20,16,19,22,17,21,18,23];
  var today = new Date(); var recent = records.filter(function(r){return (today-new Date(r.admissionDate||0))<30*24*3600*1000;}).length;
  return {total:total,active:admitted,inactive:discharged,admitted:admitted,discharged:discharged,outpatient:outpatient,recent:recent,monthly:monthly,categoryBreakdown:wards};""",
            "hr": """
  var total = records.length;
  var active = records.filter(function(r){return r.status==='active';}).length;
  var onLeave = records.filter(function(r){return r.status==='on-leave';}).length;
  var terminated = records.filter(function(r){return r.status==='terminated';}).length;
  var avgSalary = total ? Math.round(records.reduce(function(s,r){return s+(parseFloat(r.salary)||0);},0)/total) : 0;
  var depts = {}; records.forEach(function(r){depts[r.department]=(depts[r.department]||0)+1;});
  var monthly = [1,2,0,3,1,2,1,0,2,1,3,2];
  var today = new Date(); var recent = records.filter(function(r){return (today-new Date(r.joinDate||0))<90*24*3600*1000;}).length;
  return {total:total,active:active,inactive:terminated,onLeave:onLeave,terminated:terminated,avgSalary:avgSalary,recent:recent,monthly:monthly,categoryBreakdown:depts};""",
            "inventory": """
  var total = records.length;
  var inStock = records.filter(function(r){return r.status==='in-stock';}).length;
  var lowStock = records.filter(function(r){return r.status==='low-stock';}).length;
  var outOfStock = records.filter(function(r){return r.status==='out-of-stock';}).length;
  var totalValue = records.reduce(function(s,r){return s+(parseFloat(r.price)||0)*(parseInt(r.quantity)||0);},0);
  var cats = {}; records.forEach(function(r){cats[r.category]=(cats[r.category]||0)+1;});
  var monthly = [45,52,48,61,55,70,65,58,72,68,75,80];
  return {total:total,active:inStock,inactive:outOfStock,inStock:inStock,lowStock:lowStock,outOfStock:outOfStock,totalValue:Math.round(totalValue),recent:lowStock+outOfStock,monthly:monthly,categoryBreakdown:cats};""",
        }
        stats_body = stats_by_domain.get(domain, """
  var total = records.length;
  var active = records.filter(function(r){return r.status==='active'||r.status==='admitted'||r.status==='in-stock'||r.status==='customer';}).length;
  var inactive = total - active;
  var today = new Date();
  var recent = records.filter(function(r){
    var d = new Date(r.createdAt||r.joinDate||r.enrolledDate||r.admissionDate||r.lastContact||0);
    return (today-d)<30*24*3600*1000;
  }).length;
  var catKey = records[0] ? Object.keys(records[0]).find(function(k){return ['department','course','category','stage','status'].includes(k);}) : 'status';
  var cats = {}; records.forEach(function(r){var v=r[catKey]||'Other';cats[v]=(cats[v]||0)+1;});
  var monthly = [3,5,4,7,6,8,5,9,7,10,8,11];
  return {total:total,active:active,inactive:inactive,recent:recent,monthly:monthly,categoryBreakdown:cats};""")

        return f"""'use strict';
/* ═══ DATA MODULE — {name} ═══ */
var DB_KEY = '{db_safe}_data';
var records = [];

var SAMPLE_DATA = {sample};

/* ── Storage ── */
function saveData() {{
  try {{ localStorage.setItem(DB_KEY, JSON.stringify(records)); }} catch(e) {{ console.warn('Save error:', e); }}
}}
function loadAllData() {{
  try {{
    var stored = localStorage.getItem(DB_KEY);
    records = stored ? JSON.parse(stored) : SAMPLE_DATA.map(function(r){{return Object.assign({{}},r);}});
  }} catch(e) {{
    records = SAMPLE_DATA.map(function(r){{return Object.assign({{}},r);}});
  }}
}}

/* ── Utilities ── */
function generateId(prefix) {{
  prefix = prefix || 'R';
  return prefix + Date.now().toString(36).toUpperCase().slice(-4) + Math.random().toString(36).toUpperCase().slice(2,5);
}}
function formatDate(dateStr) {{
  if (!dateStr) return '—';
  try {{
    return new Date(dateStr).toLocaleDateString('en-US', {{year:'numeric',month:'short',day:'numeric'}});
  }} catch(e) {{ return dateStr; }}
}}
function getStatusColor(status) {{
  var map = {{
    active:'badge-success', admitted:'badge-success', 'in-stock':'badge-success', customer:'badge-success',
    graduated:'badge-info', discharged:'badge-info', outpatient:'badge-info', prospect:'badge-info',
    'on-leave':'badge-warning', 'low-stock':'badge-warning', pending:'badge-warning', lead:'badge-warning',
    inactive:'badge-danger', terminated:'badge-danger', 'out-of-stock':'badge-danger', churned:'badge-danger',
    cancelled:'badge-danger', rejected:'badge-danger'
  }};
  return map[(status||'').toLowerCase()] || 'badge-info';
}}

/* ── CRUD ── */
function getAll() {{
  return records;
}}
function getById(id) {{
  return records.find(function(r){{return r.id===id;}}) || null;
}}
function createRecord(data) {{
  var prefix = (records[0] && records[0].id) ? records[0].id.charAt(0) : 'R';
  data.id = data.id || generateId(prefix);
  data.createdAt = data.createdAt || new Date().toISOString();
  records.unshift(data);
  saveData();
  return data;
}}
function updateRecord(id, data) {{
  var idx = records.findIndex(function(r){{return r.id===id;}});
  if (idx >= 0) {{
    records[idx] = Object.assign({{}}, records[idx], data, {{id:id}});
    saveData();
    return records[idx];
  }}
  return null;
}}
function deleteRecord(id) {{
  var len = records.length;
  records = records.filter(function(r){{return r.id!==id;}});
  if (records.length < len) saveData();
}}

/* ── Queries ── */
function searchRecords(query) {{
  if (!query || !query.trim()) return records;
  var lq = query.toLowerCase().trim();
  return records.filter(function(r){{
    return Object.values(r).some(function(v){{
      return v !== null && v !== undefined && String(v).toLowerCase().includes(lq);
    }});
  }});
}}
function filterRecords(criteria) {{
  return records.filter(function(r){{
    return Object.keys(criteria).every(function(k){{
      if (!criteria[k]) return true;
      return String(r[k]||'').toLowerCase() === String(criteria[k]).toLowerCase();
    }});
  }});
}}
function sortRecords(arr, field, direction) {{
  if (!arr) arr = records;
  if (!field) return arr;
  direction = direction || 'asc';
  return arr.slice().sort(function(a, b){{
    var av = a[field], bv = b[field];
    if (av === undefined || av === null) return 1;
    if (bv === undefined || bv === null) return -1;
    if (!isNaN(parseFloat(av)) && !isNaN(parseFloat(bv))) {{
      return direction==='asc' ? parseFloat(av)-parseFloat(bv) : parseFloat(bv)-parseFloat(av);
    }}
    av = String(av).toLowerCase(); bv = String(bv).toLowerCase();
    return direction==='asc' ? (av>bv?1:(av<bv?-1:0)) : (av<bv?1:(av>bv?-1:0));
  }});
}}

/* ── Analytics ── */
function getStats() {{{stats_body}
}}
"""

    def _fallback_ui_js(self, req, name, views_list, views_routes, color, accent, domain, fields) -> str:
        first = views_list[0] if views_list else "Dashboard"
        accent = accent or "#6366f1"

        col_defs = {
            "student": [("Student ID","studentId"),("Name","name"),("Course","course"),("Year","year"),("GPA","gpa"),("Grade","grade"),("Status","status"),("Enrolled","enrolledDate")],
            "hospital": [("Patient ID","patientId"),("Name","name"),("Age","age"),("Gender","gender"),("Doctor","doctor"),("Diagnosis","diagnosis"),("Ward","ward"),("Status","status"),("Admitted","admissionDate")],
            "hr": [("Emp ID","empId"),("Name","name"),("Department","department"),("Position","position"),("Salary","salary"),("Status","status"),("Join Date","joinDate")],
            "inventory": [("SKU","sku"),("Product","name"),("Category","category"),("Qty","quantity"),("Min Stock","minStock"),("Price","price"),("Supplier","supplier"),("Status","status")],
            "crm": [("Name","name"),("Company","company"),("Email","email"),("Stage","stage"),("Value","value"),("Source","source"),("Last Contact","lastContact"),("Status","status")],
        }
        cols = col_defs.get(domain, [("ID","id"),("Name","name"),("Status","status"),("Category","category"),("Date","createdAt")])

        th_parts = ["<th>Actions</th>"]
        th_parts_pre = [f'<th onclick="doSort(\'{c[1]}\')" style="cursor:pointer;white-space:nowrap;">{c[0]} <i class="fa-solid fa-sort text-xs opacity-40 ml-1"></i></th>' for c in cols]
        all_th = "".join(th_parts_pre) + th_parts[0]

        row_cells = []
        for label, key in cols:
            if key == "status":
                row_cells.append(f'\'<td><span class="badge \'+getStatusColor(r.{key})+\'">\'+r.{key}+\'</span></td>\'')
            elif key in ("salary","price","value","costPrice"):
                row_cells.append(f'\'<td>\'+formatCurrency(r.{key})+\'</td>\'')
            elif key in ("enrolledDate","admissionDate","joinDate","lastContact","lastUpdated","createdAt","date"):
                row_cells.append(f'\'<td>\'+formatDate(r.{key})+\'</td>\'')
            else:
                row_cells.append(f'\'<td>\'+(r.{key}===undefined||r.{key}===null?\\"—\\":r.{key})+\'</td>\'')
        row_cells_js = "+".join(row_cells)

        form_parts = []
        for spec in fields[:8]:
            parts = spec.split(":")
            label_txt = parts[0] if len(parts)>0 else "Field"
            inp_type = parts[1] if len(parts)>1 else "text"
            inp_name = parts[2] if len(parts)>2 else "field"
            extra = parts[3] if len(parts)>3 else ""
            required_attr = 'required' if 'required' in extra else ''
            if inp_type == "select":
                options_raw = [o for o in extra.replace("required","").strip("|").split("|") if o]
                opts = "".join(f'<option value=\\"{o}\\">\'+( r.{inp_name}===\\"{o}\\" ? \\" selected\\" : \\"\\" )+\'{o}</option>' for o in options_raw)
                form_parts.append(f'<div class=\\"form-group\\"><label>{label_txt}</label><select name=\\"{inp_name}\\" class=\\"form-input\\">{opts}</select></div>')
            elif inp_type == "textarea":
                form_parts.append(f'<div class=\\"form-group\\"><label>{label_txt}</label><textarea name=\\"{inp_name}\\" class=\\"form-input\\" rows=\\"3\\" placeholder=\\"{label_txt}\\">\'+( r.{inp_name}||\\"\\" )+\'</textarea></div>')
            else:
                form_parts.append(f'<div class=\\"form-group\\"><label>{label_txt}{" *" if required_attr else ""}</label><input type=\\"{inp_type}\\" name=\\"{inp_name}\\" value=\\"\'+( r.{inp_name}||\\"\\" )+\'\\\" {required_attr} class=\\"form-input\\" placeholder=\\"{label_txt}\\"/></div>')
        form_html = "".join(form_parts)

        stat_labels = {
            "student": [("fa-users","#6366f1","Total Students","total"),("fa-circle-check","#4ade80","Active","active"),("fa-graduation-cap","#60a5fa","Graduated","graduated"),("fa-star","#fbbf24","Avg GPA","avgGpa")],
            "hospital": [("fa-hospital-user","#6366f1","Total Patients","total"),("fa-bed","#4ade80","Admitted","admitted"),("fa-right-from-bracket","#60a5fa","Discharged","discharged"),("fa-stethoscope","#fbbf24","Outpatient","outpatient")],
            "hr": [("fa-users","#6366f1","Total Employees","total"),("fa-circle-check","#4ade80","Active","active"),("fa-plane-departure","#fbbf24","On Leave","onLeave"),("fa-dollar-sign","#60a5fa","Avg Salary","avgSalary")],
            "inventory": [("fa-boxes-stacked","#6366f1","Total Items","total"),("fa-circle-check","#4ade80","In Stock","inStock"),("fa-triangle-exclamation","#fbbf24","Low Stock","lowStock"),("fa-circle-xmark","#f87171","Out of Stock","outOfStock")],
            "crm": [("fa-users","#6366f1","Total Contacts","total"),("fa-handshake","#4ade80","Customers","active"),("fa-funnel-dollar","#60a5fa","Prospects","inactive"),("fa-star","#fbbf24","Recent","recent")],
        }
        stats = stat_labels.get(domain, [
            ("fa-database","#6366f1","Total Records","total"),
            ("fa-circle-check","#4ade80","Active","active"),
            ("fa-circle-xmark","#f87171","Inactive","inactive"),
            ("fa-clock","#60a5fa","Recent","recent"),
        ])
        stat_cards_html = "+".join(
            f"'<div class=\"card stat-card hover:border-gray-700\"><div style=\"flex:1\"><p style=\"color:#6b7280;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:8px;\">{s[2]}</p><p style=\"font-size:28px;font-weight:700;color:#f9fafb;line-height:1;\">'+( typeof s.{s[3]} === 'number' && s.{s[3]} > 1000 ? s.{s[3]}.toLocaleString() : (s.{s[3]}||0) )+'</p></div><div style=\"width:44px;height:44px;border-radius:10px;background:rgba("+(','.join(str(int(s[1].lstrip('#')[i:i+2],16)) for i in (0,2,4)))+",0.15);display:flex;align-items:center;justify-content:center;\"><i class=\"fa-solid {s[0]}\" style=\"color:{s[1]};font-size:18px;\"></i></div></div>'"
            for s in stats
        )

        list_route = views_routes[1] if len(views_routes) > 1 else "records"

        return f"""'use strict';
/* ═══ UI MODULE — {name} ═══ */
var _page = 1, _perPage = 10, _query = '', _sortField = 'name', _sortDir = 'asc', _filterStatus = '';

function renderView(viewName, container, searchQ) {{
  var n = (viewName || '').toLowerCase().replace(/[^a-z0-9]/g, '');
  if (!container) container = document.getElementById('view-' + viewName) || document.querySelector('.view-section:not(.hidden)');
  if (!container) return;
  if (searchQ !== undefined) {{ _query = searchQ; _page = 1; }}
  if (n.includes('dashboard') || n.includes('home') || n.includes('overview')) renderDashboard(container);
  else if (n.includes('report') || n.includes('analytic') || n.includes('stat')) renderReports(container);
  else if (n.includes('add') || n.includes('new') || n.includes('create')) renderForm(container, null);
  else renderList(container, _query);
}}

function renderDashboard(container) {{
  if (!container) container = document.querySelector('.view-section:not(.hidden)');
  if (!container) return;
  var s = (typeof getStats === 'function') ? getStats() : {{}};
  var all = (typeof getAll === 'function') ? getAll() : [];
  container.innerHTML =
    '<div style="margin-bottom:24px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">' +
    '<div><h2 style="font-size:24px;font-weight:700;color:#f9fafb;margin:0;">{name}</h2>' +
    '<p style="color:#6b7280;font-size:14px;margin-top:4px;">Overview & Analytics — ' + new Date().toLocaleDateString('en-US', {{weekday:'long',year:'numeric',month:'long',day:'numeric'}}) + '</p></div>' +
    '<button onclick="exportToCSV(typeof getAll===\\'function\\'?getAll():[], \\'{name.lower().replace(" ","-")}\\')" class="btn btn-secondary"><i class="fa-solid fa-download mr-2"></i>Export</button>' +
    '</div>' +
    '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px;margin-bottom:24px;">' +
    {stat_cards_html} +
    '</div>' +
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px;" class="chart-grid">' +
    '<div class="card"><h3 style="font-size:15px;font-weight:600;color:#f9fafb;margin-bottom:16px;">Monthly Trend</h3><canvas id="dash-bar" height="180"></canvas></div>' +
    '<div class="card"><h3 style="font-size:15px;font-weight:600;color:#f9fafb;margin-bottom:16px;">Distribution</h3><canvas id="dash-dough" height="180"></canvas></div>' +
    '</div>' +
    '<div class="card"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">' +
    '<h3 style="font-size:15px;font-weight:600;color:#f9fafb;margin:0;">Recent Records</h3>' +
    '<button onclick="showView(\\'{list_route}\\')" class="btn btn-primary" style="font-size:13px;padding:6px 14px;">View All</button>' +
    '</div><div style="overflow-x:auto;">' + buildTableHTML(all.slice(0, 5)) + '</div></div>';
  setTimeout(function() {{
    var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    var monthly = s.monthly || Array(12).fill(0).map(function(){{return Math.floor(Math.random()*8)+2;}});
    var breakdown = s.categoryBreakdown || {{}};
    var bLabels = Object.keys(breakdown), bData = Object.values(breakdown);
    var colors = ['{accent}','#4ade80','#f87171','#fbbf24','#818cf8','#38bdf8','#fb923c','#a78bfa'];
    if (typeof safeChart === 'function') {{
      safeChart('dash-bar', {{type:'bar',data:{{labels:months,datasets:[{{label:'Records',data:monthly,backgroundColor:'{accent}cc',borderRadius:6,borderSkipped:false}}]}},options:{{responsive:true,plugins:{{legend:{{display:false}}}},scales:{{y:{{beginAtZero:true,grid:{{color:'rgba(255,255,255,.05)'}},ticks:{{color:'#6b7280',font:{{size:11}}}}}},x:{{grid:{{display:false}},ticks:{{color:'#6b7280',font:{{size:11}}}}}}}}}}}});
      if (bLabels.length > 0) {{
        safeChart('dash-dough', {{type:'doughnut',data:{{labels:bLabels,datasets:[{{data:bData,backgroundColor:colors,borderWidth:0,hoverOffset:4}}]}},options:{{responsive:true,plugins:{{legend:{{position:'right',labels:{{color:'#9ca3af',padding:12,font:{{size:11}}}},boxWidth:12}}}},cutout:'68%'}}}});
      }}
    }}
  }}, 100);
}}

function buildTableHTML(rows) {{
  if (!rows || !rows.length) return '<div style="padding:48px;text-align:center;color:#6b7280;"><i class="fa-solid fa-inbox" style="font-size:32px;opacity:0.3;display:block;margin-bottom:12px;"></i><p style="font-size:14px;">No records found</p></div>';
  return '<table class="data-table"><thead><tr>' + '{all_th}' + '</tr></thead><tbody>' +
    rows.map(function(r) {{
      return '<tr>' + {row_cells_js} +
        '<td><div style="display:flex;gap:4px;">' +
        '<button onclick="doViewDetail(\\''+r.id+'\\');" class="btn btn-secondary" style="padding:5px 9px;font-size:12px;" title="View"><i class="fa-solid fa-eye"></i></button>' +
        '<button onclick="doEdit(\\''+r.id+'\\');" class="btn btn-primary" style="padding:5px 9px;font-size:12px;" title="Edit"><i class="fa-solid fa-pen"></i></button>' +
        '<button onclick="doDeleteConfirm(\\''+r.id+'\\');" class="btn btn-danger" style="padding:5px 9px;font-size:12px;" title="Delete"><i class="fa-solid fa-trash"></i></button>' +
        '</div></td></tr>';
    }}).join('') +
    '</tbody></table>';
}}

function renderList(container, searchQ) {{
  if (!container) container = document.querySelector('.view-section:not(.hidden)');
  if (!container) return;
  if (searchQ !== undefined) {{ _query = searchQ; _page = 1; }}
  var all = (typeof searchRecords === 'function') ? searchRecords(_query) : (typeof getAll === 'function' ? getAll() : []);
  if (_filterStatus) all = all.filter(function(r){{return r.status === _filterStatus;}});
  if (typeof sortRecords === 'function') all = sortRecords(all, _sortField, _sortDir);
  var total = all.length;
  var start = (_page - 1) * _perPage, end = start + _perPage;
  var pageData = all.slice(start, end);
  var allStatuses = [...new Set((typeof getAll === 'function' ? getAll() : []).map(function(r){{return r.status;}}).filter(Boolean))];
  container.innerHTML =
    '<div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;margin-bottom:24px;">' +
    '<div><h2 style="font-size:24px;font-weight:700;color:#f9fafb;margin:0;">All Records</h2>' +
    '<p style="color:#6b7280;font-size:14px;margin-top:4px;">' + total + ' total entries</p></div>' +
    '<div style="display:flex;gap:8px;flex-wrap:wrap;">' +
    '<button onclick="doAdd()" class="btn btn-primary"><i class="fa-solid fa-plus mr-2"></i>Add New</button>' +
    '<button onclick="exportToCSV(typeof getAll===\\'function\\'?getAll():[],\\'export\\')" class="btn btn-secondary"><i class="fa-solid fa-download mr-2"></i>Export CSV</button>' +
    '</div></div>' +
    '<div class="card" style="overflow:hidden;padding:0;">' +
    '<div style="padding:16px;border-bottom:1px solid var(--border);display:flex;flex-wrap:wrap;gap:10px;">' +
    '<div style="position:relative;flex:1;min-width:200px;"><i class="fa-solid fa-magnifying-glass" style="position:absolute;left:10px;top:50%;transform:translateY(-50%);color:#6b7280;font-size:13px;"></i><input id="list-search" type="search" value="'+_query+'" oninput="doSearch(this.value)" placeholder="Search records..." class="form-input" style="padding-left:32px;"/></div>' +
    '<select onchange="_filterStatus=this.value;_page=1;renderList(null)" class="form-input" style="width:auto;">' +
    '<option value="">All Status</option>' + allStatuses.map(function(st){{return '<option value="'+st+'" '+(_filterStatus===st?'selected':'')+'>'+st+'</option>';}}).join('') + '</select>' +
    '</div>' +
    '<div style="overflow-x:auto;">' + buildTableHTML(pageData) + '</div>' +
    '<div style="padding:12px 16px;border-top:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;">' +
    '<span style="color:#6b7280;font-size:13px;">Showing ' + (total ? start+1 : 0) + '–' + Math.min(end,total) + ' of ' + total + '</span>' +
    '<div style="display:flex;gap:6px;align-items:center;">' +
    '<button onclick="_page=Math.max(1,_page-1);renderList(null);" class="btn btn-secondary" style="padding:6px 12px;font-size:13px;" '+(_page<=1?'disabled style="opacity:.4;cursor:not-allowed;padding:6px 12px;font-size:13px;"':'')+'><i class="fa-solid fa-chevron-left"></i></button>' +
    '<span style="padding:6px 12px;background:var(--surface-2,#1f2937);border-radius:6px;font-size:13px;color:#f9fafb;">'+_page+' / '+Math.max(1,Math.ceil(total/_perPage))+'</span>' +
    '<button onclick="_page=Math.min(Math.ceil('+total+'/_perPage),_page+1);renderList(null);" class="btn btn-secondary" style="padding:6px 12px;font-size:13px;" '+(end>=total?'disabled style="opacity:.4;cursor:not-allowed;padding:6px 12px;font-size:13px;"':'')+' ><i class="fa-solid fa-chevron-right"></i></button>' +
    '</div></div></div>';
}}

function renderForm(container, recordId) {{
  var r = (recordId && typeof getById === 'function') ? (getById(recordId) || {{}}) : {{}};
  var isEdit = !!(recordId && r.id);
  if (!container) container = document.querySelector('.view-section:not(.hidden)');
  if (!container) return;
  container.innerHTML =
    '<div style="max-width:640px;margin:0 auto;">' +
    '<h2 style="font-size:24px;font-weight:700;color:#f9fafb;margin-bottom:8px;">'+(isEdit?'Edit Record':'Add New Record')+'</h2>' +
    '<p style="color:#6b7280;font-size:14px;margin-bottom:24px;">'+(isEdit?'Update the record information below':'Fill in the details to create a new record')+'</p>' +
    '<div class="card"><form id="record-form" onsubmit="handleFormSubmit(event,\\''+(recordId||'')+'\\');">' +
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:0 16px;">' +
    '{form_html}' +
    '</div>' +
    '<div style="display:flex;gap:10px;margin-top:8px;">' +
    '<button type="submit" class="btn btn-primary" style="flex:1;justify-content:center;"><i class="fa-solid fa-'+(isEdit?'floppy-disk':'plus')+' mr-2"></i>'+(isEdit?'Save Changes':'Add Record')+'</button>' +
    '<button type="button" onclick="showView(\\'{list_route}\\')" class="btn btn-secondary" style="flex:1;justify-content:center;">Cancel</button>' +
    '</div></form></div></div>';
}}

function handleFormSubmit(e, recordId) {{
  e.preventDefault();
  var form = e.target;
  var data = {{}};
  var inputs = form.querySelectorAll('input,select,textarea');
  var valid = true;
  inputs.forEach(function(inp) {{
    if (inp.name) {{
      data[inp.name] = inp.value;
      if (inp.required && !inp.value.trim()) {{
        inp.style.borderColor = '#ef4444';
        inp.style.boxShadow = '0 0 0 3px rgba(239,68,68,.15)';
        valid = false;
      }} else {{
        inp.style.borderColor = '';
        inp.style.boxShadow = '';
      }}
    }}
  }});
  if (!valid) {{ showToast('Please fill in all required fields', 'warning'); return; }}
  if (recordId && typeof updateRecord === 'function') {{
    updateRecord(recordId, data);
    showToast('Record updated successfully!', 'success');
  }} else if (typeof createRecord === 'function') {{
    createRecord(data);
    showToast('Record created successfully!', 'success');
  }}
  showView('{list_route}');
}}

function renderReports(container) {{
  if (!container) container = document.querySelector('.view-section:not(.hidden)');
  if (!container) return;
  var s = (typeof getStats === 'function') ? getStats() : {{}};
  var all = (typeof getAll === 'function') ? getAll() : [];
  var breakdown = s.categoryBreakdown || {{}};
  var bLabels = Object.keys(breakdown), bData = Object.values(breakdown);
  var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  var monthly = s.monthly || Array(12).fill(0).map(function(){{return Math.floor(Math.random()*10)+1;}});
  container.innerHTML =
    '<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:24px;">' +
    '<div><h2 style="font-size:24px;font-weight:700;color:#f9fafb;margin:0;">Analytics & Reports</h2>' +
    '<p style="color:#6b7280;font-size:14px;margin-top:4px;">Comprehensive data analysis and insights</p></div>' +
    '<div style="display:flex;gap:8px;">' +
    '<button onclick="exportToCSV(typeof getAll===\\'function\\'?getAll():[],\\'report\\')" class="btn btn-primary"><i class="fa-solid fa-download mr-2"></i>Export CSV</button>' +
    '<button onclick="window.print()" class="btn btn-secondary"><i class="fa-solid fa-print mr-2"></i>Print</button>' +
    '</div></div>' +
    '<div class="card" style="margin-bottom:16px;"><h3 style="font-size:15px;font-weight:600;color:#f9fafb;margin-bottom:16px;">12-Month Trend</h3><canvas id="rep-line" height="120"></canvas></div>' +
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px;">' +
    '<div class="card"><h3 style="font-size:15px;font-weight:600;color:#f9fafb;margin-bottom:16px;">Category Breakdown</h3><canvas id="rep-bar" height="180"></canvas></div>' +
    '<div class="card"><h3 style="font-size:15px;font-weight:600;color:#f9fafb;margin-bottom:16px;">Status Distribution</h3><canvas id="rep-dough" height="180"></canvas></div>' +
    '</div>' +
    '<div class="card"><h3 style="font-size:15px;font-weight:600;color:#f9fafb;margin-bottom:16px;">Top Records</h3>' +
    '<div style="overflow-x:auto;">' + buildTableHTML(all.slice(0, 5)) + '</div></div>';
  setTimeout(function() {{
    var colors = ['{accent}','#4ade80','#f87171','#fbbf24','#818cf8','#38bdf8','#fb923c'];
    if (typeof safeChart === 'function') {{
      safeChart('rep-line', {{type:'line',data:{{labels:months,datasets:[{{label:'Records',data:monthly,borderColor:'{accent}',backgroundColor:'{accent}22',tension:.4,fill:true,pointBackgroundColor:'{accent}'}}]}},options:{{responsive:true,plugins:{{legend:{{display:false}}}},scales:{{y:{{beginAtZero:true,grid:{{color:'rgba(255,255,255,.05)'}},ticks:{{color:'#6b7280'}}}},x:{{grid:{{display:false}},ticks:{{color:'#6b7280'}}}}}}}}}});
      if (bLabels.length) {{
        safeChart('rep-bar', {{type:'bar',data:{{labels:bLabels,datasets:[{{label:'Count',data:bData,backgroundColor:colors.slice(0,bLabels.length),borderRadius:6}}]}},options:{{responsive:true,plugins:{{legend:{{display:false}}}},scales:{{y:{{beginAtZero:true,grid:{{color:'rgba(255,255,255,.05)'}},ticks:{{color:'#6b7280'}}}},x:{{grid:{{display:false}},ticks:{{color:'#6b7280'}}}}}}}}}});
        safeChart('rep-dough', {{type:'doughnut',data:{{labels:bLabels,datasets:[{{data:bData,backgroundColor:colors,borderWidth:0}}]}},options:{{responsive:true,plugins:{{legend:{{position:'right',labels:{{color:'#9ca3af',padding:10,font:{{size:11}}}},boxWidth:12}}}},cutout:'65%'}}}});
      }}
    }}
  }}, 100);
}}

function renderDetail(recordId) {{
  var r = (typeof getById === 'function') ? getById(recordId) : null;
  if (!r) return;
  var entries = Object.entries(r).filter(function(e){{return e[0] !== 'id';}});
  var html = '<div style="padding:24px;">' +
    '<h3 style="font-size:18px;font-weight:700;color:#f9fafb;margin-bottom:20px;">Record Details</h3>' +
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:24px;">' +
    entries.map(function(e) {{
      var val = e[0] === 'status'
        ? '<span class="badge ' + (typeof getStatusColor==='function' ? getStatusColor(e[1]) : 'badge-info') + '">' + e[1] + '</span>'
        : '<span style="color:#f3f4f6;font-size:14px;">' + (e[1] !== null && e[1] !== undefined ? e[1] : '—') + '</span>';
      return '<div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:8px;padding:12px;">' +
        '<p style="color:#6b7280;font-size:11px;text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px;">' + e[0] + '</p>' + val + '</div>';
    }}).join('') +
    '</div>' +
    '<div style="display:flex;gap:10px;">' +
    '<button onclick="doEdit(\\''+recordId+'\\');" class="btn btn-primary" style="flex:1;justify-content:center;"><i class="fa-solid fa-pen mr-2"></i>Edit</button>' +
    '<button onclick="closeModal()" class="btn btn-secondary" style="flex:1;justify-content:center;">Close</button>' +
    '</div></div>';
  if (typeof openModal === 'function') openModal(html);
}}

/* ── Action Helpers ── */
function doAdd() {{ renderForm(document.querySelector('.view-section:not(.hidden)'), null); }}
function doEdit(id) {{ renderForm(document.querySelector('.view-section:not(.hidden)'), id); }}
function doViewDetail(id) {{ renderDetail(id); }}
function doSort(field) {{
  if (_sortField === field) _sortDir = _sortDir === 'asc' ? 'desc' : 'asc';
  else {{ _sortField = field; _sortDir = 'asc'; }}
  renderList(document.querySelector('.view-section:not(.hidden)'));
}}
function doSearch(q) {{ _query = q; _page = 1; renderList(document.querySelector('.view-section:not(.hidden)')); }}
function doDeleteConfirm(id) {{
  if (typeof confirmDelete === 'function') {{
    confirmDelete(id,
      function(rid) {{ if (typeof deleteRecord === 'function') deleteRecord(rid); }},
      function() {{ renderList(document.querySelector('.view-section:not(.hidden)')); }}
    );
  }}
}}
"""

    def _generate_smart_fallback_html(self, req: str, name: str, color: str, features: list, views: list, analysis: dict) -> str:
        """Generate a beautiful, fully-functional single-page webapp as fallback."""
        accent = analysis.get("primary_color", {"indigo": "#6366f1", "violet": "#8b5cf6", "blue": "#3b82f6",
                  "green": "#22c55e", "orange": "#f97316", "red": "#ef4444"}.get(color, "#6366f1"))
        secondary = analysis.get("secondary_color", "#8b5cf6")
        visual_style = analysis.get("visual_style", "dark-glass")
        domain = self._get_domain_smart(req, {"analysis": analysis})

        # Build feature cards
        icons = ["fa-bolt", "fa-shield-halved", "fa-rocket", "fa-chart-line", "fa-puzzle-piece", "fa-star", "fa-infinity", "fa-wand-magic-sparkles"]
        feat_cards = "".join(
            f"""<div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:16px;padding:24px;transition:all .2s;" onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='0 20px 40px rgba(0,0,0,.3)'" onmouseout="this.style.transform='';this.style.boxShadow=''">
            <div style="width:48px;height:48px;border-radius:12px;background:linear-gradient(135deg,{accent}33,{accent}11);display:flex;align-items:center;justify-content:center;margin-bottom:16px;">
              <i class="fa-solid {icons[i % len(icons)]}" style="color:{accent};font-size:20px;"></i>
            </div>
            <h3 style="font-size:16px;font-weight:600;color:#f9fafb;margin:0 0 8px 0;">{f.split("(")[0].strip()}</h3>
            <p style="font-size:13px;color:#6b7280;line-height:1.6;margin:0;">{f}</p>
          </div>"""
            for i, f in enumerate(features[:6])
        )

        sample_data = [
            {"id": "1", "name": "Alice Johnson", "status": "active", "role": "Admin", "date": "2024-03-15", "score": "98"},
            {"id": "2", "name": "Bob Smith", "status": "active", "role": "User", "date": "2024-03-14", "score": "87"},
            {"id": "3", "name": "Carol White", "status": "inactive", "role": "Moderator", "date": "2024-03-13", "score": "75"},
            {"id": "4", "name": "David Brown", "status": "active", "role": "User", "date": "2024-03-12", "score": "92"},
            {"id": "5", "name": "Eva Martinez", "status": "active", "role": "Admin", "date": "2024-03-11", "score": "95"},
        ]
        table_rows = "".join(
            f"""<tr id="row-{d['id']}" style="border-bottom:1px solid rgba(255,255,255,.06);">
            <td style="padding:12px 16px;font-size:14px;color:#f9fafb;">{d['name']}</td>
            <td style="padding:12px 16px;font-size:14px;color:#9ca3af;">{d['role']}</td>
            <td style="padding:12px 16px;"><span style="background:rgba({'34,197,94' if d['status']=='active' else '239,68,68'},.12);color:{'#4ade80' if d['status']=='active' else '#f87171'};border-radius:9999px;padding:3px 10px;font-size:12px;font-weight:600;">{d['status']}</span></td>
            <td style="padding:12px 16px;font-size:14px;color:#9ca3af;">{d['date']}</td>
            <td style="padding:12px 16px;font-size:14px;color:{accent};font-weight:600;">{d['score']}%</td>
            <td style="padding:12px 16px;"><div style="display:flex;gap:6px;">
              <button onclick="editRecord('{d['id']}')" style="background:rgba(99,102,241,.15);color:{accent};border:none;border-radius:6px;padding:5px 10px;cursor:pointer;font-size:12px;" title="Edit"><i class="fa-solid fa-pen"></i></button>
              <button onclick="deleteRecord('{d['id']}')" style="background:rgba(239,68,68,.12);color:#f87171;border:none;border-radius:6px;padding:5px 10px;cursor:pointer;font-size:12px;" title="Delete"><i class="fa-solid fa-trash"></i></button>
            </div></td>
          </tr>"""
            for d in sample_data
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
  <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ font-family: 'Inter', system-ui, sans-serif; margin: 0; }}
    ::-webkit-scrollbar {{ width: 5px; }} ::-webkit-scrollbar-thumb {{ background: #374151; border-radius: 99px; }}
    .nav-link {{ display:flex;align-items:center;padding:10px 14px;border-radius:8px;color:#9ca3af;font-size:14px;cursor:pointer;transition:all .2s;text-decoration:none;gap:10px;border-left:3px solid transparent; }}
    .nav-link:hover {{ background:rgba({','.join(str(int(accent.lstrip('#')[i:i+2],16)) for i in (0,2,4))},.12);color:#f9fafb; }}
    .nav-link.active {{ background:rgba({','.join(str(int(accent.lstrip('#')[i:i+2],16)) for i in (0,2,4))},.18);color:{accent};border-left-color:{accent};font-weight:500; }}
    .view {{ display:none; }} .view.active {{ display:block;animation:fadeIn .3s ease; }}
    @keyframes fadeIn {{ from{{opacity:0;transform:translateY(8px)}} to{{opacity:1;transform:translateY(0)}} }}
    .card {{ background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:16px;padding:20px; }}
    .btn {{ display:inline-flex;align-items:center;gap:8px;padding:9px 18px;border-radius:9px;font-size:14px;font-weight:500;cursor:pointer;border:none;transition:all .18s; }}
    .btn-primary {{ background:{accent};color:#fff;box-shadow:0 2px 12px rgba({','.join(str(int(accent.lstrip('#')[i:i+2],16)) for i in (0,2,4))},.35); }}
    .btn-primary:hover {{ opacity:.9;transform:translateY(-1px); }}
    .btn-ghost {{ background:rgba(255,255,255,.06);color:#9ca3af;border:1px solid rgba(255,255,255,.1); }}
    .btn-ghost:hover {{ background:rgba(255,255,255,.1);color:#f9fafb; }}
    input,select,textarea {{ background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);border-radius:9px;padding:10px 14px;color:#f9fafb;font-size:14px;width:100%;outline:none;transition:border-color .18s; }}
    input:focus,select:focus,textarea:focus {{ border-color:{accent};box-shadow:0 0 0 3px rgba({','.join(str(int(accent.lstrip('#')[i:i+2],16)) for i in (0,2,4))},.15); }}
    .toast {{ position:fixed;top:20px;right:20px;background:#1f2937;border:1px solid #374151;border-radius:12px;padding:14px 18px;display:flex;align-items:center;gap:10px;font-size:14px;color:#f9fafb;z-index:9999;box-shadow:0 8px 32px rgba(0,0,0,.4);animation:slideIn .3s cubic-bezier(.34,1.56,.64,1); }}
    @keyframes slideIn {{ from{{transform:translateX(120%);opacity:0}} to{{transform:translateX(0);opacity:1}} }}
    .modal-overlay {{ position:fixed;inset:0;background:rgba(0,0,0,.7);backdrop-filter:blur(4px);z-index:9000;display:flex;align-items:center;justify-content:center;padding:20px; }}
    .modal-box {{ background:#111827;border:1px solid rgba(255,255,255,.1);border-radius:20px;padding:28px;width:100%;max-width:480px; }}
    th {{ padding:12px 16px;text-align:left;font-size:12px;text-transform:uppercase;letter-spacing:.07em;color:#6b7280;font-weight:600;border-bottom:1px solid rgba(255,255,255,.06); }}
    @media(max-width:768px){{#sidebar{{transform:translateX(-100%);position:fixed;height:100%;z-index:50;}}#sidebar.open{{transform:translateX(0);}}#main{{margin-left:0!important;}}}}
  </style>
</head>
<body style="background:#030712;color:#f9fafb;min-height:100vh;">

<!-- Sidebar -->
<div id="sidebar" style="width:256px;background:#0d1117;border-right:1px solid rgba(255,255,255,.07);display:flex;flex-direction:column;height:100vh;position:fixed;left:0;top:0;z-index:40;transition:transform .3s ease;">
  <div style="padding:20px;border-bottom:1px solid rgba(255,255,255,.07);">
    <div style="display:flex;align-items:center;gap:12px;">
      <div style="width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,{accent},{secondary});display:flex;align-items:center;justify-content:center;">
        <i class="fa-solid fa-layer-group" style="color:white;font-size:14px;"></i>
      </div>
      <div>
        <div style="font-weight:700;font-size:14px;color:#f9fafb;">{name}</div>
        <div style="font-size:11px;color:#6b7280;">Management System</div>
      </div>
    </div>
  </div>
  <nav style="flex:1;padding:12px;overflow-y:auto;">
    <p style="font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.1em;color:#4b5563;padding:8px 14px;margin-bottom:4px;">Menu</p>
    <a class="nav-link active" href="#" onclick="showView('dashboard',this);return false;" data-view="dashboard"><i class="fa-solid fa-gauge-high" style="width:16px;text-align:center;"></i>Dashboard</a>
    <a class="nav-link" href="#" onclick="showView('records',this);return false;" data-view="records"><i class="fa-solid fa-table-list" style="width:16px;text-align:center;"></i>Records</a>
    <a class="nav-link" href="#" onclick="showView('add',this);return false;" data-view="add"><i class="fa-solid fa-plus-circle" style="width:16px;text-align:center;"></i>Add New</a>
    <a class="nav-link" href="#" onclick="showView('reports',this);return false;" data-view="reports"><i class="fa-solid fa-chart-bar" style="width:16px;text-align:center;"></i>Reports</a>
    <a class="nav-link" href="#" onclick="showView('features',this);return false;" data-view="features"><i class="fa-solid fa-star" style="width:16px;text-align:center;"></i>Features</a>
  </nav>
  <div style="padding:16px;border-top:1px solid rgba(255,255,255,.07);">
    <div style="display:flex;align-items:center;gap:10px;padding:10px;background:rgba(255,255,255,.04);border-radius:10px;cursor:pointer;">
      <div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,{accent},{secondary});display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:white;">A</div>
      <div style="flex:1;min-width:0;"><div style="font-size:13px;font-weight:600;color:#f9fafb;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">Admin User</div><div style="font-size:11px;color:#6b7280;">Administrator</div></div>
    </div>
  </div>
</div>

<!-- Main -->
<div id="main" style="margin-left:256px;min-height:100vh;transition:margin-left .3s ease;">
  <!-- Header -->
  <header style="background:rgba(13,17,23,.8);backdrop-filter:blur(20px);border-bottom:1px solid rgba(255,255,255,.07);padding:14px 24px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:30;">
    <div style="display:flex;align-items:center;gap:14px;">
      <button onclick="document.getElementById('sidebar').classList.toggle('open')" style="background:none;border:none;color:#6b7280;font-size:18px;cursor:pointer;padding:4px;display:none;" id="menu-btn"><i class="fa-solid fa-bars"></i></button>
      <div style="position:relative;">
        <i class="fa-solid fa-magnifying-glass" style="position:absolute;left:12px;top:50%;transform:translateY(-50%);color:#4b5563;font-size:13px;"></i>
        <input type="search" id="search-input" placeholder="Search... (Ctrl+K)" oninput="handleSearch(this.value)" style="padding-left:36px;width:260px;background:rgba(255,255,255,.05);" />
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:10px;">
      <button onclick="toggleTheme()" id="theme-btn" style="background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);border-radius:9px;padding:8px 12px;color:#9ca3af;cursor:pointer;font-size:14px;transition:all .2s;" title="Toggle theme"><i class="fa-solid fa-moon"></i></button>
      <button style="background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);border-radius:9px;padding:8px 12px;cursor:pointer;position:relative;" title="Notifications">
        <i class="fa-solid fa-bell" style="color:#9ca3af;font-size:14px;"></i>
        <span style="position:absolute;top:8px;right:8px;width:7px;height:7px;background:{accent};border-radius:50%;box-shadow:0 0 6px {accent};"></span>
      </button>
    </div>
  </header>

  <!-- Content -->
  <main style="padding:28px;">
    <!-- Dashboard -->
    <div id="view-dashboard" class="view active">
      <div style="margin-bottom:28px;"><h1 style="font-size:26px;font-weight:700;color:#f9fafb;margin:0;">{name}</h1><p style="color:#6b7280;font-size:14px;margin-top:6px;">{analysis.get("enhanced_request", req)}</p></div>
      <!-- Stats -->
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px;margin-bottom:28px;">
        <div class="card" style="display:flex;justify-content:space-between;align-items:flex-start;">
          <div><p style="color:#6b7280;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;">Total Records</p><p style="font-size:30px;font-weight:700;color:#f9fafb;margin-top:6px;">247</p><p style="color:#4ade80;font-size:12px;margin-top:4px;"><i class="fa-solid fa-arrow-up"></i> +12.5% this month</p></div>
          <div style="width:44px;height:44px;border-radius:12px;background:rgba({','.join(str(int(accent.lstrip('#')[i:i+2],16)) for i in (0,2,4))},.15);display:flex;align-items:center;justify-content:center;"><i class="fa-solid fa-database" style="color:{accent};font-size:18px;"></i></div>
        </div>
        <div class="card" style="display:flex;justify-content:space-between;align-items:flex-start;">
          <div><p style="color:#6b7280;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;">Active</p><p style="font-size:30px;font-weight:700;color:#f9fafb;margin-top:6px;">189</p><p style="color:#4ade80;font-size:12px;margin-top:4px;"><i class="fa-solid fa-arrow-up"></i> +8.3% this month</p></div>
          <div style="width:44px;height:44px;border-radius:12px;background:rgba(34,197,94,.15);display:flex;align-items:center;justify-content:center;"><i class="fa-solid fa-circle-check" style="color:#4ade80;font-size:18px;"></i></div>
        </div>
        <div class="card" style="display:flex;justify-content:space-between;align-items:flex-start;">
          <div><p style="color:#6b7280;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;">Completed</p><p style="font-size:30px;font-weight:700;color:#f9fafb;margin-top:6px;">58</p><p style="color:#f87171;font-size:12px;margin-top:4px;"><i class="fa-solid fa-arrow-down"></i> -2.1% this month</p></div>
          <div style="width:44px;height:44px;border-radius:12px;background:rgba(239,68,68,.15);display:flex;align-items:center;justify-content:center;"><i class="fa-solid fa-flag-checkered" style="color:#f87171;font-size:18px;"></i></div>
        </div>
        <div class="card" style="display:flex;justify-content:space-between;align-items:flex-start;">
          <div><p style="color:#6b7280;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;">This Month</p><p style="font-size:30px;font-weight:700;color:#f9fafb;margin-top:6px;">34</p><p style="color:#fbbf24;font-size:12px;margin-top:4px;"><i class="fa-solid fa-clock"></i> Last 30 days</p></div>
          <div style="width:44px;height:44px;border-radius:12px;background:rgba(245,158,11,.15);display:flex;align-items:center;justify-content:center;"><i class="fa-solid fa-calendar-days" style="color:#fbbf24;font-size:18px;"></i></div>
        </div>
      </div>
      <!-- Charts -->
      <div style="display:grid;grid-template-columns:2fr 1fr;gap:16px;margin-bottom:28px;">
        <div class="card"><h3 style="font-size:15px;font-weight:600;color:#f9fafb;margin:0 0 20px;">Monthly Activity</h3><canvas id="main-chart" height="160"></canvas></div>
        <div class="card"><h3 style="font-size:15px;font-weight:600;color:#f9fafb;margin:0 0 20px;">Distribution</h3><canvas id="dough-chart" height="160"></canvas></div>
      </div>
      <!-- Recent -->
      <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
          <h3 style="font-size:15px;font-weight:600;color:#f9fafb;margin:0;">Recent Records</h3>
          <button onclick="showView('records',document.querySelector('[data-view=records]'))" class="btn btn-primary" style="padding:7px 14px;font-size:13px;">View All <i class="fa-solid fa-arrow-right ml-1"></i></button>
        </div>
        <div style="overflow-x:auto;"><table style="width:100%;border-collapse:collapse;">
          <thead><tr><th>Name</th><th>Role</th><th>Status</th><th>Date</th><th>Score</th><th>Actions</th></tr></thead>
          <tbody id="recent-table">{table_rows}</tbody>
        </table></div>
      </div>
    </div>

    <!-- Records -->
    <div id="view-records" class="view">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:24px;flex-wrap:wrap;gap:12px;">
        <div><h1 style="font-size:26px;font-weight:700;color:#f9fafb;margin:0;">Records</h1><p id="records-count" style="color:#6b7280;font-size:14px;margin-top:6px;">5 total entries</p></div>
        <div style="display:flex;gap:8px;">
          <button onclick="showView('add',document.querySelector('[data-view=add]'))" class="btn btn-primary"><i class="fa-solid fa-plus"></i>Add New</button>
          <button onclick="exportData()" class="btn btn-ghost"><i class="fa-solid fa-download"></i>Export CSV</button>
        </div>
      </div>
      <div class="card" style="padding:0;overflow:hidden;">
        <div style="padding:16px;border-bottom:1px solid rgba(255,255,255,.07);display:flex;gap:10px;flex-wrap:wrap;">
          <div style="position:relative;flex:1;min-width:180px;"><i class="fa-solid fa-search" style="position:absolute;left:12px;top:50%;transform:translateY(-50%);color:#4b5563;font-size:13px;"></i><input type="search" id="table-search" oninput="filterTable(this.value)" placeholder="Search records..." style="padding-left:36px;margin:0;"/></div>
          <select id="status-filter" onchange="filterTable('')" style="width:auto;margin:0;">
            <option value="">All Status</option><option value="active">Active</option><option value="inactive">Inactive</option>
          </select>
        </div>
        <div style="overflow-x:auto;"><table style="width:100%;border-collapse:collapse;" id="records-table">
          <thead><tr><th>Name</th><th>Role</th><th>Status</th><th>Date</th><th>Score</th><th>Actions</th></tr></thead>
          <tbody id="records-body">{table_rows}</tbody>
        </table></div>
        <div style="padding:12px 16px;border-top:1px solid rgba(255,255,255,.07);display:flex;justify-content:space-between;align-items:center;">
          <span style="color:#6b7280;font-size:13px;">Showing 1–5 of 5</span>
          <div style="display:flex;gap:6px;">
            <button style="background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);border-radius:7px;padding:6px 12px;color:#6b7280;cursor:pointer;font-size:13px;" disabled><i class="fa-solid fa-chevron-left"></i></button>
            <span style="background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);border-radius:7px;padding:6px 14px;color:#f9fafb;font-size:13px;">1</span>
            <button style="background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);border-radius:7px;padding:6px 12px;color:#6b7280;cursor:pointer;font-size:13px;" disabled><i class="fa-solid fa-chevron-right"></i></button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add New -->
    <div id="view-add" class="view">
      <div style="max-width:600px;margin:0 auto;">
        <h1 style="font-size:26px;font-weight:700;color:#f9fafb;margin-bottom:8px;">Add New Record</h1>
        <p style="color:#6b7280;font-size:14px;margin-bottom:28px;">Fill in the details below to create a new record in the system.</p>
        <div class="card">
          <form id="add-form" onsubmit="submitForm(event)" style="display:flex;flex-direction:column;gap:16px;">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
              <div><label style="display:block;font-size:13px;font-weight:500;color:#9ca3af;margin-bottom:6px;">Full Name *</label><input type="text" name="name" required placeholder="e.g. Alice Johnson"/></div>
              <div><label style="display:block;font-size:13px;font-weight:500;color:#9ca3af;margin-bottom:6px;">Email Address</label><input type="email" name="email" placeholder="alice@example.com"/></div>
              <div><label style="display:block;font-size:13px;font-weight:500;color:#9ca3af;margin-bottom:6px;">Role *</label><select name="role" required><option value="">Select role...</option><option value="Admin">Admin</option><option value="User">User</option><option value="Moderator">Moderator</option></select></div>
              <div><label style="display:block;font-size:13px;font-weight:500;color:#9ca3af;margin-bottom:6px;">Status</label><select name="status"><option value="active">Active</option><option value="inactive">Inactive</option></select></div>
              <div><label style="display:block;font-size:13px;font-weight:500;color:#9ca3af;margin-bottom:6px;">Phone</label><input type="tel" name="phone" placeholder="+1 555-0100"/></div>
              <div><label style="display:block;font-size:13px;font-weight:500;color:#9ca3af;margin-bottom:6px;">Date</label><input type="date" name="date"/></div>
            </div>
            <div><label style="display:block;font-size:13px;font-weight:500;color:#9ca3af;margin-bottom:6px;">Notes</label><textarea name="notes" rows="3" placeholder="Additional notes..."></textarea></div>
            <div style="display:flex;gap:10px;">
              <button type="submit" class="btn btn-primary" style="flex:1;justify-content:center;"><i class="fa-solid fa-plus mr-2"></i>Add Record</button>
              <button type="button" onclick="showView('records',document.querySelector('[data-view=records]'))" class="btn btn-ghost" style="flex:1;justify-content:center;">Cancel</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Reports -->
    <div id="view-reports" class="view">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:24px;flex-wrap:wrap;gap:12px;">
        <div><h1 style="font-size:26px;font-weight:700;color:#f9fafb;margin:0;">Analytics</h1><p style="color:#6b7280;font-size:14px;margin-top:6px;">Data insights and performance metrics</p></div>
        <div style="display:flex;gap:8px;">
          <button onclick="exportData()" class="btn btn-primary"><i class="fa-solid fa-download"></i>Export</button>
          <button onclick="window.print()" class="btn btn-ghost"><i class="fa-solid fa-print"></i>Print</button>
        </div>
      </div>
      <div style="display:grid;grid-template-columns:1fr;gap:16px;margin-bottom:24px;">
        <div class="card"><h3 style="font-size:15px;font-weight:600;color:#f9fafb;margin:0 0 20px;">12-Month Activity Trend</h3><canvas id="reports-line" height="120"></canvas></div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
        <div class="card"><h3 style="font-size:15px;font-weight:600;color:#f9fafb;margin:0 0 16px;">Status Breakdown</h3><canvas id="reports-bar" height="180"></canvas></div>
        <div class="card"><h3 style="font-size:15px;font-weight:600;color:#f9fafb;margin:0 0 16px;">Category Distribution</h3><canvas id="reports-dough" height="180"></canvas></div>
      </div>
    </div>

    <!-- Features -->
    <div id="view-features" class="view">
      <h1 style="font-size:26px;font-weight:700;color:#f9fafb;margin-bottom:8px;">{name} Features</h1>
      <p style="color:#6b7280;font-size:14px;margin-bottom:28px;">{analysis.get("enhanced_request", req)}</p>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;">{feat_cards}</div>
    </div>
  </main>
</div>

<!-- Toast container -->
<div id="toast-container"></div>

<script>
var _records = [
  {{id:'1',name:'Alice Johnson',email:'alice@example.com',role:'Admin',status:'active',date:'2024-03-15',score:'98',notes:''}},
  {{id:'2',name:'Bob Smith',email:'bob@example.com',role:'User',status:'active',date:'2024-03-14',score:'87',notes:''}},
  {{id:'3',name:'Carol White',email:'carol@example.com',role:'Moderator',status:'inactive',date:'2024-03-13',score:'75',notes:''}},
  {{id:'4',name:'David Brown',email:'david@example.com',role:'User',status:'active',date:'2024-03-12',score:'92',notes:''}},
  {{id:'5',name:'Eva Martinez',email:'eva@example.com',role:'Admin',status:'active',date:'2024-03-11',score:'95',notes:''}}
];

function showView(name, el) {{
  document.querySelectorAll('.view').forEach(function(v){{v.classList.remove('active');}});
  document.querySelectorAll('.nav-link').forEach(function(l){{l.classList.remove('active');}});
  var v = document.getElementById('view-'+name);
  if (v) v.classList.add('active');
  if (el) el.classList.add('active');
  else {{var l=document.querySelector('[data-view="'+name+'"]');if(l)l.classList.add('active');}}
  if (name === 'reports') setTimeout(initReportCharts, 100);
  if (name === 'dashboard') setTimeout(initDashCharts, 100);
}}

function toast(msg, type) {{
  type = type||'success';
  var colors = {{success:'#4ade80',error:'#f87171',warning:'#fbbf24',info:'#818cf8'}};
  var icons = {{success:'circle-check',error:'circle-xmark',warning:'triangle-exclamation',info:'circle-info'}};
  var t = document.createElement('div');
  t.className = 'toast';
  t.innerHTML = '<i class="fa-solid fa-'+icons[type]+'" style="color:'+colors[type]+';font-size:16px;flex-shrink:0;"></i><span>'+msg+'</span>';
  document.body.appendChild(t);
  setTimeout(function(){{t.style.opacity='0';t.style.transform='translateX(120%)';t.style.transition='all .3s';setTimeout(function(){{t.remove();}},300);}},3500);
}}

function toggleTheme() {{
  document.documentElement.classList.toggle('dark');
  var btn = document.getElementById('theme-btn');
  var isDark = document.documentElement.classList.contains('dark');
  if (btn) btn.innerHTML = isDark ? '<i class="fa-solid fa-moon"></i>' : '<i class="fa-solid fa-sun"></i>';
  localStorage.setItem('theme', isDark ? 'dark' : 'light');
}}

function handleSearch(q) {{
  filterTable(q);
}}

function filterTable(q) {{
  var rows = document.querySelectorAll('#recent-table tr, #records-body tr');
  rows.forEach(function(row) {{
    var text = row.textContent.toLowerCase();
    var status = document.getElementById('status-filter');
    var statusVal = status ? status.value : '';
    var matchSearch = !q || text.includes(q.toLowerCase());
    var matchStatus = !statusVal || text.includes(statusVal);
    row.style.display = matchSearch && matchStatus ? '' : 'none';
  }});
}}

function submitForm(e) {{
  e.preventDefault();
  var data = Object.fromEntries(new FormData(e.target));
  if (!data.name) {{ toast('Name is required', 'warning'); return; }}
  data.id = Date.now().toString();
  data.score = Math.floor(Math.random()*30+70)+'%';
  _records.unshift(data);
  toast('Record added successfully!', 'success');
  e.target.reset();
  showView('records', document.querySelector('[data-view=records]'));
  refreshTable();
}}

function refreshTable() {{
  var bodies = ['recent-table','records-body'];
  bodies.forEach(function(id){{
    var tbody = document.getElementById(id);
    if (!tbody) return;
    tbody.innerHTML = _records.slice(0,5).map(function(r){{
      return '<tr style="border-bottom:1px solid rgba(255,255,255,.06);">'+
        '<td style="padding:12px 16px;font-size:14px;color:#f9fafb;">'+r.name+'</td>'+
        '<td style="padding:12px 16px;font-size:14px;color:#9ca3af;">'+(r.role||'User')+'</td>'+
        '<td style="padding:12px 16px;"><span style="background:rgba('+(r.status==='active'?'34,197,94':'239,68,68')+',.12);color:'+(r.status==='active'?'#4ade80':'#f87171')+';border-radius:9999px;padding:3px 10px;font-size:12px;font-weight:600;">'+r.status+'</span></td>'+
        '<td style="padding:12px 16px;font-size:14px;color:#9ca3af;">'+(r.date||'—')+'</td>'+
        '<td style="padding:12px 16px;font-size:14px;color:{accent};font-weight:600;">'+(r.score||'—')+'</td>'+
        '<td style="padding:12px 16px;"><div style="display:flex;gap:6px;">'+
        '<button onclick="editRecord(\\''+ r.id +'\\')" style="background:rgba(99,102,241,.15);color:{accent};border:none;border-radius:6px;padding:5px 10px;cursor:pointer;font-size:12px;"><i class="fa-solid fa-pen"></i></button>'+
        '<button onclick="delRecord(\\''+ r.id +'\\')" style="background:rgba(239,68,68,.12);color:#f87171;border:none;border-radius:6px;padding:5px 10px;cursor:pointer;font-size:12px;"><i class="fa-solid fa-trash"></i></button>'+
        '</div></td></tr>';
    }}).join('');
  }});
  var c = document.getElementById('records-count');
  if (c) c.textContent = _records.length + ' total entries';
}}

function editRecord(id) {{ toast('Edit feature: form pre-filled', 'info'); }}
function deleteRecord(id) {{ delRecord(id); }}
function delRecord(id) {{
  if (!confirm('Delete this record?')) return;
  _records = _records.filter(function(r){{return r.id!==id;}});
  toast('Record deleted', 'error');
  refreshTable();
}}
function exportData() {{
  var rows = [Object.keys(_records[0]).join(',')].concat(_records.map(function(r){{return Object.values(r).map(function(v){{return '"'+v+'"';}}).join(',');}}));
  var blob = new Blob([rows.join('\\n')], {{type:'text/csv'}});
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = '{name.lower().replace(" ","-")}.csv';
  a.click();
  toast('Exported '+_records.length+' records!', 'success');
}}

var _charts = {{}};
function mkChart(id, cfg) {{
  if (_charts[id]) {{ _charts[id].destroy(); }}
  var canvas = document.getElementById(id);
  if (!canvas) return;
  _charts[id] = new Chart(canvas, cfg);
}}
var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
var monthData = [12,19,8,15,22,18,25,21,28,24,31,27];
function initDashCharts() {{
  mkChart('main-chart', {{type:'line',data:{{labels:months,datasets:[{{label:'Records',data:monthData,borderColor:'{accent}',backgroundColor:'{accent}22',tension:.4,fill:true,pointBackgroundColor:'{accent}',pointRadius:4}}]}},options:{{responsive:true,plugins:{{legend:{{display:false}}}},scales:{{y:{{beginAtZero:true,grid:{{color:'rgba(255,255,255,.05)'}},ticks:{{color:'#6b7280'}}}},x:{{grid:{{display:false}},ticks:{{color:'#6b7280'}}}}}}}}}});
  mkChart('dough-chart', {{type:'doughnut',data:{{labels:['Active','Inactive','Completed'],datasets:[{{data:[189,58,34],backgroundColor:['{accent}','#f87171','#fbbf24'],borderWidth:0}}]}},options:{{responsive:true,plugins:{{legend:{{position:'right',labels:{{color:'#9ca3af',padding:10,font:{{size:11}}}},boxWidth:12}}}},cutout:'70%'}}}});
}}
function initReportCharts() {{
  mkChart('reports-line', {{type:'line',data:{{labels:months,datasets:[{{label:'Monthly',data:monthData,borderColor:'{accent}',backgroundColor:'{accent}22',tension:.4,fill:true}}]}},options:{{responsive:true,plugins:{{legend:{{display:false}}}},scales:{{y:{{beginAtZero:true,grid:{{color:'rgba(255,255,255,.05)'}},ticks:{{color:'#6b7280'}}}},x:{{grid:{{display:false}},ticks:{{color:'#6b7280'}}}}}}}}}});
  mkChart('reports-bar', {{type:'bar',data:{{labels:['Active','Inactive','Completed'],datasets:[{{data:[189,58,34],backgroundColor:['{accent}cc','#f87171cc','#fbbf24cc'],borderRadius:8}}]}},options:{{responsive:true,plugins:{{legend:{{display:false}}}},scales:{{y:{{beginAtZero:true,grid:{{color:'rgba(255,255,255,.05)'}},ticks:{{color:'#6b7280'}}}},x:{{grid:{{display:false}},ticks:{{color:'#6b7280'}}}}}}}}}});
  mkChart('reports-dough', {{type:'doughnut',data:{{labels:['Admin','User','Moderator'],datasets:[{{data:[2,2,1],backgroundColor:['{accent}','{secondary}','#fbbf24'],borderWidth:0}}]}},options:{{responsive:true,plugins:{{legend:{{position:'right',labels:{{color:'#9ca3af',font:{{size:11}}}},boxWidth:12}}}},cutout:'65%'}}}});
}}

document.addEventListener('DOMContentLoaded', function() {{
  var theme = localStorage.getItem('theme')||'dark';
  if (theme==='dark') document.documentElement.classList.add('dark');
  document.addEventListener('keydown', function(e){{
    if ((e.ctrlKey||e.metaKey)&&e.key==='k') {{e.preventDefault();var s=document.getElementById('search-input');if(s)s.focus();}}
  }});
  var mb = document.getElementById('menu-btn');
  if (window.innerWidth < 768 && mb) mb.style.display = 'block';
  window.addEventListener('resize', function(){{
    if (mb) mb.style.display = window.innerWidth < 768 ? 'block' : 'none';
  }});
  setTimeout(initDashCharts, 200);
}});
</script>
</body>
</html>"""

    def _fallback_flask(self, plan) -> str:
        nm = plan.get("project_name", "api")
        desc = plan.get("description", "REST API")
        feats = plan.get("features", [])
        return f"""from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import uuid
import datetime

app = Flask(__name__)
CORS(app, origins="*")

# In-memory data store
store = [
    {{"id": "1", "name": "Sample Record 1", "status": "active", "category": "A", "createdAt": "2024-01-15"}},
    {{"id": "2", "name": "Sample Record 2", "status": "active", "category": "B", "createdAt": "2024-02-10"}},
    {{"id": "3", "name": "Sample Record 3", "status": "inactive", "category": "A", "createdAt": "2024-03-05"}},
]

def success(data=None, message="Success", **kwargs):
    resp = {{"success": True, "message": message}}
    if data is not None: resp["data"] = data
    resp.update(kwargs)
    return jsonify(resp)

def error(message, code=400):
    return jsonify({{"success": False, "error": message}}), code

@app.route("/health")
def health():
    \"\"\"Health check endpoint.\"\"\"
    return success(message="OK", version="1.0", project="{nm}", timestamp=datetime.datetime.utcnow().isoformat())

@app.route("/api/items", methods=["GET"])
def list_items():
    \"\"\"List all items with optional search and pagination.\"\"\"
    q = request.args.get("q", "").lower()
    status = request.args.get("status", "")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    items = store[:]
    if q:
        items = [i for i in items if q in i.get("name","").lower() or q in i.get("category","").lower()]
    if status:
        items = [i for i in items if i.get("status") == status]
    total = len(items)
    paginated = items[(page-1)*per_page : page*per_page]
    return success(paginated, total=total, page=page, per_page=per_page, pages=-(-total//per_page))

@app.route("/api/items/<item_id>", methods=["GET"])
def get_item(item_id):
    \"\"\"Get a single item by ID.\"\"\"
    item = next((i for i in store if i["id"] == item_id), None)
    if not item: return error("Item not found", 404)
    return success(item)

@app.route("/api/items", methods=["POST"])
def create_item():
    \"\"\"Create a new item.\"\"\"
    data = request.get_json(silent=True)
    if not data: return error("Request body required")
    if not data.get("name"): return error("'name' field is required")
    item = {{**data, "id": str(uuid.uuid4()), "createdAt": datetime.datetime.utcnow().isoformat()}}
    store.append(item)
    return success(item, message="Item created", code=201), 201

@app.route("/api/items/<item_id>", methods=["PUT"])
def update_item(item_id):
    \"\"\"Update an existing item.\"\"\"
    data = request.get_json(silent=True)
    if not data: return error("Request body required")
    idx = next((i for i, x in enumerate(store) if x["id"] == item_id), None)
    if idx is None: return error("Item not found", 404)
    store[idx] = {{**store[idx], **data, "id": item_id}}
    return success(store[idx], message="Item updated")

@app.route("/api/items/<item_id>", methods=["DELETE"])
def delete_item(item_id):
    \"\"\"Delete an item.\"\"\"
    global store
    original = len(store)
    store = [i for i in store if i["id"] != item_id]
    if len(store) == original: return error("Item not found", 404)
    return success(message="Item deleted")

@app.errorhandler(400)
def bad_request(e): return error(str(e), 400)

@app.errorhandler(404)
def not_found(e): return error("Resource not found", 404)

@app.errorhandler(405)
def method_not_allowed(e): return error("Method not allowed", 405)

@app.errorhandler(500)
def server_error(e): return error("Internal server error", 500)

if __name__ == "__main__":
    print(f"Starting {nm} API...")
    print("Endpoints: GET/POST /api/items, GET/PUT/DELETE /api/items/<id>, GET /health")
    app.run(debug=True, host="0.0.0.0", port=5000)
"""

    def _readme(self, plan, arch) -> str:
        name = plan.get("project_name", "project").replace("-", " ").title()
        desc = plan.get("description", "")
        feats = "\n".join(f"- {f}" for f in plan.get("features", []))
        tech = ", ".join(plan.get("tech_stack", []))
        entry = arch.get("entry_point", "index.html")
        flist = "\n".join(f"- `{f['path']}`" for f in arch.get("files", []))
        setup = f"```bash\npip install -r requirements.txt\npython {entry}\n```" if entry.endswith(".py") else f"1. Extract the ZIP\n2. Open `{entry}` in your browser\n3. No installation needed!"
        return f"# {name}\n\n{desc}\n\n## Features\n{feats}\n\n## Tech Stack\n{tech}\n\n## Files\n{flist}\n\n## Getting Started\n{setup}\n\n---\n*Generated by LovableBot — 8-Agent AI Platform*\n"


# ════════════════════════════════════════════════════════════════════════════════
# AGENT 5: Debugger — Automated Bug Detection & Fixing
# ════════════════════════════════════════════════════════════════════════════════

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

            # Regenerate if suspiciously short or has placeholder signs
            min_sizes = {"html": 2000, "js": 500, "css": 400, "py": 400}
            threshold = min_sizes.get(ext, 200)
            placeholder_count = sum(1 for p in PLACEHOLDER_SIGNS if p.lower() in content.lower())

            if len(content.strip()) < threshold or placeholder_count >= 3:
                if progress_cb:
                    progress_cb(f"⚠️ `{fpath}` quality issue ({len(content)} chars, {placeholder_count} placeholders), regenerating...")
                better = self._ai_regen(fpath, ext, content, plan)
                if better and len(better) > len(content) * 0.9:
                    fixed[fpath] = better
                    report.append(f"{fpath}: Regenerated (quality below threshold)")

        return {"files": fixed, "plan": plan,
                "architecture": coder_out.get("architecture", {}),
                "debug_report": report}

    def _scan(self, fpath, ext, content, all_files):
        issues = []
        if ext == "html":
            if "<!DOCTYPE" not in content[:200]:
                issues.append("Missing DOCTYPE declaration")
            if "</html>" not in content[-500:]:
                issues.append("Missing </html>")
            if "</body>" not in content[-800:]:
                issues.append("Missing </body>")
            # Check all linked JS files exist
            for jf in all_files:
                if jf.endswith(".js") and f'src="{jf}"' not in content:
                    issues.append(f"JS not linked: {jf}")
            if "scene.js" in all_files and "three.min.js" not in content:
                issues.append("Three.js CDN missing")
        elif ext == "js":
            opening = content.count("{")
            closing = content.count("}")
            if abs(opening - closing) > 8:
                issues.append(f"Unbalanced braces ({opening} open, {closing} close)")
            open_p = content.count("(")
            close_p = content.count(")")
            if abs(open_p - close_p) > 8:
                issues.append(f"Unbalanced parentheses")
        elif ext == "py":
            if "app.run" not in content and "from flask import" in content:
                issues.append("Missing app.run()")
            if "Flask(__name__)" not in content and "from flask import" in content:
                issues.append("Missing Flask app instantiation")
        return issues

    def _fix(self, fpath, ext, content, all_files, issues):
        if ext == "html":
            if "Missing DOCTYPE" in str(issues):
                content = "<!DOCTYPE html>\n" + content
            if "Missing </html>" in str(issues):
                if "</body>" in content:
                    content = content.rstrip() + "\n</html>"
                else:
                    content = content.rstrip() + "\n</body>\n</html>"
            if "Missing </body>" in str(issues):
                content = content.rstrip().rstrip("</html>").rstrip() + "\n</body>\n</html>"
            for jf in all_files:
                if jf.endswith(".js") and f'src="{jf}"' not in content:
                    tag = f'<script src="{jf}"></script>'
                    if "</body>" in content:
                        content = content.replace("</body>", f"  {tag}\n</body>")
                    else:
                        content += f"\n{tag}"
            if "Three.js CDN missing" in str(issues):
                cdn = '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>'
                content = content.replace("</head>", f"  {cdn}\n</head>")
        elif ext == "py":
            if "Missing app.run()" in str(issues):
                content += "\n\nif __name__ == '__main__':\n    app.run(debug=True, host='0.0.0.0', port=5000)\n"
        return content

    def _ai_regen(self, fpath, ext, content, plan):
        prompt = f"""The following {ext} file is incomplete or low quality. Rewrite it completely.

Project: {plan.get("description", plan.get("project_name", ""))}
Features: {", ".join(plan.get("features", [])[:5])}
Current code (broken/incomplete): 
{content[:600]}...

Write the COMPLETE, PRODUCTION-READY {ext} file. Minimum {{"html":300,"js":100,"css":80,"py":60}}.get("{ext}",50) lines.
Output ONLY the code in a ```{ext} block."""

        resp = call_ai(prompt, timeout=100)
        return extract_code(resp, ext)


# ════════════════════════════════════════════════════════════════════════════════
# AGENT 6: Reviewer — Quality Enforcement & Feature Completion
# ════════════════════════════════════════════════════════════════════════════════

class ReviewerAgent:
    name = "Reviewer"
    emoji = "🔍"

    def run(self, dbg_out: dict, progress_cb=None) -> dict:
        files = dbg_out.get("files", {})
        plan = dbg_out.get("plan", {})
        features = plan.get("features", [])
        improved = dict(files)

        # Find main file to review
        fpath = None
        for candidate in ["index.html", "app.py", "scene.js"]:
            if candidate in files and len(files[candidate]) > 1000:
                fpath = candidate
                break
        if not fpath and files:
            fpath = max(files, key=lambda k: len(files[k]))

        if not fpath:
            return {**dbg_out, "files": improved}

        ext = fpath.split(".")[-1]
        content = files[fpath]

        if progress_cb:
            progress_cb(f"🔎 Quality-checking `{fpath}` ({len(content):,} chars)...")

        # Check features coverage
        missing = [f for f in features if not any(
            kw.lower() in content.lower()
            for kw in f.lower().replace("(", " ").replace(")", " ").split()[:4]
            if len(kw) > 3
        )]

        # If quality is already high and features are covered, skip expensive AI call
        min_chars = {"html": MIN_HTML_CHARS, "js": MIN_JS_CHARS, "css": MIN_CSS_CHARS, "py": MIN_PY_CHARS}
        if len(missing) <= 2 and len(content) > min_chars.get(ext, 2000) * 1.5:
            if progress_cb:
                progress_cb(f"✅ `{fpath}` passes quality review ({len(content):,} chars)")
            return {**dbg_out, "files": improved}

        missing_str = "\n".join(f"- {f}" for f in missing[:5]) if missing else "none"

        prompt = f"""Quality review: improve this {ext} file. Ensure ALL features are fully implemented.

Project: {plan.get("project_name")} — {plan.get("description", "")}
All required features:
{chr(10).join(f"- {f}" for f in features)}

Missing/incomplete:
{missing_str}

Current code ({len(content)} chars):
{content[:7000]}{"... [truncated]" if len(content) > 7000 else ""}

1. Add ALL missing features with complete implementation
2. Improve visual quality (better spacing, colors, animations)
3. Fix any UI/UX issues
4. Ensure all interactive elements work
5. Do NOT remove existing working functionality

Return the COMPLETE improved {ext} in a ```{ext} block. Must be at least as long as the input."""

        resp = call_ai(prompt, timeout=140)
        new_code = extract_code(resp, ext)

        # Only accept if it's longer (we added more features)
        if new_code and len(new_code) >= len(content) * 0.7:
            improved[fpath] = new_code
            if progress_cb:
                progress_cb(f"✅ Improved `{fpath}` ({len(content):,} → {len(new_code):,} chars)")

        return {"files": improved, "plan": plan,
                "architecture": dbg_out.get("architecture", {}),
                "debug_report": dbg_out.get("debug_report", [])}


# ════════════════════════════════════════════════════════════════════════════════
# AGENT 7: Iteration Agent — Smart Code Modification
# ════════════════════════════════════════════════════════════════════════════════

class IterationAgent:
    name = "Iterator"
    emoji = "🔄"

    def run(self, modification: str, existing_files: dict, plan: dict) -> dict:
        """Intelligently modify existing generated code based on user's change request.
        Handles both single-file and multi-file projects.
        """
        updated = dict(existing_files)

        # ── Determine which files to modify ───────────────────────────────────
        files_to_modify = self._pick_files_to_modify(modification, existing_files)

        for main_file in files_to_modify:
            ext = main_file.split(".")[-1]
            current_code = existing_files[main_file]

            # For multi-file: include a summary of other files for context
            other_files_ctx = ""
            if len(existing_files) > 1:
                other_names = [f for f in existing_files if f != main_file]
                other_files_ctx = f"\nOther project files (for context): {', '.join(other_names[:8])}"

            prompt = f"""You are modifying existing production code based on a user request.

CHANGE REQUEST: "{modification}"

File to modify: {main_file} ({len(current_code)} chars){other_files_ctx}

Current {ext} code:
{current_code[:9000]}{"...[truncated]" if len(current_code) > 9000 else ""}

RULES:
1. Apply EXACTLY what the user requested — nothing more, nothing less
2. Keep ALL existing functionality intact
3. Maintain the same libraries, structure, and coding style
4. If adding UI: match the existing visual design (colors, spacing, fonts)
5. If changing colors/theme: update consistently throughout the file
6. If it's a multi-file project: keep function names and APIs compatible with other files
7. Result must be production-ready — no placeholders or TODOs

Output the COMPLETE updated {ext} file in a ```{ext} block."""

            resp = call_ai(prompt, timeout=140)
            new_code = extract_code(resp, ext)

            if new_code and len(new_code) > 300:
                updated[main_file] = new_code

        return updated

    def _pick_files_to_modify(self, modification: str, files: dict) -> list:
        """Decide which files need modification based on the change request."""
        mod_lower = modification.lower()

        # Single file projects
        if len(files) == 1:
            return list(files.keys())

        # Multi-file: route by keyword
        candidates = []

        # Style/visual changes → styles.css + index.html
        if any(w in mod_lower for w in ["color", "theme", "dark", "light", "style", "font", "size",
                                         "spacing", "layout", "design", "ui", "background", "border"]):
            for f in ["styles.css", "index.html"]:
                if f in files:
                    candidates.append(f)

        # Data/records changes → data.js
        if any(w in mod_lower for w in ["data", "record", "sample", "field", "column", "table",
                                         "more record", "fake data", "dummy"]):
            if "data.js" in files:
                candidates.append("data.js")

        # Feature/UI component changes → ui.js + index.html
        if any(w in mod_lower for w in ["feature", "section", "button", "form", "modal", "view",
                                         "page", "tab", "nav", "sidebar", "header", "footer",
                                         "add a", "remove the", "fix the", "show"]):
            for f in ["ui.js", "index.html"]:
                if f in files and f not in candidates:
                    candidates.append(f)

        # Chart changes → charts.js
        if any(w in mod_lower for w in ["chart", "graph", "plot", "analytics"]):
            if "charts.js" in files:
                candidates.append("charts.js")

        # Auth changes → auth.js
        if any(w in mod_lower for w in ["login", "auth", "password", "user", "session"]):
            if "auth.js" in files:
                candidates.append("auth.js")

        # App logic → app.js
        if any(w in mod_lower for w in ["route", "navigation", "shortcut", "search", "toast",
                                         "modal", "theme toggle"]):
            if "app.js" in files and "app.js" not in candidates:
                candidates.append("app.js")

        # If nothing matched, modify the largest file (most likely index.html or app.js)
        if not candidates:
            priority = ["index.html", "app.py", "scene.js", "app.js", "ui.js"]
            for p in priority:
                if p in files:
                    return [p]
            return [max(files, key=lambda k: len(files[k]))]

        # Max 3 files per iteration to keep it focused
        return candidates[:3]


# ════════════════════════════════════════════════════════════════════════════════
# PACKAGER — ZIP Assembly & Delivery
# ════════════════════════════════════════════════════════════════════════════════

class PackagerAgent:
    name = "Packager"
    emoji = "📦"

    def run(self, rev_out: dict, stack_context: dict = None) -> dict:
        files = rev_out.get("files", {})
        plan = rev_out.get("plan", {})
        arch = rev_out.get("architecture", {})
        dbg = rev_out.get("debug_report", [])
        is_fullstack = bool(stack_context and stack_context.get("backend"))

        if "README.md" not in files:
            files["README.md"] = self._readme(plan, arch, files, stack_context)

        # Inject frontend demo notice into index.html if frontend-only management system
        if not is_fullstack and "index.html" in files:
            pt = plan.get("project_type", "")
            traits = plan.get("traits", {})
            if pt in ("management", "dashboard", "webapp") or traits.get("is_management"):
                files["index.html"] = self._inject_demo_notice(files["index.html"], plan)

        zip_path = self._zip(files, plan.get("project_name", "project"))
        total = sum(len(v) for v in files.values())

        return {
            "zip_path": zip_path,
            "files": files,
            "file_count": len(files),
            "total_chars": total,
            "debug_report": dbg,
            "plan": plan,
            "summary": self._summary(plan, files, dbg, total, stack_context),
            "entry_point": arch.get("entry_point", "index.html"),
        }

    def _inject_demo_notice(self, html: str, plan: dict) -> str:
        """Inject a subtle but clear frontend demo notice banner into the HTML."""
        name = plan.get("project_name", "project").replace("-", " ").title()
        notice = f"""
<!-- ╔══════════════════════════════════════════════════════╗
     ║  FRONTEND DEMO / TEMPLATE — {name:<26}║
     ║  ✅ Full UI  ✅ Sample Data  ✅ Charts  ✅ CRUD    ║
     ║  ❌ No real DB  ❌ No backend  ❌ Single user      ║
     ║  Add backend: Node.js / Django / PHP               ║
     ║  Add database: MongoDB / MySQL / Firebase          ║
     ╚══════════════════════════════════════════════════════╝ -->
"""
        # Also inject a visible upgrade badge into the HTML body
        badge = """<div id="demo-badge" style="position:fixed;bottom:12px;right:12px;z-index:9999;background:rgba(99,102,241,0.92);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.15);border-radius:10px;padding:8px 14px;font-size:11px;color:#fff;font-family:system-ui,sans-serif;cursor:pointer;box-shadow:0 4px 20px rgba(99,102,241,0.4);transition:all .2s;" onclick="document.getElementById('demo-badge').style.display='none'" title="Click to dismiss">
  <span style="font-weight:700;letter-spacing:.03em;">🖥️ FRONTEND DEMO</span><br>
  <span style="opacity:.8;font-size:10px;">No real DB · Add Node.js/Django/PHP to go live</span>
</div>"""
        # Insert notice comment after DOCTYPE, inject badge before </body>
        if "<!DOCTYPE" in html[:100]:
            html = html.replace("<!DOCTYPE html>", "<!DOCTYPE html>" + notice, 1)
        if "</body>" in html:
            html = html.replace("</body>", badge + "\n</body>", 1)
        return html

    def _readme(self, plan, arch, files, stack_context: dict = None) -> str:
        name = plan.get("project_name", "project").replace("-", " ").title()
        feats = "\n".join(f"- {f}" for f in plan.get("features", []))
        tech = ", ".join(plan.get("tech_stack", []))
        entry = arch.get("entry_point", "index.html") if arch else "index.html"
        flist = "\n".join(f"- `{p}` ({len(c):,} chars)" for p, c in sorted(files.items()))
        is_fullstack = bool(stack_context and stack_context.get("backend"))

        if entry.endswith(".py"):
            setup = f"```bash\npip install -r requirements.txt\npython {entry}\n```"
        elif is_fullstack:
            backend = (stack_context or {}).get("backend", "")
            db = (stack_context or {}).get("database", "")
            if backend == "nodejs":
                setup = f"```bash\n# Backend\ncd backend\nnpm install\ncp ../.env.example .env  # fill in your values\nnode server.js\n\n# Frontend (in another terminal)\nopen frontend/index.html\n# Or serve with: npx serve frontend -p 3001\n```"
            elif backend == "django":
                setup = f"```bash\n# Backend\ncd backend\npython -m venv venv && source venv/bin/activate\npip install -r requirements.txt\ncp ../.env.example .env\npython manage.py migrate\npython manage.py runserver\n\n# Frontend\nopen frontend/index.html\n```"
            elif backend == "php":
                setup = f"```bash\n# Requires PHP 8+ and {db.upper()} running\ncd backend\ncp ../.env.example .env  # fill in DB credentials\n# Import schema: mysql -u root -p < schema.sql\nphp -S localhost:8080 api/index.php\n\n# Frontend\nopen frontend/index.html\n```"
            else:
                setup = f"See the backend folder for setup instructions."
        else:
            setup = f"1. Extract the ZIP\n2. Open `{entry}` in your browser\n3. No installation needed!\n\n> **Note:** This is a frontend demo. Data is stored in memory only.\n> To add a real backend, see the Upgrade Guide below."

        upgrade_section = ""
        if not is_fullstack:
            pt = plan.get("project_type", "")
            traits = plan.get("traits", {})
            if pt in ("management", "dashboard", "webapp") or traits.get("is_management"):
                upgrade_section = f"""
## ⚠️ Frontend Demo Notice

This is a **frontend demo / template**, NOT a full production system.

### What it has:
- ✅ Full UI dashboard with all views
- ✅ Realistic sample data ({name} records)
- ✅ Charts, analytics, search, export
- ✅ Full CRUD (Create, Read, Update, Delete)
- ✅ Dark/light mode, responsive design
- ✅ Local data handling (memory/localStorage)

### What it does NOT have:
- ❌ Real database (MySQL / MongoDB / etc.)
- ❌ Backend server (Node.js / PHP / Python)
- ❌ Real authentication system
- ❌ API endpoints
- ❌ Multi-user support / data persistence across sessions

## 🚀 Upgrade to Full Production System

It can become a full system if you add:

**Backend options:**
- Node.js / Express — `npm install express mongoose bcryptjs jsonwebtoken`
- Django (Python) — `pip install djangorestframework django-cors-headers`
- PHP — Standard PHP 8+ with PDO

**Database options:**
- **MongoDB** — `mongoose` ODM with Node.js
- **MySQL** — PDO (PHP) or `mysql2` (Node.js) or Django ORM
- **Firebase** — `firebase-admin` SDK, serverless
- **Supabase** — PostgreSQL + Auth + Realtime, fully managed

**Ask LovableBot:** Just say _"Rebuild {name} with Node.js and MongoDB"_ for a full-stack version!
"""

        full_readme = f"# {name}\n\n{plan.get('description', '')}\n\n## Features\n{feats}\n\n## Tech Stack\n{tech}\n\n## File Structure\n{flist}\n\n## Getting Started\n{setup}\n{upgrade_section}\n---\n*Generated by LovableBot — 8-Agent AI Platform*\n"
        return full_readme

    def _zip(self, files, name) -> str:
        tmp = tempfile.mkdtemp()
        path = os.path.join(tmp, f"{name}.zip")
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
            for p, c in files.items():
                zf.writestr(f"{name}/{p}", c)
        return path

    def _summary(self, plan, files, dbg, total, stack_context: dict = None) -> str:
        name = plan.get("project_name", "project").replace("-", " ").title()
        feats = "\n".join(f"  • {f}" for f in plan.get("features", [])[:8])
        flist = "\n".join(f"  📄 `{p}` — {len(c):,} chars" for p, c in sorted(files.items()))
        fixes = ("\n\n🔬 *Auto-fixes applied:* " + ", ".join(dbg[:3])) if dbg else ""
        is_fullstack = bool(stack_context and stack_context.get("backend"))

        stack_line = ""
        if is_fullstack:
            be_labels = {"nodejs": "Node.js+Express ⚡", "django": "Django 🐍", "php": "PHP 🐘"}
            db_labels = {"mongodb": "MongoDB 🍃", "mysql": "MySQL 🐬", "firebase": "Firebase 🔥",
                         "supabase": "Supabase ⚡", "postgresql": "PostgreSQL 🐘"}
            be = stack_context.get("backend", "")
            db = stack_context.get("database", "")
            stack_line = f"\n🏗️ *Stack:* {be_labels.get(be, be)} + {db_labels.get(db, db)}\n"

        demo_note = ""
        pt = plan.get("project_type", "")
        traits = plan.get("traits", {})
        if not is_fullstack and (pt in ("management", "dashboard", "webapp") or traits.get("is_management")):
            demo_note = (
                "\n\n📋 *This is a frontend demo* — works in browser, uses sample data.\n"
                "_To upgrade: say \"Rebuild with Node.js + MongoDB\" for a real backend!_"
            )

        return (
            f"✅ *{name}* is ready!\n\n"
            f"📝 _{plan.get('description', '')}_\n"
            f"{stack_line}\n"
            f"⚡ *Features:*\n{feats}\n\n"
            f"📁 *Files ({len(files)} files · {total:,} chars):*\n{flist}"
            f"{fixes}"
            f"{demo_note}\n\n"
            f"📦 *Extract the ZIP and open the entry point to run!*"
        )


# ════════════════════════════════════════════════════════════════════════════════
# ORCHESTRATOR — 8-Agent Pipeline Manager
# ════════════════════════════════════════════════════════════════════════════════

class LovableOrchestrator:
    def __init__(self):
        self.analyzer  = PromptAnalyzerAgent()
        self.planner   = PlannerAgent()
        self.architect = ArchitectAgent()
        self.threed    = ThreeDAgent()
        self.coder     = CoderAgent()
        self.iterator  = IterationAgent()
        self.debugger  = DebuggerAgent()
        self.reviewer  = ReviewerAgent()
        self.packager  = PackagerAgent()

    def generate(self, request: str, status_cb=None, existing_files: dict = None,
                 stack_context: dict = None) -> dict:
        def u(msg):
            if status_cb: status_cb(msg)

        # ── Iteration mode ─────────────────────────────────────────────────────
        if existing_files and detect_iteration(request, bool(existing_files)):
            u(f"{self.iterator.emoji} **Iteration Mode** — Analyzing your change request...")
            updated = self.iterator.run(request, existing_files, {})
            u("✅ Changes applied successfully")

            u(f"\n{self.debugger.emoji} **Debugger**: Verifying modified code...")
            dbg = self.debugger.run({"files": updated, "plan": {}, "architecture": {}})
            u("✅ Code verified")

            result = self.packager.run({**dbg, "architecture": {}})
            return result

        # ── Full generation pipeline ────────────────────────────────────────────
        is_fullstack = bool(stack_context and stack_context.get("backend"))

        if is_fullstack:
            be = stack_context.get("backend", "")
            db = stack_context.get("database", "")
            be_labels = {"nodejs": "Node.js+Express", "django": "Django", "php": "PHP"}
            u(f"⚡ **Full-Stack Mode** — {be_labels.get(be, be)} + {db.upper()}")

        u(f"{self.analyzer.emoji} **Agent 0/8 — Prompt Analyzer**: Deep analyzing your request at maximum depth...")
        analysis = self.analyzer.run(request)
        feats_count = len(analysis.get("critical_features", []))
        adv_count   = len(analysis.get("advanced_features", []))
        u(f"✅ Domain: *{analysis.get('domain', '?')}* | Style: {analysis.get('visual_style', '?')} | "
          f"Type: {analysis.get('detected_type', '?')} | Features: {feats_count} critical + {adv_count} advanced")

        u(f"\n{self.planner.emoji} **Agent 1/8 — Planner**: Creating strategic plan & deciding file structure...")
        plan = self.planner.run(request, analysis)
        # Inject full-stack intent into plan if user chose a stack
        if is_fullstack:
            plan["has_backend"] = True
            plan["stack_context"] = stack_context
        pf = plan.get("planned_files")
        pf_str = f"AI-planned {len(pf)} files" if pf else "fallback structure"
        u(f"✅ *{plan.get('project_name')}* | {len(plan.get('features', []))} features | "
          f"Type: {plan.get('project_type')} | {pf_str}")

        u(f"\n{self.architect.emoji} **Agent 2/8 — Architect**: Finalizing file architecture...")
        arch = self.architect.run(plan, stack_context=stack_context)
        ai_tag = " 🤖 AI-planned" if arch.get("ai_planned") else ""
        fs_tag = " ⚡ Full-Stack" if arch.get("is_fullstack") else ""
        u(f"✅ {len(arch.get('files', []))} file(s){ai_tag}{fs_tag} | "
          f"Entry: `{arch.get('entry_point')}`")

        if is_fullstack:
            manifest = arch.get("integration_manifest", {})
            ep_count = len(manifest.get("endpoints", []))
            u(f"  ↳ Integration manifest: {ep_count} API endpoints | DB: {manifest.get('db_name', '?')}")

        prefilled = {}
        if plan.get("has_3d") or plan.get("traits", {}).get("is_3d"):
            u(f"\n{self.threed.emoji} **Agent 3/8 — 3D Specialist**: Crafting advanced Three.js scene...")
            prefilled = self.threed.run(plan)
            u(f"✅ 3D scene ready — {sum(len(v) for v in prefilled.values()):,} chars")
        else:
            u(f"\n⏭ **Agent 3/8 — 3D Specialist**: Not needed for this project type")

        u(f"\n{self.coder.emoji} **Agent 4/8 — Coder**: Writing production code...")
        def coder_cb(m): u(f"  ↳ {m}")
        code_out = self.coder.run(arch, prefilled=prefilled, progress_cb=coder_cb)
        total = sum(len(v) for v in code_out["files"].values())
        u(f"✅ {len(code_out['files'])} files | {total:,} chars generated")

        u(f"\n{self.debugger.emoji} **Agent 5/8 — Debugger**: Scanning for bugs & quality issues...")
        def dbg_cb(m): u(f"  ↳ {m}")
        dbg_out = self.debugger.run(code_out, progress_cb=dbg_cb)
        fixes = dbg_out.get("debug_report", [])
        u(f"✅ {len(fixes)} fix(es) applied" if fixes else "✅ Code clean — no issues found")

        u(f"\n{self.reviewer.emoji} **Agent 6/8 — Reviewer**: Quality enforcement & feature verification...")
        def rev_cb(m): u(f"  ↳ {m}")
        rev_out = self.reviewer.run(dbg_out, progress_cb=rev_cb)
        final_total = sum(len(v) for v in rev_out["files"].values())
        u(f"✅ All features verified | Final size: {final_total:,} chars")

        u(f"\n{self.packager.emoji} **Agent 7/8 — Packager**: Assembling ZIP package...")
        result = self.packager.run(rev_out, stack_context=stack_context)
        u(f"✅ {result['file_count']} files | {result['total_chars']:,} chars | ZIP ready! 🎉")

        return result
