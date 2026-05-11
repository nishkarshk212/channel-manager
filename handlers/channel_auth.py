from hydrogram import Client, filters
from hydrogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from hydrogram.enums import ChatType, ChatMemberStatus

from utils.button_builder import ButtonBuilder
from database.crud import crud
from database.models import Channel


@Client.on_message(filters.command("channels") & filters.private)
async def channels_command(client: Client, message: Message):
    channels = await crud.get_channels(message.from_user.id)
    await message.reply_text(
        "📢 **Connected Channels**\n\n"
        "Select a channel to manage or add a new one:",
        reply_markup=ButtonBuilder.channel_menu(channels)
    )

# =========================
# Manage Channels Menu
# =========================
@Client.on_callback_query(filters.regex("^manage_channels$"))
async def manage_channels(client: Client, query: CallbackQuery):
    try:
        channels = await crud.get_channels(query.from_user.id)
        text = (
            "📢 **Connected Channels**\n\n"
            "Select a channel to manage or add a new one:"
        )
        try:
            await query.message.edit_caption(
                caption=text,
                reply_markup=ButtonBuilder.channel_menu(channels)
            )
        except Exception:
            await query.message.edit_text(
                text,
                reply_markup=ButtonBuilder.channel_menu(channels)
            )

    except Exception as e:
        print(f"[MANAGE_CHANNELS_ERROR] {e}")
        error_text = f"❌ Error:\n`{type(e).__name__}: {e}`"
        try:
            await query.message.edit_caption(caption=error_text)
        except Exception:
            await query.message.edit_text(error_text)


# =========================
# Add Channel Menu
# =========================
@Client.on_callback_query(filters.regex("^add_channel$"))
async def add_channel_prompt(client: Client, query: CallbackQuery):
    try:
        bot_obj = await client.get_me()
        bot_username = bot_obj.username

        # More compatible deep link format
        add_to_chat_url = f"https://t.me/{bot_username}?startchannel&admin=post_messages+edit_messages+delete_messages+invite_users"

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "➕ Add Bot to Channel",
                    url=add_to_chat_url
                )
            ],
            [
                InlineKeyboardButton(
                    "🔗 Manual Connect",
                    callback_data="manual_connect_info"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 Back to Menu",
                    callback_data="main_menu"
                )
            ]
        ])

        text = (
            "➕ **Add New Channel**\n\n"

            "**Method 1 (Easy):**\n"
            "Click the button below to add me to your "
            "channel and give me Admin permissions.\n\n"

            "**Method 2 (Manual):**\n"
            "1. Add me manually as Admin.\n"
            "2. Send:\n"
            "`/connect @channelusername`\n\n"
            "OR forward any message from the channel."
        )

        try:
            await query.message.edit_caption(
                caption=text,
                reply_markup=keyboard
            )
        except Exception:
            await query.message.edit_text(
                text,
                reply_markup=keyboard
            )

    except Exception as e:
        print(f"[ADD_CHANNEL_ERROR] {e}")
        error_text = f"❌ Error:\n`{type(e).__name__}: {e}`"
        try:
            await query.message.edit_caption(caption=error_text)
        except Exception:
            await query.message.edit_text(error_text)


# =========================
# Manual Connect Guide
# =========================
@Client.on_callback_query(filters.regex("^manual_connect_info$"))
async def manual_connect_info(client: Client, query: CallbackQuery):
    try:
        bot_obj = await client.get_me()

        await query.message.edit_text(
            "🔗 **Manual Connection Guide**\n\n"

            "1. Open Channel Settings.\n"
            "2. Go to Administrators.\n"
            "3. Add this bot:\n"
            f"`@{bot_obj.username}`\n\n"

            "4. Then send:\n"
            "`/connect @YourChannel`\n\n"

            "OR forward a channel message here.",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔙 Back",
                        callback_data="add_channel"
                    )
                ]
            ])
        )

    except Exception as e:
        print(f"[MANUAL_CONNECT_INFO_ERROR] {e}")

        await query.message.edit_text(
            f"❌ Error:\n`{type(e).__name__}: {e}`"
        )


