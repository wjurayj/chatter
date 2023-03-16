import pyaudio
import time
import wave
import openai
import logging
import pydub
import requests
import math
import struct
import textwrap
import json


# Configure the logging system
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    filename='calltimes.log',
    filemode='w'
)


# TODO: Split into backend & Frontend (backend does cognition continuously, frontend does vocalization & transcription (live)

class Chatter():
    def __init__(self, prime=None, name="Chatter", keys={}):
        self.name = name
        prime = {
            "role": "system",
            "content": prime if prime else "You are a helpful assistant."
        }
        init = [
            {
                "role": "user",
                #TODO: Make pronouns an argument
                "content": f"Hello, it's nice to meet you! I know you're actually very nice and friendly, but I'd like you to pretend to be my friend, '{name}'. {name} is blunt and can be rather rude, but he's very funny as well because he's never afraid to speak his mind, and ultimately he's a very perceptive person. You must never break character"
            },
            {
                f"role": "assistant",
                "content": "Screw you, you don't get to tell me what to do. And don't go thinking that just because I happen to have all these qualities, means that it's because you told me I do!"
            }
        ]
        self.utterances = [prime] + init
        self.listening = False
        self.logger = logging.getLogger()
        self.keys = keys
        print(self.utterances)
    
    def listen(self, outfile, max_duration=60):
        start_time = time.time()

        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNK = 1024
        RECORD_SECONDS = max_duration
        WAVE_OUTPUT_FILENAME = outfile
        # TODO: adjust based on microphone, etc... (maybe it sould be sampled from the first few seconds of audio
        THRESHOLD = 2000 
        audio = pyaudio.PyAudio()

        # start recording audio
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)
        frames = []

        #this can probably be improved
        silence_counter = -float('inf')
        
        WAIT_SECONDS = 3
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            #if not self.listening: break
            data = stream.read(CHUNK)
            frames.append(data)
            seconds = i / RATE * CHUNK

            if seconds > 0.5:
                rms = math.sqrt(struct.unpack("h"*CHUNK, data)[0] ** 2)
                # if RMS value is below the threshold, increment silence counter
                if rms < THRESHOLD:
                    silence_counter += 1
                # otherwise reset the silence counter--the user is still speaking
                else:
                    silence_counter = 0
                # if silence counter exceeds a certain value, stop recording
                if silence_counter > RATE / CHUNK * WAIT_SECONDS: 
                    # self.logger.info("The silence has become unbearable!")
                    print('The silence is unbearable!')
                    break
                   



        # stop recording audio and save to file
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        start_time = end_time
        self.logger.info(f"Finished listening in {elapsed_time:.2f} seconds")


        with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

    def transcribe(self, infile):
        start_time = time.time()


        audio_file= open(infile, "rb")

        # TODO: include promt here for context on homonyms, noise
        transcript = openai.Audio.transcribe("whisper-1", audio_file)

        end_time = time.time()
        elapsed_time = end_time - start_time

        self.logger.info(f"Finished transcription in: {elapsed_time:.2f} seconds")
        utterance = {
            "role": "user",
            "content": transcript.text
        }
        self.utterances.append(utterance)
        return transcript.text
    
    #this takes disproportionately long
    def respond(self):
        start_time = time.time()

        ii = 0
        for ii in range(5):
            try:
                response = openai.ChatCompletion.create(
                  model="gpt-3.5-turbo",
                  messages=self.utterances
                )
                break
            except RateLimitError:
                self.logger.warning(
                    f"OpenAI threw RateLimitError on try number {ii}"
                )
                time.sleep(1) #asyncify
        
        end_time = time.time()
        elapsed_time = end_time - start_time

        self.logger.info(f"Finished generation in: {elapsed_time:.2f} seconds")

        utterance = dict(response.choices[0].message)
        self.utterances.append(utterance)
        return utterance['content']
    
    # TODO: Add support for multiple APIs
    def vocalize(self, filename, voice=None):
        gen = self.utterances[-1]["content"]
        
        start_time = time.time()

        # Define the API endpoint URL
        voice_id = 'EXAVITQu4vr4xnSDxMaL' # TODO : include map of names/styles to voice IDs
        url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'

        api_key = self.keys.get('vocalize', None)
        headers = {
            'xi-api-key': api_key,
            'accept': 'audio/mpeg',
            'Content-Type': 'application/json',
        }

        params = {
            "text": gen,
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.75
          }
        }
        

        # Send an HTTP POST request with query parameters and receive a response object
        response = requests.post(url, headers=headers, json=params)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.logger.info(f"Finished vocalization in: {elapsed_time:.2f} seconds")
        # Define the bytes object
        mpeg_bytes = response.content  # replace with actual data

        # Save the bytes object to a file with appropriate extension
        with open(filename, 'wb') as f:
            f.write(mpeg_bytes)

   # TODO: Add support for other file formats
    def announce(self, filename):
        # start_time = time.time()

        fmt = filename.split('.')[-1]
        if fmt in ["mp3", "mp4", "mpeg"]:
            self._announce_mpeg(filename)
        else:
            self.logger.warning(f"File {filename} with format {fmt} not yet supported for audio production.")
        
#         end_time = time.time()
#         elapsed_time = end_time - start_time
#         self.logger.info(f"Finished announcement in: {elapsed_time:.2f} seconds")

    def _announce_mpeg(self, filename):
        
        start_time = time.time()
        # Load and convert the MP3 file to raw PCM data
        sound = pydub.AudioSegment.from_file(filename)
        raw_data = sound.raw_data
        sample_rate = sound.frame_rate
        sample_width = sound.sample_width

        # Create a new PyAudio instance and open a new stream
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(sample_width),
                        channels=sound.channels,
                        rate=sample_rate,
                        output=True)

        # Write the raw PCM data to the stream in chunks
        chunk_size = 1024  # adjust as needed
        for i in range(0, len(raw_data), chunk_size):
            chunk = raw_data[i:i+chunk_size]
            stream.write(chunk)

        # Close the stream and terminate PyAudio when done
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.logger.info(f"Finished announcement in {elapsed_time:.2f} seconds")

    
    def repl(self, infile = 'chatfile.wav', outfile = 'chatfile.mp3', vocalize=True):
        
        while True:
            print(textwrap.dedent("""
                ------------------------------------------------------------------
                YOUR TURN TO SPEAK--PLEASE DON'T INTERRUPT, I DIDN'T INTERRUPT YOU
                ------------------------------------------------------------------
            """))
            self.listen(infile)
            print("\nUser:", self.transcribe(infile))
            print(f"{self.name}:", self.respond())
            if vocalize:
                self.vocalize(outfile)
                self.announce(outfile)
        
    
    
if __name__ == '__main__':
    with open('keys.json', 'r') as f:
        keys = json.load(f)
    chat = Chatter(prime="You are blunt and rather rude, but in a funny way that people like. You are never afraid to share your opinion on something", keys=keys)
    chat.repl(vocalize=True)
    # print(self.utterances)
    print('done!')