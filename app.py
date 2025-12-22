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
# CSS GLOBAL — FIX LABEL OFFSET (CORRECT WAY)
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
            /* RESET SAFE */
            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
            }

            /*
             FIX DASH LABEL / TEXT OFFSET
             DO NOT USE FLEX ON LABELS
            */
            label,
            .dash-label,
            .dash-input label,
            .dash-dropdown label,
            .dash-radio-items label,
            .dash-checklist label,
            .dash-table-container label {
                line-height: 1.4 !important;
                vertical-align: middle !important;
                padding-top: 0 !important;
                padding-bottom: 0 !important;
            }

            /*
             FIX DCC DROPDOWN INTERNAL TEXT
            */
            .Select-control,
            .Select-value,
            .Select-value-label {
                line-height: 1.4 !important;
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
        pages[page] = html.Div(
            "Page non trouvée",
            style={"color": "red", "fontSize": "20px", "padding": "20px"},
        )

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
                    "letterSpacing": "1.5px",
                },
            ),
            html.Div(
                [
                    dcc.Link(
                        [
                            html.I(
                                className=data["icon"],
                                style={"marginRight": "10px", "fontSize": "18px"},
                            ),
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
                            "fontSize": "17px",
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
            "boxShadow": "2px 0 15px rgba(0,0,0,0.3)",
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
                "padding": "20px 30px",
                "backgroundColor": "#2a3a50",
                "overflow": "auto",
            },
        ),
    ],
    style={
        "height": "100vh",
        "width": "100vw",
        "margin": "0",
        "padding": "0",
    },
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
# Active link styling
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
            "fontSize": "17px",
        }
        if page == active:
            style.update(
                {
                    "backgroundColor": "rgba(0,135,147,0.85)",
                    "transform": "scale(1.03)",
                }
            )
        styles.append(style)

    return styles

# -------------------------------------------------
# Run
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)), debug=False)
