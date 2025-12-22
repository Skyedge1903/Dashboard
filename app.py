import dash
from dash import html, dcc

app = dash.Dash(__name__)

app.index_string = """
<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    <style>

        body {
            margin: 0;
            font-family: Arial, sans-serif;
        }

        /* FIX LABEL ALIGNMENT — THE ONLY SAFE WAY */
        label {
            display: inline-block;
            vertical-align: middle;
            line-height: 1.4;
            margin-bottom: 4px;
        }

        input,
        textarea,
        select {
            line-height: 1.4;
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

app.layout = html.Div(
    style={"padding": "40px"},
    children=[
        html.Div([
            html.Label("Nom"),
            dcc.Input(type="text", style={"marginLeft": "10px"}),
        ]),
        html.Br(),
        html.Div([
            html.Label("Pays"),
            dcc.Dropdown(
                options=[
                    {"label": "France", "value": "FR"},
                    {"label": "Allemagne", "value": "DE"},
                ],
                style={"width": "200px", "marginLeft": "10px"},
            ),
        ]),
    ],
)

if __name__ == "__main__":
    app.run(debug=True)
