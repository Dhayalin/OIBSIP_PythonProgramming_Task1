"""
Voice input and output handling.
Uses SpeechRecognition for listening and pyttsx3 for speaking.
"""

import speech_recognition as sr
import pyttsx3


class VoiceEngine:
    """Handles microphone input and text-to-speech output."""

    def __init__(self):
        # Speech recognizer uses Google's free web API by default
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.tts_engine = pyttsx3.init()

        # Configure TTS voice settings for a clear, natural sound
        self.tts_engine.setProperty("rate", 165)
        self.tts_engine.setProperty("volume", 1.0)

        # Try to use a female voice if available (sounds more assistant-like)
        voices = self.tts_engine.getProperty("voices")
        for voice in voices:
            if "female" in voice.name.lower() or "zira" in voice.name.lower():
                self.tts_engine.setProperty("voice", voice.id)
                break

    def initialize_microphone(self) -> tuple[bool, str]:
        """
        Detect and configure the default microphone.

        Returns:
            tuple: (success, message)
        """
        try:
            self.microphone = sr.Microphone()
            # Calibrate for ambient noise so recognition works better
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            return True, "Microphone ready."
        except OSError:
            return False, "No microphone detected. Please connect a microphone."
        except Exception:
            return False, "Could not initialize the microphone."

    def listen(self) -> tuple[bool, str]:
        """
        Listen for a voice command from the microphone.

        Returns:
            tuple: (success, recognized_text_or_error_message)
        """
        if self.microphone is None:
            return False, "Microphone is not available."

        try:
            with self.microphone as source:
                # Listen for up to 5 seconds, with 8 seconds max wait
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)

            # Send audio to Google Speech Recognition (requires internet)
            text = self.recognizer.recognize_google(audio)
            return True, text

        except sr.WaitTimeoutError:
            return False, "I didn't hear anything. Please try again."
        except sr.UnknownValueError:
            return False, "Sorry, I couldn't understand that. Please speak clearly."
        except sr.RequestError:
            return False, "Speech service unavailable. Check your internet connection."
        except OSError:
            return False, "Microphone error. Please check your microphone."
        except Exception:
            return False, "An unexpected error occurred while listening."

    def speak(self, text: str) -> None:
        """Convert text to spoken audio using pyttsx3."""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def stop_speaking(self) -> None:
        """Immediately stop any ongoing speech."""
        try:
            self.tts_engine.stop()
        except Exception:
            pass
