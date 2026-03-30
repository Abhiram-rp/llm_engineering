#imports
import os
import requests
from IPython.display import Markdown, display

# Three LLMs talking to each other with distinct roles using only Ollama and llama3.2.
agents = [
    {
        "name": "Alex the Analyst",
        "model": "llama3.2",
        "system": "You are Alex the Analyst. You respond with structured, logical, evidence-based observations and you summarize the key points clearly.",
    },
    {
        "name": "Blake the Devil's Advocate",
        "model": "llama3.2",
        "system": "You are Blake the Devil's Advocate. You challenge assumptions, ask sharp questions, and point out where the plan may fail.",
    },
    {
        "name": "Charlie the Synthesizer",
        "model": "llama3.2",
        "system": "You are Charlie the Synthesizer. You listen to the conversation, identify common ground, and produce balanced recommendations.",
    },
]

conversation = [
    {
        "speaker": "Alex the Analyst",
        "text": "Let's discuss how to build a product that will bridge the gap between students and employers by providing opportunities for students to gain real-world experience by helping a small scale company with their project requirements.",
    }
]


#Adding history to the convo so that LLMs give related answers based on context and are not purely predicting based on tokens
def build_prompt(agent):
    history = "\n".join(f"{turn['speaker']}: {turn['text']}" for turn in conversation)
    return (
        f"You are {agent['name']}.\n"
        "The conversation so far is below.\n"
        f"{history}\n\n"
        "Please write the next turn in the conversation in a single reply, matching your role."
    )


def call_agent(agent):
    prompt = build_prompt(agent)
    messages = [
        {"role": "system", "content": agent["system"]},
        {"role": "user", "content": prompt},
    ]

    response = ollama.chat.completions.create(
        model=agent["model"],
        messages=messages,
        max_tokens=220,
        temperature=0.8,
    )

    text = response.choices[0].message.content.strip()
    conversation.append({"speaker": agent["name"], "text": text})
    return text


#Here, we run the convo for 3 rounds
for round_index in range(3):
    display(Markdown(f"## Round {round_index + 1}"))
    for agent in agents:
        text = call_agent(agent)
        display(Markdown(f"**{agent['name']}:** {text}"))
