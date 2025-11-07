# gpt_allocation.py
import os
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd

# Charger la clé API depuis le fichier .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ Aucune clé API trouvée dans le fichier .env.")
else:
    print("✅ Clé API détectée.")

# Initialiser le client OpenAI
client = OpenAI(api_key=api_key)

def generate_portfolio_allocation(profile):
    """
    Génère une allocation de portefeuille basée sur le profil investisseur
    grâce à GPT.
    Entrée :
        profile : dictionnaire avec les champs suivants :
            - risk : 'Prudent', 'Équilibré' ou 'Dynamique'
            - horizon : 'court', 'moyen', 'long'
            - capital : montant en euros
            - esg : booléen (optionnel)
    Sortie :
        DataFrame avec les classes d’actifs et leur pourcentage d’allocation
    """
    
    prompt = f"""
    Tu es un expert en gestion d’actifs.
    Crée une allocation de portefeuille cohérente pour ce profil :

    Niveau de risque : {profile.get('risk')}
    Horizon d’investissement : {profile.get('horizon')}
    Capital disponible : {profile.get('capital')} €
    ESG (investissement durable) : {profile.get('esg', False)}

    Réponds sous la forme d’un tableau clair avec 3 colonnes :
    - Classe d’actif
    - Description
    - Pourcentage d’allocation (%)
    Le total doit faire 100%.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        text = response.choices[0].message.content.strip()

        # Conversion texte → DataFrame simple
        lines = [l.split("|") for l in text.split("\n") if "|" in l]
        df = pd.DataFrame(lines[1:], columns=[c.strip() for c in lines[0]])
        df["Pourcentage d’allocation (%)"] = (
            df["Pourcentage d’allocation (%)"].str.replace("%", "").astype(float)
        )
        return df

    except Exception as e:
        print("❌ Erreur API :", e)
        return pd.DataFrame()
