"""
EchoChamber Studio — app.py
===========================
A simulation of discursive bubbles using Romanian political comments.
Each "agent" responds from the perspective of its own political community.

This file is intentionally kept simple and well-commented.
Sociology students: you don't need to understand every line —
focus on the functions that interest you and modify them freely.

Structure:
  1. IMPORTS & SETUP
  2. DESIGN CONSTANTS  (colors, fonts, HTML templates)
  3. HELPER FUNCTIONS  (fetch article, neutral summary, etc.)
  4. TAB 1 — Agents   (all agents respond to same stimulus)
  5. TAB 2 — News     (load article → summarize → chat)
  6. TAB 3 — Debate   (agentic thread with LLM router)
  7. BUILD UI          (assemble the Gradio interface)
  8. LAUNCH
"""

# ─────────────────────────────────────────────────────────────────────────────
# 1. IMPORTS & SETUP
# ─────────────────────────────────────────────────────────────────────────────

import os
from dotenv import load_dotenv
from openai import OpenAI
import google.generativeai as genai

# Incarcam variabilele de mediu din fisierul .env local
load_dotenv()

# Importam configuratia din core/config.py
try:
    from core import config
    print("[INFO] Configuratia core/config.py a fost incarcata cu succes.")
except ImportError as e:
    raise ImportError(
        "Nu s-a putut importa core/config.py. Verifica daca fisierul exista "
        "si daca variabilele din el sunt scrise corect."
    ) from e


# =====================================================================
# 3. HELPER FUNCTIONS
# =====================================================================

def create_gemini_client():
    """
    Configureaza clientul Gemini folosind cheia din .env.
    Cheia NU trebuie scrisa direct in cod.
    """
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("Lipseste GEMINI_API_KEY din fisierul .env")

    genai.configure(api_key=api_key)


def create_openrouter_client():
    """
    Creeaza clientul OpenRouter folosind cheia din .env.
    OpenRouter foloseste clientul OpenAI cu base_url diferit.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise RuntimeError("Lipseste OPENROUTER_API_KEY din fisierul .env")

    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )


def call_main_model(prompt: str) -> str:
    """
    Apeleaza modelul principal configurat in core/config.py.
    In cazul nostru, modelul principal este Gemini.
    """
    create_gemini_client()

    model = genai.GenerativeModel(config.MODEL_PRINCIPAL)

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": config.TEMPERATURE
        }
    )

    return response.text


def call_fallback_model(prompt: str) -> str:
    """
    Apeleaza modelul fallback prin OpenRouter.
    Se foloseste doar daca modelul principal esueaza.
    """
    client = create_openrouter_client()

    response = client.chat.completions.create(
        model=config.MODEL_FALLBACK,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=config.TEMPERATURE
    )

    return response.choices[0].message.content


def ask_model(prompt: str) -> str:
    """
    Trimite promptul catre modelul principal.
    Daca modelul principal esueaza, incearca modelul fallback.
    """
    try:
        print("\n[Trimitere] Se apeleaza modelul principal...")
        return call_main_model(prompt)

    except Exception as e:
        print(f"\n[Eroare Model Principal]: {e}")
        print("[Fallback] Se incearca modelul de rezerva...")
        return call_fallback_model(prompt)


# =====================================================================
# 8. LAUNCH (Rularea in terminal)
# =====================================================================

if __name__ == "__main__":
    print("--- Aplicatia EchoChamber a pornit ---")

    user_prompt = input("Introduceti un prompt pentru model: ")

    if not user_prompt.strip():
        user_prompt = "Explica pe scurt ce este o bula informationala."
        print(f"Nu ai introdus nimic. Folosim: '{user_prompt}'")

    response = ask_model(user_prompt)

    print("\n================ RASPUNS ================")
    print(response)
    print("=========================================\n")