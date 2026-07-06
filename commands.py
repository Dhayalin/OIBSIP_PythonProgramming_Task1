
import webbrowser

import requests
import wikipedia

from utils import (
    EXIT_PHRASES,
    GREETING_PHRASES,
    WEBSITES,
    get_current_date,
    get_current_day,
    get_current_time,
    normalize_text,
)


def process_command(text: str) -> tuple[str, bool]:

    command = normalize_text(text)

    
    if any(phrase in command for phrase in EXIT_PHRASES):
        return "Goodbye! Have a great day.", True

    
    if any(phrase in command for phrase in GREETING_PHRASES):
        return _handle_greeting(command)

    
    if "time" in command:
        return f"The current time is {get_current_time()}.", False

    if "date" in command:
        return f"Today's date is {get_current_date()}.", False

    if "day" in command and "today" in command:
        return f"Today is {get_current_day()}.", False

    
    for site_name, url in WEBSITES.items():
        if site_name in command and (
            "open" in command or "launch" in command or "go to" in command or command.strip() == site_name
        ):
            return _open_website(site_name, url)

    
    if "wikipedia" in command or "search wikipedia" in command:
        return _search_wikipedia(command)

    
    return (
        "Sorry, I didn't understand that command. "
        "Try asking for the time, opening a website, or searching Wikipedia.",
        False,
    )


def _handle_greeting(command: str) -> tuple[str, bool]:
    if "good morning" in command:
        return "Good morning! I'm Nova. How can I help you today?", False
    if "good evening" in command:
        return "Good evening! I'm Nova. How can I help you today?", False
    return "Hello! I'm Nova, your voice assistant. How can I help you today?", False


def _open_website(site_name: str, url: str) -> tuple[str, bool]:
    
    try:
        webbrowser.open(url)
        return f"Opening {site_name.capitalize()} for you.", False
    except Exception:
        return f"Sorry, I couldn't open {site_name.capitalize()}.", False


def _search_wikipedia(command: str) -> tuple[str, bool]:

    topic = command
    if "for" in command:
        topic = command.split("for", 1)[1].strip()
    else:
        for word in ("search", "wikipedia", "on", "about"):
            topic = topic.replace(word, "")
        topic = topic.strip()

    if not topic:
        return "Please tell me what you want to search on Wikipedia.", False

    
    if not _has_internet():
        return "No internet connection. Please check your network and try again.", False

    try:
        
        wikipedia.set_lang("en")
        summary = wikipedia.summary(topic, sentences=2)
        return f"Here is what I found about {topic}: {summary}", False
    except wikipedia.exceptions.DisambiguationError as error:
        
        try:
            summary = wikipedia.summary(error.options[0], sentences=2)
            return f"I found multiple results. Here is one about {error.options[0]}: {summary}", False
        except Exception:
            return f"Wikipedia found multiple pages for '{topic}'. Please be more specific.", False
    except wikipedia.exceptions.PageError:
        return f"Sorry, I couldn't find a Wikipedia page for '{topic}'.", False
    except requests.exceptions.RequestException:
        return "Could not reach Wikipedia. Please check your internet connection.", False
    except Exception:
        return "Something went wrong while searching Wikipedia.", False


def _has_internet() -> bool:
    
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except requests.exceptions.RequestException:
        return False
