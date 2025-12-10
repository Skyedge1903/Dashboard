import pandas as pd
import plotly.express as px
from template import Page
import plotly.graph_objects as go

# Charger les données
df_t10yie = pd.read_csv('data/T10YIE.csv')
df_m2sl = pd.read_csv('data/M2SL.csv')
df_wtisplc = pd.read_csv('data/WTISPLC.csv')

# Convertir les dates en datetime
df_t10yie['observation_date'] = pd.to_datetime(df_t10yie['observation_date'])
df_m2sl['observation_date'] = pd.to_datetime(df_m2sl['observation_date'])
df_wtisplc['observation_date'] = pd.to_datetime(df_wtisplc['observation_date'])

# Filtrer pour mars 2003 - février 2025
start_date = '2003-03-01'
end_date = '2025-11-01'
df_t10yie_filtered = df_t10yie[(df_t10yie['observation_date'] >= start_date) & (df_t10yie['observation_date'] <= end_date)]
df_m2sl_filtered = df_m2sl[(df_m2sl['observation_date'] >= start_date) & (df_m2sl['observation_date'] <= end_date)]
df_wtisplc_filtered = df_wtisplc[(df_wtisplc['observation_date'] >= start_date) & (df_wtisplc['observation_date'] <= end_date)]

# Calculer le rapport pétrole/M2 ajusté pour la croissance
df_combined = pd.merge(df_wtisplc_filtered, df_m2sl_filtered, on='observation_date')

# Extraire l'année et calculer le facteur de croissance (croissance annuelle moyenne de 2 %)
df_combined['year'] = df_combined['observation_date'].dt.year
g = -0.024  # Croissance annuelle moyenne pour les USA
df_combined['growth_factor'] = (1 + g) ** (df_combined['year'] - 2003)
df_combined['M2_adjusted'] = df_combined['M2SL'] * df_combined['growth_factor']
df_combined['ratio'] = df_combined['WTISPLC'] / df_combined['M2_adjusted']

# Moyenne mensuelle pour l'inflation implicite
df_t10yie_monthly = df_t10yie_filtered.groupby(df_t10yie_filtered['observation_date'].dt.to_period('M'))['T10YIE'].mean().reset_index()
df_t10yie_monthly['observation_date'] = df_t10yie_monthly['observation_date'].dt.to_timestamp()

# Normalisation
# Rapport pétrole/M2 ajusté (inversé : max = -1, min = 1)
ratio_min = df_combined['ratio'].min()
ratio_max = df_combined['ratio'].max()
df_combined['ratio_normalized'] = 1 - 2 * (df_combined['ratio'] - ratio_min) / (ratio_max - ratio_min)  # Inversion

# Inflation implicite (standard : max = 1, min = -1)
inflation_min = df_t10yie_monthly['T10YIE'].min()
inflation_max = df_t10yie_monthly['T10YIE'].max()
df_t10yie_monthly['T10YIE_normalized'] = 2 * (df_t10yie_monthly['T10YIE'] - inflation_min) / (inflation_max - inflation_min) - 1  # Pas d'inversion

# Fusionner les données normalisées
df_normalized = pd.merge(df_combined[['observation_date', 'ratio_normalized']],
                         df_t10yie_monthly[['observation_date', 'T10YIE_normalized']],
                         on='observation_date')

# Trier les données par date pour garantir l'ordre chronologique
df_normalized = df_normalized.sort_values('observation_date')

# Identifier la valeur la plus récente
latest_date = df_normalized['observation_date'].max()
latest_data = df_normalized[df_normalized['observation_date'] == latest_date]

# Graphique "a" : Rapport pétrole/M2 ajusté normalisé (inversé)
fig1 = px.line(
    df_combined,
    x='observation_date',
    y='ratio_normalized',
    title="Rapport Pétrole/M2 ajusté pour la croissance, normalisé inversé (mars 2003 - fév 2025)",
    labels={'ratio_normalized': 'Rapport normalisé (inversé)', 'observation_date': 'Date'},
    color_discrete_sequence=['#FFD700']
)

# Graphique "b" : Inflation implicite normalisée (non inversée)
fig2 = px.line(
    df_t10yie_monthly,
    x='observation_date',
    y='T10YIE_normalized',
    title="Inflation implicite normalisée (mars 2003 - fév 2025)",
    labels={'T10YIE_normalized': 'Inflation normalisée', 'observation_date': 'Date'},
    color_discrete_sequence=['#627EEA']
)

# Création de la figure de base avec une ligne et des marqueurs
fig3 = px.line(
    df_normalized,
    x='ratio_normalized',
    y='T10YIE_normalized',
    title="Relation entre Rapport Pétrole/M2 Ajusté (Inversé) et Inflation (Normalisés)",
    labels={
        'ratio_normalized': 'Croissance Économique (Rapport Pétrole/M2 Ajusté Normalisé Inversé)',
        'T10YIE_normalized': 'Inflation (Normalisée)'
    },
    color_discrete_sequence=['#00CC96'],  # Vert émeraude élégant
    hover_data={'observation_date': True}
)

