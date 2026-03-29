from google import genai
import random
import requests
import datetime
import webbrowser
import wikipedia
import pywhatkit
import feedparser
from gtts import gTTS
import pygame
import time
import speech_recognition as sr
from dotenv import load_dotenv
import os

ui_callback = None
stop_speech_flag = False

load_dotenv()
TMDB_API = os.getenv("TMDB_API")

pygame.mixer.init()


def should_stop():
    return stop_speech_flag

def stop_speaking():
    global stop_speech_flag
    stop_speech_flag = True
    pygame.mixer.music.stop()


def speak(text):
    global ui_callback, stop_speech_flag

    if stop_speech_flag:
        return

    print("Lumira:", text)

    if ui_callback:
        ui_callback("Lumira: " + text)

    filename = f"lumira_voice_{int(time.time()*1000)}.mp3"

    try:
        tts = gTTS(text=text, lang="en")
        tts.save(filename)

        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            if stop_speech_flag:
                pygame.mixer.music.stop()
                return
            time.sleep(0.1)

        pygame.mixer.music.stop()
        pygame.mixer.music.unload()

    except Exception as e:
        print("Speech error:", e)

    finally:
        if os.path.exists(filename):
            os.remove(filename)

def listen_command():
    if should_stop():
        return ""

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)

        try:
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
        except:
            return ""

    if should_stop():
        return ""

    try:
        command = recognizer.recognize_google(audio)
        print("You:", command)

        command = command.lower()

        if "stop" in command:
            stop_speaking()
            return ""

        return command

    except:
        return ""

def wish_user():
    if should_stop():
        return

    hour = datetime.datetime.now().hour

    if hour < 12:
        speak("Good Morning")
    elif hour < 18:
        speak("Good Afternoon")
    else:
        speak("Good Evening")

def get_time():
    if should_stop():
        return

    t = datetime.datetime.now().strftime("%H:%M:%S")
    speak(f"The time is {t}")
    return t

def get_weather():
    if should_stop():
        return

    url = "https://api.open-meteo.com/v1/forecast?latitude=19.07&longitude=72.87&current_weather=true"
    data = requests.get(url).json()

    if should_stop():
        return

    temp = data["current_weather"]["temperature"]
    speak(f"The current temperature is {temp} degree celsius")
    return temp


def search_movie(movie, tmdb):
    if should_stop():
        return

    url = f"https://api.themoviedb.org/3/search/movie?api_key={tmdb}&query={movie}"
    data = requests.get(url).json()

    if data["results"]:
        m = data["results"][0]

        if should_stop(): return
        speak(f"Title: {m.get('title')}")

        if should_stop(): return
        speak(f"Rating: {m['vote_average']}")

        if should_stop(): return
        speak(f"Release Date: {m.get('release_date')}")

        if should_stop(): return
        speak(f"Overview: {m.get('overview')}")

        return m
    else:
        speak("Movie not found")


def wiki_search(query):
    if should_stop():
        return

    try:
        result = wikipedia.summary(query, sentences=2)

        if should_stop():
            return

        speak(result)
        return result
    except:
        speak("No wikipedia result")


def get_news():
    if should_stop():
        return

    rss_feeds = [
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "http://feeds.bbci.co.uk/news/world/rss.xml",
        "https://www.aljazeera.com/xml/rss/all.xml",
        "https://www.theguardian.com/world/rss",
        "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"
    ]

    feed = feedparser.parse(random.choice(rss_feeds))

    speak("Here are the top news headlines")

    news = []

    for entry in feed.entries[:5]:
        if should_stop():
            return news

        speak(entry.title)
        news.append(entry.title)

    return news


def play_song(song):
    if should_stop():
        return

    speak(f"Playing {song} on YouTube")

    if should_stop():
        return

    pywhatkit.playonyt(song)

def open_website(site):
    if should_stop():
        return

    if "." not in site:
        url = f"https://{site}.com"
    else:
        url = f"https://{site}"

    speak(f"Opening {site}")

    if should_stop():
        return

    webbrowser.open(url)


wake_words = ["lumira", "assistant", "hey"]

def is_wake_word(command):
    return any(word in command for word in wake_words)

def listen_to_wake():
    speak("On idle mode, call me whenever you need me")

    while True:
        if should_stop():
            return

        command = listen_command()

        if should_stop():
            return

        if not command:
            continue

        if is_wake_word(command):
            speak("How can I help you?")
            time.sleep(1)
            break


def execute_command(command, tmdb):
    if should_stop():
        return

    if "time" in command:
        return get_time()

    elif "weather" in command:
        return get_weather()

    elif "news" in command:
        return get_news()

    elif "movie" in command:
        movie_name = command.replace("movie", "").strip()
        return search_movie(movie_name, tmdb)

    elif "wikipedia" in command or "wiki" in command:
        query = command.replace("wikipedia", "").replace("wiki", "").strip()
        return wiki_search(query)

    elif "play" in command:
        song = command.replace("play", "").strip()
        play_song(song)

    elif "open" in command:
        site = command.replace("open", "").strip()
        open_website(site)

    elif "exit" in command or "stop" in command:
        speak("Goodbye")
        exit()
    
    elif "shutdown assistant" in command or "turn off" in command:
        speak("Shutting down")
        os.exit(0)