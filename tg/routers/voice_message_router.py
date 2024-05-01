import os
import pathlib

from aiogram import F
from aiogram.dispatcher.router import Router
from aiogram.types import FSInputFile, Message
from loguru import logger

from analytics.types import EventType
from config import settings
from services import AnalyticsService, AssistantService, SttService, TtsService
from utils import Strings

router = Router()
bot = settings.bot


@router.message(F.voice)
async def voice_message(message: Message):
    """
    Handles voice messages by downloading the voice message, converting it to text with the SttService,
    processing the text with the AssistantService, converting the response to speech with the TtsService,
    and sending the speech audio back to the user.

    Parameters:
    - message (Message): The message object received from the user.

    Returns:
    - None
    """

    AnalyticsService.track_event(
        user_id=message.from_user.id, event_type=EventType.VoiceMessageSent
    )

    await message.answer(Strings.WAIT_MSG)

    file = await bot.get_file(message.voice.file_id)
    file_on_disk = pathlib.Path("", f"{message.voice.file_id}.ogg")
    await bot.download_file(file.file_path, destination=file_on_disk)

    try:
        text = await SttService.speech_to_text(file_on_disk)
        response = await AssistantService.request(message.from_user.id, text)

        await message.answer(response)

        try:
            response_audio_file_path = await TtsService.text_to_speech(response)
            response = FSInputFile(response_audio_file_path)
            await message.answer_voice(response)
        except Exception as e:
            logger.info(
                f"Error in voice_message_router while converting answer to audio: {e}"
            )
        finally:
            os.remove(response_audio_file_path)
    except Exception as e:
        logger.info(f"Error in voice_message_router: {e}")
    finally:
        os.remove(file_on_disk)
