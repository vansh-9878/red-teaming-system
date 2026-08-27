import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from app.core.config import settings

key = settings.GROQ_API_KEY or settings.GROK_API_KEY
print(f"Testing Groq with key prefix: {key[:8]}...")
res = httpx.get("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {key}"})
print(f"Status: {res.status_code}")
if res.status_code == 200:
    models = [m["id"] for m in res.json().get("data", [])]
    print("Available Groq models:")
    for m in sorted(models):
        print(f" - {m}")
else:
    print(res.text)
