import requests  # Import the requests library
from flask import Flask, jsonify, request, send_from_directory
import sounddevice as sd
import scipy.io.wavfile as wavfile
import speech_recognition as sr
import random
import json
import os
import subprocess
import time

app = Flask(__name__)

# Define services to be run in separate processes
services = [
    {"name": "record", "port": 5001, "script": "record.py"},
    {"name": "transcribe", "port": 5002, "script": "transcribe.py"},
    {"name": "feedback", "port": 5003, "script": "feedback.py"},
]

processes = []

# Start the services
for service in services:
    process = subprocess.Popen(["python", service["script"]])
    processes.append(process)
    print(f"Starting service {service['name']} on port {service['port']}")

# Wait for services to be ready
time.sleep(5)

# Load French sentences from JSON file
with open('./french_sentences.json', 'r', encoding='utf-8') as f:
    french_sentences = json.load(f)

@app.route('/')
def index():
    return send_from_directory('./template/', 'index.html')

@app.route('/get_sentence')
def get_sentence():
    selected_sentence = random.choice(french_sentences)
    return jsonify({"sentence": selected_sentence})

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
        transcribe_response = requests.post("http://localhost:5002/transcribe", json={"audio_file": audio_file})
        
        if transcribe_response.status_code != 200:
            return jsonify({"error": f"Transcription failed with status {transcribe_response.status_code}"}), transcribe_response.status_code
        
        transcribe_data = transcribe_response.json()
        recognized_text = transcribe_data.get('recognized_text', "")

        if not recognized_text:
            return jsonify({"error": "No recognized text from transcription."}), 400

        # Get feedback from the feedback service
        feedback_response = requests.post("http://localhost:5003/feedback", json={"recognized_text": recognized_text, "reference_phrase": selected_sentence})
        
        if feedback_response.status_code != 200:
            return jsonify({"error": f"Feedback failed with status {feedback_response.status_code}"}), feedback_response.status_code
        
        feedback_data = feedback_response.json()
        feedback = feedback_data.get('feedback', [])
        match = feedback_data.get('match', False)

        # Return the processed results
        return jsonify({"recognized_text": recognized_text, "feedback": feedback, "match": match})

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(port=5000)

# Terminate the services at the end
for process in processes:
    process.terminate()