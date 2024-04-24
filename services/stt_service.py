class SttService:
    """
    A class for converting speech to text using an OpenAI client and a configuration.
    """

    def __init__(self, async_client, config):
        """
        Initializes the speech-to-text service with an OpenAI client and a configuration.

        Parameters:
        - async_client: An OpenAI client for making requests to the speech service.
        - config: A dictionary containing configuration options for the speech service, such as the model to use.
        """
        self.async_client = async_client
        self.config = config

    def speech_to_text(self, path_to_file):
        """
        Converts the speech in the given audio file to text.

        Parameters:
        - path_to_file: The path to the audio file containing the speech to be converted.

        Returns:
        - The transcription of the speech as text.
        """
        audio_file = open(path_to_file, "rb")
        transcription = self.async_client.audio.transcriptions.create(
            model=self.config["model"], file=audio_file, response_format="text"
        )
        return transcription
