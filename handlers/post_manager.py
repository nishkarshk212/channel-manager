from pyrogram import Client, filters, types
from database.crud import crud
from database.models import Post
from utils.button_builder import ButtonBuilder
from services.post_service import post_service
import asyncio
from datetime import datetime
import pytz

# Simple in-memory state for post creation
user_states = {}

def get_post_kb(user_id):
    state = user_states.get(user_id, {})
    return ButtonBuilder.post_confirmation(
        has_text=bool(state.get("caption")),
        has_media=bool(state.get("file_id")),
        has_buttons=bool(state.get("buttons")),
        has_schedule=bool(state.get("schedule_time"))
    )

@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast_command_handler(client: Client, message: types.Message):
    user_states[message.from_user.id] = {
        "step": "idle",
        "content_type": "text",
        "file_id": None,
        "caption": None,
        "buttons": [],
        "schedule_time": None
    }
    await message.reply_text(
        "📝 **Broadcast Panel**\n\nUse the buttons below to build your post.",
        reply_markup=get_post_kb(message.from_user.id)
    )

@Client.on_callback_query(filters.regex("^create_post$"))
async def start_post_creation(client: Client, query: types.CallbackQuery):
    user_states[query.from_user.id] = {
        "step": "idle",
        "content_type": "text",
        "file_id": None,
        "caption": None,
        "buttons": [],
        "schedule_time": None
    }
    await query.message.edit_text(
        "📝 **Broadcast Panel**\n\nUse the buttons below to build your post.",
        reply_markup=get_post_kb(query.from_user.id)
    )

@Client.on_callback_query(filters.regex("^set_post_text$"))
async def set_text_prompt(client: Client, query: types.CallbackQuery):
    user_states[query.from_user.id]["step"] = "waiting_for_text"
    await query.message.edit_text("📝 **Send the text/caption for your post.**")

@Client.on_callback_query(filters.regex("^set_post_media$"))
async def set_media_prompt(client: Client, query: types.CallbackQuery):
    user_states[query.from_user.id]["step"] = "waiting_for_media"
    await query.message.edit_text("🖼 **Send the media (Photo, Video, etc.) for your post.**")

@Client.on_callback_query(filters.regex("^add_buttons$"))
async def add_buttons_prompt(client: Client, query: types.CallbackQuery):
    user_states[query.from_user.id]["step"] = "waiting_for_buttons"
    await query.message.edit_text(
        "➕ **Add Inline Buttons**\n\n"
        "Send me buttons in the following format:\n"
        "`Button Text | https://link.com`\n\n"
        "One button per line. Send /done when finished."
    )

@Client.on_callback_query(filters.regex("^schedule_post$"))
async def schedule_post_prompt(client: Client, query: types.CallbackQuery):
    user_states[query.from_user.id]["step"] = "waiting_for_schedule"
    await query.message.edit_text(
        "📅 **Schedule Post**\n\n"
        "Please send the date and time in the following format:\n"
        "`YYYY-MM-DD HH:MM` (e.g., `2024-12-25 15:30`)\n\n"
        "Current UTC Time: `" + datetime.utcnow().strftime("%Y-%m-%d %H:%M") + "`"
    )

