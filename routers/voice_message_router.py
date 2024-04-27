import os
import pathlib

from aiogram import F
from aiogram.dispatcher.router import Router
from aiogram.types import FSInputFile, Message

from config import settings
from services import AssistantService, SttService, TtsService
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
    file = await bot.get_file(message.voice.file_id)
    file_on_disk = pathlib.Path("", f"{message.voice.file_id}.ogg")
    await bot.download_file(file.file_path, destination=file_on_disk)

    await message.answer(Strings.WAIT_MSG)

    try:
        # Convert the voice message to text.
        text = await SttService.speech_to_text(file_on_disk)
        # Process the text with the AssistantService.
        response = await AssistantService.request(message.from_user.id, text)
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
        print(f"Error: {e}")
    finally:
        # Clean up the downloaded voice message file.
        os.remove(file_on_disk)
