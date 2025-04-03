from dash import dcc, html


class Page:
    def __init__(self, grid_layout):
        self.grid_layout = grid_layout
        self.graphs = {}

    def create_dark_graph(self, figure):
        figure.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0, 0, 0, 0)',  # Transparent
            plot_bgcolor='rgba(0, 0, 0, 0)',  # Transparent
            font=dict(color='#ffffff', family="Arial, sans-serif"),
            title=dict(x=0.5, y=0.98, xanchor='center', yanchor='top', pad=dict(t=20)),
            margin=dict(l=20, r=20, t=40, b=20),
            autosize=True,
            width=None,
            height=None,
        )
        return dcc.Graph(
            figure=figure,
            style={
                'height': '100%',
                'width': '100%',
                'borderRadius': '12px',
                'overflow': 'hidden',
                'flexGrow': '1',
            },
            config={
                'responsive': True,
                'autosizable': True,
                'displayModeBar': False
            }
        )

    def append(self, graph_id, figure):
        self.graphs[graph_id] = self.create_dark_graph(figure)

    def render(self):
        num_rows = len(self.grid_layout)
        num_columns = len(self.grid_layout[0].split())
        grid_template_areas = ' '.join([f'"{row}"' for row in self.grid_layout])

        grid_style = {
            'display': 'grid',
            'gridTemplateAreas': grid_template_areas,
            'gridTemplateColumns': ' '.join(['1fr'] * num_columns),
            'gridTemplateRows': ' '.join(['1fr'] * num_rows),
            'height': '100vh',
            'width': '100%',
            'backgroundColor': 'transparent',
            'gap': '30px',
            'padding': '20px 35px 35px 20px',
            'boxSizing': 'border-box',
            'overflow': 'hidden',
        }

        unique_ids = set()
        for row in self.grid_layout:
            for graph_id in row.split():
                unique_ids.add(graph_id)

        grid_container = html.Div(
            [html.Div(
                self.graphs[graph_id],
                id=f'graph-card-{graph_id}',  # ID unique pour chaque carte
                className='graph-card',  # Classe pour le JavaScript
                style={
                    'gridArea': graph_id,
                    'background': 'linear-gradient(145deg, #1f2a44 0%, #263544 100%)',
                    'borderRadius': '12px',
                    'boxShadow': '0 4px 15px rgba(0, 0, 0, 0.3)',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'height': '100%',
                    'width': '100%',
                    'overflow': 'hidden',
                    'transition': 'transform 0.2s ease',  # Transition fluide
                })
                for graph_id in unique_ids if graph_id in self.graphs
            ],
            style=grid_style
        )
        return grid_container
