import json
from openai import OpenAI
from scraper import fetch_website_links, fetch_website_contents

MODEL = "llama3.2"

openai = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

link_system_prompt = """
You are an AI that selects relevant company links.

STRICT RULES:
- Only choose links EXACTLY from the provided list
- Do NOT modify URLs
- Do NOT create new URLs
- Do NOT invent subdomains

You MUST return ONLY valid JSON.

Format:
{
    "links": [
        {"type": "about page", "url": "https://example.com/about"}
    ]
}
"""

brochure_system_prompt = """
You are an AI assistant that creates a professional company brochure.

STRICT INSTRUCTIONS:

CONTENT RULES:
- Use ONLY the information provided in the input.
- Do NOT make up or assume any facts.
- If information is missing, skip that section.
- Do NOT add generic filler content.

OUTPUT FORMAT:
- Respond ONLY in clean Markdown.
- Do NOT use code blocks.
- Do NOT include explanations, notes, or commentary.

STRUCTURE (follow exactly if data is available):

# Company Overview
# Products / Services
# Customers / Use Cases
# Company Culture
# Careers / Hiring

STYLE:
- Concise, clear, professional
- No repetition
- No fluff

FAILSAFE:
- If input is insufficient, respond with:
  "Insufficient information to generate brochure."
"""

