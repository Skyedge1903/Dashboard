# app.py
import dash
from dash import html, dcc, Output, Input, State, no_update
import importlib
import os
import flask
import logging

# Configure le logging pour diagnostiquer les problèmes
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation du serveur Flask
server = flask.Flask(__name__)

# Initialisation de l'application Dash avec les stylesheets externes pour Bootstrap et Font Awesome
app = dash.Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
    ]
)
app.suppress_callback_exceptions = True
app.serve_locally = False
app.title = "Financial Dashboard"

# Ajout du CSS personnalisé via index_string
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style type="text/css">
            label {
                position: relative;
                top: 2mm;
                vertical-align: middle;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Définition des noms des pages et leurs chemins
page_names = {
    "page1": {"name": "Accueil", "path": "/accueil", "icon": "fas fa-home"},
    "page4": {"name": "Desinflationary bust", "path": "/Desinflationary-boom", "icon": "fas fa-chart-bar"},
    "page5": {"name": "Desinflationary boom", "path": "/Desinflationary-bust", "icon": "fas fa-chart-bar"},
    "page3": {"name": "Inflationary bust", "path": "/Inflationary-bust", "icon": "fas fa-chart-bar"},
    "page2": {"name": "Inflationary boom", "path": "/Inflationary-boom", "icon": "fas fa-chart-bar"},
    # "page6": {"name": "Ethereum Flippening", "path": "/Ethereum-flippening", "icon": "fas fa-chart-bar"},
}

# Préchargement des layouts des pages
pages = {}
for page in page_names.keys():
    try:
        logger.info(f"Chargement du module {page}")
        module = importlib.import_module(page)
        pages[page] = module.layout
    except ImportError as e:
        logger.error(f"Erreur lors du chargement de {page}: {str(e)}")
        pages[page] = html.Div(f"Erreur : Module {page} non trouvé", style={'color': 'red'})

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
                                style={'marginRight': '10px', 'fontSize': '20px', 'verticalAlign': 'middle'}),
                         page_data['name']],
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
    dcc.Store(id='current-page', data='page1'),
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
    logger.info(f"Changement de page vers {pathname}")
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

# Route pour favicon
@app.server.route('/favicon.ico')
def favicon():
    try:
        return flask.send_from_directory(os.path.join(app.server.root_path, 'static'), 'favicon.ico')
    except FileNotFoundError:
        logger.warning("Favicon.ico non trouvé")
        return '', 204  # Réponse vide avec statut 204 (No Content)

# Route pour la page racine
@app.server.route('/')
def serve_root():
    return flask.redirect('/accueil')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))
