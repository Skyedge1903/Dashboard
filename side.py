import json
import pandas as pd
from datetime import datetime

# Vos données JSON (remplacez ceci par votre JSON ou chargez-le depuis un fichier)
with open("data/hash-rate.json", "r") as f:
    data = json.load(f)

# Extraire les données de hash-rate et market-price
hash_rate_data = data["hash-rate"]
market_price_data = data["market-price"]

# Convertir les données en DataFrame
hash_rate_df = pd.DataFrame(hash_rate_data)
market_price_df = pd.DataFrame(market_price_data)

# Renommer les colonnes
hash_rate_df.columns = ["timestamp", "hash_rate"]
market_price_df.columns = ["timestamp", "market_price"]

# Convertir les timestamps (en millisecondes) en dates
hash_rate_df["timestamp"] = hash_rate_df["timestamp"].apply(lambda x: datetime.fromtimestamp(x / 1000).strftime('%Y-%m-%d'))
market_price_df["timestamp"] = market_price_df["timestamp"].apply(lambda x: datetime.fromtimestamp(x / 1000).strftime('%Y-%m-%d'))

# Fusionner les deux DataFrames sur la colonne timestamp
merged_df = pd.merge(hash_rate_df, market_price_df, on="timestamp", how="outer")

# Renommer la colonne timestamp en Date
merged_df = merged_df.rename(columns={"timestamp": "Date"})

# Trier par date
merged_df = merged_df.sort_values("Date")

# Sauvegarder en CSV
merged_df.to_csv("data.csv", index=False)

print("Le fichier 'data.csv' a été créé avec succès !")