@Client.on_message(filters.private & ~filters.command(["start", "help", "connect", "broadcast", "ping"]))
async def handle_messages(client: Client, message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_states:
        return

    state = user_states[user_id]
    
    if state["step"] == "waiting_for_text":
        state["caption"] = message.text or message.caption
        entities = message.entities or message.caption_entities
        if entities:
            state["entities"] = [e.__dict__ for e in entities] if hasattr(entities[0], "__dict__") else entities
        else:
            state["entities"] = None
        state["step"] = "idle"
        await message.reply_text("✅ **Text saved with formatting!**", reply_markup=get_post_kb(user_id))

    elif state["step"] == "waiting_for_media":
        if message.photo:
            state["content_type"] = "photo"
            state["file_id"] = message.photo.file_id
        elif message.video:
            state["content_type"] = "video"
            state["file_id"] = message.video.file_id
        elif message.document:
            state["content_type"] = "document"
            state["file_id"] = message.document.file_id
        elif message.audio:
            state["content_type"] = "audio"
            state["file_id"] = message.audio.file_id
        elif message.animation:
            state["content_type"] = "animation"
            state["file_id"] = message.animation.file_id
        elif message.voice:
            state["content_type"] = "voice"
            state["file_id"] = message.voice.file_id
        elif message.sticker:
            state["content_type"] = "sticker"
            state["file_id"] = message.sticker.file_id
        
        state["step"] = "idle"
        await message.reply_text(f"✅ **Media saved!** ({state['content_type']})", reply_markup=get_post_kb(user_id))
    
    elif state["step"] == "waiting_for_schedule":
        try:
            dt = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
            if dt < datetime.utcnow():
                return await message.reply_text("❌ Time must be in the future!")
            
            state["schedule_time"] = dt
            state["step"] = "idle"
            await message.reply_text(f"✅ **Post scheduled for {dt.strftime('%Y-%m-%d %H:%M')} UTC!**", reply_markup=get_post_kb(user_id))
        except ValueError:
            await message.reply_text("❌ Invalid format. Use: `YYYY-MM-DD HH:MM`")

    elif state["step"] == "waiting_for_buttons":
        if message.text == "/done":
            state["step"] = "idle"
            return await message.reply_text("✅ **Buttons saved!**", reply_markup=get_post_kb(user_id))
        
        try:
            for line in message.text.split("\n"):
                if "|" not in line: continue
                text, url = line.split("|", 1)
                state["buttons"].append({"text": text.strip(), "url": url.strip()})
            await message.reply_text(f"✅ Added {len(state['buttons'])} buttons. Send more or /done.")
        except Exception:
            await message.reply_text("❌ Invalid format. Use: `Text | URL`")

    elif state["step"] == "waiting_for_telegraph_title":
        state["telegraph_title"] = message.text
        state["step"] = "waiting_for_telegraph_content"
        await message.reply_text("📝 **Now send the content (HTML/Text) for your Telegraph page.**")

    elif state["step"] == "waiting_for_telegraph_content":
        title = state.get("telegraph_title", "Custom Page")
        content = message.text.replace("\n", "<br>")
        if not content.startswith("<p>"):
            content = f"<p>{content}</p>"
        
        await message.reply_text("📄 **Creating Telegraph page...**")
        link = await telegraph_service.create_page(title=title, html_content=content)
        
        if link:
            await message.reply_text(f"✅ **Telegraph page created!**\n\nLink: {link}")
        else:
            await message.reply_text("❌ Failed to create Telegraph page.")
        
        state["step"] = "idle"
        # If they were in the middle of a broadcast, show the KB, otherwise just reset
        if state.get("caption") or state.get("file_id"):
            await message.reply_text("Back to post creation:", reply_markup=get_post_kb(user_id))
        else:
            del user_states[user_id]

from services.telegraph_service import telegraph_service

@Client.on_callback_query(filters.regex("^tool_custom_telegraph$"))
async def custom_telegraph_start(client: Client, query: types.CallbackQuery):
    user_states[query.from_user.id] = {"step": "waiting_for_telegraph_title"}
    await query.message.edit_text("📄 **Custom Telegraph Creator**\n\nPlease send the **Title** for your page.")

@Client.on_callback_query(filters.regex("^create_telegraph$"))
async def create_telegraph_handler(client: Client, query: types.CallbackQuery):
    user_id = query.from_user.id
    state = user_states.get(user_id)
    if not state or not state["caption"]:
        return await query.answer("❌ Please set text/caption first.", show_alert=True)

    await query.answer("📄 Creating Telegraph page...")
    # Basic HTML sanitization for Telegraph
    content = state["caption"].replace("\n", "<br>")
    if not content.startswith("<p>"):
        content = f"<p>{content}</p>"

    link = await telegraph_service.create_page(
        title="Broadcast Post",
        html_content=content
    )
    
    if link:
        state["buttons"].append({"text": "📄 Read More", "url": link})
        await query.message.reply_text(f"✅ **Telegraph page created!**\nLink: {link}\nAdded to post buttons.")
        await query.message.edit_reply_markup(reply_markup=get_post_kb(user_id))
    else:
        await query.message.reply_text("❌ Failed to create Telegraph page.")

@Client.on_callback_query(filters.regex("^preview_post$"))
async def preview_post(client: Client, query: types.CallbackQuery):
    user_id = query.from_user.id
    state = user_states.get(user_id)
    if not state or (not state["caption"] and not state["file_id"]):
        return await query.answer("Post is empty! Set text or media first.", show_alert=True)

    await query.answer("Generating preview...")
    
    reply_markup = None
    if state["buttons"]:
        kb = []
        for btn in state["buttons"]:
            kb.append([types.InlineKeyboardButton(btn["text"], url=btn["url"])])
        reply_markup = types.InlineKeyboardMarkup(kb)

    try:
        await post_service.send_to_channel(
            client, user_id, state["content_type"], state["file_id"], state["caption"], reply_markup, state.get("entities")
        )
    except Exception as e:
        await query.message.reply_text(f"❌ Preview failed: {e}")

@Client.on_callback_query(filters.regex("^publish_now$"))
async def publish_now(client: Client, query: types.CallbackQuery):
    user_id = query.from_user.id
    state = user_states.get(user_id)
    if not state or (not state["caption"] and not state["file_id"]):
        return await query.answer("Post is empty!", show_alert=True)

    channels = await crud.get_channels(user_id)
    if not channels:
        return await query.answer("❌ No channels connected.", show_alert=True)

    # If schedule time is set, save to DB and return
    if state.get("schedule_time"):
        post_data = Post(
            user_id=user_id,
            channel_ids=[ch["channel_id"] for ch in channels],
            content_type=state["content_type"],
            media_file_id=state["file_id"],
            caption=state["caption"],
            entities=state.get("entities"),
            buttons=state["buttons"],
            scheduled_at=state["schedule_time"],
            status="scheduled"
        )
        await crud.create_post(post_data)
        await query.message.edit_text(
            f"📅 **Post Scheduled!**\n\n"
            f"Your post will be published to {len(channels)} channels on "
            f"`{state['schedule_time'].strftime('%Y-%m-%d %H:%M')}` UTC."
        )
        del user_states[user_id]
        return

    # Normal broadcast
    success_count = 0
    await query.message.edit_text("🚀 **Broadcasting...**")

    reply_markup = None
    if state["buttons"]:
        kb = []
        for btn in state["buttons"]:
            kb.append([types.InlineKeyboardButton(btn["text"], url=btn["url"])])
        reply_markup = types.InlineKeyboardMarkup(kb)

    for ch in channels:
        try:
            await post_service.send_to_channel(
                client, ch["channel_id"], state["content_type"], state["file_id"], state["caption"], reply_markup, state.get("entities")
            )
            success_count += 1
        except Exception as e:
            await client.send_message(user_id, f"❌ Failed in {ch['title']}: {e}")

    await query.message.edit_text(f"✅ **Broadcast Complete!**\nPosted to {success_count} channels.")
    del user_states[user_id]

@Client.on_callback_query(filters.regex("^discard_post$"))
async def discard_post(client: Client, query: types.CallbackQuery):
    if query.from_user.id in user_states:
        del user_states[query.from_user.id]
    await query.message.edit_text("🗑 **Post discarded.**", reply_markup=ButtonBuilder.main_menu())
