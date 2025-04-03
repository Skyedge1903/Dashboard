from template import Page
import plotly.express as px
import pandas as pd

# Définition du layout en grille
grid_layout = ["a a b b", "a a b b", "c c c c", "c c c c"]
page2 = Page(grid_layout)

# Données chiffrées pour les comparaisons
data = {
    'Actif': ['Or (OR)', 'Bitcoin (BTC)', 'Ethereum (ETH)', 'Immobilier', 'Terrains/Forêts'],
    'Liquidité (Volume quotidien, milliards USD)': [276.42, 37.03, 15.53, 5.18, 3.5],
    'Volatilité (Annualisée, %)': [15.23, 53.80, 55.10, 7.50, 7.50],
    'Inflation de l’offre (%)': [1.68, 0.83, -0.18, 1.30, 0]  # Correction du nom
}

df = pd.DataFrame(data)

# Choix d'une palette de couleurs cohérente
color_palette = {
    'Or (OR)': '#FFD700',  # Or
    'Bitcoin (BTC)': '#F7931A',  # Orange Bitcoin
    'Ethereum (ETH)': '#627EEA',  # Bleu Ethereum
    'Immobilier': '#8B4513',  # Marron (Terre)
    'Terrains/Forêts': '#228B22'  # Vert (Forêt)
}

# Graphique 1 : Liquidité
fig1 = px.bar(
    df,
    x='Actif',
    y='Liquidité (Volume quotidien, milliards USD)',
    title='Liquidité : Volume quotidien (milliards USD)',
    text=df['Liquidité (Volume quotidien, milliards USD)'].round(2),
    color='Actif',
    color_discrete_map=color_palette
)
fig1.update_traces(texttemplate='%{text}', textposition='outside')

# Graphique 2 : Volatilité
fig2 = px.bar(
    df,
    x='Actif',
    y='Volatilité (Annualisée, %)',
    title='Volatilité : Variation annualisée (%)',
    text=df['Volatilité (Annualisée, %)'].round(2),
    color='Actif',
    color_discrete_map=color_palette
)
fig2.update_traces(texttemplate='%{text}', textposition='outside')

# Graphique 3 : Inflation de l’offre
fig3 = px.scatter(
    df,
    x='Actif',
    y='Inflation de l’offre (%)',
    title="Inflation de l’offre : Augmentation annuelle (%)",
    color='Actif',
    color_discrete_map=color_palette,
    size=[abs(x) + 5 for x in df['Inflation de l’offre (%)']],
    text=df['Inflation de l’offre (%)'].round(2)
)
fig3.update_traces(textposition='top center')
fig3.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='gray')

# Normalisation des valeurs
df['Norm_Liquidité'] = (df['Liquidité (Volume quotidien, milliards USD)'] - df['Liquidité (Volume quotidien, milliards USD)'].min()) / \
                       (df['Liquidité (Volume quotidien, milliards USD)'].max() - df['Liquidité (Volume quotidien, milliards USD)'].min())

df['Norm_Volatilité'] = 1 - (df['Volatilité (Annualisée, %)'] - df['Volatilité (Annualisée, %)'].min()) / \
                         (df['Volatilité (Annualisée, %)'].max() - df['Volatilité (Annualisée, %)'].min())

df['Norm_Inflation'] = 1 - (df['Inflation de l’offre (%)'] - df['Inflation de l’offre (%)'].min()) / \
                        (df['Inflation de l’offre (%)'].max() - df['Inflation de l’offre (%)'].min())

# Score final basé sur la moyenne des valeurs normalisées
df['Score_Global'] = (df['Norm_Liquidité'] + df['Norm_Volatilité'] + df['Norm_Inflation']) / 3

# Tri pour afficher un vrai podium
df_podium = df.sort_values('Score_Global', ascending=False).reset_index(drop=True)

# Création d'un podium visuel avec des tailles différentes
podium_colors = ['#FFD700', '#C0C0C0', '#CD7F32']  # Or, Argent, Bronze
default_color = "#D3D3D3"  # Gris pour les autres
df_podium['Podium_Color'] = [podium_colors[i] if i < 3 else default_color for i in range(len(df_podium))]
df_podium['Size'] = [70, 60, 50] + [30] * (len(df_podium) - 3)  # Tailles pour podium

# Graphique du podium
fig4 = px.bar(
    df_podium,
    x='Actif',
    y='Score_Global',
    title="🏆 Podium Global : Score basé sur la moyenne des valeurs normalisées",
    text=df_podium['Score_Global'].round(2),
    color='Actif',
    color_discrete_map=color_palette
)
fig4.update_traces(
    texttemplate='%{text}',
    textposition='outside',
    marker=dict(line=dict(color='black', width=1.5))
)

# Rendu des graphiques sur la page
page2.append('a', fig1)
page2.append('b', fig2)
page2.append('c', fig3)
page2.append('d', fig4)

layout = page2.render()
