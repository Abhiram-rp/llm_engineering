import os
import json
import requests
from openai import OpenAI
import gradio as gr

MODEL = "llama3.2"
openai = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')

system_message = """
You are a helpful assistant who answers questions about whatever the user asks.
Always be accurate. If you don't know the answer, say so.
"""

search_docs_function = {
    "name": "search_docs",
    "description": "Searches for relevant documents based on a query.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to find relevant documents."
            }
        },
        "required": ["query"]
    }
}

run_code_function = {
    "name": "run_code",
    "description": "Executes a piece of code and returns the output.",
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "The code to be executed."
            }
        },
        "required": ["code"]
    }
}

explain_code_function = {
    "name": "explain_code",
    "description": "Provides an explanation for a given piece of code.",
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "The code to be explained."
            }
        },
        "required": ["code"]
    }
}

tools = [
    {"type": "function", "function": search_docs_function},
    {"type": "function", "function": run_code_function},
    {"type": "function", "function": explain_code_function}
]
