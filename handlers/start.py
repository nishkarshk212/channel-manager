from pyrogram import Client, filters, types
from pyrogram.types import Message
from utils.button_builder import ButtonBuilder
from utils.logger import logger
from database.models import User
from database.crud import crud

START_IMAGE_URL = "https://i.ibb.co/RGmW9ZGH/2026-05-08-19-18-13.jpg"

@Client.on_message(filters.command("ping") & filters.private)
async def ping_pong(client: Client, message: Message):
    await message.reply_text("🏓 Pong! The bot is alive and receiving messages.")

@Client.on_message(filters.command(["start", "panel"]) & filters.private)
async def start_command(client: Client, message: Message):
    # Register user if not exists
    user = await crud.get_user(message.from_user.id)
    if not user:
        from database.models import User as UserDoc
        await crud.create_user(UserDoc(
            user_id=message.from_user.id,
            username=message.from_user.username,
            role="owner"
        ))
    
    welcome_text = (
        "👋 **Welcome to Channel Manager Bot!**\n\n"
        "I can help you manage your Telegram channels professionally.\n\n"
        "**Main Features:**\n"
        "• Multi-channel support\n"
        "• Post scheduling\n"
        "• Custom inline buttons\n"
        "• Analytics & more\n\n"
        "Use the menu below to get started."
    )
    await message.reply_photo(
        START_IMAGE_URL,
        caption=welcome_text,
        reply_markup=ButtonBuilder.main_menu()
    )

@Client.on_callback_query(filters.regex("^main_menu$"))
async def back_to_main_menu(client: Client, query: types.CallbackQuery):
    welcome_text = (
        "👋 **Welcome to Channel Manager Bot!**\n\n"
        "I can help you manage your Telegram channels professionally.\n\n"
        "**Main Features:**\n"
        "• Multi-channel support\n"
        "• Post scheduling\n"
        "• Custom inline buttons\n"
        "• Analytics & more\n\n"
        "Use the menu below to get started."
    )
    try:
        await query.message.edit_caption(
            caption=welcome_text,
            reply_markup=ButtonBuilder.main_menu()
        )
    except Exception:
        # Fallback if message is not a photo (e.g. from an old session)
        await query.message.delete()
        await query.message.reply_photo(
            START_IMAGE_URL,
            caption=welcome_text,
            reply_markup=ButtonBuilder.main_menu()
        )

@Client.on_message(filters.command("settings") & filters.private)
async def settings_command(client: Client, message: Message):
    user = await crud.get_user(message.from_user.id)
    user_settings = user.get("settings", {})
    await message.reply_text(
        "⚙️ **Bot Settings**\n\nCustomize how the bot works for you:",
        reply_markup=ButtonBuilder.settings_menu(user_settings)
    )

@Client.on_message(filters.command("posts") & filters.private)
async def posts_command(client: Client, message: Message):
    all_posts = await crud.get_scheduled_posts()
    user_posts = [p for p in all_posts if int(p.get("user_id")) == message.from_user.id]
    
    if not user_posts:
        return await message.reply_text("📅 No scheduled posts found.")

    text = "📅 **Your Scheduled Posts**\n\n"
    for i, post in enumerate(user_posts, 1):
        text += f"{i}. {post['content_type'].capitalize()} - {post['scheduled_at']}\n"
    
    await message.reply_text(text, reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]))

@Client.on_callback_query(filters.regex("^bot_settings$"))
async def bot_settings_handler(client: Client, query: types.CallbackQuery):
    user = await crud.get_user(query.from_user.id)
    user_settings = user.get("settings", {})
    text = "⚙️ **Bot Settings**\n\nCustomize how the bot works for you:"
    try:
        await query.message.edit_caption(
            caption=text,
            reply_markup=ButtonBuilder.settings_menu(user_settings)
        )
    except Exception:
        await query.message.edit_text(
            text,
            reply_markup=ButtonBuilder.settings_menu(user_settings)
        )

@Client.on_callback_query(filters.regex("^extra_tools$"))
async def extra_tools_handler(client: Client, query: types.CallbackQuery):
    text = "🛠 **Extra Tools**\n\nAdvanced features for professional management:"
    try:
        await query.message.edit_caption(
            caption=text,
            reply_markup=ButtonBuilder.extra_tools_menu()
        )
    except Exception:
        await query.message.edit_text(
            text,
            reply_markup=ButtonBuilder.extra_tools_menu()
        )

@Client.on_callback_query(filters.regex("^tool_refresh_session$"))
async def refresh_session_handler(client: Client, query: types.CallbackQuery):
    await query.answer("🔄 Refreshing peer cache...")
    channels = await crud.get_channels(query.from_user.id)
    if not channels:
        return await query.message.edit_text("❌ No channels connected to refresh.", reply_markup=ButtonBuilder.extra_tools_menu())

    success = 0
    failed = 0
    for ch in channels:
        try:
            await client.get_chat(ch["channel_id"])
            success += 1
        except Exception:
            # Try via username if available
            if ch.get("username"):
                try:
                    await client.get_chat(ch["username"])
                    success += 1
                    continue
                except Exception:
                    pass
            failed += 1

    await query.message.edit_text(
        f"✅ **Session Refresh Complete!**\n\n"
        f"Successfully re-cached: {success} channels\n"
        f"Failed to resolve: {failed} channels\n\n"
        f"If a channel failed, try removing and adding it again.",
        reply_markup=ButtonBuilder.extra_tools_menu()
    )

@Client.on_callback_query(filters.regex("^view_scheduled$"))
async def view_scheduled_handler(client: Client, query: types.CallbackQuery):
    all_posts = await crud.get_scheduled_posts()
    user_posts = [p for p in all_posts if int(p.get("user_id")) == query.from_user.id]
    
    if not user_posts:
        return await query.answer("📅 No scheduled posts found.", show_alert=True)

    text = "📅 **Your Scheduled Posts**\n\n"
    for i, post in enumerate(user_posts, 1):
        text += f"{i}. {post['content_type'].capitalize()} - {post['scheduled_at']}\n"
    
    reply_markup = types.InlineKeyboardMarkup([[types.InlineKeyboardButton("🔙 Back", callback_data="main_menu")]])
    try:
        await query.message.edit_caption(caption=text, reply_markup=reply_markup)
    except Exception:
        await query.message.edit_text(text, reply_markup=reply_markup)
