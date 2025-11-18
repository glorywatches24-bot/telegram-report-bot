# main.py  (this is the only file you need)
import os
import instaloader
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Get token from environment (Render sets this automatically if you add a "TOKEN" env var)
BOT_TOKEN = os.getenv("TOKEN")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN found in environment variables!")

# Instaloader instance – minimal overhead
L = instaloader.Instaloader(
    download_pictures=False,
    download_videos=False,
    download_video_thumbnails=False,
    download_geotags=False,
    download_comments=False,
    save_metadata=False,
    compress_json=False,
    filename_pattern="{profile}",
    quiet=True,
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Instagram Quick Reporter Bot\n\n"
        "Send me an Instagram username (with or without @) and I’ll give you a direct report button.",
    )

async def handle_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    username = update.message.text.strip().lstrip("@")
    
    checking_msg = await update.message.reply_text(f"Checking @{username} ...")

    try:
        profile = instaloader.Profile.from_username(L.context, username)

        report_url = f"https://help.instagram.com/contact/636276399721841?username={username}"

        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("Report this account", url=report_url)
        ]])

        bio = (profile.biography or "No bio").replace("\n", " ").strip()[:200]
        if len(profile.biography or "") > 200:
            bio += "..."

        text = (
            f"**@{username}**\n\n"
            f"**Bio:** {bio}\n"
            f"**Followers:** {profile.followers:,}\n"
            f"**Posts:** {profile.mediacount:,}\n\n"
            "Tap the button below to open Instagram's official report form →"
        )

        await checking_msg.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")

    except instaloader.exceptions.ProfileNotExistsException:
        await checking_msg.edit_text("Profile does not exist.")
    except instaloader.exceptions.PrivateProfileNotFollowedException:
        await checking_msg.edit_text("Profile is private and cannot be accessed without following.")
    except instaloader.exceptions.ConnectionException:
        await checking_msg.edit_text("Instagram is rate-limiting us. Try again in a minute.")
    except Exception as e:
        await checking_msg.edit_text("Something went wrong. Try again later.")
        raise  # let it crash in logs so you can see real errors

def main() -> None:
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username))

    print("Bot starting...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
