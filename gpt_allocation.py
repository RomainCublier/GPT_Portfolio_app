# ==========================================
# 📁 gpt_allocation.py
# GPT Portfolio Assistant – Allocation Engine
# ==========================================

import os
import json
from openai import OpenAI

def generate_portfolio_allocation(capital, horizon, risque, esg):
    """
    Génère une allocation de portefeuille avec GPT.
    Retourne une liste de dictionnaires contenant :
    - Ticker
    - Poids
    - Classe (catégorie d’actif)
    """

    # Charger la clé API depuis Streamlit Cloud
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return [{"Ticker": "ERROR", "Poids": 0, "Classe": "Clé API introuvable"}]

    client = OpenAI(api_key=api_key)

    # 🔧 Prompt explicite avec format JSON obligatoire
    prompt = f"""
    Tu es un expert en gestion d'actifs.
    Crée une allocation de portefeuille optimale pour :

    - Capital : {capital} €
    - Horizon d’investissement : {horizon}
    - Niveau de risque : {risque}
    - Intégration ESG : {esg}

    Le total des poids doit faire 1.00 (100%).
    Utilise des ETF et indices connus.

    Renvoie uniquement ta réponse au format JSON suivant :
    {{
        "allocation": [
            {{"Ticker": "SPY", "Poids": 0.30, "Classe": "Actions US"}},
            {{"Ticker": "SX5E", "Poids": 0.25, "Classe": "Actions Europe"}},
            {{"Ticker": "AGG", "Poids": 0.25, "Classe": "Obligations"}},
            {{"Ticker": "GLD", "Poids": 0.20, "Classe": "Or"}}
        ]
    }}
    Pas d’explications, pas de texte supplémentaire — uniquement du JSON valide.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )

        raw_text = response.choices[0].message.content.strip()

        # Essayer de parser la réponse en JSON
        data = json.loads(raw_text)
        return data.get("allocation", [])

    except json.JSONDecodeError:
        return [{"Ticker": "ERROR", "Poids": 0, "Classe": "Réponse GPT non lisible"}]

    except Exception as e:
        return [{"Ticker": "ERROR", "Poids": 0, "Classe": f"Erreur : {str(e)}"}]
