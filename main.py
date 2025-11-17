import os
import instaloader
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("TOKEN")

L = instaloader.Instaloader(
    download_pictures=False,
    download_videos=False,
    save_metadata=False,
    download_comments=False
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👮 Instagram Quick Reporter Bot\n\n"
        "Send me an Instagram username (without @), and I’ll generate a button "
        "to open Instagram's official report page for that account.",
        parse_mode="Markdown"
    )

async def handle_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip().replace("@", "")
    await update.message.reply_text(f"🔎 Checking profile: {username} ...")

    try:
        profile = instaloader.Profile.from_username(L.context, username)
        bio = profile.biography or "No bio available."

        report_link = f"https://www.instagram.com/{username}/report/"

        keyboard = [
            [InlineKeyboardButton("🚨 Report on Instagram", url=report_link)]
        ]
        markup = InlineKeyboardMarkup(keyboard)

        response = (
            f"👤 **Username:** {username}\n"
            f"📜 **Bio:** {bio}\n"
            f"👥 **Followers:** {profile.followers}\n"
            f"🖼 **Posts:** {profile.mediacount}\n\n"
            "Tap below to report this account ⬇️"
        )

        await update.message.reply_text(response, reply_markup=markup, parse_mode="Markdown")

    except:
        await update.message.reply_text(
            "❌ Could not access this profile. It may be private or unavailable."
        )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username))

if __name__ == "__main__":
    app.run_polling()
