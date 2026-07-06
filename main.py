"""
Python Voice Assistant - Entry Point
Run this file to start the application.

Usage:
    python main.py
"""

from gui import VoiceAssistantGUI


def main():
    """Launch the Voice Assistant GUI."""
    app = VoiceAssistantGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
