# chatter

Press control-C when you're done speaking to finish recording & prompt a generation. To end the program, use a SIGINT when it is not recording (pressing control-C twice in quick succession should always work)

To run v2, initialize whichever components you would like to use in the ```main``` function in ```chatter_v2.py```. 

Built using OpenAI speech-to-text and text-to-text, as well as ElevenLabs.io voice-to-speech tools.
API keys available with free trials from both provider: store in new file called ``` keys.json ```. Then call ``` python chatter.py ```

Shoutout Perplexity.ai for many helpful code snippets!
