from pyrogram import Client, filters, types
from utils.button_builder import ButtonBuilder

COMMAND_HELP = {
    "start": "🏠 **Start / Panel**\n\nCommand: `/start` or `/panel`\n\nOpens the main management menu where you can access all features like post creation, channel management, and settings.",
    "connect": "🔗 **Connect Channel**\n\nCommand: `/connect @channel_username`\n\nUse this command to manually link a channel to the bot. Make sure the bot is an admin in the channel first.",
    "broadcast": "🚀 **Broadcast**\n\nCommand: `/broadcast`\n\nOpens the post creation panel. You can set text, media, custom buttons, and even schedule the post for later.",
    "channels": "📢 **Manage Channels**\n\nCommand: `/channels`\n\nView and manage all your connected channels. You can see stats or remove channels from here.",
    "posts": "📅 **Post History**\n\nCommand: `/posts`\n\nView your scheduled and published posts. You can also cancel upcoming scheduled posts.",
    "settings": "⚙️ **Settings**\n\nCommand: `/settings`\n\nConfigure bot preferences like auto-captioning, watermarking, and language settings.",
    "stats": "📊 **Analytics**\n\nCommand: `/stats`\n\nView detailed statistics for your channels, including member count and post engagement.",
    "ping": "🏓 **Ping**\n\nCommand: `/ping`\n\nCheck if the bot is online and responsive."
}

def get_help_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton("🏠 Start", callback_data="help_cmd_start"),
            types.InlineKeyboardButton("🔗 Connect", callback_data="help_cmd_connect")
        ],
        [
            types.InlineKeyboardButton("🚀 Broadcast", callback_data="help_cmd_broadcast"),
            types.InlineKeyboardButton("📢 Channels", callback_data="help_cmd_channels")
        ],
        [
            types.InlineKeyboardButton("📅 Posts", callback_data="help_cmd_posts"),
            types.InlineKeyboardButton("⚙️ Settings", callback_data="help_cmd_settings")
        ],
        [
            types.InlineKeyboardButton("📊 Stats", callback_data="help_cmd_stats"),
            types.InlineKeyboardButton("🏓 Ping", callback_data="help_cmd_ping")
        ],
        [
            types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
        ]
    ]
    return types.InlineKeyboardMarkup(buttons)

@Client.on_message(filters.command("help") & filters.private)
async def help_command(client: Client, message: types.Message):
    await message.reply_text(
        "📖 **Help Panel**\n\nSelect a command below to see detailed information and usage instructions.",
        reply_markup=get_help_keyboard()
    )

@Client.on_callback_query(filters.regex("^view_help$"))
async def help_callback(client: Client, query: types.CallbackQuery):
    text = "📖 **Help Panel**\n\nSelect a command below to see detailed information and usage instructions."
    try:
        await query.message.edit_caption(
            caption=text,
            reply_markup=get_help_keyboard()
        )
    except Exception:
        await query.message.edit_text(
            text,
            reply_markup=get_help_keyboard()
        )

@Client.on_callback_query(filters.regex("^help_cmd_"))
async def help_detail_callback(client: Client, query: types.CallbackQuery):
    cmd = query.data.replace("help_cmd_", "")
    description = COMMAND_HELP.get(cmd, "No description available.")
    
    back_button = types.InlineKeyboardMarkup([[
        types.InlineKeyboardButton("🔙 Back to Help", callback_data="view_help")
    ]])
    
    try:
        await query.message.edit_caption(caption=description, reply_markup=back_button)
    except Exception:
        await query.message.edit_text(description, reply_markup=back_button)
