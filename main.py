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

BOT_TOKEN = os.getenv("TOKEN")
if not BOT_TOKEN:
    raise ValueError("TOKEN environment variable missing!")

L = instaloader.Instaloader(
    download_pictures=False,
    download_videos=False,
    download_video_thumbnails=False,
    download_geotags=False,
    download_comments=False,
    save_metadata=False,
    compress_json=False,
    quiet=True,
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Instagram Quick Reporter Bot\n\n"
        "Send me a username (with or without @) and I'll give you a direct report button."
    )

async def handle_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    username = update.message.text.strip().lstrip("@")
    msg = await update.message.reply_text(f"Checking @{username}...")

    try:
        profile = instaloader.Profile.from_username(L.context, username)
        report_url = f"https://help.instagram.com/contact/636276399721841?username={username}"
        
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Report this account", url=report_url)]])
        
        bio = (profile.biography or "No bio").replace("\n", " ")[:200]
        if len(profile.biography or "") > 200:
            bio += "..."

        text = (
            f"**@{username}**\n\n"
            f"Bio: {bio}\n"
            f"Followers: {profile.followers:,}\n"
            f"Posts: {profile.mediacount:,}\n\n"
            "Tap button to report →"
        )
        await msg.edit_text(text, reply_markup=keyboard, parse_mode="MarkdownV2")

    except instaloader.ProfileNotExistsException:
        await msg.edit_text("Profile does not exist.")
    except instaloader.PrivateProfileNotFollowedException:
        await msg.edit_text("Private profile – can't access without following.")
    except instaloader.ConnectionException:
        await msg.edit_text("Instagram is rate-limiting. Try again later.")
    except Exception as e:
        await msg.edit_text("Error occurred.")
        raise

def main() -> None:
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username))
    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
