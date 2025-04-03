# app.py

import dash
from dash import html, dcc, Output, Input, State, no_update
import importlib

# Définition des noms des pages et leurs chemins
page_names = {
    "page1": {"name": "Accueil", "path": "/accueil", "icon": "fas fa-home"},
    "page5": {"name": "Desinflationary bust", "path": "/Desinflationary-bust", "icon": "fas fa-chart-bar"},
    "page4": {"name": "Desinflationary boom", "path": "/Desinflationary-boom", "icon": "fas fa-chart-bar"},
    "page3": {"name": "Inflationary bust", "path": "/Inflationary-bust", "icon": "fas fa-chart-bar"},
    "page2": {"name": "Inflationary boom", "path": "/Inflationary-boom", "icon": "fas fa-chart-bar"},
    "page6": {"name": "Ethereum Flippening", "path": "/Ethereum-flippening", "icon": "fas fa-chart-bar"},
}

# Préchargement des layouts des pages
pages = {}
for page in page_names.keys():
    try:
        module = importlib.import_module(page)
        pages[page] = module.layout
    except ImportError:
        pages[page] = html.Div(f"Erreur : Module {page} non trouvé", style={'color': 'red'})

# Initialisation de l'application Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # Point d'entrée WSGI pour Gunicorn

# Sommaire avec un design harmonieux
def create_sidebar():
    return html.Div(
        [
            html.H2("Dashboard",
                    style={'fontSize': '30px', 'color': '#ffffff', 'textAlign': 'center', 'padding': '25px 0',
                           'fontFamily': 'Arial, sans-serif', 'letterSpacing': '1.5px'}),
            html.Div(
                [
                    dcc.Link(
                        [html.I(className=f"{page_data['icon']} mr-2",
                                style={'marginRight': '10px', 'fontSize': '20px'}), page_data['name']],
                        href=page_data['path'],
                        id=f"nav-link-{page}",
                        className="nav-link",
                        style={'padding': '15px 20px', 'color': '#ffffff', 'borderRadius': '10px',
                               'marginBottom': '15px', 'display': 'flex', 'alignItems': 'center',
                               'textDecoration': 'none', 'fontSize': '18px', 'fontFamily': 'Arial, sans-serif',
                               'transition': 'background-color 0.3s, transform 0.2s'}
                    ) for page, page_data in page_names.items()
                ],
                style={'padding': '0 20px'}
            ),
        ],
        style={'width': '300px', 'background': 'linear-gradient(180deg, #1f2a44 0%, #3b2f5b 100%)', 'height': '100vh',
               'position': 'fixed', 'top': '0', 'left': '0', 'boxShadow': '2px 0 15px rgba(0, 0, 0, 0.3)',
               'overflow': 'hidden'}
    )

# Mise en page principale
app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    create_sidebar() if len(page_names) > 1 else None,
    html.Div(id='page-container', style={'marginLeft': '300px' if len(page_names) > 1 else '0', 'height': '100vh',
                                         'width': 'calc(100vw - 300px)' if len(page_names) > 1 else '100vw',
                                         'overflow': 'hidden', 'padding': '15px 30px 30px 15px',
                                         'backgroundColor': '#2a3a50'}),
    dcc.Store(id='current-page', data='page1'),  # Stocke la page actuelle
], style={'margin': '0', 'padding': '0', 'height': '100vh', 'width': '100vw', 'overflow': 'hidden',
          'background': 'linear-gradient(135deg, #2a3a50 0%, #3b4a60 100%)', 'position': 'fixed', 'top': '0',
          'left': '0'})

# Callback pour gérer le changement de page
@app.callback(
    Output('page-container', 'children'),
    Output('current-page', 'data'),
    Input('url', 'pathname'),
    prevent_initial_call=False
)
def display_page(pathname):
    if pathname is None or pathname == '/':
        page = "page1"
    else:
        path_to_page = {data['path']: page for page, data in page_names.items()}
        page = path_to_page.get(pathname, "page1")

    layout = pages.get(page, html.Div("Page non trouvée",
                                      style={'padding': '20px', 'fontSize': '24px', 'color': '#ff4d4d',
                                             'fontFamily': 'Arial, sans-serif'}))
    return html.Div(layout, id=f'page-content-{page}', style={'height': '100%', 'width': '100%'}), page

# Callback pour mettre à jour le style des boutons
@app.callback(
    [Output(f"nav-link-{page}", "style") for page in page_names.keys()],
    Input('url', 'pathname')
)
def update_active_link(pathname):
    base_style = {'padding': '15px 20px', 'color': '#ffffff', 'borderRadius': '10px', 'marginBottom': '15px',
                  'display': 'flex', 'alignItems': 'center', 'textDecoration': 'none', 'fontSize': '18px',
                  'fontFamily': 'Arial, sans-serif', 'transition': 'background-color 0.3s, transform 0.2s'}
    active_style = base_style.copy()
    active_style.update({'backgroundColor': 'rgba(0, 135, 147, 0.8)', 'color': 'white', 'transform': 'scale(1.05)'})

    if pathname is None or pathname == '/':
        active_page = "page1"
    else:
        path_to_page = {data['path']: page for page, data in page_names.items()}
        active_page = path_to_page.get(pathname, "page1")

    return [active_style if page == active_page else base_style for page in page_names.keys()]

