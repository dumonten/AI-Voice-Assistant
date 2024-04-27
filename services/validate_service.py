import json

from openai import AsyncOpenAI


class ValidateService:
    """
    ValidateService is a class responsible for validating key values identified by the user.
    It uses an asynchronous client to interact with an external service for validation.
    """

    # A dictionary containing configuration options for the speech service, such as the model to use.
    config = {
        "model": "gpt-4-turbo",
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "validate_value",
                    "description": (
                        "Use this function to accurately determine the correctness of the key life values identified by the user. "
                        "If multiple key values are present, they will be delineated by commas. "
                        "The outcome of this evaluation is a boolean value, "
                        "indicating whether the data is accurate (True) or not (False)."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "isCorrect": {
                                "type": "boolean",
                                "description": (
                                    "Conditions for a 'True' Value:\n"
                                    "- No Nonsensical Words: The identified meanings should not include meaningless or 'crazy' words.\n"
                                    "- Mutual Exclusivity: Values that are mutually exclusive should not be identified together; for instance, 'love' and 'cruelty' are contradictory and should not be present together.\n"
                                    "- No Overly General Values: The system should refrain from defining overly broad or generalized values that do not provide a specific insight into the user's preferences or beliefs, such as 'good' or 'bad,' which may be too vague to be useful.\n"
                                    "Conditions for a 'False' Value:\n"
                                    "- Anything That Does Not Meet the Conditions for 'True'\n"
                                    "- Empty String"
                                ),
                            },
                        },
                        "required": ["isCorrect"],
                    },
                },
            },
        ],
    }

    # An OpenAI client for making requests to the speech service.
    async_client = None

    @classmethod
    def initialize(cls, async_client: AsyncOpenAI):
        """
        Initializes the SttService with an instance of AsyncOpenAI.

        Parameters:
        - async_client (AsyncOpenAI): An instance of AsyncOpenAI to use for making requests to the speech service.
        """

        cls.async_client = async_client

    @classmethod
    async def validate_key_values(cls, messages: str) -> bool:
        """
        Validates the key values identified by the user.

        This method checks the correctness of the key life values identified by the user.
        It uses the async client to create a chat completion, which involves processing the user's messages
        with a specified function to evaluate the values for accuracy.

        Parameters:
        - messages (str): The messages received from the user, which contain the key values to be validated.

        Returns:
        - bool: True if the values are correct, False otherwise or if an exception occurs.
        """

        if cls.async_client is None:
            raise ValueError(
                "async_client must be initialized before calling speech_to_text."
            )

        try:
            response = await cls.async_client.chat.completions.create(
                model=cls.config["model"],
                messages=messages,
                tools=cls.config["tools"],
                tool_choice={
                    "type": "function",
                    "function": {"name": "validate_value"},
                },
            )
            output = response.choices[0].message.tool_calls[0]
            arguments_dict = json.loads(output.function.arguments)
            return arguments_dict["isCorrect"]
        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            return False
