from hydrogram import Client, filters
from hydrogram.types import CallbackQuery, Message
from database.crud import crud
from services.analytics import analytics_service

@Client.on_message(filters.command("stats") & filters.private)
async def stats_command(client: Client, message: Message):
    channels = await crud.get_channels(message.from_user.id)
    if not channels:
        return await message.reply_text("No channels connected.")

    text = "📊 **Channel Analytics**\n\n"
    for ch in channels:
        stats = await analytics_service.get_channel_stats(client, ch["channel_id"])
        if stats:
            text += f"📢 **{stats['title']}**\n"
            text += f"👥 Members: {stats['members']}\n"
            text += f"🔗 @{stats['username'] or 'N/A'}\n\n"

    await message.reply_text(text)

@Client.on_callback_query(filters.regex("^view_analytics$"))
async def view_analytics(client: Client, query: CallbackQuery):
    channels = await crud.get_channels(query.from_user.id)
    if not channels:
        return await query.answer("No channels connected.", show_alert=True)

    text = "📊 **Channel Analytics**\n\n"
    for ch in channels:
        stats = await analytics_service.get_channel_stats(client, ch["channel_id"])
        if stats:
            text += f"📢 **{stats['title']}**\n"
            text += f"👥 Members: {stats['members']}\n"
            text += f"🔗 @{stats['username'] or 'N/A'}\n\n"

    try:
        await query.message.edit_caption(caption=text, reply_markup=query.message.reply_markup)
    except Exception:
        await query.message.edit_text(text, reply_markup=query.message.reply_markup)
