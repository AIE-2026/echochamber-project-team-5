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
"""
EchoChamber Studio - app.py
===========================
A simulation of discursive bubbles using Romanian political comments.
... (poți lăsa comentariul tău original aici)
"""

# =====================================================================
# 1. IMPORTS & SETUP
# =====================================================================
import os
from dotenv import load_dotenv

# Încărcăm variabilele de mediu din fișierul .env local
load_dotenv()

# Încercăm să importăm configurația din core/config.py (dacă e gata)
try:
    from core import config
    print("[INFO] Configurația core/config.py a fost încărcată cu succes.")
except ImportError:
    print("[WARN] core/config.py nu a fost găsit sau are erori. Folosim fallback local.")
    config = None


# =====================================================================
# 3. HELPER FUNCTIONS (Simulare apeluri LLM)
# =====================================================================
def call_main_model(prompt: str) -> str:
    """Simulează apelul către modelul principal (e.g., GPT-4 sau Gemini)."""
    # Dacă nu există cheie în .env, simulăm o eroare pentru a testa fallback-ul
    if not os.getenv("MAIN_MODEL_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Main model API key missing!")
    
    return f"[Main Model] Răspuns la promptul: '{prompt}'"


def call_fallback_model(prompt: str) -> str:
    """Simulează apelul către modelul de rezervă dacă cel principal eșuează."""
    return f"[Fallback Model] Modelul principal a picat. Răspuns de rezervă pentru: '{prompt}'"


# =====================================================================
# 8. LAUNCH (Rularea în terminal)
# =====================================================================
if __name__ == "__main__":
    print("--- Aplicația EchoChamber a pornit ---")
    
    # 1. Utilizatorul scrie un prompt
    user_prompt = input("Introduceți un prompt pentru model: ")
    
    if not user_prompt.strip():
        user_prompt = "Test prompt implicit"
        print(f"Nu ai introdus nimic. Folosim: '{user_prompt}'")

    # 2 & 4. Trimite promptul și testează Fallback-ul dacă pică
    try:
        print("\n[Trimitere] Se apelează modelul principal...")
        response = call_main_model(user_prompt)
    except Exception as e:
        print( earth_colors = f"\n[Eroare Model Principal]: {e}")
        print("[Fallback] Se încearcă modelul de rezervă...")
        response = call_fallback_model(user_prompt)
    
    # 3. Aplicația printează răspunsul
    print("\n================ RĂSPUNS ================")
    print(response)
    print("=========================================\n")