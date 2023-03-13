import pyaudio
import time
import wave
import openai
import logging

# Configure the logging system
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    filename='calltimes.log',
    filemode='w'
)



class Chatter():
    def __init__(self, prime=None, name="Chatter"):
        self.name = name
        prime = {
            "role": "system",
            "content": prime if prime else "You are a helpful assistant."
        }
        self.utterances = [prime]
        self.listening = False
        self.logger = logging.getLogger()
    
    def listen(self, outfile, max_duration=60):
        start_time = time.time()

        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNK = 1024
        RECORD_SECONDS = max_duration
        WAVE_OUTPUT_FILENAME = outfile#"output.wav"

        audio = pyaudio.PyAudio()

        # start recording audio
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)
        frames = []

        #this can probably be improved
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            #if not self.listening: break
            try:
                data = stream.read(CHUNK)
                frames.append(data)
            except KeyboardInterrupt:    
                break



        # stop recording audio and save to file
        stream.stop_stream()
        stream.close()
        audio.terminate()

        with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))


        # your code here

        end_time = time.time()
        elapsed_time = end_time - start_time
        self.logger.info(f"Finished listening in {elapsed_time:.2f} seconds")

    def transcribe(self, infile):
        start_time = time.time()


        audio_file= open(infile, "rb")
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

        response = openai.ChatCompletion.create(
          model="gpt-3.5-turbo",
          messages=self.utterances
        )
        
        end_time = time.time()
        elapsed_time = end_time - start_time

        self.logger.info(f"Finished generation in: {elapsed_time:.2f} seconds")

        utterance = dict(response.choices[0].message)
        self.utterances.append(utterance)
        return utterance['content']
    
    def repl(self, filename):
        while True:
            print("speak now or forever hold your peace; press control-C when finished")
            self.listen(filename)
            print("\nUser:", self.transcribe(filename))
            print(f"{self.name}:", self.respond())
        
    
    
if __name__ == '__main__':
    chat = Chatter()
    filename = 'chatfile.wav'
    chat.repl(filename)
    print('done!')