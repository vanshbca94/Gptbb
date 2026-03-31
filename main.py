"""
LovableBot — Telegram Bot
Ultimate AI Code Studio: 8 agents, full-stack generation, infinite complexity.
Everything AI-driven. Bot asks clarifying questions before building.
"""

import os
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from telegram.constants import ParseMode, ChatAction
from agents import LovableOrchestrator, detect_iteration, needs_backend, generate_clarifying_question

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
orchestrator = LovableOrchestrator()

# Per-user session
user_sessions: dict[int, dict] = {}

# ─── Static messages ───────────────────────────────────────────────────────────

WELCOME_MSG = """✨ *LovableBot* — Ultimate AI Code Studio

I generate complete, production-ready projects using *8 specialized AI agents*.

*What I build:*
🎨 Landing pages — Tailwind, animations, pricing, testimonials
📊 Dashboards — Chart.js, KPIs, sidebar, dark mode
🎮 Games — Snake, Tetris, platformers, canvas physics
🌐 3D Scenes — Three.js, orbit controls, particles
🛒 E-commerce — Product grid, cart, filters, checkout UI
💼 Management Systems — Student, Hospital, HR, Inventory, CRM
🐍 Python APIs — Flask REST, auth, CRUD, validation
⚡ Full-Stack Apps — Node.js/Django/PHP + MongoDB/MySQL/Firebase/Supabase

*What makes me different:*
🔄 *Iteration* — Say "make it dark" or "add login" after any build
🏗️ *Full-Stack* — Real backend + database, not just a demo
📋 *Upgrade Path* — Frontend demos include full backend upgrade guide
🤖 *AI Everything* — I ask what I need, decide what you need, and build it

Just describe what you want. I'll figure out the rest! 🚀"""

HELP_MSG = """🆘 *Help & Commands*

*/start* — Welcome & overview
*/help* — This menu
*/examples* — 30+ example prompts
*/last* — Show your last project's files
*/rebuild* — Rebuild your last project from scratch
*/status* — Current build status
*/cancel* — Stop current build
*/stack* — Change stack for next build (frontend/fullstack)

*How it works:*
1. Send a description of what you want
2. I may ask about backend/database preferences
3. 8 agents collaborate (3–8 min depending on complexity)
4. You get a complete ZIP with all project files
5. Say "change X" or "add Y" to iterate!

*Stack options when asked:*
• *Frontend Only* — HTML/CSS/JS demo, works instantly in browser
• *Node.js + Express* — Real backend API server
• *Django (Python)* — Python backend with REST framework
• *PHP* — Classic PHP backend
• *Databases* — MongoDB, MySQL, Firebase, Supabase

*Tip:* Frontend demos include a built-in upgrade guide showing exactly how to add any backend!"""

EXAMPLES_MSG = """💡 *Example Prompts* — copy and send!

*🎨 Landing Pages*
• A SaaS landing for an AI writing tool called "Quill" — hero, features, 3-tier pricing
• A portfolio for a UX designer with case studies, testimonials, and contact form

*📊 Dashboards*
• An analytics dashboard for an e-commerce store with revenue charts and order tables
• A crypto portfolio tracker with price charts and allocation pie chart

*🎮 Games*
• A snake game with neon visuals, power-ups, and high score leaderboard
• A Tetris clone with modern gradient pieces and level progression

*🌐 3D Scenes*
• A 3D solar system with textured planets, asteroid belt, and comet
• A 3D particle galaxy where particles form a spiral on mouse hover

*💼 Management Systems*
• A student management system with grades, attendance, and GPA analytics
• A hospital management system with patient records and appointment booking
• An inventory system with stock tracking, suppliers, and purchase orders
• An HR system with employees, payroll, and performance reviews
• A CRM with pipeline kanban, deal tracking, and sales analytics

*🐍 Python APIs*
• A Flask REST API for a notes app with user auth, tags, and search
• A FastAPI task manager with priority, due dates, and categories

*⚡ Full-Stack (choose stack when prompted)*
• A full-stack student portal with Node.js + MongoDB
• A hotel booking system with Django + PostgreSQL
• A real estate platform with PHP + MySQL

Pick one or write your own! ✍️"""

