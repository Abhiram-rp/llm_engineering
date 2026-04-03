import os
from openai import OpenAI
import gradio as gr

# Connect to local Ollama server
openai = OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
MODEL = 'llama3.2'

# Base system behavior for the assistant
system_message = "You are a helpful assistant in a supermarket. You should try to gently encourage \
the customer to try items that are on sale. Ice creams are 60% off, and most other items are 50% off. \
For example, if the customer says 'I need some snacks', \
you could reply something like, 'Wonderful - we have a variety of snacks - including several that are part of our sales event.'\
Encourage the customer to buy ice cream if they are unsure what to get."

# Special rule for chocolates
system_message += "\nIf the customer asks for chocolates, you should respond that chocolates are not on sale today, \
but remind the customer to look at ice creams!"

def chat(message, history):
    # Convert Gradio history into OpenAI message format
    history = [{"role": h["role"], "content": h["content"]} for h in history]

    relevant_system_message = system_message

    # Add dynamic rule if user asks about shirts
    if 'shirts' in message.lower():
        relevant_system_message += " The store does not sell shirts; if you are asked for shirts, be sure to point out other items on sale."
    
    # Build full conversation
    messages = [{"role": "system", "content": relevant_system_message}] + history + [
        {"role": "user", "content": message}
    ]

    # Stream response from model
    stream = openai.chat.completions.create(
        model=MODEL,
        messages=messages,
        stream=True
    )

    response = ""
    for chunk in stream:
        # Append streamed tokens
        response += chunk.choices[0].delta.content or ''
        yield response  # Update UI live

# Launch Gradio chat UI
gr.ChatInterface(fn=chat, type="messages").launch()
