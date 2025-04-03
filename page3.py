from template import Page
import plotly.express as px
import pandas as pd
import numpy as np

# Définition du layout en grille : a en haut à gauche, b en bas à gauche, c à droite, d en bas à droite
grid_layout = ["a a c c", "a a c c", "b b d d", "b b d d"]
page3 = Page(grid_layout)


# --- Fonction pour définir la couleur de fond ---
def update_background_color(fig):
    fig.update_layout(
        paper_bgcolor='#1f2a44',
        plot_bgcolor='#1f2a44',
        geo=dict(
            bgcolor='#1f2a44',
            showcountries=True,
            countrycolor="white",
            showland=True,
            landcolor="#2a3f5f"
        )
    )
    return fig


# --- Partie 1 : Indice Big Mac (Carte a) ---
try:
    df_bigmac = pd.read_csv("data/big-mac-raw-index.csv")
except FileNotFoundError:
    print("Erreur : Fichier 'big-mac-raw-index.csv' introuvable.")
    exit()

# Conversion de la date et tri
df_bigmac['date'] = pd.to_datetime(df_bigmac['date'])
df_bigmac = df_bigmac.sort_values(by='date', ascending=False)

# Sélectionner la donnée la plus récente pour chaque pays
df_latest = df_bigmac.groupby('iso_a3').first().reset_index()
df_latest['USD_percent'] = df_latest['USD'] * 100

# Liste des pays de la zone euro
eurozone_countries = [
    'AUT', 'BEL', 'CYP', 'EST', 'FIN', 'FRA', 'DEU', 'GRC', 'IRL', 'ITA',
    'LVA', 'LTU', 'LUX', 'MLT', 'NLD', 'PRT', 'SVK', 'SVN', 'ESP'
]

# Extraire la valeur de la zone euro (EUZ) pour janvier 2025
eurozone_data = df_bigmac[df_bigmac['iso_a3'] == 'EUZ'].iloc[0]
eurozone_value = eurozone_data['USD'] * 100

# Créer un DataFrame pour les pays de la zone euro
eurozone_df = pd.DataFrame({
    'iso_a3': eurozone_countries,
    'name': ['Autriche', 'Belgique', 'Chypre', 'Estonie', 'Finlande', 'France', 'Allemagne',
             'Grèce', 'Irlande', 'Italie', 'Lettonie', 'Lituanie', 'Luxembourg', 'Malte',
             'Pays-Bas', 'Portugal', 'Slovaquie', 'Slovénie', 'Espagne'],
    'USD_percent': [eurozone_value] * len(eurozone_countries),
    'date': [eurozone_data['date']] * len(eurozone_countries)
})

# Fusionner et nettoyer
df_map = df_latest[df_latest['iso_a3'] != 'EUZ'].copy()
df_map = pd.concat([df_map, eurozone_df], ignore_index=True)

# Ajuster la plage de couleurs pour refléter les variations
min_percent = df_map['USD_percent'].min()
max_percent = df_map['USD_percent'].max()

# Carte a : Indice Big Mac
fig_a = px.choropleth(
    df_map,
    locations="iso_a3",
    color="USD_percent",
    hover_name="name",
    hover_data={"date": True, "USD_percent": ":.2f"},
    color_continuous_scale="RdYlGn",  # Rouge (sous-évalué) à Vert (surévalué)
    range_color=[min_percent, max_percent],
    title="Indice Big Mac - Sur/Sous-évaluation des devises (%) - Janvier 2025",
    labels={'USD_percent': 'Évaluation (%)'},
    projection="natural earth"
)
fig_a.update_geos(fitbounds="locations", visible=True)
fig_a = update_background_color(fig_a)
page3.append('a', fig_a)

# --- Partie 2 : Indice de Dévaluation Relative (Carte b) ---
try:
    df = pd.read_csv("data/API_PA.NUS.FCRF_DS2_en_csv_v2_13510.csv", skiprows=4)
except FileNotFoundError:
    print("Erreur : Fichier 'API_PA.NUS.FCRF_DS2_en_csv_v2_13510.csv' introuvable.")
    exit()

# Sélectionner les colonnes pertinentes (2010-2023)
years = [str(year) for year in range(2010, 2024)]
df = df[['Country Name', 'Country Code'] + years].dropna(subset=years)
df = df.rename(columns={'Country Name': 'name', 'Country Code': 'iso_a3'})

# Convertir en numérique
for year in years:
    df[year] = pd.to_numeric(df[year], errors='coerce')
df = df.dropna(subset=years)

# Calculer la variation et normaliser
df['change_percent'] = ((df['2023'] - df['2010']) / df['2010']) * 100
df['abs_change'] = df['change_percent'].abs()
stable_currencies = df.nsmallest(5, 'abs_change')[['iso_a3', 'name', 'change_percent']]

