"""
LovableBot — Telegram Bot
Lovable-parity: generates complete, production-ready projects
with iteration/modification support and smart session memory.
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
from agents import LovableOrchestrator, detect_iteration

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
orchestrator = LovableOrchestrator()

# Per-user session: stores build state + last generated files for iteration
user_sessions: dict[int, dict] = {}

# ─── Static messages ──────────────────────────────────────────────────────────

WELCOME_MSG = """✨ *LovableBot* — AI Code Studio

I generate complete, production-ready projects using *7 specialized AI agents* — like Lovable.dev, but right here in Telegram.

*What I build:*
🎨 Landing pages — Tailwind, animations, pricing, testimonials
📊 Dashboards — Chart.js, KPIs, sidebar, dark mode
🎮 Games — Snake, Tetris, platformers, canvas physics
🌐 3D Scenes — Three.js, orbit controls, lighting, particles
🛒 E-commerce — Product grid, cart, filters, checkout UI
🐍 Python APIs — Flask REST, auth, CRUD, validation
💼 Web Apps — Todo, notes, timers, tools, editors

*Special powers:*
🔄 *Iteration* — After a build, say "make it dark" or "add login" to modify it
⚡ *Smart detection* — I auto-pick the right tech stack
🎨 *Tailwind + Alpine.js* — Every UI looks professional

Just describe what you want. I'll start building! 🚀"""

HELP_MSG = """🆘 *Help & Commands*

*/start* — Welcome
*/help* — This menu  
*/examples* — 20+ example prompts
*/last* — Show your last project's files
*/rebuild* — Rebuild your last project from scratch
*/status* — Current build status
*/cancel* — Stop current build

*How it works:*
1. Send a description of what you want
2. 7 agents collaborate (3–6 min)
3. You get a ZIP file with your project
4. Say "change X" or "add Y" to iterate!

*Best prompts include:*
• The app name or branding
• Key features you want
• Style preferences (dark, minimal, colorful)
• Target audience

*Pro tip:* After a build, you can say things like:
_"Make the hero section taller"_
_"Change the color scheme to green"_
_"Add a contact form to the landing page"_
_"Fix the mobile navbar"_"""

EXAMPLES_MSG = """💡 *Example Prompts* — copy and send!

*🎨 Landing Pages*
• A SaaS landing for a AI writing tool called "Quill" — hero, features, 3-tier pricing
• A portfolio for a UX designer with case studies, testimonials, and contact form
• A startup homepage for a crypto wallet app with dark theme

*📊 Dashboards*
• An analytics dashboard for an e-commerce store with revenue charts and order tables
• A crypto portfolio tracker with price charts and allocation pie chart
• A social media analytics dashboard with engagement metrics

*🎮 Games*
• A snake game with neon visuals, power-ups, and high score leaderboard
• A Tetris clone with modern gradient pieces and level progression
• A memory card matching game with emoji cards and timer

*🌐 3D Scenes*
• A 3D solar system with textured planets, asteroid belt, and comet
• A 3D low-poly island with trees, ocean waves, and floating islands
• A 3D particle galaxy where particles form a spiral on mouse hover

*🛒 E-commerce*
• A sneaker store with product grid, size picker, cart drawer, and wishlist
• A digital marketplace for icons with search, category filters, and preview modal

*🐍 Python APIs*
• A Flask REST API for a notes app with user auth, tags, and search
• A FastAPI task manager with priority, due dates, and categories

Pick one or write your own! ✍️"""

ITERATION_HINTS = [
    "💡 *Tip:* You can modify this project by describing what to change!",
    "_Examples: \"make it dark mode\", \"add a contact form\", \"change color to green\"_"
]


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_session(user_id: int) -> dict:
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "building": False,
            "cancelled": False,
            "step": "",
            "last_files": None,       # dict of {filename: content}
            "last_plan": None,        # plan dict from last build
            "last_project_name": "",
        }
    return user_sessions[user_id]


def is_building(user_id: int) -> bool:
    return user_sessions.get(user_id, {}).get("building", False)


