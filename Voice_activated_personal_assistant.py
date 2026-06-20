import speech_recognition as sr
from gtts import gTTS
import requests
import feedparser
import pygame
import time
from datetime import datetime
from zoneinfo import ZoneInfo
import threading
import os


# ---------------------------
# TEXT TO SPEECH
# ---------------------------

pygame.mixer.init()

def speak(text):
    print(f"\nAssistant: {text}")

    tts = gTTS(text=text, lang="en")
    filename = "response.mp3"

    tts.save(filename)

    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    try:
        os.remove(filename)
    except:
        pass


# ---------------------------
# SPEECH RECOGNITION
# ---------------------------

def listen():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("\nListening...")
        recognizer.adjust_for_ambient_noise(source)

        try:
            audio = recognizer.listen(source, timeout=5)

            command = recognizer.recognize_google(audio)

            print("You:", command)

            return command.lower()

        except sr.UnknownValueError:
            return ""

        except Exception:
            return ""


# ---------------------------
# TIME
# ---------------------------

def get_time():
    ist_time = datetime.now(
        ZoneInfo("Asia/Kolkata")
    )

    return ist_time.strftime("%I:%M %p IST")


# ---------------------------
# WEATHER
# ---------------------------

def get_weather(city):

    try:
        geo_url = (
            f"https://geocoding-api.open-meteo.com/"
            f"v1/search?name={city}&count=1"
        )

        geo_response = requests.get(
            geo_url,
            timeout=10
        ).json()

        if "results" not in geo_response:
            return "City not found."

        latitude = geo_response["results"][0]["latitude"]
        longitude = geo_response["results"][0]["longitude"]

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={latitude}&longitude={longitude}"
            f"&current=temperature_2m"
        )

        weather_response = requests.get(
            weather_url,
            timeout=10
        ).json()

        temperature = weather_response["current"][
            "temperature_2m"
        ]

        return (
            f"The current temperature in "
            f"{city} is {temperature} degree Celsius."
        )

    except:
        return "Unable to fetch weather information."


# ---------------------------
# NEWS
# ---------------------------

def get_news():

    try:
        feed = feedparser.parse(
            "https://feeds.bbci.co.uk/news/rss.xml"
        )

        headlines = []

        for entry in feed.entries[:5]:
            headlines.append(entry.title)

        return headlines

    except:
        return []


# ---------------------------
# REMINDER
# ---------------------------

def reminder_worker(message, seconds):

    time.sleep(seconds)

    speak(f"Reminder: {message}")


def set_reminder(message, seconds):

    threading.Thread(
        target=reminder_worker,
        args=(message, seconds),
        daemon=True
    ).start()

    speak(
        f"Reminder set for {seconds} seconds."
    )


# ---------------------------
# COMMAND PROCESSOR
# ---------------------------

def process_command(command):

    command = command.lower().strip()

    # Greetings
    if any(word in command for word in [
        "hello",
        "hi",
        "hey"
    ]):
        speak(
            "Hello, how can I help you?"
        )

    # Time
    elif "time" in command:

        speak(
            f"The current time is {get_time()}"
        )

    # Weather
    elif any(word in command for word in [
        "weather",
        "temperature",
        "forecast"
    ]):

        city = input(
            "Enter city name: "
        )

        speak(
            get_weather(city)
        )

    # News
    elif "news" in command:

        headlines = get_news()

        if not headlines:
            speak(
                "Unable to fetch news."
            )
            return

        speak(
            "Here are the latest headlines."
        )

        for i, item in enumerate(
            headlines,
            start=1
        ):
            speak(
                f"Headline {i}: {item}"
            )

    # Reminder
    elif "remind" in command:

        try:
            seconds = int(
                input(
                    "Reminder time (seconds): "
                )
            )

            message = input(
                "Reminder message: "
            )

            set_reminder(
                message,
                seconds
            )

        except:
            speak(
                "Invalid reminder."
            )

    # Exit
    elif any(word in command for word in [
        "exit",
        "quit",
        "bye"
    ]):

        speak("Goodbye.")
        return False

    else:

        speak(
            "Sorry, I did not understand that."
        )

    return True


# ---------------------------
# MAIN
# ---------------------------

def main():

    speak(
        "Hello, I am your personal assistant."
    )

    while True:

        print(
            "\n1. Voice Command"
        )
        print(
            "2. Type Command"
        )

        choice = input(
            "\nChoose option: "
        )

        if choice == "1":

            command = listen()

            if command:

                if process_command(command) is False:
                    break

        else:

            command = input(
                "\nYou: "
            )

            if process_command(command) is False:
                break


if __name__ == "__main__":
    main()