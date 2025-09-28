import speech_recognition as sr

def listen():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        try:
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            print("🎙️ Listening...")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=7)
            text = recognizer.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            print("⏱️ Timeout: No speech detected.")
            return ""
        except sr.UnknownValueError:
            print("❓ Sorry, I didn’t catch that.")
            return ""
        except sr.RequestError as e:
            print(f"❌ Could not request results from Google: {e}")
            return ""
