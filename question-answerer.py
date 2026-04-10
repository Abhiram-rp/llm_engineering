import os
import json
import requests
from openai import OpenAI
import gradio as gr

MODEL = "llama3.2"
openai = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')
