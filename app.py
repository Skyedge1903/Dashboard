# app.py

import dash
from dash import html, dcc, Output, Input
import importlib
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
# GLOBAL CSS (FINAL FIX)
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
        /* RESET */
        * {
            box-sizing: border-box;
        }

        html, body {
            margin: 0;
            padding: 0;
            height: 100%;
            font-family: Arial, sans-serif;
        }

        /* DEFINITIVE LABEL FIX */
        label {
            display: flex !important;
            align-items: center !important;
            height: 100% !important;
            line-height: 1 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* NORMALIZE INPUT HEIGHT */
        input, select, textarea {
            height: 36px;
            line-height: 36px;
            padding: 0 8px;
        }

        /* COMMON FORM ROW */
        .form-row {
            display: flex;
            align-items: center;
            gap: 12px;
            height: 36px;
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
    "page2": {"name": "Inflationary boom", "path": "/Inflationary-boom", "icon": "fas fa-chart-bar"},
    "page3": {"name": "Inflationary bust", "path": "/Inflationary-bust", "icon": "fas fa-chart-bar"},
    "page4": {"name": "Desinflationary boom", "path": "/Desinflationary-boom", "icon": "fas fa-chart-bar"},
    "page5": {"name": "Desinflationary bust", "path": "/Desinflationary-bust", "icon": "fas fa-chart-bar"},
}

# -----------------------------------------------------------------------------
# Load pages
# -----------------------------------------------------------------------------
pages = {}
for page in page_names:
    try:
        pages[page] = importlib.import_module(page).layout
    except Exception as e:
        logger.error(e)
        pages[page] = html.Div("Page introuvable", style={"color": "red"})

# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
def create_sidebar():
    return html.Div(
        [
            html.H2(
                "Dashboard",
                style={
                    "color": "white",
                    "textAlign": "center",
                    "padding": "24px 0"
                }
            ),
            *[
                dcc.Link(
                    page_data["name"],
                    href=page_data["path"],
                    id=f"nav-link-{page}",
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "padding": "14px 20px",
                        "color": "white",
                        "textDecoration": "none",
                        "borderRadius": "8px",
                        "marginBottom": "12px"
                    }
                )
                for page, page_data in page_names.items()
            ],
        ],
        style={
            "width": "280px",
            "height": "100vh",
            "position": "fixed",
            "left": 0,
            "top": 0,
            "background": "#1f2a44"
        },
    )

# -----------------------------------------------------------------------------
# Layout
# -----------------------------------------------------------------------------
app.layout = html.Div(
    [
        dcc.Location(id="url"),
        create_sidebar(),
        html.Div(
            id="page-container",
            style={
                "marginLeft": "280px",
                "minHeight": "100vh",
                "padding": "24px",
                "background": "#2a3a50"
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
def render_page(pathname):
    if not pathname or pathname == "/":
        pathname = "/accueil"

    page = next(
        (k for k, v in page_names.items() if v["path"] == pathname),
        "page1"
    )
    return pages[page]

# -----------------------------------------------------------------------------
# Run
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)
