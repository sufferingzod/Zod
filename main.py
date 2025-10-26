from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
import logging

# Basic config
BOT_TOKEN = "8267986170:AAFznQBnnIic2JLwSQZODhZi645JaAaxln8"
OWNER_ID = 7444391256  # <-- replace with your Telegram numeric ID

logging.basicConfig(level=logging.INFO)

# This dictionary will store which user sent which message
user_map = {}
greeted_users = set()  # track who already got greeted


# Greeting message
def get_greeting():
    return (
        "👋 Hi, welcome to Zod Loader support bot.\n"
        "Please type your questions here I'll reply as soon as i can!\n\n"
        "Made by @ZodOwner — if you don’t get a reply, contact him."
    )


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /start command (ensures greeting is always sent)."""
    user = update.message.from_user
    if user.id not in greeted_users:
        greeted_users.add(user.id)
        await update.message.reply_text(get_greeting())
    else:
        await update.message.reply_text("You're already connected. How can I help you?")


async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles messages sent to the bot by users."""
    user = update.message.from_user
    text = update.message.text.lower()

    # Notify the owner (you)
    msg_to_owner = f"📩 Message from {user.first_name} (@{user.username or 'no_username'}) [id: {user.id}]:\n{text}"
    await context.bot.send_message(chat_id=OWNER_ID, text=msg_to_owner)

    # Store mapping so replies can be routed
    user_map[OWNER_ID] = user.id

    # Auto reply for specific keywords
    if any(keyword in text for keyword in ["key", "loader"]):
        auto_reply = (
            "💬 (Auto Reply)\n"
            "WEAK : 2$ | 600PKR\n"
            "MONTH : 5$ | 1500PKR"
        )
        await update.message.reply_text(auto_reply)


async def handle_owner_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles your replies to the bot."""
    text = update.message.text

    if OWNER_ID not in user_map:
        await update.message.reply_text("No active user to reply to yet.")
        return

    # Send reply to the last user who messaged
    user_id = user_map[OWNER_ID]
    await context.bot.send_message(chat_id=user_id, text=f"{text}\n\n(Msɢ ʙʏ OWNER)")
    await update.message.reply_text("✅ Sent successfully (Your reply was forwarded).")


async def handle_owner_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner messages that aren’t replies."""
    await handle_owner_reply(update, context)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # /start command handler (guaranteed greeting)
    app.add_handler(CommandHandler("start", handle_start))

    # Handler for messages from others (users)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.User(user_id=OWNER_ID), handle_user_message))
    # Handler for messages from you (owner)
    app.add_handler(MessageHandler(filters.TEXT & filters.User(user_id=OWNER_ID), handle_owner_message))

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
