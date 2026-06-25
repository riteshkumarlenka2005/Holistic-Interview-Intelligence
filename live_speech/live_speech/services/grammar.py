import requests

LT_SERVER = "http://localhost:8081"  # Local LanguageTool server

def check_grammar(text):
    try:
        resp = requests.post(
            f"{LT_SERVER}/v2/check",
            data={"text": text, "language": "en-US"}
        )
        return resp.json()
    except requests.exceptions.ConnectionError:
        # fallback to public API
        resp = requests.post(
            "https://api.languagetoolplus.com/v2/check",
            data={"text": text, "language": "en-US"}
        )
        return resp.json()
