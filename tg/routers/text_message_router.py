import os

from aiogram import F
from aiogram.dispatcher.router import Router
from aiogram.types import FSInputFile, Message
from loguru import logger

from analytics.types import EventType
from services import AnalyticsService, AssistantService, TtsService
from utils import Strings

router = Router()


@router.message(F.text)
async def text_message(message: Message):
    """
    Handles text messages by sending a wait message to the user, processing the text with the AssistantService,
    converting the response to speech with the TtsService, and sending the speech audio back to the user.

    Parameters:
    - message (Message): The message object received from the user.

    Returns:
    - None
    """

    AnalyticsService.track_event(
        user_id=message.from_user.id, event_type=EventType.TextMessageSent
    )

    await message.answer(Strings.WAIT_MSG)

    try:
        response = await AssistantService.request(message.from_user.id, message.text)

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
        logger.info(f"Error in text_message_router: {e}")
