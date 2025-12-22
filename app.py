import dash
from dash import html, dcc, Output, Input
import flask
import importlib
import logging

# --------------------------------------------------
# Logging
# --------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Server
# --------------------------------------------------
server = flask.Flask(__name__)

app = dash.Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True
)

app.title = "Financial Dashboard"

# --------------------------------------------------
# HTML TEMPLATE + CSS FIX
# --------------------------------------------------
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

        /* CRITICAL FIX */
        label {
            display: block !important;
            line-height: normal !important;
            padding: 0 !important;
            margin-bottom: 6px;
            white-space: normal;
        }

        /* NEVER FLEX LABELS */
        label * {
            display: inline;
        }

        /* INPUT SPACING */
        input, select, textarea {
            margin-bottom: 14px;
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

# --------------------------------------------------
# Pages
# --------------------------------------------------
page_names = {
    "page1": {"name": "Accueil", "path": "/accueil"},
    "page2": {"name": "Inflationary boom", "path": "/inflationary-boom"},
}

pages = {}
for page in page_names:
    try:
        module = importlib.import_module(page)
        pages[page] = module.layout
    except Exception:
        pages[page] = html.Div("Page introuvable")

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
def sidebar():
    return html.Div(
        [
            html.H2("Dashboard", style={"color": "white", "marginBottom": "30px"}),
            *[
                dcc.Link(
                    page_names[p]["name"],
                    href=page_names[p]["path"],
                    style={
                        "display": "block",
                        "color": "white",
                        "padding": "12px",
                        "textDecoration": "none",
                        "marginBottom": "8px",
                        "borderRadius": "6px",
                        "background": "#34495e"
                    }
                )
                for p in page_names
            ]
        ],
        style={
            "width": "260px",
            "padding": "20px",
            "background": "#1f2a44",
            "minHeight": "100vh"
        }
    )

# --------------------------------------------------
# Layout
# --------------------------------------------------
app.layout = html.Div(
    [
        dcc.Location(id="url"),
        sidebar(),
        html.Div(
            id="page-container",
            style={
                "marginLeft": "260px",
                "padding": "30px",
                "minHeight": "100vh",
                "background": "#2a3a50",
                "color": "white"
            }
        )
    ]
)

# --------------------------------------------------
# Routing
# --------------------------------------------------
@app.callback(
    Output("page-container", "children"),
    Input("url", "pathname")
)
def route(pathname):
    for page, data in page_names.items():
        if pathname == data["path"]:
            return pages[page]
    return pages["page1"]

# --------------------------------------------------
# Run
# --------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)
