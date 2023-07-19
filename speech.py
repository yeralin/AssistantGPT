"""Google Cloud Speech API client"""

from io import BytesIO

from google.cloud.speech import (RecognitionAudio, RecognitionConfig,
                                 SpeechClient)


class Speech:
    """Speech class for Google Cloud Speech API."""

    def __init__(self):
        self.client = SpeechClient()
        self.config = RecognitionConfig(
            encoding=RecognitionConfig.AudioEncoding.OGG_OPUS,
            sample_rate_hertz=48000,
            language_code='en-US',
        )

    def recognize(self, recording: BytesIO):
        """
        Recognizes the speech in the given audio recording.

        Args:
            recording (BytesIO): The audio content to be recognized.

        Returns:
            str or None: The transcribed speech if recognized, None otherwise.
        """
        recording.seek(0)
        
        # Create RecognitionAudio object with the given content
        audio = RecognitionAudio(content=recording.read())

        # Call the recognize method of the client with the config and audio
        response = self.client.recognize(config=self.config, audio=audio)

        # Check if there are any results in the response
        if len(response.results) > 0:
            # Return the transcribed speech from the first/best result
            return response.results[0].alternatives[0].transcript
        
        return None
