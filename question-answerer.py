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

If search_docs returns "No relevant documentation found", say "I don't know".
Do NOT answer from memory. If search_docs returns relevant documentation, use that to answer the question.
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

def search_docs(query):
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json"
        response = requests.get(url).json()
        if response.get("Abstract"):
            return response["Abstract"]
        return "No relevant documentation found"
    except Exception as e:
        return f"Error during search: {str(e)}" 


def explain_code(code, language="python"):
    return f"""
Explain the following {language} code:

{code}

Provide:
1. Summary
2. Step-by-step explanation
3. Time complexity
4. Space complexity
5. Potential improvements
"""

#Tool caller
def call_tool(tool_name, parameters):
    if tool_name == "search_docs":
        return search_docs(parameters["query"])
    
    elif tool_name == "run_code":
        # Implement code execution logic here
        return "Code execution not implemented yet."
    
    elif tool_name == "explain_code":
        return explain_code(parameters["code"])
    
    else:
        return f"Unknown tool: {tool_name}"
