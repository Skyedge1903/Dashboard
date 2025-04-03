import pandas as pd
import plotly.express as px
from template import Page  # Assurez-vous que ce module existe dans votre environnement
import numpy as np


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


# --- Fonction pour calculer les points d'un cercle géodésique ---
def calculate_circle_points(lat_center, lon_center, radius_km, num_points=100):
    # Rayon de la Terre en km
    R = 6371.0
    # Distance angulaire en radians
    angular_distance = radius_km / R
    # Coordonnées du centre en radians
    lat_rad = np.radians(lat_center)
    lon_rad = np.radians(lon_center)

    # Générer les points du cercle
    angles = np.linspace(0, 2 * np.pi, num_points)
    lats, lons = [], []

    for angle in angles:
        # Calcul des coordonnées géodésiques
        lat_new = np.arcsin(np.sin(lat_rad) * np.cos(angular_distance) +
                            np.cos(lat_rad) * np.sin(angular_distance) * np.cos(angle))
        lon_new = lon_rad + np.arctan2(
            np.sin(angle) * np.sin(angular_distance) * np.cos(lat_rad),
            np.cos(angular_distance) - np.sin(lat_rad) * np.sin(lat_new)
        )
        # Conversion en degrés
        lats.append(np.degrees(lat_new))
        lons.append(np.degrees(lon_new))

    return lats, lons


grid_layout = ["a"]
page5 = Page(grid_layout)

# Charger les données de croissance du PIB
df_growth = pd.read_csv("data/API_NY.GDP.MKTP.KD.ZG_DS2_fr_csv_v2_17870.csv", skiprows=4)
df_growth = df_growth[['Country Name', 'Country Code', '2019', '2020', '2021', '2022', '2023']]

# Calculer la croissance moyenne sur les années 2019 à 2023
df_growth['Croissance Moyenne 5 Ans'] = df_growth[['2019', '2020', '2021', '2022', '2023']].mean(axis=1, skipna=True)

# Définir les bornes réelles des données
min_growth = -6
max_growth = 33
total_range = max_growth - min_growth
zero_point = -min_growth / total_range
blue_center = zero_point + (1 / 3 * (1 - zero_point))

# Définir une échelle de couleurs personnalisée
custom_color_scale = [
    [0.0, "darkred"],
    [zero_point, "lightcoral"],
    [zero_point, "lightblue"],
    [blue_center, "blue"],
    [1.0, "darkblue"]
]

# Créer la carte choroplèthe
fig_map = px.choropleth(
    df_growth,
    locations="Country Code",
    color="Croissance Moyenne 5 Ans",
    hover_name="Country Name",
    hover_data={"Croissance Moyenne 5 Ans": ":.2f"},
    color_continuous_scale=custom_color_scale,
    range_color=[min_growth, max_growth],
    title="Croissance Moyenne du PIB sur 5 Ans (2019-2023) par Pays",
    labels={'Croissance Moyenne 5 Ans': 'Croissance Moyenne (%)'},
    projection="natural earth",
)

# Coordonnées de Guiyang
lat_guiyang = 26.627244742506964
lon_guiyang = 106.64292722915717

# Ajouter le point central à Guiyang
fig_map.add_scattergeo(
    lat=[lat_guiyang],
    lon=[lon_guiyang],
    mode="markers",
    marker=dict(
        size=8,
        color="white",
        symbol="circle"
    ),
    name="Guiyang, Chine"
)

# Calculer les points du cercle de 4100 km
circle_lats, circle_lons = calculate_circle_points(lat_guiyang, lon_guiyang, 4100)

# Ajouter le cercle à la carte
fig_map.add_scattergeo(
    lat=circle_lats,
    lon=circle_lons,
    mode="lines",
    line=dict(
        width=2,
        color="yellow",
        dash="dash"
    ),
    name="Rayon de 4100 km (50% population)"
)

fig_map.update_geos(
    fitbounds="locations",
    visible=True,
    showcoastlines=True,
    coastlinecolor="white",
)

fig_map.update_layout(
    showlegend=True,
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    )
)

fig_map = update_background_color(fig_map)
page5.append('a', fig_map)
layout = page5.render()