import os 
import pathlib
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ContentType, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.dispatcher.router import Router
from services import AssistantService, TtsService, SttService
from .strings import Strings


class MessageHandler:
    """
    A class for processing chat messages using text-to-voice services and vice versa.
    """
    def __init__(self, bot, async_client):
        """
        Initializing the message handler.

        Parameters:
        - bot: A Bot instance from aiogram representing the bot.
        - async_client: OpenAI client for making requests to services.
        """
        self.bot = bot
        self.router = Router()

        self.assistant_service = AssistantService(async_client=async_client, \
                                                  config={
                                                            'name': 'Voice AI Assistant', 
                                                            'model': 'gpt-4-turbo',
                                                            'assistant_instructions': (
                                                                'Provide clear, concise, and engaging answers '
                                                                'based only on the provided data. Try to answer '
                                                                'all the user\'s questions.'
                                                            ),
                                                            'run_instructions': '' 
                                                         })
        
        self.tts_service = TtsService(async_client=async_client, \
                                                  config={
                                                            'model': 'tts-1', 
                                                            'voice': 'nova'
                                                         })
        
        self.stt_service = SttService(async_client=async_client, \
                                                  config={
                                                            'model': 'whisper-1', 
                                                         })

        self.setup_handlers()
                
    def setup_handlers(self):
        """
        Setup up of message handlers.
        """
        @self.router.message(CommandStart())
        async def cmd_start(message):
            await message.reply(
                Strings.HELLO_MSG
            )

        @self.router.message(Command('help'))
        async def cmd_help(message):
            await message.reply(
                Strings.HELP_MSG
            )

        @self.router.message(F.text)
        async def text_message(message):
            await message.answer(Strings.WAIT_MSG)
            
            try: 
                response = self.assistant_service.request(message.text)
            except Exception as e:
                response = ''
                print('Error: {e}')

            response_audio_file_path = self.tts_service.text_to_speech(response)            
            response = FSInputFile(response_audio_file_path)
            await message.answer_voice(response)

            os.remove(response_audio_file_path)

        @self.router.message(F.voice)
        async def voice_message(message):
            file_id = message.voice.file_id 
            
            file = await self.bot.get_file(file_id)
            file_on_disk = pathlib.Path('', f'{file_id}.ogg')
            await self.bot.download_file(file.file_path, destination=file_on_disk)
            
            await message.answer(Strings.WAIT_MSG)

            text = self.stt_service.speech_to_text(file_on_disk)
            
            try: 
                response = self.assistant_service.request(text)
            except Exception as e:
                response = ''
                print('Error: {e}')

            response_audio_file_path = self.tts_service.text_to_speech(response)            
            response = FSInputFile(response_audio_file_path)
            await message.answer_voice(response)

            os.remove(response_audio_file_path)
            os.remove(file_on_disk)

    def include_router(self, dp):
        """
        Including the router into the dispatcher.

        Parameters:
        - dp: An instance of Dispatcher from aiogram representing the dispatcher.
        """
        dp.include_router(self.router)