# ─── Commands ─────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💡 Examples", callback_data="examples"),
         InlineKeyboardButton("🆘 Help", callback_data="help")],
        [InlineKeyboardButton("🚀 Build Something!", callback_data="build_prompt")]
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
            f"⏳ *Build running...*\n\n`{sess.get('step','working...')}`",
            parse_mode=ParseMode.MARKDOWN
        )
    elif sess["last_project_name"]:
        await update.message.reply_text(
            f"✅ Last build: *{sess['last_project_name']}*\n"
            f"💬 Send a modification to iterate on it, or describe a new project!",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(
            "💤 No active build. Send a project idea to get started!"
        )


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
    await update.message.reply_text(
        "\n".join(lines) + "\n\n💬 _Send a change request to modify it!_",
        parse_mode=ParseMode.MARKDOWN
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
    # Clear existing files to force a fresh build
    sess["last_files"] = None
    await update.message.reply_text(
        f"🔄 *Rebuilding:* _{original_request[:120]}_\n\nStarting fresh build...",
        parse_mode=ParseMode.MARKDOWN
    )
    # Trigger a new build with the original request
    fake_update = update
    context.user_data["rebuild_request"] = original_request
    await _run_build(fake_update, context, original_request, uid)


async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    sess = get_session(uid)
    if sess["building"]:
        sess["cancelled"] = True
        sess["building"] = False
        await update.message.reply_text("❌ Build cancelled. Send a new idea anytime!")
    else:
        await update.message.reply_text("Nothing to cancel. Ready when you are! 🚀")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "examples":
        await query.message.reply_text(EXAMPLES_MSG, parse_mode=ParseMode.MARKDOWN)
    elif query.data == "help":
        await query.message.reply_text(HELP_MSG, parse_mode=ParseMode.MARKDOWN)
    elif query.data == "build_prompt":
        await query.message.reply_text(
            "✍️ Describe what you want to build and I'll start right away!\n\n"
            "_Examples:_\n"
            "• \"A SaaS landing page for a tool called Quill\"\n"
            "• \"A snake game with neon visuals and power-ups\"\n"
            "• \"A 3D solar system with orbiting planets\"",
            parse_mode=ParseMode.MARKDOWN
        )
    elif query.data == "rebuild":
        await rebuild_cmd(update, context)


# ─── Main message handler ─────────────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    username = update.effective_user.first_name or "there"
    request = update.message.text.strip()
    if not request:
        return

    if is_building(uid):
        await update.message.reply_text(
            "⏳ I'm still building your project! Please wait or /cancel to stop.",
        )
        return

    sess = get_session(uid)
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
    else:
        await update.message.reply_text(
            f"🚀 *Building your project, {username}!*\n\n"
            f"📋 _{request[:150]}{'...' if len(request) > 150 else ''}_\n\n"
            f"⚙️ 7 agents: Planner → Architect → 3D Specialist → Coder → Debugger → Reviewer → Packager\n\n"
            f"⏳ _This takes 3–6 minutes. I'll update you as we go..._",
            parse_mode=ParseMode.MARKDOWN
        )

    await _run_build(update, context, request, uid)


async def _run_build(update: Update, context: ContextTypes.DEFAULT_TYPE, request: str, uid: int):
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
            if status_msg is None:
                status_msg = await update.message.reply_text(full, parse_mode=ParseMode.MARKDOWN)
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
                existing_files=existing_files if is_iter else None
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
            await update.message.reply_chat_action(ChatAction.TYPING)
        except Exception:
            pass

    await task

    # Flush remaining updates
    for m in sync_updates_queue:
        await push_status(m)

    if sess.get("cancelled"):
        sess["building"] = False
        return

    sess["building"] = False

    if error:
        await update.message.reply_text(
            f"❌ *Build failed*\n\n`{error[:300]}`\n\nTry again or rephrase your request.",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if not result:
        await update.message.reply_text("❌ Something went wrong. Please try again.")
        return

    # ── Store results in session ──────────────────────────────────────
    sess["last_files"] = result.get("files", {})
    sess["last_plan"] = result.get("plan", {})
    sess["last_project_name"] = result.get("plan", {}).get("project_name", "project")

    await push_status("✅ All done! Sending your project...")

    # ── Deliver results ───────────────────────────────────────────────
    await _deliver(update, result, is_iter)


async def _deliver(update: Update, result: dict, is_iter: bool):
    zip_path = result.get("zip_path")
    summary = result.get("summary", "")
    files = result.get("files", {})
    plan = result.get("plan", {})
    project_name = plan.get("project_name", "project")
    entry_point = result.get("entry_point", "index.html")

    # 1. Send ZIP file
    if zip_path and os.path.exists(zip_path):
        try:
            with open(zip_path, "rb") as zf:
                caption = (
                    f"📦 *{'Update' if is_iter else 'Project'}: {project_name}*\n"
                    f"{result.get('file_count', 0)} files · {result.get('total_chars', 0):,} chars"
                )
                await update.message.reply_document(
                    document=zf,
                    filename=f"{project_name}.zip",
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN
                )
        except Exception as e:
            logger.error(f"ZIP send failed: {e}")
            await update.message.reply_text("⚠️ ZIP send failed. Check if files were generated.")

    # 2. Summary message
    if summary:
        try:
            await update.message.reply_text(summary, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            await update.message.reply_text(summary[:4000])

    # 3. Send main file as inline preview (first 3000 chars as code)
    main_content = files.get(entry_point) or files.get("index.html") or files.get("app.py")
    if main_content:
        ext = entry_point.split(".")[-1]
        lang = {"html": "html", "py": "python", "js": "javascript"}.get(ext, "")
        preview = main_content[:3000]
        if len(main_content) > 3000:
            preview += f"\n\n... ({len(main_content) - 3000:,} more chars in ZIP)"
        try:
            await update.message.reply_text(
                f"👁 *Preview — `{entry_point}`*\n\n```{lang}\n{preview}\n```",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception:
            pass

    # 4. Iteration hint + action buttons
    keyboard = [
        [InlineKeyboardButton("🔄 Build Another", callback_data="build_prompt"),
         InlineKeyboardButton("💡 Examples", callback_data="examples")],
        [InlineKeyboardButton("📋 Show Files", callback_data="rebuild")]
    ]
    hint = "\n".join(ITERATION_HINTS)
    await update.message.reply_text(
        f"🎉 *Done!* {'Changes applied!' if is_iter else 'Your project is ready!'}\n\n{hint}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ─── Error handler ────────────────────────────────────────────────────────────

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")


# ─── Main ─────────────────────────────────────────────────────────────────────

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
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    logger.info("LovableBot started — Lovable-parity mode with iteration support")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
