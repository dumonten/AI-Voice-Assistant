import asyncio

from aiogram import Bot, Dispatcher
from openai import OpenAI

from config import settings
from utils import MessageHandler


async def main():
    async_client = OpenAI(api_key=settings.OPENAI_KEY)

    bot = Bot(token=settings.BOT_KEY)
    dp = Dispatcher()

    message_handler = MessageHandler(bot=bot, async_client=async_client)
    message_handler.setup_handlers()
    message_handler.include_router(dp=dp)

    print("Bot is started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt or SystemExit:
        print("The bot's work has been interrupted")