ITERATION_HINTS = [
    "💡 *Tip:* You can modify this project anytime!",
    "_Say: \"make it dark mode\", \"add a contact form\", \"change color to green\", \"add login page\"_"
]

# ─── Session helpers ───────────────────────────────────────────────────────────

def get_session(user_id: int) -> dict:
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "building": False,
            "cancelled": False,
            "step": "",
            "last_files": None,
            "last_plan": None,
            "last_project_name": "",
            # Stack selection state
            "pending_request": None,
            "awaiting_stack": False,
            "awaiting_backend": False,
            "awaiting_db": False,
            "chosen_backend": None,
            "chosen_db": None,
            "stack_context": None,
            # Clarifying questions state
            "awaiting_clarification": False,
            "clarification_original": None,
            "clarification_question": "",
        }
    return user_sessions[user_id]


def is_building(user_id: int) -> bool:
    return user_sessions.get(user_id, {}).get("building", False)


def clear_stack_state(sess: dict):
    sess["pending_request"] = None
    sess["awaiting_stack"] = False
    sess["awaiting_backend"] = False
    sess["awaiting_db"] = False
    sess["chosen_backend"] = None
    sess["chosen_db"] = None
    sess["stack_context"] = None
    sess["awaiting_clarification"] = False
    sess["clarification_original"] = None
    sess["clarification_question"] = ""


# ─── Clarifying questions helpers ──────────────────────────────────────────────

_OBVIOUS_TYPES = [
    "game", "snake", "tetris", "chess", "pacman", "platformer", "breakout", "pong",
    "landing page", "landing-page", "homepage", "hero section", "saas page",
    "dashboard", "analytics dashboard", "chart", "kpi", "metrics",
    "ecommerce", "e-commerce", "shop", "store", "cart",
    "3d", "three.js", "sphere", "orbit", "webgl",
    "flask api", "rest api", "python api", "fastapi",
    "portfolio", "resume", "cv site",
    "student management", "hospital management", "inventory management",
    "hr system", "crm", "hotel management", "library management",
    "restaurant management", "real estate",
]


def _needs_clarification(request: str) -> bool:
    """Return True if the request is short or vague enough to benefit from 1 clarifying question."""
    r = request.lower().strip()
    if len(r.split()) > 22:
        return False
    return not any(o in r for o in _OBVIOUS_TYPES)


# ─── Stack selection keyboards ─────────────────────────────────────────────────

def stack_type_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🖥️ Frontend Only (Demo/Template)", callback_data="stack_frontend")],
        [InlineKeyboardButton("⚡ Node.js + Express", callback_data="backend_nodejs"),
         InlineKeyboardButton("🐍 Django (Python)", callback_data="backend_django")],
        [InlineKeyboardButton("🐘 PHP", callback_data="backend_php")],
        [InlineKeyboardButton("❌ Cancel", callback_data="stack_cancel")],
    ])


def database_keyboard(backend: str):
    rows = [
        [InlineKeyboardButton("🍃 MongoDB", callback_data="db_mongodb"),
         InlineKeyboardButton("🐬 MySQL", callback_data="db_mysql")],
        [InlineKeyboardButton("🔥 Firebase", callback_data="db_firebase"),
         InlineKeyboardButton("⚡ Supabase", callback_data="db_supabase")],
        [InlineKeyboardButton("❌ Cancel", callback_data="stack_cancel")],
    ]
    if backend == "django":
        rows.insert(0, [InlineKeyboardButton("🐘 PostgreSQL", callback_data="db_postgresql")])
    return InlineKeyboardMarkup(rows)


BACKEND_LABELS = {
    "nodejs": "Node.js + Express ⚡",
    "django": "Django (Python) 🐍",
    "php": "PHP 🐘",
}

DB_LABELS = {
    "mongodb": "MongoDB 🍃",
    "mysql": "MySQL 🐬",
    "firebase": "Firebase 🔥",
    "supabase": "Supabase ⚡",
    "postgresql": "PostgreSQL 🐘",
}


