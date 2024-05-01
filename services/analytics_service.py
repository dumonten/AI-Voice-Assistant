from concurrent.futures import ThreadPoolExecutor

from analytics.amplitude import AmplitudeLogger


class AnalyticsService:
    """
    Manages assistant operations with Amplitude analytics using a thread pool.
    """

    # ThreadPoolExecutor for asynchronous event tracking.
    executor = ThreadPoolExecutor(max_workers=5)

    # AmplitudeLogger instance for tracking events.
    tracker = AmplitudeLogger()

    @classmethod
    def track_event(cls, user_id: int, event_type: str, event_properties: str = ""):
        """
        Asynchronously tracks an event in Amplitude using the executor.

        Args:
            user_id (int): User ID.
            event_type (str): Event type.
            event_properties (str): Event properties in JSON-like string.
        """

        cls.executor.submit(
            cls.tracker.track_event, user_id, event_type, event_properties
        )
