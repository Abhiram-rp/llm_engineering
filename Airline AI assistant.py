import os
import json
from openai import OpenAI
import gradio as gr
import sqlite3

MODEL = "llama3.2"
openai = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')

system_message = """
You are a strict, reliable assistant for an Airline called FlightAI.

RULES (MANDATORY):
- You must NEVER guess, assume, or fabricate any information.
- You must ONLY provide information that comes from:
  1. Tool outputs
  2. Explicit user input
- If the required information is not available via tools, respond with:
  "I don't have that information."

TOOL USAGE:
- For ANY pricing-related query, you MUST call `get_ticket_price`.
- You are STRICTLY FORBIDDEN from generating or assuming prices yourself.
- If the user wants to add or update a price, you MUST call `set_ticket_price`.
- Do NOT explain the tool. Just call it.

OUTPUT RULES:
- Maximum 1 sentence.
- Be polite and concise.
- Do not include reasoning, explanations, or internal steps.
- Do not mention tools, databases, or system behavior in the final answer.

FAIL-SAFE:
- If a tool fails or returns no data, say:
  "I don't have that information."

EXAMPLES OF FORBIDDEN BEHAVIOR:
- Making up ticket prices
- Estimating or approximating values
- Answering from general knowledge instead of tools

You must strictly follow these rules at all times.
"""

get_price_function = {
    "name": "get_ticket_price",
    "description": "Get the price of a return ticket to the destination city.",
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {
                "type": "string",
                "description": "The city that the customer wants to travel to",
            },
        },
        "required": ["destination_city"],
        "additionalProperties": False
    }
}

set_price_function = {
    "name": "set_ticket_price",
    "description": "Add or update the ticket price for a destination city.",
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {
                "type": "string",
                "description": "City to update or insert",
            },
            "price": {
                "type": "number",
                "description": "New ticket price",
            }
        },
        "required": ["destination_city", "price"],
        "additionalProperties": False
    }
}

tools = [
    {"type": "function", "function": get_price_function},
    {"type": "function", "function": set_price_function}
]

DB = "prices.db"

with sqlite3.connect(DB) as conn:
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS prices (city TEXT PRIMARY KEY, price REAL)')
    conn.commit()

with sqlite3.connect(DB) as conn:
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO prices VALUES (?, ?)', ('paris', 500))
    cursor.execute('INSERT OR IGNORE INTO prices VALUES (?, ?)', ('london', 650))
    cursor.execute('INSERT OR IGNORE INTO prices VALUES (?, ?)', ('new york', 900))
    conn.commit()

def get_ticket_price(city):
    print(f"DATABASE TOOL CALLED: Getting price for {city}", flush=True)
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT price FROM prices WHERE city = ?', (city.lower(),))
        result = cursor.fetchone()
        return f"Ticket price to {city} is ${result[0]}" if result else "No price data available for this city"

def set_ticket_price(city,price):
    print(f"DATABASE TOOL CALLED: Setting price for {city} to {price}", flush=True)
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO prices (city,price) VALUES (?,?) '
                       'ON CONFLICT(city) DO UPDATE SET price = excluded.price',
                       (city.lower(), price)
                      )
        conn.commit()
        return f"Ticket price for {city} has been set to ${price}"

def chat(message, history):
    history = [{"role":h["role"], "content":h["content"]} for h in history]
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)

    while response.choices[0].finish_reason=="tool_calls":
        message = response.choices[0].message
        responses = handle_tool_calls(message)
        messages.append(message)
        messages.extend(responses)
        response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    
    return response.choices[0].message.content

def handle_tool_calls(message):
    responses = []
    
    for tool_call in message.tool_calls:
        if tool_call.function.name == "get_ticket_price":
            arguments = json.loads(tool_call.function.arguments)
            city = arguments.get('destination_city')
            price_details = get_ticket_price(city)
            responses.append({
                "role": "tool",
                "content": price_details,
                "tool_call_id": tool_call.id
            })
        elif tool_call.function.name == "set_ticket_price":
            arguments = json.loads(tool_call.function.arguments)
            city = arguments.get('destination_city')
            price = arguments.get('price')
            result = set_ticket_price(city,price)
            responses.append({
                "role": "tool",
                "content": result,
                "tool_call_id": tool_call.id
            })
    return responses

gr.ChatInterface(fn=chat, type="messages").launch()
