import json
import time

from openai import AsyncOpenAI

from repositories import UserRepository
from utils import Strings

from .validate_service import ValidateService


class AssistantService:
    """
    A class for interacting with an AI assistant using an OpenAI client and a configuration.
    """

    # A dictionary containing configuration options for the speech service, such as the model to use.
    config = {
        "name": "Voice AI Assistant",
        "model": "gpt-4-turbo",
        "assistant_instructions": (
            "You should engage in a conversation with the user to understand their personal values, "
            "beliefs, and what they consider important in life. You should ask open-ended questions "
            "to encourage the user to share their thoughts and feelings. The goal is to gather insights "
            "into the user's core values, which could include aspects such as family, career, personal growth, "
            "health, and community. You should listen carefully to the user's responses and use them to identify "
            "patterns or recurring themes that reflect the user's life values."
        ),
        "run_instructions": "",
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "save_values",
                    "description": (
                        "Get the key life values of the user."
                        "After you determine the basic values of the user, call this function."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key_values": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": (
                                    "An array of strings representing the user's identified key life values."
                                    "Each string in the array should be a single value that the user has "
                                    "identified as important to their life. Record the values in English."
                                ),
                            }
                        },
                        "required": ["key_values"],
                    },
                },
            },
        ],
    }

    # An OpenAI client for making requests to the speech service.
    async_client = None

    assistant = None

    threads = {}

    @classmethod
    async def initialize(cls, async_client: AsyncOpenAI):
        """
        Initializes the AssistantService with an instance of AsyncOpenAI and creates an assistant.

        Parameters:
        - async_client (AsyncOpenAI): An instance of AsyncOpenAI to use for making requests to the assistant service.
        """

        cls.async_client = async_client
        cls.assistant = await cls.async_client.beta.assistants.create(
            name=cls.config["name"],
            instructions=cls.config["assistant_instructions"],
            model=cls.config["model"],
            tools=cls.config["tools"],
        )

    @classmethod
    async def create_thread(cls, user_id: int) -> str:
        """
        Creates a new thread for a user or conversation.

        Parameters:
        - user_id (int): A unique identifier for the user or conversation.

        Returns:
        - str: The thread ID.
        """

        thread = await cls.async_client.beta.threads.create()
        cls.threads[user_id] = thread.id
        return thread.id

    @classmethod
    async def request(cls, user_id: int, prompt: str) -> str:
        """
        Sends a prompt to the assistant and retrieves the response.

        Parameters:
        - user_id (int): A unique identifier for the user or conversation.
        - prompt (str): The text prompt to send to the assistant.

        Returns:
        - str: The assistant's response as text.

        Raises:
        - Exception: If the run status is not 'completed' or if no assistant message is found.
        """

        if cls.async_client is None:
            raise ValueError(
                "async_client must be initialized before calling speech_to_text."
            )

        if user_id not in cls.threads:
            await cls.create_thread(user_id)

        thread_id = cls.threads[user_id]

        user_message = await cls.async_client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=prompt
        )

        run = await cls.async_client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=cls.assistant.id,
            instructions=cls.config["run_instructions"],
        )

        if run.status == "requires_action":
            tool_outputs = []
            for tool in run.required_action.submit_tool_outputs.tool_calls:
                if tool.function.name == "save_values":
                    is_saved = await cls.save_values(
                        user_id=user_id,
                        key_values=", ".join(
                            json.loads(tool.function.arguments)["key_values"]
                        ),
                    )

                    if is_saved:
                        output = Strings.KEY_VALUES_ARE_DEFINED
                    else:
                        output = Strings.KEY_VALUES_ARE_NOT_DEFINED

                    tool_outputs.append(
                        {
                            "tool_call_id": tool.id,
                            "output": output,
                        }
                    )

                run = await cls.async_client.beta.threads.runs.submit_tool_outputs_and_poll(
                    thread_id=thread_id, run_id=run.id, tool_outputs=tool_outputs
                )

        if run.status == "completed":
            messages = await cls.async_client.beta.threads.messages.list(
                thread_id=thread_id
            )
            if messages.data and messages.data[0].role == "assistant":
                ans = messages.data[0].content[0].text.value
                return ans
            else:
                raise ValueError("No assistant message found")
        else:
            raise ValueError(f'Run status is not <completed>, it\'s "{run.status}".')

    @classmethod
    async def save_values(cls, user_id: int, key_values: str) -> bool:
        """
        Asynchronously saves or updates user values in the database after validation.

        This class method first validates the provided key_values using a validation service.
        If the validation is successful, it attempts to update the user's values in the database.
        If the user does not exist (indicated by a ValueError), it saves the user's values as a new record.
        The method returns a boolean indicating the success of the validation process.

        Parameters:
        - cls (type): The class that this method is bound to.
        - user_id (int): The unique identifier for the user.
        - key_values (str): The key-value pairs to be saved or updated for the user.

        Returns:
        - bool: True if the validation is successful, False otherwise.
        """

        print(f"------> UserId: {user_id}. User KeyValues: {key_values}")

        is_correct = await ValidateService.validate_key_values(key_values)

        if is_correct:
            # If validation is successful, attempt to update the user's values
            user_repo = UserRepository()
            try:
                await user_repo.update_user_values(
                    user_id=user_id, key_values=key_values
                )
                print("------> User values updated successfully.")
            except ValueError as ve:
                try:
                    # If the user does not exist, save the user's values as a new record
                    await user_repo.save_user_values(
                        user_id=user_id, key_values=key_values
                    )
                    print("------> User values saved successfully.")
                except ValueError as ve:
                    print(f"------> Error in DB: {ve}.")
        return is_correct

    @classmethod
    async def clear_context(cls, user_id: int):
        """
        Deletes a thread for a user or conversation.

        Parameters:
        - user_id (int): A unique identifier for the user or conversation.
        """

        if user_id in cls.threads:
            del cls.threads[user_id]
