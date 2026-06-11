import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.llm.groq_client import ask_llm

print(ask_llm("divyang pension scheme kya hai? simple explain karo"))
