import os
import logging
import re
from typing import Dict

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)

# --------------------------------------------
#  Logging
# --------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# --------------------------------------------
#  Conversation states
# --------------------------------------------
(
    MAIN_MENU,
    ASK_QUESTION,
    GET_ASSISTANCE,
    FIND_INFO,
    GENERAL_CHAT,
) = range(5)

# --------------------------------------------
#  Built‑in knowledge base (keyword → response)
# --------------------------------------------
KNOWLEDGE_BASE: Dict[str, str] = {
    # Telegram
    r"telegram|bot|channel|group": (
        "Telegram is a cloud‑based messaging platform. "
        "You can create channels, groups, and bots. "
        "For bot setup, use @BotFather to get a token and then deploy your bot."
    ),
    # Social media
    r"social media|instagram|facebook|twitter|linkedin|tiktok": (
        "Social media platforms are great for reaching audiences. "
        "Each has its own best practices – post consistently, engage with followers, "
        "and use analytics to refine your strategy."
    ),
    # Digital marketing
    r"digital marketing|marketing|advertising|campaign": (
        "Digital marketing includes SEO, content marketing, social media, "
        "email marketing, and paid ads. A good strategy uses a mix of channels "
        "and measures results with analytics tools."
    ),
    # SEO
    r"seo|search engine optimization|ranking|keywords": (
        "SEO helps your website rank higher in search results. "
        "Focus on quality content, proper keywords, meta tags, backlinks, "
        "and a fast, mobile‑friendly site."
    ),
    # Websites
    r"website|web development|hosting|domain": (
        "Building a website involves choosing a domain, hosting, "
        "and a platform (e.g., WordPress, custom code). "
        "Ensure it is secure, fast, and mobile‑responsive."
    ),
    # Technology
    r"technology|tech|innovation|ai|machine learning|blockchain": (
        "Technology evolves rapidly. Staying updated with industry news, "
        "learning new skills, and experimenting with tools helps you keep pace."
    ),
    # Programming
    r"programming|code|python|javascript|developer|software": (
        "Programming is the art of giving computers instructions. "
        "Popular languages include Python, JavaScript, Java, and C++. "
        "Practice, read documentation, and build projects to improve."
    ),
    # Business
    r"business|startup|entrepreneur|management|leadership": (
        "Running a business requires planning, finance, marketing, "
        "and customer focus. Good leadership and adaptability are key to success."
    ),
    # General information
    r"general|information|news|current events": (
        "I can help with general information, but my knowledge is limited. "
        "For the latest news, please check trusted news sources."
    ),
    # Bot development
    r"bot development|telegram bot|api|webhook|polling": (
        "Telegram bots are built using the Bot API. You can use libraries like "
        "python‑telegram‑bot. They run either via webhook or long polling. "
        "Start with @BotFather to create a bot and get a token."
    ),
    # Online safety
    r"online safety|security|privacy|password|phishing": (
        "Stay safe online by using strong, unique passwords, enabling two‑factor "
        "authentication, and being cautious of suspicious links and requests."
    ),
}

# Assistance responses (similar, but more guidance‑oriented)
ASSISTANCE_BASE: Dict[str, str] = {
    r"telegram bot setup|setup|configure bot": (
        "To set up a Telegram bot:\n"
        "1. Open @BotFather on Telegram.\n"
        "2. Send /newbot and follow the prompts.\n"
        "3. Copy the bot token.\n"
        "4. Write your bot code and deploy (e.g., on Railway).\n"
        "5. Run the bot – it will respond to commands."
    ),
    r"telegram channel|channel management": (
        "Manage Telegram channels by:\n"
        "- Posting valuable content regularly.\n"
        "- Engaging with subscribers via polls and comments.\n"
        "- Using analytics to understand your audience.\n"
        "- Promoting your channel through cross‑posting and ads."
    ),
    r"telegram advertising|ads": (
        "Telegram Ads allow you to promote your channel or bot. "
        "Set a budget, target relevant audiences, and track performance. "
        "Always follow Telegram's ad policies."
    ),
    r"social media assistance|social media help": (
        "For social media, focus on:\n"
        "- Consistent branding.\n"
        "- Engaging content (images, videos, stories).\n"
        "- Interaction with followers.\n"
        "- Scheduling tools to save time."
    ),
    r"website assistance|website help|build website": (
        "To build a website, decide on a purpose, choose a platform (e.g., WordPress), "
        "select hosting, and design a user‑friendly interface. Consider SEO from the start."
    ),
    r"seo assistance|seo help": (
        "SEO help: optimize page titles, meta descriptions, headings, "
        "improve page speed, build quality backlinks, and create useful content."
    ),
    r"marketing assistance|marketing help": (
        "Marketing help: define your target audience, craft a compelling message, "
        "choose channels (social, email, content), and measure ROI."
    ),
    r"technical troubleshooting|troubleshoot|fix": (
        "For technical issues, identify the problem, search for error messages, "
        "check logs, and break down the issue step by step. If stuck, seek help "
        "from forums or documentation."
    ),
    r"general guidance|help|support": (
        "I can provide general guidance on many topics. Please be specific so I can assist better."
    ),
}

# --------------------------------------------
#  Helper: get_response
# --------------------------------------------
def get_response(text: str, knowledge: Dict[str, str]) -> str:
    """Match user text against knowledge base and return a response."""
    text_lower = text.lower()
    for pattern, response in knowledge.items():
        if re.search(pattern, text_lower):
            return response
    return (
        "I’m currently unable to provide a reliable answer to that question using my built‑in knowledge. "
        "Please try asking in a different way or choose another option."
    )

