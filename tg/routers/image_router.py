import os
import pathlib

from aiogram import F
from aiogram.dispatcher.router import Router
from aiogram.types import FSInputFile, Message
from loguru import logger

from analytics.types import EventType
from config import settings
from services import AnalyticsService, AssistantService, EmotionService, TtsService
from utils import Strings

router = Router()
bot = settings.bot


@router.message(F.photo)
async def image(message: Message):
    """
    Handles messages with image by sending a wait message to the user, processing the image with the EmotionService,
    converting the response to speech with the TtsService, and sending the speech audio back to the user.

    Parameters:
    - message (Message): The message object received from the user.

    Returns:
    - None
    """

    AnalyticsService.track_event(
        user_id=message.from_user.id, event_type=EventType.ImageSent
    )

    await message.answer(Strings.WAIT_MSG)

    file = await bot.get_file(message.photo[-1].file_id)
    file_on_disk = pathlib.Path("", f"{message.photo[-1].file_id}.jpg")
    await bot.download_file(file.file_path, destination=file_on_disk)

    emotion_state = await EmotionService.identify_emotions(file_on_disk)
    os.remove(file_on_disk)

    try:
        # Request a response from the AssistantService.
        response = await AssistantService.request(
            message.from_user.id, Strings.EMOTION_STATE_USER_ANS + emotion_state
        )

        await message.answer(response)

        # Convert the response text to speech.
        response_audio_file_path = await TtsService.text_to_speech(response)
        # Prepare the audio file for sending.
        response = FSInputFile(response_audio_file_path)
        # Send the speech audio back to the user.
        await message.answer_voice(response)
        # Clean up the temporary audio file.
        os.remove(response_audio_file_path)
    except Exception as e:
        # Handle any exceptions that occur during the process.
        logger.info(f"Error in image_router: {e}")
