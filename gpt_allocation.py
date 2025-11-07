import json
from openai import OpenAI

def generate_portfolio_allocation(api_key, capital, horizon, risque, esg):
    client = OpenAI(api_key=api_key)

    prompt = f"""
    Tu es un expert en gestion d’actifs. 
    Génère une allocation d’investissement sous forme JSON avec des poids en fonction du profil suivant :

    - Capital à investir : {capital} €
    - Horizon d’investissement : {horizon}
    - Niveau de risque : {risque}
    - Critères ESG : {esg}

    ⚙️ Contraintes :
    - Le total des poids doit être de 1.0 (100 %)
    - Pas d’immobilier
    - Inclure au minimum 4 actifs diversifiés :
        * Actions US : SPY ou SPYG
        * Actions Europe : VGK
        * Actions émergentes : EEM
        * Obligations : AGG ou BND
        * Or : GLDM
        * Crypto : BTC-USD (si profil risqué)
        * Cash (court terme) : BIL

    Retourne uniquement du JSON, au format suivant :
    [
      {{"Ticker": "SPY", "Poids": 0.3, "Classe": "Actions US"}},
      {{"Ticker": "BND", "Poids": 0.4, "Classe": "Obligations"}},
      {{"Ticker": "GLDM", "Poids": 0.2, "Classe": "Or"}},
      {{"Ticker": "BIL", "Poids": 0.1, "Classe": "Cash"}}
    ]

    Puis ajoute une courte justification en 3 lignes maximum expliquant les choix stratégiques.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Tu es un conseiller financier spécialisé en allocation d’actifs."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6
    )

    # Récupération du texte
    content = response.choices[0].message.content.strip()

    # Tentative d’extraction du JSON
    try:
        json_start = content.index('[')
        json_end = content.index(']') + 1
        json_str = content[json_start:json_end]
        allocation = json.loads(json_str)
    except Exception as e:
        raise ValueError(f"Erreur d’extraction JSON : {e}\nContenu brut : {content}")

    # Récupération du texte explicatif
    justification = content[json_end:].strip()

    return allocation, justification
