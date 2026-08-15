import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 👇 ИН ҶО TOKEN-И БОТФАТЕР-РО ГУЗОР
TOKEN = "8684879388:AAGL_6r_pV6ZJcXDyRA6uvcTa3lMOG8M0Vo"
import os
import re
import asyncio
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================
# TOKEN
# =========================

TOKEN = "TOKEN-И-ТУ-РО-ИН-ҶО-ГУЗОР"

# =========================
# Папкаҳо
# =========================

BASE = Path("video_data")
IMAGES = BASE / "images"
OUTPUT = BASE / "output"

IMAGES.mkdir(parents=True, exist_ok=True)
OUTPUT.mkdir(parents=True, exist_ok=True)


# =========================
# Ҳолати корбар
# =========================

users = {}


# =========================
# /start
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    users[update.effective_user.id] = {
        "script": "",
        "images": []
    }

    await update.message.reply_text(
        "🎬 БОТИ ВИДЕО-СОЗ\n\n"
        "Ман метавонам аз рӯи сенарияи ту видео тайёр кунам.\n\n"
        "📝 Қадами 1:\n"
        "Сенарияи видеоро фирист.\n\n"
        "Масалан:\n"
        "«Видео 20 сония. Аввал китобро нишон деҳ. "
        "Баъд аксияро нишон деҳ. Дар охир Kitob_sarmoya "
        "ва даъват ба харид нишон дода шавад.»"
    )


# =========================
# Қабули сенария
# =========================

async def receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in users:
        users[user_id] = {
            "script": "",
            "images": []
        }

    users[user_id]["script"] = text
    users[user_id]["images"] = []

    await update.message.reply_text(
        "✅ Сенария қабул шуд.\n\n"
        "Ҳоло 🖼️ расмҳои китобҳо ё дигар расмҳоятро "
        "як-як фирист.\n\n"
        "Вақте ҳамаи расмҳоро фиристодӣ, навис:\n"
        "👉 /make"
    )


# =========================
# Қабули расм
# =========================

async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id not in users:
        users[user_id] = {
            "script": "",
            "images": []
        }

    if not users[user_id]["script"]:
        await update.message.reply_text(
            "⚠️ Аввал сенарияро фирист."
        )
        return

    photo = update.message.photo[-1]

    file = await context.bot.get_file(photo.file_id)

    number = len(users[user_id]["images"]) + 1

    filename = IMAGES / f"{user_id}_{number}.jpg"

    await file.download_to_drive(str(filename))

    users[user_id]["images"].append(str(filename))

    await update.message.reply_text(
        f"🖼️ Расми №{number} қабул шуд.\n\n"
        "Расми дигар фирист ё /make навис."
    )


# =========================
# Аз сенария ҷумлаҳо месозем
# =========================

def split_script(script):

    parts = re.split(r"[.!?]\s+|\n+", script)

    parts = [
        p.strip()
        for p in parts
        if p.strip()
    ]

    if not parts:
        parts = [script]

    return parts


# =========================
# Font
# =========================

def get_font(size):

    fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]

    for font in fonts:
        if os.path.exists(font):
            return ImageFont.truetype(font, size)

    return ImageFont.load_default()


# =========================
# Сохтани кадр
# =========================

def create_frame(image_path, text, output_path):

    width = 1080
    height = 1920

    img = Image.open(image_path).convert("RGB")

    # Ба 1080x1920 мутобиқ мекунем
    img.thumbnail((width - 80, height - 500))

    canvas = Image.new(
        "RGB",
        (width, height),
        "black"
    )

    x = (width - img.width) // 2
    y = 150

    canvas.paste(img, (x, y))

    draw = ImageDraw.Draw(canvas)

    font = get_font(58)

    # Матнро ба сатрҳо тақсим мекунем
    words = text.split()
    lines = []
    line = ""

    for word in words:

        test = line + " " + word

        box = draw.textbbox(
            (0, 0),
            test,
            font=font
        )

        if box[2] > width - 100:
            lines.append(line)
            line = word
        else:
            line = test

    if line:
        lines.append(line)

    text_y = height - 420

    for line in lines:

        box = draw.textbbox(
            (0, 0),
            line,
            font=font
        )

        text_width = box[2] - box[0]

        text_x = (width - text_width) // 2

        # соя
        draw.text(
            (text_x + 3, text_y + 3),
            line,
            font=font,
            fill="black"
        )

        draw.text(
            (text_x, text_y),
            line,
            font=font,
            fill="white"
        )

        text_y += 75

    canvas.save(output_path)


# =========================
# Сохтани видео
# =========================

def make_video(user_id):

    data = users[user_id]

    script = data["script"]
    images = data["images"]

    if not images:
        raise Exception("Расмҳо нестанд.")

    parts = split_script(script)

    # Агар саҳнаҳо аз расмҳо зиёд бошанд,
    # расмҳоро такрор мекунем
    selected = []

    for i in range(len(parts)):
        selected.append(
            images[i % len(images)]
        )

    frame_dir = BASE / f"frames_{user_id}"
    frame_dir.mkdir(exist_ok=True)

    frames = []

    for i, (image, text) in enumerate(
        zip(selected, parts)
    ):

        frame = frame_dir / f"frame_{i}.jpg"

        create_frame(
            image,
            text,
            frame
        )

        frames.append(frame)

    output_file = OUTPUT / f"video_{user_id}.mp4"

    # 3 сония барои ҳар саҳна
    duration = 3

    command = [
        "ffmpeg",
        "-y",
        "-framerate",
        "1",
        "-i",
        str(frame_dir / "frame_%d.jpg"),
        "-vf",
        "scale=1080:1920",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-r",
        "30",
        str(output_file)
    ]

    subprocess.run(
        command,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    return output_file


# =========================
# /make
# =========================

async def make_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id not in users:
        await update.message.reply_text(
            "Аввал /start-ро пахш кун."
        )
        return

    data = users[user_id]

    if not data["script"]:
        await update.message.reply_text(
            "📝 Аввал сенарияро фирист."
        )
        return

    if not data["images"]:
        await update.message.reply_text(
            "🖼️ Аввал ақаллан 1 расм фирист."
        )
        return

    await update.message.reply_text(
        "🎬 Видео сохта истодааст...\n"
        "⏳ Каме интизор шав."
    )

    try:

        video = await asyncio.to_thread(
            make_video,
            user_id
        )

        with open(video, "rb") as file:

            await update.message.reply_video(
                video=file,
                caption="🎬 Видеои ту тайёр шуд! ✅"
            )

    except Exception as e:

        await update.message.reply_text(
            "❌ Ҳангоми сохтани видео хато шуд.\n\n"
            f"{str(e)[:500]}"
        )


# =========================
# MAIN
# =========================

def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("make", make_command)
    )

    app.add_handler(
        MessageHandler(
            filters.PHOTO,
            receive_photo
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            receive_text
        )
    )

    print("🎬 VIDEO BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()
