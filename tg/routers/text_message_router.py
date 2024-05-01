import os

from aiogram import F
from aiogram.dispatcher.router import Router
from aiogram.types import FSInputFile, Message

from services import AssistantService, TtsService
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

    await message.answer(Strings.WAIT_MSG)

    try:
        # Request a response from the AssistantService.
        response = await AssistantService.request(message.from_user.id, message.text)

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
        print(f"Error: {e}")
        return
