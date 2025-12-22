import dash
from dash import html, dcc, Output, Input
import importlib
import os
import flask
import logging

# -------------------------------------------------
# Logging
# -------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------------------------
# Flask / Dash init
# -------------------------------------------------
server = flask.Flask(__name__)

app = dash.Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True,
)

app.title = "Financial Dashboard"
app.serve_locally = False

# -------------------------------------------------
# CSS GLOBAL — FIX LABEL ALIGNMENT
# -------------------------------------------------
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

            body {
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
            }

            /* FIX DASH LABEL ALIGNMENT */
            label {
                display: flex !important;
                align-items: center !important;
                line-height: normal !important;
                margin-bottom: 4px;
            }

            /* FIX INPUT / DROPDOWN WRAPPERS */
            .dash-input,
            .dash-dropdown,
            .dash-radio-items,
            .dash-checklist {
                display: flex;
                align-items: center;
            }

            /* FIX DCC DROPDOWN INTERNAL */
            .Select-control {
                display: flex;
                align-items: center;
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

# -------------------------------------------------
# Pages
# -------------------------------------------------
page_names = {
    "page1": {"name": "Accueil", "path": "/accueil", "icon": "fas fa-home"},
    "page2": {"name": "Inflationary boom", "path": "/Inflationary-boom", "icon": "fas fa-chart-bar"},
    "page3": {"name": "Inflationary bust", "path": "/Inflationary-bust", "icon": "fas fa-chart-bar"},
    "page4": {"name": "Desinflationary boom", "path": "/Desinflationary-boom", "icon": "fas fa-chart-bar"},
    "page5": {"name": "Desinflationary bust", "path": "/Desinflationary-bust", "icon": "fas fa-chart-bar"},
}

pages = {}
for page in page_names:
    try:
        module = importlib.import_module(page)
        pages[page] = module.layout
        logger.info(f"Loaded {page}")
    except Exception as e:
        logger.error(e)
        pages[page] = html.Div("Page non trouvée")

# -------------------------------------------------
# Sidebar
# -------------------------------------------------
def create_sidebar():
    return html.Div(
        [
            html.H2(
                "Dashboard",
                style={
                    "color": "white",
                    "textAlign": "center",
                    "padding": "25px 0",
                },
            ),
            html.Div(
                [
                    dcc.Link(
                        [
                            html.I(className=data["icon"], style={"marginRight": "10px"}),
                            data["name"],
                        ],
                        href=data["path"],
                        id=f"nav-link-{page}",
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "padding": "15px 20px",
                            "color": "white",
                            "textDecoration": "none",
                            "borderRadius": "10px",
                            "marginBottom": "12px",
                        },
                    )
                    for page, data in page_names.items()
                ],
                style={"padding": "0 20px"},
            ),
        ],
        style={
            "width": "300px",
            "height": "100vh",
            "position": "fixed",
            "left": "0",
            "top": "0",
            "background": "linear-gradient(180deg, #1f2a44, #3b2f5b)",
        },
    )

# -------------------------------------------------
# Layout
# -------------------------------------------------
app.layout = html.Div(
    [
        dcc.Location(id="url"),
        create_sidebar(),
        html.Div(
            id="page-container",
            style={
                "marginLeft": "300px",
                "height": "100vh",
                "padding": "20px",
                "backgroundColor": "#2a3a50",
            },
        ),
    ]
)

# -------------------------------------------------
# Routing
# -------------------------------------------------
@app.callback(
    Output("page-container", "children"),
    Input("url", "pathname"),
)
def display_page(pathname):
    path_map = {v["path"]: k for k, v in page_names.items()}
    page = path_map.get(pathname, "page1")
    return pages[page]

# -------------------------------------------------
# Active link
# -------------------------------------------------
@app.callback(
    [Output(f"nav-link-{p}", "style") for p in page_names],
    Input("url", "pathname"),
)
def update_links(pathname):
    path_map = {v["path"]: k for k, v in page_names.items()}
    active = path_map.get(pathname, "page1")

    styles = []
    for page in page_names:
        style = {
            "display": "flex",
            "alignItems": "center",
            "padding": "15px 20px",
            "color": "white",
            "textDecoration": "none",
            "borderRadius": "10px",
            "marginBottom": "12px",
        }
        if page == active:
            style["backgroundColor"] = "rgba(0,135,147,0.8)"
        styles.append(style)

    return styles

# -------------------------------------------------
# Run
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)
