import dash
from dash import html, dcc, Output, Input
import importlib
import flask
import logging
import os

# --------------------------------------------------
# Logging
# --------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Flask server
# --------------------------------------------------
server = flask.Flask(__name__)

# --------------------------------------------------
# Dash app
# --------------------------------------------------
app = dash.Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True,
)

app.title = "Financial Dashboard"

# --------------------------------------------------
# Pages
# --------------------------------------------------
page_names = {
    "page1": {"name": "Accueil", "path": "/accueil", "icon": "fas fa-home"},
    "page2": {"name": "Inflationary boom", "path": "/Inflationary-boom", "icon": "fas fa-chart-bar"},
    "page3": {"name": "Inflationary bust", "path": "/Inflationary-bust", "icon": "fas fa-chart-bar"},
    "page4": {"name": "Desinflationary bust", "path": "/Desinflationary-bust", "icon": "fas fa-chart-bar"},
    "page5": {"name": "Desinflationary boom", "path": "/Desinflationary-boom", "icon": "fas fa-chart-bar"},
}

pages = {}
for page in page_names:
    try:
        module = importlib.import_module(page)
        pages[page] = module.layout
    except Exception as e:
        logger.error(e)
        pages[page] = html.Div("Erreur de chargement", style={"color": "red"})

# --------------------------------------------------
# GLOBAL CSS RESET + LABEL FIX
# --------------------------------------------------
GLOBAL_CSS = """
* {
    box-sizing: border-box;
}

html, body {
    margin: 0;
    padding: 0;
    height: 100%;
    font-family: Arial, sans-serif;
}

label {
    display: flex !important;
    align-items: center !important;
    line-height: normal !important;
    padding: 0 !important;
    margin: 0 !important;
    vertical-align: middle !important;
}

.dash-input,
.dash-dropdown,
.dash-radio-items,
.dash-checklist {
    display: flex;
    align-items: center;
}

.Select-control,
.Select-value,
.Select-input {
    display: flex !important;
    align-items: center !important;
}
"""

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
def create_sidebar():
    return html.Div(
        [
            html.H2(
                "Dashboard",
                className="sidebar-title"
            ),
            html.Div(
                [
                    dcc.Link(
                        [
                            html.I(className=page["icon"]),
                            html.Span(page["name"], className="nav-text"),
                        ],
                        href=page["path"],
                        id=f"nav-link-{key}",
                        className="nav-link"
                    )
                    for key, page in page_names.items()
                ],
                className="nav-container"
            ),
        ],
        className="sidebar"
    )

# --------------------------------------------------
# Layout
# --------------------------------------------------
app.layout = html.Div(
    [
        dcc.Location(id="url"),
        html.Style(GLOBAL_CSS),
        create_sidebar(),
        html.Div(id="page-container", className="content"),
    ],
    className="app-root"
)

# --------------------------------------------------
# Callbacks
# --------------------------------------------------
@app.callback(
    Output("page-container", "children"),
    Input("url", "pathname"),
)
def display_page(pathname):
    path_map = {v["path"]: k for k, v in page_names.items()}
    page_key = path_map.get(pathname, "page1")
    return pages.get(page_key, html.Div("Page inconnue"))

@app.callback(
    [Output(f"nav-link-{k}", "className") for k in page_names],
    Input("url", "pathname"),
)
def update_nav(pathname):
    path_map = {v["path"]: k for k, v in page_names.items()}
    active = path_map.get(pathname, "page1")

    return [
        "nav-link active" if k == active else "nav-link"
        for k in page_names
    ]

# --------------------------------------------------
# Routes
# --------------------------------------------------
@app.server.route("/")
def root():
    return flask.redirect("/accueil")

# --------------------------------------------------
# Run
# --------------------------------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8050)),
        debug=False
    )
