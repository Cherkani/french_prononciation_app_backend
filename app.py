import requests
from flask import Flask, jsonify, request, send_from_directory
import sounddevice as sd
import scipy.io.wavfile as wavfile
import speech_recognition as sr
import random
import json
import os
import re
import unicodedata
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load French sentences from JSON file
with open('./french_sentences.json', 'r', encoding='utf-8') as f:
    french_sentences = json.load(f)

@app.route('/')
def index():
    return send_from_directory('./template/', 'index.html')

@app.route('/get_sentence')
def get_sentence():
    selected_sentence = random.choice(french_sentences)
    print(f"Selected sentence: {selected_sentence}")
    return jsonify({"sentence": selected_sentence})

@app.route('/record_audio', methods=['POST'])
def record_audio():
    duration = int(request.json.get('duration', 5))
    filename = request.json.get('filename', "output.wav")
    sample_rate = 44100  # Standard sample rate

    # Enregistrement de l'audio
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
    sd.wait()
    wavfile.write(filename, sample_rate, recording)
    print(f"Enregistrement sauvegardé sous : {filename}")

    return jsonify({"message": f"Recording saved as {filename}", "filename": filename})

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    data = request.json
    audio_file = data.get('audio_file')
    
    if not audio_file or not os.path.exists(audio_file):
        return jsonify({"error": "No audio file provided or file does not exist"}), 400

    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
            recognized_text = recognizer.recognize_google(audio, language="fr-FR")
            return jsonify({"recognized_text": recognized_text})

    except sr.UnknownValueError:
        return jsonify({"error": "Speech Recognition could not understand audio"}), 400
    except sr.RequestError as e:
        return jsonify({"error": f"Error with the recognition service: {e}"}), 500

def normalize_text(text):
    # Supprimer les accents
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    # Supprimer la ponctuation et les tirets
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip().lower()

@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.json
    recognized_text = normalize_text(data.get('recognized_text', ""))
    reference_phrase = normalize_text(data.get('reference_phrase', ""))

    if not recognized_text or not reference_phrase:
        return jsonify({"error": "Missing recognized text or reference phrase"}), 400

    # Word-by-word feedback
    reference_words = reference_phrase.split()
    recognized_words = recognized_text.split()
    feedback = []

    for ref_word, recog_word in zip(reference_words, recognized_words):
        if ref_word == recog_word:
            feedback.append(f"Correct: '{recog_word}'")
        else:
            feedback.append(f"Incorrect: You said '{recog_word}', should be '{ref_word}'")

    # Extra/missing words
    if len(reference_words) < len(recognized_words):
        extra_words = recognized_words[len(reference_words):]
        feedback.append(f"Extra words: {' '.join(extra_words)}")
    elif len(reference_words) > len(recognized_words):
        missing_words = reference_words[len(recognized_words):]
        feedback.append(f"Missing words: {' '.join(missing_words)}")

    match = recognized_text == reference_phrase
    return jsonify({"match": match, "feedback": feedback})

@app.route('/process_audio', methods=['POST'])
def process_audio():
    data = request.json
    audio_file = data.get('audio_file')  # This should be a file path, e.g., 'output.wav'
    selected_sentence = data.get('selected_sentence')

    # Check if audio_file and selected_sentence are present
    if not audio_file or not selected_sentence:
        return jsonify({"error": "Missing audio file or selected sentence"}), 400

    try:
        # Send the audio file to the transcription service
        transcribe_response = transcribe_audio()
        
        if transcribe_response.status_code != 200:
            return jsonify({"error": f"Transcription failed with status {transcribe_response.status_code}"}), transcribe_response.status_code
        
        transcribe_data = transcribe_response.json
        recognized_text = transcribe_data.get('recognized_text', "")

        if not recognized_text:
            return jsonify({"error": "No recognized text from transcription."}), 400

        # Get feedback from the feedback service
        feedback_response = feedback()
        
        if feedback_response.status_code != 200:
            return jsonify({"error": f"Feedback failed with status {feedback_response.status_code}"}), feedback_response.status_code
        
        feedback_data = feedback_response.json
        feedback = feedback_data.get('feedback', [])
        match = feedback_data.get('match', False)

        # Return the processed results
        return jsonify({"recognized_text": recognized_text, "feedback": feedback, "match": match})

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(port=5000)
    
# import requests  # Import the requests library
# from flask import Flask, jsonify, request, send_from_directory
# import sounddevice as sd
# import scipy.io.wavfile as wavfile
# import speech_recognition as sr
# import random
# import json
# import os
# import subprocess
# import time
# import threading
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)

# # Define services to be run in separate processes
# services = [
#     {"name": "record", "port": 5001, "script": "record.py"},
#     {"name": "transcribe", "port": 5002, "script": "transcribe.py"},
#     {"name": "feedback", "port": 5003, "script": "feedback.py"},
# ]

# processes = []

# # Start the services
# for service in services:
#     process = subprocess.Popen(["python", service["script"]])
#     processes.append(process)
#     print(f"Starting service {service['name']} on port {service['port']}")

# # Wait for services to be ready
# time.sleep(5)

# # Load French sentences from JSON file
# with open('./french_sentences.json', 'r', encoding='utf-8') as f:
#     french_sentences = json.load(f)

# @app.route('/')
# def index():
#     return send_from_directory('./template/', 'index.html')

# @app.route('/get_sentence')
# def get_sentence():
#     selected_sentence = random.choice(french_sentences)
#     print(f"Selected sentence: {selected_sentence}")
#     return jsonify({"sentence": selected_sentence})

# @app.route('/process_audio', methods=['POST'])
# def process_audio():
#     data = request.json
#     audio_file = data.get('audio_file')  # This should be a file path, e.g., 'output.wav'
#     selected_sentence = data.get('selected_sentence')

#     # Check if audio_file and selected_sentence are present
#     if not audio_file or not selected_sentence:
#         return jsonify({"error": "Missing audio file or selected sentence"}), 400

#     try:
#         # Send the audio file to the transcription service
#         transcribe_response = requests.post("http://localhost:5002/transcribe", json={"audio_file": audio_file})
        
#         if transcribe_response.status_code != 200:
#             return jsonify({"error": f"Transcription failed with status {transcribe_response.status_code}"}), transcribe_response.status_code
        
#         transcribe_data = transcribe_response.json()
#         recognized_text = transcribe_data.get('recognized_text', "")

#         if not recognized_text:
#             return jsonify({"error": "No recognized text from transcription."}), 400

#         # Get feedback from the feedback service
#         feedback_response = requests.post("http://localhost:5003/feedback", json={"recognized_text": recognized_text, "reference_phrase": selected_sentence})
        
#         if feedback_response.status_code != 200:
#             return jsonify({"error": f"Feedback failed with status {feedback_response.status_code}"}), feedback_response.status_code
        
#         feedback_data = feedback_response.json()
#         feedback = feedback_data.get('feedback', [])
#         match = feedback_data.get('match', False)

#         # Return the processed results
#         return jsonify({"recognized_text": recognized_text, "feedback": feedback, "match": match})

#     except Exception as e:
#         return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# def keep_alive():
#     while True:
#         try:
#             requests.get("http://localhost:5000/")
#         except Exception as e:
#             print(f"Keep-alive request failed: {str(e)}")
#         time.sleep(30)

# if __name__ == "__main__":
#     # Démarrer le thread keep-alive
#     threading.Thread(target=keep_alive, daemon=True).start()
    
#     # Utiliser gunicorn pour démarrer l'application en production
#     from gunicorn.app.wsgiapp import run
#     run()

# # Terminate the services at the end
# for process in processes:
#     process.terminate()