import asyncio

from aiogram import Dispatcher

from config import settings
from routers import (
    help_command_router,
    start_command_router,
    text_message_router,
    voice_message_router,
)
from services import AssistantService, SttService, TtsService, ValidateService


async def main():
    """
    Initializes the bot, sets up routers for handling different types of messages and commands,
    and starts the bot's polling loop.

    Returns:
    - None
    """
    dp = Dispatcher()

    bot = settings.bot
    async_client = settings.async_client

    # Initialize services with the async client.
    await AssistantService.initialize(async_client=async_client)
    ValidateService.initialize(async_client=async_client)
    SttService.initialize(async_client=async_client)
    TtsService.initialize(async_client=async_client)

    # Include routers for handling different types of messages and commands.
    dp.include_router(start_command_router)
    dp.include_router(help_command_router)
    dp.include_router(text_message_router)
    dp.include_router(voice_message_router)

    print("Bot is started.")
    # Start the bot's polling loop.
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        # Run the main function asynchronously.
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        # Handle keyboard interrupts and system exits gracefully.
        print("The bot's work has been interrupted.")
