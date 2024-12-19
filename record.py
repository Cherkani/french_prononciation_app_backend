from flask import Flask, request, jsonify
from flask_cors import CORS
import sounddevice as sd
import scipy.io.wavfile as wavfile

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes by default

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

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5001)