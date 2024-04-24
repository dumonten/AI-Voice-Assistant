
class AssistantService:
    """
    A class for interacting with an AI assistant service using an OpenAI client and a configuration.
    """

    def __init__(self, async_client, config):
        """
        Initializes the assistant service with an OpenAI client and a configuration.

        Parameters:
        - async_client: An OpenAI client for making requests to the assistant service.
        - config: A dictionary containing configuration options for the assistant service, such as the name, model, and instructions.
        """
        self.async_client = async_client
        self.config = config

        self.assistant = self.async_client.beta.assistants.create(
            name=self.config['name'],
            instructions=self.config['assistant_instructions'],
            model=self.config['model'],
        )
        
        self.thread = self.async_client.beta.threads.create()

    def request(self, promt):
        """
        Sends a prompt to the assistant and retrieves the response.

        Parameters:
        - prompt: The text prompt to send to the assistant.

        Returns:
        - The assistant's response as text.

        Raises:
        - Exception: If the run status is not 'completed' or if no assistant message is found.
        """
        user_message = self.async_client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role='user',
            content=promt
        )

        run = self.async_client.beta.threads.runs.create_and_poll(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            instructions=self.config['run_instructions']
        )

        if run.status == 'completed':
            messages = self.async_client.beta.threads.messages.list(
                thread_id=self.thread.id
            )
                
            if messages.data and messages.data[0].role == 'assistant': 
                ans = messages.data[0].content[0].text.value
                return ans
            else: 
                raise Exception('No assistant message found')
        else:
            raise Exception(f'Run status is not <completed>, it\'s "{run.status}".')
