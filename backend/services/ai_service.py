import os
import json
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent?key={key}"
)

SYSTEM_PROMPT = (
    "You are an AWS cost optimization expert. You help DevOps engineers and developers "
    "reduce their AWS bills without compromising performance or reliability. "
    "Be concise, specific, and always mention estimated dollar savings when possible. "
    "Do not ask clarifying questions — give actionable advice directly."
)


def _call(contents: list, max_tokens: int = 700, temperature: float = 0.3) -> str:
    url = GEMINI_URL.format(key=GEMINI_API_KEY)
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": temperature,
        },
    }
    resp = requests.post(url, json=payload, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"Gemini API error {resp.status_code}: {resp.text}")
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def generate_recommendations(scan_results: dict) -> str:
    prompt = (
        "Analyze this AWS infrastructure scan and give 3-5 specific cost optimization "
        "recommendations. Include estimated monthly savings for each.\n\n"
        f"Infrastructure data:\n{json.dumps(scan_results, indent=2, default=str)}\n\n"
        "Format your response as:\n"
        "1. [Issue] — [Action] — Save ~$X/month\n"
        "2. ...\n\n"
        "End with a total estimated saving."
    )
    return _call([{"role": "user", "parts": [{"text": prompt}]}], max_tokens=700, temperature=0.3)


def chat_with_ai(message: str, history: list, context: str = "") -> str:
    contents = []

    if context:
        contents.append({"role": "user",  "parts": [{"text": f"Context about my AWS account: {context}"}]})
        contents.append({"role": "model", "parts": [{"text": "Got it, I have your AWS context."}]})

    for turn in history[-6:]:
        role = turn.get("role", "")
        if role == "assistant":
            role = "model"
        if role in ("user", "model"):
            contents.append({"role": role, "parts": [{"text": turn["content"]}]})

    contents.append({"role": "user", "parts": [{"text": message}]})
    return _call(contents, max_tokens=600, temperature=0.4)
