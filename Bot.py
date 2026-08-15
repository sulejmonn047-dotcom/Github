import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 👇 ИН ҶО TOKEN-И БОТФАТЕР-РО ГУЗОР
TOKEN = "TOKEN-И-ТУ-РО-ИН-ҶО-ГУЗОР"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Салом!\n\n"
        "Ман боти видео-соз ҳастам. 🤖\n\n"
        "📹 Ҳоло версияи аввал аст.\n"
        "Ба наздикӣ сохтани видео илова мешавад."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Фармонҳо:\n\n"
        "/start — оғоз\n"
        "/help — кӯмак"
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    print("🤖 BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()
