import json
import asyncio
from listener import Listener
from thinker import Thinker

with open('../keys.json') as f:
    keys = json.load(f)

# Raskin design principle: The user is never wrong
    # Design to make humans' constraints beautiful
class Chatter_v2:
    def __init__(self, listener=None, thinker=None, speaker=None):
        # self.speaker = Speaker()
        self.listener = listener
        self.thinker = thinker
        self.speaker = speaker
        self._interlink()
        pass
    
    def _interlink(self):
        # TODO: make each worker have its own function
        if self.speaker
            self.speaker.set_thinker(self.thinker)
            self.thinker.set_speaker(self.speaker)
    
        if self.listener():
            self.listener.thinker = self.thinker
            self.thinker.listener = self.listener
        
    def run_cycle(self):
        # self.listener.start()
        self.listen()
        self.thinker.process()
        # self.think()
        # self.speaker.speak()
        self.speak()
        
    def listen(self):
        if self.listener:
            self.listener.start()
        else:
            thinker.receive(input("Type your input: "))
    
    def speak(self):
        if self.speaker:
            #self.speaker.speak()
            pass
        else:
            pass
        
    def think(self):
        #think out loud 
        self.thinker.think(record=not self.speaker)
    
    def repl(self):
        while True:
            self.run_cycle()

        
if __name__ == "__main__":
    listener = Listener({})
    thinker = Thinker({})
    chat = Chatter_v2(listener, thinker)
    chat.repl()
