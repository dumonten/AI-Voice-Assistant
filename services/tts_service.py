import uuid


class TtsService:
    """
    A class for converting text to speech using an OpenAI client and a configuration.
    """
    def __init__(self, async_client, config):
        """
        Initializes the text-to-speech service with an OpenAI client and a configuration.

        Parameters:
        - async_client: An OpenAI client for making requests to the speech service.
        - config: A dictionary containing configuration options for the speech service, such as the model and voice to use.
        """
        self.async_client = async_client
        self.config = config

    def text_to_speech(self, text):
        """
        Converts the given text to speech and saves it as an MP3 file.

        Parameters:
        - text: The text to be converted to speech.

        Returns:
        - The path to the generated MP3 file.
        """
        path_to_file = str(uuid.uuid4()) + '.mp3'
        with self.async_client\
                             .audio.speech\
                             .with_streaming_response\
                             .create(model=self.config['model'], 
                                     voice=self.config['voice'], 
                                     input=text) as model: 
            model.stream_to_file(path_to_file)
        return path_to_file
