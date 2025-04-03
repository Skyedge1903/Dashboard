import pandas as pd
import numpy as np
from template import Page  # Assurez-vous que ce module existe dans votre environnement
import plotly.express as px
import plotly.graph_objects as go


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


# Définir la disposition de la grille
grid_layout = ["b b c c", "b b c c", "a a d d", "a a d d"]
page4 = Page(grid_layout)

# Charger les données depuis les fichiers CSV
df_exchange = pd.read_csv("data/API_PA.NUS.FCRF_DS2_en_csv_v2_13510.csv", skiprows=4)
df_exchange = df_exchange[['Country Name', 'Country Code', '2013', '2023']]
df_exchange.columns = ['Country Name', 'Code ISO 3', 'Exchange Rate 2013', 'Exchange Rate 2023']

df_default = pd.read_csv("data/defaut_note.csv")
df_default.columns = ['Notation S&P', 'Probabilité de Défaut sur 10 Ans (%)']

df_ratings = pd.read_csv("data/noteS&P.csv")
df_ratings.columns = ['Pays', 'Code ISO 3', 'Notation S&P']

df_yields = pd.read_csv("data/treasury_yields_with_iso3.csv")
df_yields = df_yields[['Country', 'Code ISO 3', 'Rating S&P', '10Y Bond Yield']]
df_yields['10Y Bond Yield'] = df_yields['10Y Bond Yield'].str.rstrip('%').astype(float) / 100

# Fusionner les données
df_combined = pd.merge(df_yields[['Code ISO 3', '10Y Bond Yield']], df_ratings[['Code ISO 3', 'Notation S&P']],
                       on='Code ISO 3', how='inner')
df_combined = pd.merge(df_combined, df_default, on='Notation S&P', how='left')
df_combined = pd.merge(df_combined, df_exchange[['Code ISO 3', 'Exchange Rate 2013', 'Exchange Rate 2023']],
                       on='Code ISO 3', how='inner')

# Map a : Rendements des obligations par pays avec échelle en bleu
fig_a = px.choropleth(
    df_combined,
    locations="Code ISO 3",
    color="10Y Bond Yield",
    hover_name="Code ISO 3",
    hover_data={"10Y Bond Yield": ":.2%"},
    color_continuous_scale="Blues",  # Échelle en bleu
    title="Rendements des Obligations à 10 Ans par Pays",
    labels={'10Y Bond Yield': 'Rendement'},
    projection="natural earth"
)
fig_a.update_geos(fitbounds="locations", visible=True)
fig_a = update_background_color(fig_a)
page4.append('a', fig_a)

# Map b : Notes de crédit par pays (inchangée)
rating_order = ["AAA", "AA+", "AA", "AA-", "A+", "A", "A-", "BBB+", "BBB", "BBB-", "BB+", "BB", "BB-", "B+", "B", "B-",
                "CCC+", "CCC", "CCC-", "CC", "C", "D"]
df_combined['Rating Value'] = df_combined['Notation S&P'].apply(
    lambda x: rating_order.index(x) if x in rating_order else np.nan)

fig_b = px.choropleth(
    df_combined,
    locations="Code ISO 3",
    color="Rating Value",
    hover_name="Code ISO 3",
    hover_data={"Notation S&P": True},
    color_continuous_scale="RdYlGn_r",  # Échelle originale conservée
    title="Notes S&P par Pays",
    labels={'Rating Value': 'Note (Ordinal)'},
    projection="natural earth"
)
fig_b.update_geos(fitbounds="locations", visible=True)
fig_b = update_background_color(fig_b)
page4.append('b', fig_b)

# Map c : Risque de défaut basé sur les notes (inchangée)
fig_c = px.choropleth(
    df_combined,
    locations="Code ISO 3",
    color="Probabilité de Défaut sur 10 Ans (%)",
    hover_name="Code ISO 3",
    hover_data={"Notation S&P": True, "Probabilité de Défaut sur 10 Ans (%)": ":.2f"},
    color_continuous_scale="RdYlGn_r",  # Échelle originale conservée
    title="Risque de Défaut sur 10 Ans par Pays (%)",
    labels={'Probabilité de Défaut sur 10 Ans (%)': 'Probabilité de Défaut (%)'},
    projection="natural earth"
)
fig_c.update_geos(fitbounds="locations", visible=True)
fig_c = update_background_color(fig_c)
page4.append('c', fig_c)

# Calculs pour le bar graph
df_combined['Dévaluation (%)'] = ((df_combined['Exchange Rate 2023'] - df_combined['Exchange Rate 2013']) / df_combined[
    'Exchange Rate 2013']) * 100
df_combined['Taux de dévaluation annuel'] = (df_combined['Exchange Rate 2023'] / df_combined['Exchange Rate 2013']) ** (
        1 / 10) - 1
df_combined['Taux d’intérêt réel ajusté'] = df_combined['10Y Bond Yield'] - df_combined['Taux de dévaluation annuel']
df_combined['Probabilité de défaut annuelle'] = df_combined['Probabilité de Défaut sur 10 Ans (%)'] / 100 / 10
df_combined['Taux d’intérêt réel ajusté pour le risque'] = (1 - df_combined['Probabilité de défaut annuelle']) * (
        1 + df_combined['Taux d’intérêt réel ajusté']) - 1

# Liste d'exclusion pour le graph d
exclude_countries = ["HRV", "LTU", "UGA", "KEN", "BGD"]

# Filtrer les données pour exclure les pays indésirables
df_filtered = df_combined[~df_combined['Code ISO 3'].isin(exclude_countries)]

# Bar graph d : Top 10 des meilleures dettes avec échelle en bleu et titre réduit
df_top10 = df_filtered.sort_values(by='Taux d’intérêt réel ajusté pour le risque', ascending=False).head(13)

fig_d = px.bar(
    df_top10,
    x='Code ISO 3',
    y='Taux d’intérêt réel ajusté pour le risque',
    color='Taux d’intérêt réel ajusté pour le risque',
    color_continuous_scale="Blues",  # Échelle en bleu
    title="Top 13 des Meilleures Dettes (Taux d’intérêt réel ajusté)",  # Titre réduit
    labels={'Taux d’intérêt réel ajusté pour le risque': 'Taux Ajusté'},  # Étiquette simplifiée
    hover_data={'Code ISO 3': True, 'Taux d’intérêt réel ajusté pour le risque': ':.2%'}
)
fig_d.update_layout(
    paper_bgcolor='#1f2a44',
    plot_bgcolor='#1f2a44',
    font_color='white'
)
page4.append('d', fig_d)

# Rendu du layout
layout = page4.render()
