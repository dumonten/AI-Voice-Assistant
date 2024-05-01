from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from analytics.types import EventType
from services import AnalyticsService
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

    AnalyticsService.track_event(
        user_id=message.from_user.id, event_type=EventType.StartCommand
    )

    await message.reply(Strings.HELLO_MSG)
