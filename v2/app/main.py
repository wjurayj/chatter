import os
import sys
import wave
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
sys.path.append('..')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/text')
def text():
    return render_template('text.html')

@socketio.on('audio')
def handle_audio(data):
    # Process the incoming audio data
    save_audio_to_file(data)


@socketio.on('send_text')
def handle_send_text(text):
    words = text.split()
    for word in words:
        emit('receive_word', word)
        socketio.sleep(0.2)  # Adjust this value to control the speed of the word-by-word display
    emit('processing_done')

# ... (previous code)

        
def save_audio_to_file(audio_data):
    
    file_path = os.path.join('audio_files', f'{time.time()}.wav')

    with wave.open(file_path, 'wb') as wave_file:
        wave_file.setnchannels(1)
        wave_file.setsampwidth(2)  # 2 bytes (16 bits) per sample
        wave_file.setframerate(16000)  # 16 kHz sampling rate
        wave_file.writeframes(audio_data)

if __name__ == '__main__':
    if not os.path.exists('audio_files'):
        os.makedirs('audio_files')
    socketio.run(app, debug=True)