# --------------------------------------------
#  Main menu keyboard
# --------------------------------------------
def main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("1️⃣ Ask a Question", callback_data="question")],
        [InlineKeyboardButton("2️⃣ Get Assistance", callback_data="assistance")],
        [InlineKeyboardButton("3️⃣ Find Information", callback_data="search")],
        [InlineKeyboardButton("4️⃣ General Chat", callback_data="chat")],
    ]
    return InlineKeyboardMarkup(keyboard)

def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")]]
    return InlineKeyboardMarkup(keyboard)

# --------------------------------------------
#  Handlers
# --------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send welcome message and main menu."""
    welcome = (
        "👋 Welcome!\n\n"
        "I’m your smart assistant, ready to provide quick answers, useful information, "
        "and assistance whenever you need it.\n\n"
        "What would you like to do?\n\n"
        "1️⃣ Ask a Question\n"
        "2️⃣ Get Assistance\n"
        "3️⃣ Search for Information\n"
        "4️⃣ General Chat\n\n"
        "💡 Simply select an option or type your request below.\n\n"
        "🚀 Fast • Smart • Simple • Helpful"
    )
    await update.message.reply_text(welcome, reply_markup=main_menu_keyboard())
    return MAIN_MENU

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message."""
    help_text = (
        "🤖 **AskMate AI**\n\n"
        "I’m a built‑in assistant that can respond to questions about various topics "
        "like Telegram, social media, marketing, programming, and more.\n\n"
        "• Use the **menu buttons** to choose a mode.\n"
        "• Type your question or request directly.\n"
        "• I respond with pre‑prepared helpful information – I do not use external AI or internet search.\n\n"
        "Commands:\n"
        "/start – show main menu\n"
        "/menu – show main menu\n"
        "/help – show this message"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show main menu."""
    await update.message.reply_text("Main menu:", reply_markup=main_menu_keyboard())
    return MAIN_MENU

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle inline button presses."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_to_menu":
        await query.edit_message_text(
            "Main menu:", reply_markup=main_menu_keyboard()
        )
        return MAIN_MENU

    if data == "question":
        await query.edit_message_text(
            "❓ What would you like to ask?\n\n"
            "Send your question below and I’ll do my best to help.",
            reply_markup=back_to_menu_keyboard(),
        )
        return ASK_QUESTION

    if data == "assistance":
        await query.edit_message_text(
            "🛠 What do you need assistance with?\n\n"
            "Describe your request below and I’ll guide you through the available options.",
            reply_markup=back_to_menu_keyboard(),
        )
        return GET_ASSISTANCE

    if data == "search":
        await query.edit_message_text(
            "🔎 Find Information\n\n"
            "Enter your request below. Note: this uses my built‑in information, "
            "not live internet search.",
            reply_markup=back_to_menu_keyboard(),
        )
        return FIND_INFO

    if data == "chat":
        await query.edit_message_text(
            "💬 General Chat\n\n"
            "Send me a message and I’ll respond using my built‑in knowledge and available responses.",
            reply_markup=back_to_menu_keyboard(),
        )
        return GENERAL_CHAT

    # fallback
    await query.edit_message_text(
        "Main menu:", reply_markup=main_menu_keyboard()
    )
    return MAIN_MENU

async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process user question."""
    text = update.message.text
    response = get_response(text, KNOWLEDGE_BASE)
    await update.message.reply_text(response, reply_markup=back_to_menu_keyboard())
    return ASK_QUESTION

async def handle_assistance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process assistance request."""
    text = update.message.text
    response = get_response(text, ASSISTANCE_BASE)
    await update.message.reply_text(response, reply_markup=back_to_menu_keyboard())
    return GET_ASSISTANCE

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process search/information request."""
    text = update.message.text
    response = get_response(text, KNOWLEDGE_BASE)
    await update.message.reply_text(response, reply_markup=back_to_menu_keyboard())
    return FIND_INFO

async def handle_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process general chat message."""
    text = update.message.text
    response = get_response(text, KNOWLEDGE_BASE)
    await update.message.reply_text(response, reply_markup=back_to_menu_keyboard())
    return GENERAL_CHAT

async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Fallback for any unexpected input in menu state."""
    await update.message.reply_text(
        "Please use the menu buttons below:", reply_markup=main_menu_keyboard()
    )
    return MAIN_MENU

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors and notify user gracefully."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "Sorry, something went wrong. Please try again or use /start to restart."
        )

# --------------------------------------------
#  Main application
# --------------------------------------------
def main() -> None:
    # Read token from environment
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.critical("TELEGRAM_BOT_TOKEN environment variable is not set. Exiting.")
        return

    # Create application
    application = ApplicationBuilder().token(token).build()

    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("menu", menu_command),
        ],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(button_callback, pattern="^(question|assistance|search|chat|back_to_menu)$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, fallback),
            ],
            ASK_QUESTION: [
                CallbackQueryHandler(button_callback, pattern="^back_to_menu$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question),
            ],
            GET_ASSISTANCE: [
                CallbackQueryHandler(button_callback, pattern="^back_to_menu$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_assistance),
            ],
            FIND_INFO: [
                CallbackQueryHandler(button_callback, pattern="^back_to_menu$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search),
            ],
            GENERAL_CHAT: [
                CallbackQueryHandler(button_callback, pattern="^back_to_menu$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_chat),
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
            CommandHandler("menu", menu_command),
            CommandHandler("help", help_command),
        ],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_error_handler(error_handler)

    # Start long polling
    logger.info("Bot started with long polling.")
    application.run_polling()

if __name__ == "__main__":
    main()