reference_index = stable_currencies['change_percent'].mean()
df['devaluation_relative'] = df['change_percent'] - reference_index
valid_countries = df[~df['iso_a3'].isin(['WLD', 'ARB', 'AFE', 'AFW', 'TEA', 'TEC', 'TLA', 'TMN', 'TSA', 'TSS', 'UMC'])]

# Normalisation logarithmique
valid_countries['devaluation_log'] = np.log1p(valid_countries['devaluation_relative'].clip(lower=0))
mean_log = valid_countries['devaluation_log'].mean()
std_log = valid_countries['devaluation_log'].std()
valid_countries['devaluation_normalized'] = (valid_countries['devaluation_log'] - mean_log) / std_log

# Ajuster la plage de couleurs
min_deval = valid_countries['devaluation_normalized'].min()
max_deval = valid_countries['devaluation_normalized'].max()

# Carte b : Indice de Dévaluation Relative
fig_b = px.choropleth(
    valid_countries,
    locations="iso_a3",
    color="devaluation_normalized",
    hover_name="name",
    hover_data={"devaluation_relative": ":.2f", "change_percent": ":.2f"},
    color_continuous_scale="RdYlGn_r",  # Rouge (forte dévaluation) à Vert (stable)
    range_color=[min_deval, max_deval],
    title="Indice de Dévaluation Relative des Devises 📉 (2010-2023)",
    labels={'devaluation_normalized': 'Indice (📉)'},
    projection="natural earth"
)
fig_b.update_geos(fitbounds="locations", visible=True)
fig_b = update_background_color(fig_b)
page3.append('b', fig_b)

# --- Partie 3 : Indice des Meilleures Devises (Carte c) ---
df_combined = pd.merge(
    df_map[['iso_a3', 'name', 'USD_percent']],
    valid_countries[['iso_a3', 'devaluation_normalized']],
    on='iso_a3',
    how='inner'
)

# Normalisation pour le score
df_combined['USD_norm'] = (df_combined['USD_percent'].max() - df_combined['USD_percent']) / \
                          (df_combined['USD_percent'].max() - df_combined[
                              'USD_percent'].min())  # Sous-évaluation = score élevé
df_combined['deval_norm'] = (df_combined['devaluation_normalized'].max() - df_combined['devaluation_normalized']) / \
                            (df_combined['devaluation_normalized'].max() - df_combined[
                                'devaluation_normalized'].min())  # Stabilité = score élevé
df_combined['best_currency_score'] = (df_combined['USD_norm'] + df_combined['deval_norm']) / 2

# Ajuster la plage de couleurs
min_score = df_combined['best_currency_score'].min()
max_score = df_combined['best_currency_score'].max()

# Carte c : Indice des Meilleures Devises
fig_c = px.choropleth(
    df_combined,
    locations="iso_a3",
    color="best_currency_score",
    hover_name="name",
    hover_data={"USD_percent": ":.2f", "devaluation_normalized": ":.2f", "best_currency_score": ":.2f"},
    color_continuous_scale="YlGnBu",  # Jaune (faible) à Bleu (fort)
    range_color=[min_score, max_score],
    title="Indice des Meilleures Devises - Sous-évaluées & Stables (2010-2023)",
    labels={'best_currency_score': 'Score'},
    projection="natural earth"
)
fig_c.update_geos(fitbounds="locations", visible=True)
fig_c = update_background_color(fig_c)
page3.append('c', fig_c)

# --- Partie 4 : Graphique en barres des 10 meilleures monnaies (d) ---
# Liste des codes ISO Alpha-3 à exclure (incluant QAT)
excluded_iso_a3 = [
    'JOR', 'OMN', 'QAT', 'GTM', 'BHR', 'SAU', 'ARE', 'ATG', 'DMA', 'GRD', 'KNA',
    'LCA', 'VCT', 'AIA', 'MSR', 'BHS', 'BLZ', 'BMU', 'CYM', 'PAN', 'LBN', 'EST', 'LTU', 'HKG',
]

# Filtrer le DataFrame pour exclure ces pays
df_filtered = df_combined[~df_combined['iso_a3'].isin(excluded_iso_a3)]

# Sélectionner les 13 meilleures monnaies après filtrage
top_10_best = df_filtered.nlargest(13, 'best_currency_score')

# Créer le graphique en barres
fig_d = px.bar(
    top_10_best,
    x='name',
    y='best_currency_score',
    title="Top 13 des Meilleures Devises (Hors Devises Liées au USD)",
    labels={'name': 'Pays', 'best_currency_score': 'Score'},
    color='best_currency_score',
    color_continuous_scale="YlGnBu",
    range_color=[min_score, max_score]
)
fig_d.update_layout(
    paper_bgcolor='#1f2a44',
    plot_bgcolor='#1f2a44',
    font_color='white',
    title_font_color='white',
    showlegend=False
)

# Ajouter au rendu
page3.append('d', fig_d)

# Rendu du layout
layout = page3.render()