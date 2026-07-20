import os
from google import genai
from google.genai import types

_client = None


def _load_key():
    """
    Loads the Gemini API key.

    Supports two modes:

    1. GEMINI_API_KEY = /path/to/credential/file
       → read the file and return its contents

    2. GEMINI_API_KEY = "actual-api-key-text"
       → treat the value as the key directly
    """
    value = os.getenv("GEMINI_API_KEY", "").strip()
    if not value:
        return ""

    # If value is a path to a file, load it
    if os.path.exists(value):
        try:
            with open(value, "r") as f:
                return f.read().strip()
        except Exception:
            return ""

    # Otherwise treat the value as the actual key
    return value


def get_client():
    """
    Returns a cached Gemini client instance.
    """
    global _client
    if _client is None:
        key = _load_key()
        _client = genai.Client(api_key=key)
    return _client


def ask_gemini(prompt: str) -> str:
    """
    Sends a prompt to Gemini and returns the text response.
    """
    client = get_client()
    try:
        resp = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=256,
                temperature=0.7,
            )
        )
        return resp.text.strip()
    except Exception as e:
        return f"Gemini error: {e}"


def stream_gemini(prompt: str):
    """
    Streams a Gemini response chunk-by-chunk.
    """
    client = get_client()
    try:
        stream = client.models.generate_content_stream(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=256,
                temperature=0.7,
            )
        )
        for chunk in stream:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        yield f"Gemini error: {e}"


def stream_gemini_admin(prompt: str):
    """
    Faster, hotter streaming for admins.
    """
    client = get_client()
    try:
        stream = client.models.generate_content_stream(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=512,
                temperature=0.9,
                top_p=0.95,
                top_k=40,
            )
        )
        for chunk in stream:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        yield f"Gemini error: {e}"


def build_thesis(bio: str) -> str:
    """
    Generates a short RPG-style character thesis.
    """
    client = get_client()
    prompt = f"Generate a concise RPG character thesis for: {bio}"
    try:
        resp = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=128,
                temperature=0.4,
            )
        )
        return resp.text.strip()
    except Exception as e:
        return f"Gemini error: {e}"

def markdown_to_irc(text: str) -> str:
    """
    Minimal Markdown → IRC converter.
    Bold → IRC bold
    Italic → plain
    Code → plain
    """
    if not text:
        return ""

    # Bold: **text**
    text = text.replace("**", "\x02")

    # Strip backticks
    text = text.replace("`", "")

    # Strip underscores used for italics
    text = text.replace("_", "")

    return text