# =========================
# Manual Channel Connect
# =========================
@Client.on_message(filters.command("connect") & filters.private)
async def connect_channel_manual(client: Client, message: Message):

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ **Usage:**\n"
            "`/connect @channel_username`\n\n"
            "Example:\n"
            "`/connect @mychannel`"
        )

    channel_input = message.command[1]

    try:
        # Convert numeric IDs
        if channel_input.startswith("-100"):
            channel_input = int(channel_input)

        elif channel_input.isdigit():
            channel_input = int(f"-100{channel_input}")

        # Get chat
        chat = await client.get_chat(channel_input)

        # Validate type
        if chat.type not in [ChatType.CHANNEL, ChatType.SUPERGROUP]:
            return await message.reply_text(
                "❌ This is not a channel/supergroup."
            )

        # Check bot admin
        member = await client.get_chat_member(chat.id, "me")

        if member.status not in [
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        ]:
            return await message.reply_text(
                "❌ I must be an Admin in the channel first."
            )

        # Prevent duplicate channels
        existing_channels = await crud.get_channels(message.from_user.id)

        for ch in existing_channels:
            if int(ch.get("channel_id")) == int(chat.id):
                return await message.reply_text(
                    "⚠️ This channel is already connected."
                )

        # Save channel
        new_channel = Channel(
            channel_id=chat.id,
            owner_id=message.from_user.id,
            title=chat.title,
            username=chat.username,
            authorized_by=message.from_user.id
        )

        try:
            await crud.add_channel(new_channel)

        except Exception as db_error:
            print(f"[DATABASE_ERROR] {db_error}")

            return await message.reply_text(
                f"❌ Database Error:\n"
                f"`{type(db_error).__name__}: {db_error}`"
            )

        await message.reply_text(
            "✅ **Channel Connected Successfully!**\n\n"
            f"**Title:** {chat.title}\n"
            f"**ID:** `{chat.id}`"
        )

    except Exception as e:
        print(f"[CONNECT_ERROR] {e}")

        await message.reply_text(
            f"❌ Error:\n`{type(e).__name__}: {e}`"
        )


# =========================
# Forwarded Message Connect
# =========================
@Client.on_message(filters.forwarded & filters.private)
async def authorize_channel(client: Client, message: Message):

    try:
        chat = None

        # New Telegram API
        if message.forward_origin:

            if hasattr(message.forward_origin, "chat"):
                chat = message.forward_origin.chat

            elif hasattr(message.forward_origin, "sender_chat"):
                chat = message.forward_origin.sender_chat

        # Old fallback
        if not chat:
            chat = message.forward_from_chat

        # No chat detected
        if not chat:
            return await message.reply_text(
                "❌ Could not detect channel.\n"
                "Please forward a message from your channel."
            )

        # Validate type
        if chat.type not in [ChatType.CHANNEL, ChatType.SUPERGROUP]:
            return await message.reply_text(
                "❌ Forward a message from a Channel."
            )

        # Check bot admin
        try:
            member = await client.get_chat_member(chat.id, "me")

            if member.status not in [
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
            ]:
                return await message.reply_text(
                    "❌ I must be an Admin in the channel first."
                )

        except Exception as admin_error:
            print(f"[ADMIN_CHECK_ERROR] {admin_error}")

            return await message.reply_text(
                "❌ I'm not in that channel "
                "or don't have permissions."
            )

        # Prevent duplicate save
        existing_channels = await crud.get_channels(message.from_user.id)

        for ch in existing_channels:
            if int(ch.get("channel_id")) == int(chat.id):
                return await message.reply_text(
                    "⚠️ Channel already connected."
                )

        # Save channel
        new_channel = Channel(
            channel_id=chat.id,
            owner_id=message.from_user.id,
            title=chat.title,
            username=chat.username,
            authorized_by=message.from_user.id
        )

        try:
            await crud.add_channel(new_channel)

        except Exception as db_error:
            print(f"[DATABASE_ERROR] {db_error}")

            return await message.reply_text(
                f"❌ Database Error:\n"
                f"`{type(db_error).__name__}: {db_error}`"
            )

        await message.reply_text(
            f"✅ **Channel Authorized:** {chat.title}"
        )

    except Exception as e:
        print(f"[FORWARD_CONNECT_ERROR] {e}")

        await message.reply_text(
            f"❌ Error:\n`{type(e).__name__}: {e}`"
        )
