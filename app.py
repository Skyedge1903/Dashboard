# app.py

import dash
from dash import html, dcc, Output, Input
import importlib
import os
import flask
import logging

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Flask server
# -----------------------------------------------------------------------------
server = flask.Flask(__name__)

# -----------------------------------------------------------------------------
# Dash app
# -----------------------------------------------------------------------------
app = dash.Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True
)

app.title = "Financial Dashboard"

# -----------------------------------------------------------------------------
# GLOBAL CSS FIX (CRITICAL)
# -----------------------------------------------------------------------------
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* === CSS RESET MINIMAL === */
            html, body {
                margin: 0;
                padding: 0;
                height: 100%;
                width: 100%;
                font-family: Arial, sans-serif;
            }

            /* === FIX LABEL ALIGNMENT (ROOT CAUSE) === */
            label {
                display: inline-flex;
                align-items: center;
                line-height: normal;
                vertical-align: middle;
            }

            input, select, textarea {
                line-height: normal;
                vertical-align: middle;
            }

            /* Prevent flex parents from breaking text alignment */
            * {
                box-sizing: border-box;
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
"""

# -----------------------------------------------------------------------------
# Pages configuration
# -----------------------------------------------------------------------------
page_names = {
    "page1": {"name": "Accueil", "path": "/accueil", "icon": "fas fa-home"},
    "page4": {"name": "Desinflationary bust", "path": "/Desinflationary-boom", "icon": "fas fa-chart-bar"},
    "page5": {"name": "Desinflationary boom", "path": "/Desinflationary-bust", "icon": "fas fa-chart-bar"},
    "page3": {"name": "Inflationary bust", "path": "/Inflationary-bust", "icon": "fas fa-chart-bar"},
    "page2": {"name": "Inflationary boom", "path": "/Inflationary-boom", "icon": "fas fa-chart-bar"},
}

# -----------------------------------------------------------------------------
# Load pages
# -----------------------------------------------------------------------------
pages = {}
for page in page_names:
    try:
        module = importlib.import_module(page)
        pages[page] = module.layout
    except ImportError as e:
        logger.error(f"Erreur chargement {page}: {e}")
        pages[page] = html.Div(
            f"Erreur : module {page} non trouvé",
            style={"color": "red", "padding": "20px"}
        )

# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
def create_sidebar():
    return html.Div(
        [
            html.H2(
                "Dashboard",
                style={
                    "fontSize": "30px",
                    "color": "#ffffff",
                    "textAlign": "center",
                    "padding": "25px 0",
                    "letterSpacing": "1.5px"
                }
            ),
            html.Div(
                [
                    dcc.Link(
                        [
                            html.I(
                                className=page_data["icon"],
                                style={"marginRight": "10px", "fontSize": "20px"}
                            ),
                            page_data["name"],
                        ],
                        href=page_data["path"],
                        id=f"nav-link-{page}",
                        style={
                            "padding": "15px 20px",
                            "color": "#ffffff",
                            "borderRadius": "10px",
                            "marginBottom": "15px",
                            "display": "flex",
                            "alignItems": "center",
                            "textDecoration": "none",
                            "fontSize": "18px",
                        },
                    )
                    for page, page_data in page_names.items()
                ],
                style={"padding": "0 20px"},
            ),
        ],
        style={
            "width": "300px",
            "background": "linear-gradient(180deg, #1f2a44 0%, #3b2f5b 100%)",
            "height": "100vh",
            "position": "fixed",
            "top": "0",
            "left": "0",
            "boxShadow": "2px 0 15px rgba(0,0,0,0.3)",
        },
    )

# -----------------------------------------------------------------------------
# Layout
# -----------------------------------------------------------------------------
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        create_sidebar(),
        html.Div(
            id="page-container",
            style={
                "marginLeft": "300px",
                "minHeight": "100vh",
                "padding": "20px 30px",
                "backgroundColor": "#2a3a50",
            },
        ),
    ]
)

# -----------------------------------------------------------------------------
# Routing
# -----------------------------------------------------------------------------
@app.callback(
    Output("page-container", "children"),
    Input("url", "pathname"),
)
def display_page(pathname):
    if not pathname or pathname == "/":
        pathname = "/accueil"

    path_to_page = {v["path"]: k for k, v in page_names.items()}
    page = path_to_page.get(pathname, "page1")

    return pages.get(page)

# -----------------------------------------------------------------------------
# Run
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)
