import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from template import Page
from datetime import date

# =====================================================================
# Chargement et filtrage des données
# =====================================================================
df_t10yie = pd.read_csv('data/T10YIE.csv')
df_m2sl = pd.read_csv('data/M2SL.csv')
df_wtisplc = pd.read_csv('data/WTISPLC.csv')

df_t10yie['observation_date'] = pd.to_datetime(df_t10yie['observation_date'])
df_m2sl['observation_date'] = pd.to_datetime(df_m2sl['observation_date'])
df_wtisplc['observation_date'] = pd.to_datetime(df_wtisplc['observation_date'])

start_date = '2003-03-01'
end_date = date.today().strftime("%Y-%m-%d")

df_t10yie = df_t10yie[
    (df_t10yie['observation_date'] >= start_date)
    & (df_t10yie['observation_date'] <= end_date)
]

df_m2sl = df_m2sl[
    (df_m2sl['observation_date'] >= start_date)
    & (df_m2sl['observation_date'] <= end_date)
]

df_wtisplc = df_wtisplc[
    (df_wtisplc['observation_date'] >= start_date)
    & (df_wtisplc['observation_date'] <= end_date)
]

# =====================================================================
# Croissance réelle annuelle du PIB américain
# =====================================================================
gdp_growth_by_year = {
    2003: 0.028,
    2004: 0.038,
    2005: 0.035,
    2006: 0.028,
    2007: 0.020,
    2008: 0.001,
    2009: -0.026,
    2010: 0.027,
    2011: 0.016,
    2012: 0.023,
    2013: 0.021,
    2014: 0.025,
    2015: 0.029,
    2016: 0.018,
    2017: 0.025,
    2018: 0.030,
    2019: 0.026,
    2020: -0.022,
    2021: 0.061,
    2022: 0.025,
    2023: 0.029,
    2024: 0.028,
    2025: 0.020,
    2026: 0.020,
}

# =====================================================================
# WTI : passage en moyenne mensuelle
# =====================================================================
df_wtisplc_monthly = (
    df_wtisplc
    .set_index('observation_date')
    .resample('MS')['WTISPLC']
    .mean()
    .reset_index()
)

# =====================================================================
# Fusion mensuelle WTI / M2
# =====================================================================
df_combined = pd.merge(
    df_wtisplc_monthly,
    df_m2sl,
    on='observation_date',
    how='inner'
)

df_combined['year'] = df_combined['observation_date'].dt.year

# =====================================================================
# Croissance réelle cumulée — base 2003 = 1
# =====================================================================
base_year = 2003
last_year = int(df_combined['year'].max())

missing_years = [
    year
    for year in range(base_year + 1, last_year + 1)
    if year not in gdp_growth_by_year
]

if missing_years:
    raise ValueError(
        f"Taux de croissance du PIB manquants : {missing_years}"
    )

growth_factors = {base_year: 1.0}

for year in range(base_year + 1, last_year + 1):
    growth_factors[year] = (
        growth_factors[year - 1]
        * (1.0 + gdp_growth_by_year[year])
    )

df_combined['cumulative_factor'] = (
    df_combined['year'].map(growth_factors)
)

df_combined['M2_adjusted'] = (
    df_combined['M2SL']
    / df_combined['cumulative_factor']
)

df_combined['ratio'] = (
    df_combined['WTISPLC']
    / df_combined['M2_adjusted']
)

# =====================================================================
# M2 réelle : M2 nominale déflatée par la croissance réelle cumulée
# =====================================================================
df_combined['M2_real'] = (
    df_combined['M2SL'] / df_combined['cumulative_factor']
)

# =====================================================================
# Ratio pétrole / M2 réelle
# =====================================================================
df_combined['ratio'] = (
    df_combined['WTISPLC'] / df_combined['M2_real']
)

# =====================================================================
# Inflation mensuelle : moyenne du T10YIE
# =====================================================================
df_t10yie_monthly = (
    df_t10yie
    .groupby(df_t10yie['observation_date'].dt.to_period('M'))['T10YIE']
    .mean()
    .reset_index()
)

df_t10yie_monthly['observation_date'] = (
    df_t10yie_monthly['observation_date'].dt.to_timestamp()
)

# =====================================================================
# Normalisation
# =====================================================================
ratio_min, ratio_max = df_combined['ratio'].min(), df_combined['ratio'].max()

df_combined['ratio_normalized'] = 1 - 2 * (
    (df_combined['ratio'] - ratio_min) / (ratio_max - ratio_min)
)

infl_min, infl_max = (
    df_t10yie_monthly['T10YIE'].min(),
    df_t10yie_monthly['T10YIE'].max()
)

df_t10yie_monthly['T10YIE_normalized'] = 2 * (
    (df_t10yie_monthly['T10YIE'] - infl_min) / (infl_max - infl_min)
) - 1

df_normalized = pd.merge(
    df_combined[['observation_date', 'ratio_normalized']],
    df_t10yie_monthly[['observation_date', 'T10YIE_normalized']],
    on='observation_date'
).sort_values('observation_date')

# =====================================================================
# Quadrants et closest quadrants
# =====================================================================
def get_quadrant(row):
    x = row['ratio_normalized']
    y = row['T10YIE_normalized']

    if x <= 0 and y >= 0:
        return 'Inflationary Bust', 'rgb(255,69,0)'
    elif x > 0 and y >= 0:
        return 'Inflationary Boom', 'rgb(255,105,180)'
    elif x <= 0 and y < 0:
        return 'Disinflationary Bust', 'rgb(65,105,225)'
    elif x > 0 and y < 0:
        return 'Disinflationary Boom', 'rgb(50,205,50)'
    else:
        return 'On Axis', 'gray'


