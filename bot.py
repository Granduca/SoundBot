import datetime
import json
import logging
import traceback

from telegram import Update, ParseMode, InlineQuery, InlineQueryResultAudio, InlineQueryResultVoice
from telegram.error import NetworkError
from telegram.ext import CallbackContext, CommandHandler, InlineQueryHandler
from urllib3.exceptions import HTTPError

from freesound.request import search_sound, view_browse, Sound

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def handle_start(update: Update, context: CallbackContext):
    username = f" @{update.effective_user.username}" if update.effective_user.username else ''
    logger.info(f"New user has come {update.effective_user.name} "
                f"(id: {update.effective_user.id}){username}")
    text = "👋 Hello and welcome to 🔉 Sound bot" \
           "\nYou can easily search sound from <a href='https:\\freesound.org'>freesound.org</a> with this bot" \
           f"Just type @{context.bot.bot.username} in your private chat and search for sounds!"
    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


def handle_search_inline_query(update: Update, _context: CallbackContext):
    user_id = update.effective_user.id
    username = f"@{update.effective_user.username}" if update.effective_user.username else None
    inline_query: InlineQuery = update.inline_query
    search_query = inline_query.query
    logger.info(f"{username or user_id} query: {search_query}")
    if search_query:
        sounds = search_sound(search_query)
        audio_results = list()
        for sound in sounds:
            audio_result = sound_to_inline_query(sound)
            audio_results.append(audio_result)
        logger.info(audio_results)
        return inline_query.answer(audio_results)
    else:
        sounds = view_browse()
        audio_results = list()
        for sound in sounds:
            audio_result = sound_to_inline_query(sound)
            audio_results.append(audio_result)
        logger.info(audio_results)
        return inline_query.answer(audio_results)


def sound_to_inline_query(sound: Sound):
    duration = round(float(sound.duration) / 1000)
    duration = datetime.timedelta(seconds=duration)
    duration_text = f"{duration.seconds // 60:02d}:{duration.seconds % 60:02d}"
    audio_result = InlineQueryResultAudio(sound.id,
                                          audio_url=sound.mp3,
                                          title=sound.title,
                                          caption=f'{sound.description}\n{sound.url}\nAuthor: {sound.author}',
                                          performer=f'({duration_text}) {sound.description}',
                                          filename=sound.title,
                                          audio_duration=duration.seconds,
                                          thumb_url=sound.spectrum)
    return audio_result


def handle_error(update, context: CallbackContext) -> None:
    error: Exception = context.error
    message = f"{type(error).__name__}: {error}"

    if not any([isinstance(error, NetworkError), isinstance(error, HTTPError)]):
        tb_list = traceback.format_exception(None, error, error.__traceback__)
        tb = ''.join(tb_list)

        if update:
            message += f"\nupdate = {json.dumps(update.to_dict(), indent=2, ensure_ascii=False)}"
        if context:
            message += f"\n\ncontext.bot_data = {context.bot_data}" \
                       f"\n\ncontext.chat_data = {context.chat_data}" \
                       f"\n\ncontext.user_data = {context.user_data}" \
                       f"\n\nTRACEBACK:\n{tb}"
    logger.error(message)


start_cmd_handler = CommandHandler("start", handle_start)
search_query_handler = InlineQueryHandler(handle_search_inline_query, run_async=True)

handlers = [start_cmd_handler, search_query_handler]
