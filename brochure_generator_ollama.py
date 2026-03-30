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

def clean_json(text):
    start = text.find("{")
    end = text.rfind("}") + 1
    return text[start:end]

def get_links_user_prompt(url, links):
    return f"""
Here is a list of links from {url}.

Select the most relevant links for a company brochure.

STRICT RULES:
- Only pick from this list
- Do NOT modify URLs
- Do NOT create new URLs

Links:
{chr(10).join(links)}
"""

def safe_fetch(url):
    try:
        return fetch_website_contents(url)
    except Exception as e:
        print(f"⚠️ Skipping {url}: {e}")
        return ""

def select_relevant_links(url):
    print(f"Selecting relevant links for {url} using {MODEL}")
    
    all_links = fetch_website_links(url)

    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": get_links_user_prompt(url, all_links)}
        ]
    )

    result = response.choices[0].message.content

    try:
        result = clean_json(result)
        parsed = json.loads(result)

        valid_links = set(all_links)
        filtered_links = [
            link for link in parsed.get("links", [])
            if link.get("url") in valid_links
        ]

        print(f"Found {len(filtered_links)} valid links")

        return {"links": filtered_links}

    except Exception as e:
        print("⚠️ JSON parsing failed:", e)
        print("Raw output:", result)
        return {"links": []}

def fetch_page_and_all_relevant_links(url):
    contents = fetch_website_contents(url)
    relevant_links = select_relevant_links(url)

    result = f"## Landing Page:\n\n{contents}\n\n## Relevant Links:\n"

    for link in relevant_links["links"]:
        link_url = link.get("url")
        link_type = link.get("type", "unknown")

        if not link_url:
            continue

        result += f"\n\n### {link_type}\n"
        result += safe_fetch(link_url)

    return result

def generate_brochure(url, company_name):
    print(f"Generating brochure for {company_name}")

    website_content = fetch_page_and_all_relevant_links(url)

    user_prompt = f"""
You are given content from a company website.

Company Name: {company_name}

TASK:
Generate a concise brochure using ONLY the provided content.

STRICT RULES:
- Do NOT invent or assume any information
- Do NOT use external knowledge
- Skip missing sections
- No repetition
- No filler

OUTPUT:
- Clean Markdown only
- No code blocks
- No explanations

--- WEBSITE CONTENT START ---
{website_content}
--- WEBSITE CONTENT END ---
"""

    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": brochure_system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    url = "https://huggingface.co"
    company_name = "Hugging Face"

    brochure = generate_brochure(url, company_name)
    print("\n\n===== FINAL BROCHURE =====\n")
    print(brochure)
