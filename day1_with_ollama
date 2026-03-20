# imports

import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from IPython.display import Markdown, display
from openai import OpenAI

#There are no env variables required since Ollama is run on local machine
#We will initialize the OpenAI client library to point to my local computer for Ollama
#We need to have ollama installed locally. Now we run "ollama run llama3.2" in the terminal

openai = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')

#Here we define the system prompt and the user prompt
system_prompt = "You are a title generator who generates titles for short stories"

user_prompt = 
"""
He found the old key buried beneath the roots of a dying tree.
No lock in his house matched it, yet he couldn’t bring himself to throw it away.
That night, a door appeared in his dreams—tall, wooden, and humming softly.
When he woke up, the door was standing in his room.
His hands trembled as the key slid in perfectly.
Inside wasn’t a place, but a moment—his childhood, frozen and waiting.
He saw himself laughing, fearless and whole.
A voice whispered, “You can stay, or you can remember.”
He stepped back, tears blurring the edges of the memory.
And when the door vanished, he carried the courage it left behind
"""

#The API from OpenAI expects to recieve messages in this particular format.
messages = [
    {"role":"system","content":system_prompt},
    {"role":"user", "content":user_prompt}
            ]

#Building the response object
response = openai.chat.completions.create(
    model="llama3.2",
    messages=messages
)

print(response.choices[0].message.content)
