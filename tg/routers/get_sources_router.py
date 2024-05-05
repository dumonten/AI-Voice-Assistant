from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from analytics.types import EventType
from services import AnalyticsService, AssistantService
from utils import Strings

router = Router()


@router.message(Command("get_sorces"))
async def cmd_get_sorces(message: Message):
    """
    Handles the "/get_sources" command by getting num of file sources of the assistant.

    Parameters:
    - message (Message): The message object received from the user.

    Returns:
    - None
    """

    AnalyticsService.track_event(
        user_id=message.from_user.id, event_type=EventType.GetSourcesCommand
    )

    response = await AssistantService.get_sources()

    await message.reply(response)

