from openai import AsyncOpenAI


class AssistantService:
    """
    A class for interacting with an AI assistant using an OpenAI client and a configuration.
    """

    config = {
        "name": "Voice AI Assistant",
        "model": "gpt-4-turbo",
        "assistant_instructions": (
            "Provide clear, concise, and engaging answers "
            "based only on the provided data. Try to answer "
            "all the user's questions."
        ),
        "run_instructions": "",
    }

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