# Définition des quadrants avec des couleurs subtiles
quadrants = [
    {
        'name': 'Inflationary Bust',
        'x0': -1, 'x1': 0, 'y0': 0, 'y1': 1,
        'color': 'rgba(255, 69, 0, 0.3)',  # Rouge orangé (OrangeRed) plus marqué
        'x_text': -1.1, 'y_text': 0.5
    },
    {
        'name': 'Inflationary Boom',
        'x0': 0, 'x1': 1, 'y0': 0, 'y1': 1,
        'color': 'rgba(255, 105, 180, 0.3)',  # Rose vif (HotPink)
        'x_text': 1.1, 'y_text': 0.5
    },
    {
        'name': 'Disinflationary Bust',
        'x0': -1, 'x1': 0, 'y0': -1, 'y1': 0,
        'color': 'rgba(65, 105, 225, 0.3)',  # Bleu royal (RoyalBlue)
        'x_text': -1.1, 'y_text': -0.5
    },
    {
        'name': 'Disinflationary Boom',
        'x0': 0, 'x1': 1, 'y0': -1, 'y1': 0,
        'color': 'rgba(50, 205, 50, 0.3)',  # Vert lime (LimeGreen)
        'x_text': 1.1, 'y_text': -0.5
    }
]

# Ajout des quadrants en arrière-plan
for quadrant in quadrants:
    fig3.add_shape(
        type="rect",
        x0=quadrant['x0'], x1=quadrant['x1'],
        y0=quadrant['y0'], y1=quadrant['y1'],
        fillcolor=quadrant['color'],
        line=dict(width=0),
        layer='below'  # Quadrants en dessous des données
    )
    fig3.add_annotation(
        x=quadrant['x_text'], y=quadrant['y_text'],
        text=quadrant['name'],
        showarrow=False,
        font=dict(size=12, color="white", family="Arial"),  # Titres en blanc
        xanchor="right" if quadrant['x_text'] < 0 else "left",
        textangle=-90 if quadrant['x_text'] < 0 else 90  # Rotation verticale
    )

# Mise à jour des traces pour les points et lignes (taille réduite pour les points normaux)
fig3.update_traces(
    mode='lines+markers',
    line=dict(width=2, dash='solid'),
    marker=dict(size=6, line=dict(width=1, color='#FFFFFF'))  # Taille réduite à 6
)

# Correction de l'affichage de la date pour le dernier point
latest_date_str = latest_date.strftime("%Y-%m")  # Conversion explicite de la date en chaîne
fig3.add_trace(
    go.Scatter(
        x=latest_data['ratio_normalized'],
        y=latest_data['T10YIE_normalized'],
        mode='markers',
        marker=dict(
            color='#FF4500',
            size=18,  # Taille augmentée à 18
            line=dict(width=2, color='#FFFFFF')
        ),
        hovertemplate=f'Date: {latest_date_str}<br>Rapport: %{{x:.3f}}<br>Inflation: %{{y:.3f}}',  # Date fixée directement
        showlegend=False  # Pas de légende
    )
)

# Mise à jour du layout avec tous les titres en blanc et sans légende
fig3.update_layout(
    template='plotly_white',  # Fond blanc épuré
    title=dict(
        text="Relation entre Rapport Pétrole/M2 Ajusté (Inversé) et Inflation (Normalisés)",
        font=dict(size=18, family="Arial", color="white"),  # Titre principal en blanc
        x=0.5,  # Centré
        pad=dict(t=20)
    ),
    xaxis=dict(
        title_font=dict(size=14, family="Arial", color="white"),  # Titre axe X en blanc
        tickfont=dict(size=12, color="white"),  # Étiquettes axe X en blanc
        gridcolor='rgba(200, 200, 200, 0.5)',
        zerolinecolor='rgba(150, 150, 150, 0.8)',
        range=[-1.2, 1.2]
    ),
    yaxis=dict(
        title_font=dict(size=14, family="Arial", color="white"),  # Titre axe Y en blanc
        tickfont=dict(size=12, color="white"),  # Étiquettes axe Y en blanc
        gridcolor='rgba(200, 200, 200, 0.5)',
        zerolinecolor='rgba(150, 150, 150, 0.8)',
        range=[-1.2, 1.2]
    ),
    font=dict(family="Arial", color="white"),  # Police générale en blanc
    showlegend=False,  # Légende globale désactivée
    margin=dict(l=50, r=50, t=80, b=50)
)

# Mise en page en grille
grid_layout = ["a a b b", "a a b b", "c c c c", "c c c c"]
page1 = Page(grid_layout)
page1.append('a', fig1)
page1.append('b', fig2)
page1.append('c', fig3)
layout = page1.render()
