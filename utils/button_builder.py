from pyrogram import types

class ButtonBuilder:
    @staticmethod
    def main_menu():
        return types.InlineKeyboardMarkup([
            [
                types.InlineKeyboardButton("📝 Create Post", callback_data="create_post"),
                types.InlineKeyboardButton("🚀 Broadcast", callback_data="publish_now")
            ],
            [
                types.InlineKeyboardButton("📢 Channels", callback_data="manage_channels"),
                types.InlineKeyboardButton("📅 Scheduled", callback_data="view_scheduled")
            ],
            [
                types.InlineKeyboardButton("⚙️ Settings", callback_data="bot_settings"),
                types.InlineKeyboardButton("📊 Analytics", callback_data="view_analytics")
            ],
            [
                types.InlineKeyboardButton("🛠 Tools", callback_data="extra_tools"),
                types.InlineKeyboardButton("📖 Help", callback_data="view_help")
            ]
        ])

    @staticmethod
    def channel_menu(channels):
        buttons = []
        for ch in channels:
            buttons.append([types.InlineKeyboardButton(f"📢 {ch['title']}", callback_data=f"ch_{ch['channel_id']}")])
        
        buttons.append([types.InlineKeyboardButton("➕ Connect New Channel", callback_data="add_channel")])
        buttons.append([types.InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")])
        return types.InlineKeyboardMarkup(buttons)

    @staticmethod
    def post_confirmation(has_text=False, has_media=False, has_buttons=False, has_schedule=False, selected_count=0):
        return types.InlineKeyboardMarkup([
            [
                types.InlineKeyboardButton(f"{'✅' if has_text else '📝'} Set Text", callback_data="set_post_text"),
                types.InlineKeyboardButton(f"{'✅' if has_media else '🖼'} Set Media", callback_data="set_post_media")
            ],
            [
                types.InlineKeyboardButton(f"{'✅' if has_buttons else '➕'} Set Buttons", callback_data="add_buttons"),
                types.InlineKeyboardButton(f"{'✅' if has_schedule else '📅'} Schedule", callback_data="schedule_post")
            ],
            [
                types.InlineKeyboardButton(f"📢 Channels ({selected_count})", callback_data="select_broadcast_channels"),
                types.InlineKeyboardButton("👀 Preview", callback_data="preview_post")
            ],
            [
                types.InlineKeyboardButton("📄 Telegraph", callback_data="create_telegraph"),
                types.InlineKeyboardButton("🗑 Discard", callback_data="discard_post")
            ],
            [
                types.InlineKeyboardButton("🚀 Broadcast Now", callback_data="publish_now")
            ],
            [
                types.InlineKeyboardButton("🔙 Back", callback_data="main_menu")
            ]
        ])

    @staticmethod
    def channel_selection_menu(channels, selected_ids):
        buttons = []
        for ch in channels:
            is_selected = ch["channel_id"] in selected_ids
            status = "✅" if is_selected else "❌"
            buttons.append([types.InlineKeyboardButton(
                f"{status} {ch['title']}", 
                callback_data=f"toggle_ch_{ch['channel_id']}"
            )])
        
        buttons.append([types.InlineKeyboardButton("✅ Done", callback_data="preview_broadcast")])
        return types.InlineKeyboardMarkup(buttons)

    @staticmethod
    def settings_menu(user_settings):
        return types.InlineKeyboardMarkup([
            [
                types.InlineKeyboardButton(f"📝 Auto-Caption: {'✅' if user_settings.get('auto_caption') else '❌'}", callback_data="toggle_auto_caption")
            ],
            [
                types.InlineKeyboardButton(f"🖼 Watermark: {'✅' if user_settings.get('watermark') else '❌'}", callback_data="toggle_watermark")
            ],
            [
                types.InlineKeyboardButton("🌐 Language", callback_data="change_lang"),
                types.InlineKeyboardButton("🔙 Back", callback_data="main_menu")
            ]
        ])

    @staticmethod
    def extra_tools_menu():
        return types.InlineKeyboardMarkup([
            [
                types.InlineKeyboardButton("📄 Custom Telegraph", callback_data="tool_custom_telegraph"),
                types.InlineKeyboardButton("✂️ Shortlink", callback_data="tool_shortlink")
            ],
            [
                types.InlineKeyboardButton("🏷 Hashtags", callback_data="tool_hashtags"),
                types.InlineKeyboardButton("🔄 Refresh Session", callback_data="tool_refresh_session")
            ],
            [
                types.InlineKeyboardButton("🤖 AI Suggestion", callback_data="tool_ai_caption")
            ],
            [
                types.InlineKeyboardButton("🔙 Back", callback_data="main_menu")
            ]
        ])
