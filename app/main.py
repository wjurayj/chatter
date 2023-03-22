import os
import sys
import wave
import time
sys.path.append('../v2')
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from chatter_v2 import Chatter_v2, setup_logger
from thinker import Thinker
import openai#.error import RateLimitError, APIConnectionError

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
def handle_send_text(text, chatter=None):
    chat.thinker.receive(text) #chat needs reworking for web app
    
    gen = my_generator()#chat.think()
    # words = text.split()
    for word in gen:
        emit('receive_word', word)
        socketio.sleep(0.05)  # Adjust this value to control the speed of the word-by-word display
    emit('processing_done')

# ... (previous code)

def generator_wrapper(gen_func):
    def wrapper(*args, **kwargs):
        gen = gen_func(*args, **kwargs)
        has_error = True
        t = 0
        nfails = 4
        # for i in range(nfails):
        #     try:
        #         gen = gen_func(*args, **kwargs)#self._process(webapp)
        #         return gen
        ntries = 4
        for i in range(ntries):
            try:
                # Try to get the first value from the generator
                first_value = next(gen)
                # has_error = False
                break
            except openai.error.RateLimitError:
                print(f"Hit rate limit on try #{i}")
                time.sleep(2**i)
                gen = gen_func(*args, **kwargs)
                
            except openai.error.APIConnectionError:
                print(f"API connection error on try #{i}")
                gen = gen_func(*args, **kwargs)
                time.sleep(2**i)

            except Exception as e:

                # Handle the error (e.g., log it, sleep and retry, etc.)
                print(f"Unknown error occurred: {e}")
                time.sleep(2**t)
                t += 1

                # Add any necessary delay or handling logic here
        yield first_value
        yield from gen

    return wrapper


@generator_wrapper
def my_generator():
    return chat.thinker._process(webapp=True)

        
def save_audio_to_file(audio_data):
    
    file_path = os.path.join('audio_files', f'{time.time()}.wav')

    with wave.open(file_path, 'wb') as wave_file:
        wave_file.setnchannels(1)
        wave_file.setsampwidth(2)  # 2 bytes (16 bits) per sample
        wave_file.setframerate(16000)  # 16 kHz sampling rate
        wave_file.writeframes(audio_data)

if __name__ == '__main__':
    tlogger = setup_logger('thinker', log_file='logs/thinker.log')
    # thinker = Thinker({}, tlogger)
    thinker = Thinker({"model":"gpt-4-0314"}, tlogger)
    chat = Chatter_v2(listener=None, thinker=thinker, speaker=None)
    # chat.repl()
    # chat.save()

    # if not os.path.exists('audio_files'):
    #     os.makedirs('audio_files')
    try:
        socketio.run(app, debug=True)
    except KeyboardInterrupt:
        print('Web server exited from terminal')
    chat.save()