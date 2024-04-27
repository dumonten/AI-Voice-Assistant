from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from utils import Strings

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Handles the "/start" command by sending a welcome message to the user.

    Parameters:
    - message (Message): The message object received from the user.

    Returns:
    - None
    """
    await message.reply(Strings.HELLO_MSG)