def get_closest_quad(row):
    x = row['ratio_normalized']
    y = row['T10YIE_normalized']

    if x == 0 or y == 0:
        return 'On Axis', 'gray'

    flip_x = abs(x) <= abs(y)

    new_x = -x if flip_x else x
    new_y = y if flip_x else -y

    return get_quadrant(
        pd.Series({
            'ratio_normalized': new_x,
            'T10YIE_normalized': new_y
        })
    )


df_normalized[['quad_label', 'quad_color']] = df_normalized.apply(
    get_quadrant,
    axis=1,
    result_type='expand'
)

df_normalized[['closest_label', 'closest_color']] = df_normalized.apply(
    get_closest_quad,
    axis=1,
    result_type='expand'
)

df_normalized['distance'] = np.sqrt(
    df_normalized['ratio_normalized'] ** 2
    + df_normalized['T10YIE_normalized'] ** 2
)

# =====================================================================
# Clustering des points consécutifs
# =====================================================================
clusters = []
current_cluster = [df_normalized.iloc[0].to_dict()]

for i in range(1, len(df_normalized)):
    prev = current_cluster[-1]
    curr = df_normalized.iloc[i].to_dict()

    if (
        prev['quad_label'] == curr['quad_label']
        and prev['closest_label'] == curr['closest_label']
    ):
        current_cluster.append(curr)
    else:
        clusters.append(current_cluster)
        current_cluster = [curr]

clusters.append(current_cluster)

cluster_points = []

for cluster in clusters:
    dfc = pd.DataFrame(cluster)

    dates = dfc['observation_date']
    cluster_start_date = dates.min()

    dmin = dates.min().strftime("%Y-%m")
    dmax = dates.max().strftime("%Y-%m")

    hover_label = dmin if dmin == dmax else f"{dmin} à {dmax}"

    cluster_points.append({
        'start_date': cluster_start_date,
        'hover_label': hover_label,
        'avg_dist': dfc['distance'].mean(),
        'quad_label': dfc['quad_label'].iloc[0],
        'quad_color': dfc['quad_color'].iloc[0],
        'closest_label': dfc['closest_label'].iloc[0],
        'closest_color': dfc['closest_color'].iloc[0],
    })

df_clustered = pd.DataFrame(cluster_points)

# =====================================================================
# Graphique A : rapport normalisé
# =====================================================================
fig1 = px.line(
    df_combined,
    x='observation_date',
    y='ratio_normalized',
    title="Rapport Pétrole / M2 réelle (Normalisé, Inversé)",
    color_discrete_sequence=['#FFD700']
)

fig1.update_layout(
    template='plotly_white',
    xaxis_title='Date',
    yaxis_title='Ratio normalisé',
    font=dict(family="Arial")
)

# =====================================================================
# Graphique B : inflation normalisée
# =====================================================================
fig2 = px.line(
    df_t10yie_monthly,
    x='observation_date',
    y='T10YIE_normalized',
    title="Inflation implicite normalisée",
    color_discrete_sequence=['#627EEA']
)

fig2.update_layout(
    template='plotly_white',
    xaxis_title='Date',
    yaxis_title='Inflation normalisée',
    font=dict(family="Arial")
)

# =====================================================================
# Graphique C : frise chronologique
# =====================================================================
fig3 = go.Figure()

max_dist = df_normalized['distance'].max()

quad_dict = {
    'Inflationary Bust': 'rgb(255,69,0)',
    'Inflationary Boom': 'rgb(255,105,180)',
    'Disinflationary Bust': 'rgb(65,105,225)',
    'Disinflationary Boom': 'rgb(50,205,50)',
}

for label, color in quad_dict.items():
    df_sub = df_clustered[df_clustered['quad_label'] == label]

    if not df_sub.empty:
        sizes = 10 + 40 * (df_sub['avg_dist'] / max_dist)

        fig3.add_trace(go.Scatter(
            x=df_sub['start_date'],
            y=[0] * len(df_sub),
            mode='markers',
            marker=dict(
                size=sizes,
                color=color,
                line=dict(width=1, color='white')
            ),
            name=label,
            hovertemplate=(
                '%{x|%Y-%m}<br>'
                'Interval: %{customdata[0]}<br>'
                'Distance: %{customdata[1]:.2f}'
                '<extra></extra>'
            ),
            customdata=df_sub[['hover_label', 'avg_dist']].values
        ))

# Petites boules pour le closest quadrant
df_clustered_filtered = df_clustered[
    df_clustered['closest_label'] != 'On Axis'
]

if not df_clustered_filtered.empty:
    fig3.add_trace(go.Scatter(
        x=df_clustered_filtered['start_date'],
        y=[0.3] * len(df_clustered_filtered),
        mode='markers',
        marker=dict(
            size=10,
            color=df_clustered_filtered['closest_color'],
            line=dict(width=0.5, color='white')
        ),
        customdata=df_clustered_filtered['closest_label'],
        hovertemplate='Closest: %{customdata}<extra></extra>',
        showlegend=False
    ))

fig3.update_layout(
    template='plotly_white',
    title="Frise Chronologique des Quadrants avec Intensité",
    xaxis=dict(title='Date'),
    yaxis=dict(
        showline=False,
        showticklabels=False,
        showgrid=False,
        range=[-0.2, 0.5]
    ),
    showlegend=True,
    height=300,
    font=dict(family="Arial"),
    margin=dict(l=50, r=50, t=80, b=50)
)

# =====================================================================
# Page finale
# =====================================================================
grid_layout = [
    "a a b b",
    "a a b b",
    "c c c c",
    "c c c c"
]

page1 = Page(grid_layout)

page1.append('a', fig1)
page1.append('b', fig2)
page1.append('c', fig3)

layout = page1.render()
