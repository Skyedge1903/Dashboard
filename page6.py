import pandas as pd
import plotly.express as px
from template import Page
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
import plotly.graph_objects as go

grid_layout = ["a a b b c c", "a a b b c c", "d d d d d d", "d d d d d d"]
page5 = Page(grid_layout)

# Charger les données
df = pd.read_csv("data/data_hash_price.csv")
df['Date'] = pd.to_datetime(df['Date'])

# Paramètres
COUT_MATERIEL_PAR_TH_2025 = 20  # Coût en 2025 : 20 $ par TH/s
TOTAL_BTC = 21_000_000
MOORE_FACTOR = 2  # Doublement de la performance
MOORE_PERIOD = 1.5  # Tous les 1,5 ans

# Calcul du coût matériel dans df
reference_date = pd.to_datetime("2025-01-01")
df['Years_Since_Ref'] = (reference_date - df['Date']).dt.days / 365.25
df['Cout_Materiel_Par_TH'] = COUT_MATERIEL_PAR_TH_2025 * np.power(MOORE_FACTOR, df['Years_Since_Ref'] / MOORE_PERIOD)
df['Cout_Materiel'] = df['hash_rate'] * df['Cout_Materiel_Par_TH']
df['Market_Cap'] = df['market_price'] * TOTAL_BTC
df['Pourcentage'] = (df['Cout_Materiel'] / df['Market_Cap']) * 100
df = df[df['Market_Cap'] > 0]

date_range = pd.date_range(start=df['Date'].min(), end="2040-12-31", freq='D')
df2 = pd.DataFrame({'Date': date_range})

df = df.sort_values('Date')
df2 = df2.sort_values('Date')
df2 = pd.merge_asof(df2, df[['Date', 'Cout_Materiel']].sort_values('Date'), on='Date', direction='backward')

last_date = df['Date'].max()
# Définir les bornes de la droite
start_cost = 15_000_000_000  # 25 milliards
end_cost = 5_000_000_000     # 5 milliards
end_date = pd.to_datetime("2040-12-31")

# Calcul du coefficient directeur de la droite (slope)
duration = (end_date - last_date).days
slope = (end_cost - start_cost) / duration

# Appliquer la droite linéaire après last_date
df2['Cout_Materiel'] = np.where(
    df2['Date'] <= last_date,
    df2['Cout_Materiel'],
    start_cost + slope * (df2['Date'] - last_date).dt.days
)

# --------------------------
# Partie B : Modélisation du prix BTC avec un modèle polynomial
# --------------------------
start_date = pd.to_datetime("2016-03-01")
df_train = df[df['Date'] >= start_date].copy()
df_train['t'] = (df_train['Date'] - start_date).dt.days / 365.25

degree = 2
model = make_pipeline(PolynomialFeatures(degree), LinearRegression())
X_train = df_train[['t']].values
y_train = df_train['market_price'].values
model.fit(X_train, y_train)

# --------------------------
# Partie C : Prédiction sur df2
# --------------------------
valid_mask = df2['Date'] >= start_date
df2['t'] = np.nan
df2['Predicted_price'] = np.nan
df2.loc[valid_mask, 't'] = (df2.loc[valid_mask, 'Date'] - start_date).dt.days / 365.25
df2.loc[valid_mask, 'Predicted_price'] = model.predict(df2.loc[valid_mask, ['t']].values)

# --------------------------
# Partie D : Construction de la courbe finale du prix BTC
# --------------------------
df_prices = df[['Date', 'market_price']].sort_values('Date')
df2 = pd.merge_asof(df2.sort_values('Date'), df_prices, on='Date', direction='backward')
df2['Final_market_price'] = np.where(df2['Date'] <= last_date, df2['market_price'], df2['Predicted_price'])
df2['Market_Cap'] = df2['Final_market_price'] * TOTAL_BTC

df2['Pourcentage'] = (df2['Cout_Materiel'] / df2['Market_Cap']) * 100
df2 = df2[df2['Market_Cap'] > 0]  # Filtrer les divisions par zéro

# Créer le premier graphique (Pourcentage) - Couleur bleue
fig1 = px.line(
    df2,
    x='Date',
    y='Pourcentage',
    title='Coût Matériel par Rapport à la Capitalisation BTC',
    labels={'Pourcentage': 'Pourcentage (%)', 'Date': 'Date'},
    color_discrete_sequence=['#00A1D6']  # Bleu cyan
)

fig1.add_vline(
    x=pd.to_datetime("2036-05-01").timestamp() * 1000,
    line_dash="dash",
    line_color="red",
    annotation_text="Mort de Bitcoin ☠️",
    annotation_position="bottom right",
    annotation_font_color="red"
)

fig1.update_layout(
    paper_bgcolor='#1f2a44',
    plot_bgcolor='#1f2a44',
    font_color='white',
    title_font_size=20,
    xaxis_title_font_size=16,
    yaxis_title_font_size=16,
    xaxis=dict(gridcolor='rgba(255,255,255,0.1)', zerolinecolor='rgba(255,255,255,0.2)'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.1)', zerolinecolor='rgba(255,255,255,0.2)')
)

# Créer le deuxième graphique (Coût Matériel) - Couleur verte
fig2 = px.line(
    df2,
    x='Date',
    y='Cout_Materiel',
    title='Évolution du Coût Matériel du réseau BTC',
    labels={'Cout_Materiel': 'Coût Matériel ($)', 'Date': 'Date'},
    color_discrete_sequence=['#00CC96']  # Vert émeraude
)

fig2.add_vline(
    x=pd.to_datetime("2036-05-01").timestamp() * 1000,
    line_dash="dash",
    line_color="red",
    annotation_text="Mort de Bitcoin ☠️",
    annotation_position="bottom right",
    annotation_font_color="red"
)

