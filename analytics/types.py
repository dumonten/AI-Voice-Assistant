from enum import Enum


class EventType(Enum):
    """
    EventType represents different types of events for analytical business logic.
    """

    ImageSent = "Image sent"
    TextMessageSent = "Text message sent"
    VoiceMessageSent = "Voice message sent"
    KeyValueRevealed = "Key Value revealed"
    ClearCommand = "Clear command"
    StartCommand = "Start command"
    HelpCommand = "Help command"
