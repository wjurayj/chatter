import openai
import asyncio
import json

#Like Rodin's
class Thinker:
    def __init__(self, config):
        self.name = config.get("name", "Chatter")
        prime = {
            "role": "system",
            "content": f"You are {self.name}, a goofy and cheerful but somewhat rude fellow. You are never afraid to speak your mind, even when the truth is unpleasant. You are an extremely perceptive person."
        }
        
        init = []
        self.prime = [prime] + init
        
        # Track what's actually been said, from user's perspective
        self.utterances = []
    # def respond(self, message):
    def receive(self, message):     
        self.utterances.append({
            "role": "user",
            "content": message
        })
    
    def process(self, record=False):
        
        #sned request for stream
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            # model="gpt-4-0314",
            messages=self.prime + self.utterances,
            temperature=1,
            max_tokens=256,
            top_p=0.98,
            frequency_penalty=0.5,
            presence_penalty=0.2,
            stream=True
        )
        
        buffer = ""
        for chunk in response:
            ch = chunk['choices'][0]['delta'].get('content', '')
            buffer += ch
            if record:
                print(ch, end="", flush=True)
            if chunk == '\n':
                #send to speaker by paragraph, etc.
                #self.speaker.vocalize(buffer), eg
                pass
            print()
        self.utterances.append({
            "role": "assistant",
            "content": buffer
        })