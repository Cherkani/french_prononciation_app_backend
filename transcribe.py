from flask import Flask, request, jsonify
from flask_cors import CORS
import speech_recognition as sr

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes by default

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio_file' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio_file']
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

if __name__ == "__main__":
    app.run(port=5002)