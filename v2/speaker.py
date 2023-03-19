import json
import requests
import os
import threading
import queue
import time
import logging
import pydub
import pyaudio

# Configure the logging system
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    filename='logs/speaker.log',
    filemode='w'
)

class Speaker:
    def __init__(self, config):
        self.api_key = config.get('api_key', None) #set to none
        self.dir = "./bot_audio/"
        self.queue = queue.Queue()
        self.thinker = None
        self.speaking = False
        self.logger = logging.getLogger()
        self.daemon = None

        
    # TODO: Handle interruptions gracefully--it's not their fault
    def start(self):
        self.daemon = threading.Thread(target=self.run, args=(), daemon=True)
        self.daemon.start()
        

    def run(self):
        self.speaking = True
        while self.speaking or not self.queue.empty():
            thread = self.queue.get()
            # thread = threading.Thread(target=self.proclaim, args=(filename,), daemon=True)
            thread.start()
            thread.join()
        self.logger.info(f"Finished saying all vocalizations in speaker's queue")
        # 
        # self.daemon.start()
    
    # def stop(self):
    #     self.daemon.join()

    def roger(self):
        self.speaking = False
        self.daemon.join()
        self.logger.info("Joined daemon thread--freeing up listener")
        pass
    
    # TODO: Add support for multiple APIs
    
    
    #Bug: doesn't read out all the bits necessarily
    #Problem: the first message *still* takes too long to speak
    def verbalize(self, message):
        self.logger.info(f"Verbalizing message {message}")

        filename = self.formulate(message)
        thread = threading.Thread(target=self.proclaim, args=(filename,), daemon=True)
        self.queue.put(thread)
        if not self.speaking:
            self.start()
                                 
        self.logger.info(f"Started verbalizing {message}")
        
    # def play_queue(self):
        
    def vocalize(self):
        pass
        
    
    def formulate(self, message, voice=None):
        # gen = self.utterances[-1]["content"]
        
        start_time = time.time()

        # Define the API endpoint URL
        voice_id = 'EXAVITQu4vr4xnSDxMaL' # TODO : include map of names/styles to voice IDs
        url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
        # TODO: Stream the audio
        # url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream'

        headers = {
            'xi-api-key': self.api_key,
            'accept': 'audio/mpeg',
            'Content-Type': 'application/json',
        }

        params = {
            "text": message,
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
        
        filename = os.path.join(self.dir, f"{start_time}.mp3")
        with open(filename, 'wb') as f:
            f.write(mpeg_bytes)
            
        # self.queue.put(filename)
        return filename
    

    def _proclaim_mpeg(self, filename):
        
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

        
   # TODO: Add support for other file formats
    def proclaim(self, filename):
        # start_time = time.time()

        fmt = filename.split('.')[-1]
        if fmt in ["mp3", "mp4", "mpeg"]:
            self._proclaim_mpeg(filename)
        else:
            self.logger.warning(f"File {filename} with format {fmt} not yet supported for audio production.")
        
#         end_time = time.time()
#         elapsed_time = end_time - start_time
#         self.logger.info(f"Finished announcement in: {elapsed_time:.2f} seconds")