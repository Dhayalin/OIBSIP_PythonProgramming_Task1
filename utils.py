from datetime import datetime


APP_NAME = "Nova Assistant"
APP_TAGLINE = "Your intelligent desktop companion"



STATUS_IDLE = "Idle"
STATUS_LISTENING = "Listening"
STATUS_PROCESSING = "Processing"
STATUS_SPEAKING = "Speaking"
STATUS_ERROR = "Error"



MIC_CONNECTED = "Connected"
MIC_DISCONNECTED = "Not Connected"
MIC_CHECKING = "Checking..."



WEBSITES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "gmail": "https://mail.google.com",
}



GREETING_PHRASES = (
    "hello",
    "hi",
    "good morning",
    "good evening",
)


EXIT_PHRASES = (
    "goodbye",
    "exit",
    "stop assistant",
)



def get_current_time() -> str:
    """Return the current time in 12-hour format."""
    return datetime.now().strftime("%I:%M %p")


def get_current_date() -> str:
    """Return today's date."""
    return datetime.now().strftime("%d %B %Y")


def get_current_day() -> str:
    """Return the current weekday."""
    return datetime.now().strftime("%A")


def normalize_text(text: str) -> str:
    """Normalize spoken text."""
    return " ".join(text.lower().strip().split())