# ─── Commands ──────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💡 Examples", callback_data="examples"),
         InlineKeyboardButton("🆘 Help", callback_data="help")],
        [InlineKeyboardButton("🚀 Build Something!", callback_data="build_prompt")],
        [InlineKeyboardButton("⚡ Full-Stack Build", callback_data="fullstack_prompt")],
    ]
    await update.message.reply_text(
        WELCOME_MSG, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_MSG, parse_mode=ParseMode.MARKDOWN)


async def examples_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(EXAMPLES_MSG, parse_mode=ParseMode.MARKDOWN)


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    sess = get_session(uid)
    if sess["building"]:
        await update.message.reply_text(
            f"⏳ *Build running...*\n\n`{sess.get('step', 'working...')}`",
            parse_mode=ParseMode.MARKDOWN
        )
    elif sess.get("awaiting_clarification"):
        q = sess.get("clarification_question", "")
        await update.message.reply_text(
            f"⏸️ *Waiting for your answer*\n\n_{q}_\n\nJust reply in the chat, or /cancel to abort.",
            parse_mode=ParseMode.MARKDOWN
        )
    elif sess.get("awaiting_stack") or sess.get("awaiting_backend") or sess.get("awaiting_db"):
        await update.message.reply_text(
            "⏸️ *Waiting for your stack choice*\n\nPlease select an option from the keyboard above, or /cancel to abort.",
            parse_mode=ParseMode.MARKDOWN
        )
    elif sess["last_project_name"]:
        sc = sess.get("stack_context") or {}
        stack_info = ""
        if sc.get("backend"):
            stack_info = f"\n🏗️ Stack: {BACKEND_LABELS.get(sc['backend'], sc['backend'])} + {DB_LABELS.get(sc.get('db', ''), 'no DB')}"
        await update.message.reply_text(
            f"✅ Last build: *{sess['last_project_name']}*{stack_info}\n"
            f"💬 Send a modification to iterate, or describe a new project!",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text("💤 No active build. Send a project idea to get started!")


async def last_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    sess = get_session(uid)
    files = sess.get("last_files")
    if not files:
        await update.message.reply_text("❌ No previous project found. Build something first!")
        return
    name = sess.get("last_project_name", "project")
    lines = [f"📁 *Last project: {name}*\n"]
    for fname, content in sorted(files.items()):
        lines.append(f"• `{fname}` — {len(content):,} chars")
    sc = sess.get("stack_context") or {}
    if sc.get("backend"):
        lines.append(f"\n🏗️ *Stack:* {BACKEND_LABELS.get(sc['backend'], sc['backend'])} + {DB_LABELS.get(sc.get('db', ''), 'no DB')}")
    await update.message.reply_text(
        "\n".join(lines) + "\n\n💬 _Send a change request to modify it!_",
        parse_mode=ParseMode.MARKDOWN
    )


async def stack_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_building(uid):
        await update.message.reply_text("⏳ Building now! Use /cancel first to change stack.")
        return
    await update.message.reply_text(
        "🏗️ *Stack Preference*\n\nThis will apply to your next build.\n"
        "Choose whether you want a frontend-only project or a full-stack with a real backend:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=stack_type_keyboard()
    )


async def rebuild_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    sess = get_session(uid)
    plan = sess.get("last_plan")
    if not plan:
        await update.message.reply_text("❌ No previous project to rebuild. Send a new project idea!")
        return
    if is_building(uid):
        await update.message.reply_text("⏳ Already building! Use /cancel first.")
        return
    original_request = plan.get("user_request", "")
    if not original_request:
        await update.message.reply_text("❌ Can't find the original request. Try describing your project again.")
        return
    sess["last_files"] = None
    sc = sess.get("stack_context")
    await update.message.reply_text(
        f"🔄 *Rebuilding:* _{original_request[:120]}_\n\nStarting fresh build...",
        parse_mode=ParseMode.MARKDOWN
    )
    await _run_build(update, context, original_request, uid, stack_context=sc)


async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    sess = get_session(uid)
    if sess["building"]:
        sess["cancelled"] = True
        sess["building"] = False
        clear_stack_state(sess)
        await update.message.reply_text("❌ Build cancelled. Send a new idea anytime!")
    elif sess.get("awaiting_clarification"):
        clear_stack_state(sess)
        await update.message.reply_text("❌ Cancelled. Send a new project idea anytime!")
    elif sess.get("awaiting_stack") or sess.get("awaiting_backend") or sess.get("awaiting_db"):
        clear_stack_state(sess)
        await update.message.reply_text("❌ Stack selection cancelled. Send a new idea anytime!")
    else:
        await update.message.reply_text("Nothing to cancel. Ready when you are! 🚀")


# ─── Button callback handler ───────────────────────────────────────────────────

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    sess = get_session(uid)
    data = query.data

    # ── Static informational buttons ──────────────────────────────────────────
    if data == "examples":
        await query.message.reply_text(EXAMPLES_MSG, parse_mode=ParseMode.MARKDOWN)
        return
    if data == "help":
        await query.message.reply_text(HELP_MSG, parse_mode=ParseMode.MARKDOWN)
        return
    if data == "build_prompt":
        await query.message.reply_text(
            "✍️ Describe what you want to build!\n\n"
            "_Examples:_\n"
            "• \"A student management system with grades and attendance\"\n"
            "• \"A SaaS landing page for a tool called Quill\"\n"
            "• \"A snake game with neon visuals and power-ups\"\n"
            "• \"A 3D solar system with orbiting planets\"",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "fullstack_prompt":
        await query.message.reply_text(
            "⚡ *Full-Stack Build Mode*\n\n"
            "Describe your project and I'll ask you which backend and database you want.\n\n"
            "_Examples:_\n"
            "• \"A student management system\"\n"
            "• \"A hospital patient portal\"\n"
            "• \"An e-commerce store with real cart and orders\"",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "rebuild":
        await rebuild_cmd(update, context)
        return

    # ── Clarify: build immediately without answering ───────────────────────────
    if data == "clarify_skip":
        pending = sess.get("clarification_original")
        clear_stack_state(sess)
        if not pending:
            await query.message.reply_text("❌ No pending request. Describe a project first!")
            return
        try:
            await query.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        await query.message.reply_text(
            f"🚀 *Building right away!*\n\n"
            f"📋 _{pending[:150]}_\n\n"
            f"⚙️ 8 agents: Analyzer → Planner → Architect → Coder → Debugger → Reviewer → Packager\n\n"
            f"⏳ _This takes 3–8 minutes. I'll update you as we go..._",
            parse_mode=ParseMode.MARKDOWN
        )
        await _run_build(query, context, pending, uid, stack_context=None)
        return

    # ── Stack cancel ───────────────────────────────────────────────────────────
    if data == "stack_cancel":
        clear_stack_state(sess)
        try:
            await query.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        await query.message.reply_text("❌ Cancelled. Send a new project idea whenever you're ready!")
        return

    # ── Stack type selection: frontend only ────────────────────────────────────
    if data == "stack_frontend":
        pending = sess.get("pending_request")
        clear_stack_state(sess)
        if not pending:
            await query.message.reply_text("❌ No pending request. Describe a project first!")
            return
        try:
            await query.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        await query.message.reply_text(
            f"🖥️ *Frontend Only* — Building your demo/template!\n\n"
            f"📋 _{pending[:120]}_\n\n"
            f"_Includes upgrade guide for adding a real backend later._\n\n"
            f"⏳ Starting build with 8 AI agents...",
            parse_mode=ParseMode.MARKDOWN
        )
        await _run_build(query, context, pending, uid, stack_context={"backend": None})
        return

    # ── Backend selection ──────────────────────────────────────────────────────
    if data.startswith("backend_"):
        backend = data.replace("backend_", "")
        sess["chosen_backend"] = backend
        sess["awaiting_backend"] = False
        sess["awaiting_db"] = True
        try:
            await query.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        await query.message.reply_text(
            f"✅ Backend: *{BACKEND_LABELS.get(backend, backend)}*\n\n"
            f"Now choose your *database*:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=database_keyboard(backend)
        )
        return

    # ── Database selection ─────────────────────────────────────────────────────
    if data.startswith("db_"):
        db = data.replace("db_", "")
        backend = sess.get("chosen_backend")
        pending = sess.get("pending_request")

        if not backend or not pending:
            clear_stack_state(sess)
            await query.message.reply_text("❌ Session expired. Please send your project description again.")
            return

        stack_ctx = {"backend": backend, "database": db}
        clear_stack_state(sess)
        sess["stack_context"] = stack_ctx

        try:
            await query.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass

        be_label = BACKEND_LABELS.get(backend, backend)
        db_label = DB_LABELS.get(db, db)

        await query.message.reply_text(
            f"⚡ *Full-Stack Build!*\n\n"
            f"📋 _{pending[:120]}_\n\n"
            f"🏗️ *Stack:* {be_label} + {db_label}\n\n"
            f"⚙️ 8 agents: Analyzer → Planner → Architect → 3D? → Coder → Debugger → Reviewer → Packager\n\n"
            f"⏳ _Full-stack builds take 5–10 minutes. I'll update you as we go..._",
            parse_mode=ParseMode.MARKDOWN
        )
        await _run_build(query, context, pending, uid, stack_context=stack_ctx)
        return


# ─── Main message handler ──────────────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    username = update.effective_user.first_name or "there"
    request = update.message.text.strip()
    if not request:
        return

    sess = get_session(uid)

    # ── Handle clarification answers (highest priority, even during builds) ───
    if sess.get("awaiting_clarification") and not is_building(uid):
        original = sess.get("clarification_original", "")
        question = sess.get("clarification_question", "")
        answer = request
        combined = f"{original}. Additional details: {answer}"
        sess["awaiting_clarification"] = False
        sess["clarification_original"] = None
        sess["clarification_question"] = ""
        await update.message.reply_text(
            f"✅ *Got it! Building with your context:*\n\n"
            f"📋 _{combined[:200]}_\n\n"
            f"⚙️ 8 agents: Analyzer → Planner → Architect → Coder → Debugger → Reviewer → Packager\n\n"
            f"⏳ _This takes 3–8 minutes. I'll update you as we go..._",
            parse_mode=ParseMode.MARKDOWN
        )
        await _run_build(update, context, combined, uid, stack_context=None)
        return

    if is_building(uid):
        await update.message.reply_text(
            "⏳ I'm still building your project! Please wait or /cancel to stop.",
        )
        return

    # ── If still waiting for stack choice, re-show the keyboard ───────────────
    if sess.get("awaiting_stack") or sess.get("awaiting_backend") or sess.get("awaiting_db"):
        await update.message.reply_text(
            "⏸️ Please complete your stack selection using the buttons above, or /cancel to start over.",
        )
        return

    existing_files = sess.get("last_files")
    is_iter = bool(existing_files) and detect_iteration(request, bool(existing_files))

    if is_iter:
        proj = sess.get("last_project_name", "your project")
        await update.message.reply_text(
            f"🔄 *Iteration mode* — modifying *{proj}*\n\n"
            f"Change: _{request}_\n\n"
            f"⏳ Applying changes...",
            parse_mode=ParseMode.MARKDOWN
        )
        await _run_build(update, context, request, uid, stack_context=sess.get("stack_context"))
        return

    # ── Detect if we need to ask about backend/stack ───────────────────────────
    if needs_backend(request) and not is_iter:
        sess["pending_request"] = request
        sess["awaiting_stack"] = True
        await update.message.reply_text(
            f"🤔 *Stack Choice Needed*\n\n"
            f"Your request sounds like it could benefit from a *real backend*.\n\n"
            f"📋 _{request[:120]}_\n\n"
            f"How would you like this built?",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=stack_type_keyboard()
        )
        return

    # ── Ask a clarifying question for short/vague requests ────────────────────
    if _needs_clarification(request) and not is_iter:
        loop = asyncio.get_event_loop()
        question = await loop.run_in_executor(None, lambda: generate_clarifying_question(request))
        if question:
            sess["awaiting_clarification"] = True
            sess["clarification_original"] = request
            sess["clarification_question"] = question
            keyboard = [
                [InlineKeyboardButton("🚀 Build Without Answering", callback_data="clarify_skip")],
                [InlineKeyboardButton("❌ Cancel", callback_data="stack_cancel")],
            ]
            await update.message.reply_text(
                f"🤔 *Quick question before I build:*\n\n"
                f"_{question}_\n\n"
                f"_Just reply with your answer, or tap 'Build Without Answering' to proceed immediately._",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

    # ── Regular build ──────────────────────────────────────────────────────────
    await update.message.reply_text(
        f"🚀 *Building your project, {username}!*\n\n"
        f"📋 _{request[:150]}{'...' if len(request) > 150 else ''}_\n\n"
        f"⚙️ 8 agents: Analyzer → Planner → Architect → 3D? → Coder → Debugger → Reviewer → Packager\n\n"
        f"⏳ _This takes 3–8 minutes. I'll update you as we go..._",
        parse_mode=ParseMode.MARKDOWN
    )
    await _run_build(update, context, request, uid, stack_context=None)


# ─── Core build runner ─────────────────────────────────────────────────────────

async def _run_build(update, context: ContextTypes.DEFAULT_TYPE, request: str, uid: int,
                     stack_context: dict = None):
    sess = get_session(uid)
    sess["building"] = True
    sess["cancelled"] = False

    existing_files = sess.get("last_files")
    is_iter = bool(existing_files) and detect_iteration(request, bool(existing_files))

    log_lines = []
    status_msg = None

    async def push_status(text: str):
        nonlocal status_msg
        if sess.get("cancelled"):
            return
        sess["step"] = text
        log_lines.append(text)
        display = "\n".join(log_lines[-14:])
        full = (
            f"🏭 *Build Log*\n\n{display}\n\n"
            f"⏳ _{'Applying changes' if is_iter else 'Building your project'}..._"
        )
        try:
            msg_obj = update.message if hasattr(update, "message") else update
            if status_msg is None:
                status_msg = await msg_obj.reply_text(full, parse_mode=ParseMode.MARKDOWN)
            else:
                await status_msg.edit_text(full, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            pass

    await push_status("🔄 Initializing...")
    await asyncio.sleep(0.3)

    loop = asyncio.get_event_loop()
    result = None
    error = None
    sync_updates_queue = []

    def run_sync():
        nonlocal result, error
        try:
            def cb(msg):
                sync_updates_queue.append(msg)
            result = orchestrator.generate(
                request,
                status_cb=cb,
                existing_files=existing_files if is_iter else None,
                stack_context=stack_context,
            )
        except Exception as e:
            error = str(e)
            logger.exception(f"Build error for user {uid}")

    task = loop.run_in_executor(None, run_sync)

    while not task.done():
        if sess.get("cancelled"):
            break
        if sync_updates_queue:
            msgs = sync_updates_queue[:]
            sync_updates_queue.clear()
            for m in msgs:
                await push_status(m)
        await asyncio.sleep(2.5)
        try:
            msg_obj = update.message if hasattr(update, "message") else update
            await msg_obj.reply_chat_action(ChatAction.TYPING)
        except Exception:
            pass

    await task

    for m in sync_updates_queue:
        await push_status(m)

    if sess.get("cancelled"):
        sess["building"] = False
        return

    sess["building"] = False

    if error:
        await _reply(update, f"❌ *Build failed*\n\n`{error[:300]}`\n\nTry again or rephrase your request.",
                     parse_mode=ParseMode.MARKDOWN)
        return

    if not result:
        await _reply(update, "❌ Something went wrong. Please try again.")
        return

    sess["last_files"] = result.get("files", {})
    sess["last_plan"] = result.get("plan", {})
    sess["last_project_name"] = result.get("plan", {}).get("project_name", "project")
    if stack_context and stack_context.get("backend"):
        sess["stack_context"] = stack_context

    await push_status("✅ All done! Sending your project...")
    await _deliver(update, result, is_iter, stack_context)


async def _reply(update, text, **kwargs):
    try:
        if hasattr(update, "message") and update.message:
            await update.message.reply_text(text, **kwargs)
        elif hasattr(update, "reply_text"):
            await update.reply_text(text, **kwargs)
    except Exception as e:
        logger.error(f"Reply failed: {e}")


# ─── Result delivery ───────────────────────────────────────────────────────────

async def _deliver(update, result: dict, is_iter: bool, stack_context: dict = None):
    zip_path = result.get("zip_path")
    summary = result.get("summary", "")
    files = result.get("files", {})
    plan = result.get("plan", {})
    project_name = plan.get("project_name", "project")
    entry_point = result.get("entry_point", "index.html")
    is_fullstack = bool(stack_context and stack_context.get("backend"))

    # 1. Send ZIP file
    if zip_path and os.path.exists(zip_path):
        try:
            with open(zip_path, "rb") as zf:
                caption = (
                    f"📦 *{'Update' if is_iter else 'Project'}: {project_name}*\n"
                    f"{result.get('file_count', 0)} files · {result.get('total_chars', 0):,} chars"
                )
                if is_fullstack:
                    be = stack_context.get("backend", "")
                    db = stack_context.get("database", "")
                    caption += f"\n🏗️ {BACKEND_LABELS.get(be, be)} + {DB_LABELS.get(db, db)}"
                msg_obj = update.message if hasattr(update, "message") else update
                await msg_obj.reply_document(
                    document=zf,
                    filename=f"{project_name}.zip",
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN
                )
        except Exception as e:
            logger.error(f"ZIP send failed: {e}")

    # 2. Summary message
    if summary:
        try:
            await _reply(update, summary, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            await _reply(update, summary[:4000])

    # 3. Send main file preview (first 2500 chars)
    main_content = files.get(entry_point) or files.get("index.html") or files.get("app.py")
    if main_content:
        ext = entry_point.split(".")[-1]
        lang = {"html": "html", "py": "python", "js": "javascript"}.get(ext, "")
        preview = main_content[:2500]
        if len(main_content) > 2500:
            preview += f"\n\n... ({len(main_content) - 2500:,} more chars in ZIP)"
        try:
            await _reply(update,
                f"👁 *Preview — `{entry_point}`*\n\n```{lang}\n{preview}\n```",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception:
            pass

    # 4. Upgrade hint for frontend-only builds
    if not is_fullstack and not is_iter and _is_management_type(plan):
        upgrade_msg = _build_upgrade_hint(project_name)
        try:
            await _reply(update, upgrade_msg, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            pass

    # 5. Action buttons
    keyboard = [
        [InlineKeyboardButton("🔄 Build Another", callback_data="build_prompt"),
         InlineKeyboardButton("💡 Examples", callback_data="examples")],
        [InlineKeyboardButton("⚡ Build Full-Stack Version", callback_data="fullstack_prompt")],
    ]
    hint = "\n".join(ITERATION_HINTS)
    await _reply(update,
        f"🎉 *Done!* {'Changes applied!' if is_iter else 'Your project is ready!'}\n\n{hint}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def _is_management_type(plan: dict) -> bool:
    pt = plan.get("project_type", "")
    return pt in ("management", "dashboard", "webapp") or plan.get("traits", {}).get("is_management")


def _build_upgrade_hint(project_name: str) -> str:
    name = project_name.replace("-", " ").title()
    return (
        f"ℹ️ *About this build — {name}*\n\n"
        f"This is a *frontend demo/template* that:\n"
        f"✅ Has full UI dashboard & all views\n"
        f"✅ Has realistic sample data & full CRUD\n"
        f"✅ Has charts, analytics, search, export\n"
        f"✅ Works instantly in any browser (no server needed)\n\n"
        f"❌ Does not have a real database\n"
        f"❌ Does not have a real backend server\n"
        f"❌ Does not support multiple users\n\n"
        f"*To make it a full production system, say:*\n"
        f"_\"Rebuild {name} with Node.js and MongoDB\"_\n"
        f"_\"Rebuild {name} with Django and PostgreSQL\"_\n"
        f"_\"Add a PHP + MySQL backend to this\"_\n\n"
        f"Or tap *⚡ Build Full-Stack Version* below!"
    )


# ─── Error handler ─────────────────────────────────────────────────────────────

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}", exc_info=context.error)


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("examples", examples_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("cancel", cancel_cmd))
    app.add_handler(CommandHandler("last", last_cmd))
    app.add_handler(CommandHandler("rebuild", rebuild_cmd))
    app.add_handler(CommandHandler("stack", stack_cmd))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    logger.info("LovableBot started — Ultimate 8-Agent AI Code Studio with full-stack support")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
