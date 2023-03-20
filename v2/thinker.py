import openai
import asyncio
import json
import logging
import time
import textwrap

# Configure the logging system
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    filename='logs/thinker.log',
    filemode='w'
)

class Thinker:
    def __init__(self, config, logger=None):
        self.name = config.get("name", "Chatter")
        self.model = config.get("model", "gpt-3.5-turbo-0301")
        self.speaker = None
        self.logger = logger if logger else logging.getLogger()
        self.logger.warning(f"Initialized Thinker using model {self.model}")

        prime = {
            "role": "system",
            "content": f"You are {self.name}, a goofy and cheerful but somewhat rude fellow. You are never afraid to speak your mind, even when the truth is unpleasant. You are an extremely perceptive person."
        }
        
        init = [
            {
                "role": "user",
                "content": f"Hello, it's nice to meet you! I know you're actually very nice and friendly, but I'd like you to pretend to be my friend, '{self.name}'. {self.name} is blunt and can be rather rude, but he's very funny as well because he's never afraid to speak his mind, and ultimately he's a very perceptive person. You must never break character"
            },
            {
                f"role": "assistant",
                "content": "Screw you, you don't get to tell me what to do. And don't go thinking that just because I happen to have all these qualities, means that it's because you told me I do!"
            }
        ]
        # init = []

        self.prime = [prime] #+ init
        
        # Track what's actually been said, from user's perspective
        self.utterances = init
    # def respond(self, message):
    def receive(self, message):     
        self.utterances.append({
            "role": "user",
            "content": message
        })
        self.logger.info(f"> {message}")
        
    def verbalize(self):
        pass
    
    def process(self, nfails = 4):
        for i in range(nfails):
            try:
                self._process()
                break
            except openai.error.RateLimitError:
                print(f"Hit rate limit on try #{i}")
                time.sleep(2**i)
                      

    def _process(self):
        #sned request for stream
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.prime + self.utterances,
            temperature=1,
            # max_tokens=256,
            top_p=0.98,
            frequency_penalty=0.5,
            presence_penalty=0.2,
            stream=True
        )
        
        utterance = ""
        buffer = ""
        for chunk in response:
            ch = chunk['choices'][0]['delta'].get('content', '')
            buffer += ch
            print(ch, end="", flush=True)
            if '\n' in ch: #break down by more frequent/all punctuation, like a period?
                #send to speaker by paragraph, etc.
                if self.speaker:
                    # print('verbalizing!')
                    
                    #this blocks text rendering a little, which I don't want
                    self.speaker.verbalize(buffer)#, eg
                utterance += buffer
                buffer = ""
                pass
        if buffer:
            if self.speaker: #don't write if we're in a code block; instead the UI should render this
                # print('verbalizing the last bit!')
                self.speaker.verbalize(buffer)
            utterance += buffer
        print()

        self.utterances.append({
            "role": "assistant",
            "content": utterance
        })
        self.logger.info(f"% {utterance}")

        
#         if self.speaker:
#             print('rogering speaker')
#             self.speaker.roger()