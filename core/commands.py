import webbrowser
import datetime
import os
import subprocess
from core.config.setttings import WEATHER_API_KEY, NEWS_API_KEY
import requests
from core.memory import remember, recall

# Function to execute NirCmd commands
def execute_nircmd(command):
    try:
        # Run the NirCmd command
        subprocess.run(['nircmd.exe', command], check=True)
        return f"Command '{command}' executed successfully."
    except subprocess.CalledProcessError as e:
        return f"Failed to execute the command: {e}"

def get_weather(city="New York"):
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}"
    response = requests.get(url).json()
    temp = response['current']['temp_c']
    condition = response['current']['condition']['text']
    return f"The current temperature in {city} is {temp}°C with {condition}."

def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    response = requests.get(url).json()
    articles = response['articles'][:3]
    headlines = [a['title'] for a in articles]
    return "Here are the top headlines: " + "; ".join(headlines)

def handle_command(text):
    # First, check for system control commands like volume control
    if "mute volume" in text:
        return execute_nircmd('mutesysvolume 1')  # Mute volume
    elif "unmute volume" in text:
        return execute_nircmd('mutesysvolume 0')  # Unmute volume
    elif "set volume to" in text:
        # Extract the volume percentage from the text (e.g., "set volume to 50")
        try:
            volume = int(text.split("set volume to")[-1].strip())
            # Convert percentage to volume level (0-65535)
            volume_level = int(volume * 655.35)
            return execute_nircmd(f'setsysvolume {volume_level}')
        except ValueError:
            return "Sorry, I couldn't understand the volume level."
    elif "open website" in text:
        # Open a website URL
        url = text.split("open website")[-1].strip()
        return execute_nircmd(f'exec show "{url}"')  # Open website

    # Then, check for assistant queries (weather, news, etc.)
    if "weather" in text:
        return get_weather()
    if "news" in text:
        return get_news()
    if "remember my name is" in text:
        name = text.split("is")[-1].strip()
        remember("name", name)
        return f"Got it. I’ll remember your name is {name}."
    if "what's my name" in text:
        name = recall("name")
        return f"Your name is {name}." if name else "I don’t know your name yet."
    if "open google" in text:
        webbrowser.open("https://www.google.com")
        return "Opening Google."
    elif "time" in text:
        return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}"
    elif "open notepad" in text:
        os.system("notepad.exe")
        return "Opening Notepad."

    # If no command matched, handle it as a GPT-style question or a generic query
    return f"Sorry, I didn't understand the command: {text}"