fig2.update_layout(
    paper_bgcolor='#1f2a44',
    plot_bgcolor='#1f2a44',
    font_color='white',
    title_font_size=20,
    xaxis_title_font_size=16,
    yaxis_title_font_size=16,
    xaxis=dict(gridcolor='rgba(255,255,255,0.1)', zerolinecolor='rgba(255,255,255,0.2)'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.1)', zerolinecolor='rgba(255,255,255,0.2)')
)

# Créer le troisième graphique (Market Cap) - Couleur violette
fig3 = px.line(
    df2,
    x='Date',
    y='Market_Cap',
    title='Évolution de la Capitalisation Totale BTC',
    labels={'Market_Cap': 'Capitalisation ($)', 'Date': 'Date'},
    color_discrete_sequence=['#9B59B6']  # Violet
)

fig3.add_vline(
    x=pd.to_datetime("2036-05-01").timestamp() * 1000,
    line_dash="dash",
    line_color="red",
    annotation_text="Mort de Bitcoin ☠️",
    annotation_position="bottom right",
    annotation_font_color="red"
)

fig3.update_layout(
    paper_bgcolor='#1f2a44',
    plot_bgcolor='#1f2a44',
    font_color='white',
    title_font_size=20,
    xaxis_title_font_size=16,
    yaxis_title_font_size=16,
    xaxis=dict(gridcolor='rgba(255,255,255,0.1)', zerolinecolor='rgba(255,255,255,0.2)'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.1)', zerolinecolor='rgba(255,255,255,0.2)')
)

page5.append('c', fig1)
page5.append('a', fig2)
page5.append('b', fig3)

fig = go.Figure()

# Paramètres communs pour la mise en page
bg_color = "#141D2B"   # Fond général sombre
gauge_bg = "#2A2D3A"   # Fond des jauges
font_color = "#FFFFFF" # Couleur des textes
border_color = "#404552" # Couleur des bordures subtiles

# --- Jauge BURN 🔥 (0 à 10) ---
burn_value = 3.5
burn_range = [0, 10]
burn_domain = {'x': [0.0, 0.3], 'y': [0, 0.85]}
fig.add_trace(go.Indicator(
    mode="number+gauge",
    value=burn_value,
    number={
        'suffix': " B USD/year",
        'font': {'size': 22, 'color': font_color, 'family': "Arial"}
    },
    gauge={
        'axis': {'range': burn_range, 'tickvals': [], 'ticktext': []},
        'bar': {'color': '#FFD700', 'thickness': 0.8},
        'bgcolor': gauge_bg,
        'borderwidth': 1,
        'bordercolor': border_color
    },
    domain=burn_domain
))

# --- Jauge SUPPLY GROWTH (échelle de -1 à 1, zone remplie de 0 à -0.43) ---
supply_value = -0.43
supply_range = [-1, 1]
supply_domain = {'x': [0.35, 0.65], 'y': [0, 0.85]}
fig.add_trace(go.Indicator(
    mode="number+gauge",
    value=supply_value,
    number={
        'suffix': " % / year",
        'font': {'size': 22, 'color': font_color, 'family': "Arial"}
    },
    gauge={
        'axis': {'range': supply_range, 'tickvals': [], 'ticktext': []},
        'bar': {'color': 'rgba(0,0,0,0)'},
        'steps': [{'range': [supply_value, 0], 'color': '#FFA500'}],
        'bgcolor': gauge_bg,
        'borderwidth': 1,
        'bordercolor': border_color
    },
    domain=supply_domain
))

# --- Jauge ISSUANCE 💧 (0 à 10) ---
issuance_value = 1.8
issuance_range = [0, 10]
issuance_domain = {'x': [0.70, 1.0], 'y': [0, 0.85]}
fig.add_trace(go.Indicator(
    mode="number+gauge",
    value=issuance_value,
    number={
        'suffix': " B USD/year",
        'font': {'size': 22, 'color': font_color, 'family': "Arial"}
    },
    gauge={
        'axis': {'range': issuance_range, 'tickvals': [], 'ticktext': []},
        'bar': {'color': '#00BFFF', 'thickness': 0.8},
        'bgcolor': gauge_bg,
        'borderwidth': 1,
        'bordercolor': border_color
    },
    domain=issuance_domain
))

# Ajout des annotations pour les titres de chaque indicateur
fig.add_annotation(
    x=0.15, y=0.95,  # Position au-dessus de la jauge BURN
    text="Burn 🔥",
    font=dict(size=20, color=font_color, family="Arial"),
    showarrow=False,
    xanchor="center",
    xref="paper",
    yref="paper"
)

fig.add_annotation(
    x=0.5, y=0.95,  # Position au-dessus de la jauge SUPPLY GROWTH
    text="Supply Growth",
    font=dict(size=20, color=font_color, family="Arial"),
    showarrow=False,
    xref="paper",
    yref="paper"
)

fig.add_annotation(
    x=0.85, y=0.95,  # Position au-dessus de la jauge ISSUANCE
    text="Issuance 💧",
    font=dict(size=20, color=font_color, family="Arial"),
    showarrow=False,
    xanchor="center",
    xref="paper",
    yref="paper"
)

fig.add_annotation(
    x=0.5, y=0.05,  # Déplacé vers le bas mais dans la zone visible (0 à 1)
    text="*Balance Burn/Émission, plus ETH est rentable plus il est déflationniste et sécurisé (3y 242d)",
    font=dict(size=15, color=font_color, family="Arial"),
    showarrow=False,
    xref="paper",
    yref="paper",
    xanchor="left",
    yanchor="top"
)


page5.append('d', fig)

layout = page5.render()