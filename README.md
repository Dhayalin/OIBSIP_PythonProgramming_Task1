# OIBSIP_PythonProgramming_Task1

## Voice Assistant
A modern Python-based Voice Assistant with a Tkinter GUI that performs speech recognition, text-to-speech, website launching, Wikipedia search, and date/time queries through voice commands.
This project was built to learn and implement concepts such as speech recognition, text-to-speech, GUI development, multithreading, and modular programming in Python.

---

## Features

* Modern desktop interface built with CustomTkinter
* Speech recognition using a microphone
* Text-to-speech responses
* Real-time conversation window
* Current time, date, and day information
* Responsive interface using background threads
* Basic error handling for speech recognition and network issues


## Voice Commands

| Category     | Example                                     |
| ------------ | ------------------------------------------- |
| Greeting     | "Hello", "Hi"                               |
| Time         | "What is the time?"                         |
| Date         | "What is today's date?"                     |
| Day          | "What day is today?"                        |
| Open Website | "Open Google", "Open YouTube", "Open Gmail" |
| Wikipedia    | "Search Wikipedia for Python"               |
| Exit         | "Goodbye", "Exit"                           |

## Project Structure

OIBSIP_PythonProgramming_Task1/
 main.py
 gui.py
 voice.py
 commands.py
 utils.py
 requirements.txt
 README.md

File          - Purpose                                       
 
`main.py`     - Starts the application                        
`gui.py`      - Creates and manages the user interface        
`voice.py`    - Handles speech recognition and text-to-speech 
`commands.py`- Processes voice commands                      
`utils.py`    -Stores constants and helper functions         



## Technologies Used

* Python
* CustomTkinter
* SpeechRecognition
* PyAudio
* pyttsx3
* wikipedia
* threading
* datetime
* requests
* webbrowser


## Installation

Install the required packages:

```bash
pip install -r requirements.txt
```

If PyAudio installation fails on Windows:

```bash
pip install pipwin
pipwin install pyaudio
```


## Running the Project

bash
python main.py


After launching the application:

1. Wait until the microphone is ready.
2. Click Start Listening.
3. Speak a supported command.
4. The assistant processes the command and responds through both text and speech.

---

## Workflow

```
User Voice
    ↓
Speech Recognition
    ↓
Command Processing
    ↓
Perform Action
    ↓
Display Response
    ↓
Speak Response

```

## Error Handling

The application handles common situations such as:

Microphone not detected
Unclear speech input
Internet connectivity issues
Unsupported commands
Wikipedia search errors

These messages are displayed in the conversation window to provide clear feedback to the user.
