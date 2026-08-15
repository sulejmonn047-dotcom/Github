import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Салом!\n\n"
        "Ман боти видео-соз ҳастам.\n"
        "Ҳоло версияи санҷишӣ ҳастам. 🤖\n\n"
        "Баъд аз ин ба ман сохтани видео илова мекунем."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Фармонҳо:\n\n"
        "/start — оғоз\n"
        "/help — кӯмак"
    )


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN ёфт нашуд!")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    print("🤖 Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
