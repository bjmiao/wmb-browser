import json

import dash_bootstrap_components as dbc
from dash import ALL, MATCH, Input, Output, Patch, State, callback, dcc, html
from dash.exceptions import PreventUpdate

# from wmb_browser.viewmodel import CategoricalFigurePanel, ContinuousFigurePanel
from wmb_browser.viewmodel.ScatterPlotDiv import ScatterPlotDiv
from wmb_browser.backend.human_dataset import human_datasets as sapien_dataset

DEMO_TEXT = """\
{"coord": "tsne", "datasource": "mCH_Inhi",
    "figures": [
        {"type": "scatter", "colorby": "_Region"},
        {"type": "scatter", "colorby": "_mCGFrac"}
    ]
}
"""
input_div = dbc.Card([
        dbc.CardHeader("Create your browser layout"),
        dbc.CardBody(
            [
                dcc.Markdown("""
                    ## Human brain atlas

                    Welcome to the human brain atlas! You can gain a quick overview of the data from the
                    recent Science paper [Single-cell DNA methylation and 3D genome architecture in the human brain](!https://doi.org/10.1126/science.adf5357).
                """),
                dbc.Container(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Button(
                                        "Add panel",
                                        className="my-1 mr-2",
                                        outline=True,
                                        size="sm",
                                        id="add-panel",
                                        style={
                                            "height": 100,
                                            "background-color": "#2962a1",  # Set background color
                                            "color": "#ffffff",  # Set text color
                                            "text-align": "center",  # Set text alignment
                                            "font-size": "20px",  # Set font size
                                        },
                                    )
                                ),
                                dbc.Col(
                                    dbc.Textarea(id="new-item-input", style={"height": 100}, value=DEMO_TEXT),
                                    className="mb-1",
                                    xxl=10,
                                    xl=10,
                                    lg=8,
                                    md=6,
                                    sm=12,
                                ),
                            ]
                        )
                    ]
                ),
            ]
        ),
    ]
)


def _generate_panel_dev(input_string, panel_index):
    """Generate a figure.

    Args:
        input_string should be lines of JSON strings indicating
            what type of plots should be generated
    Returns:
        success: True or false, whether this add-panel succeed
        panel_dev: the Div for the figure
    """
    figure_json = None
    try:
        figure_json = json.loads(input_string)
    except json.decoder.JSONDecodeError as e:
        print(e)
        raise PreventUpdate
    figure_container = None
    # figure_types = figure_json['type']
    # if type(figure_types) == str: # only one type:
    #     figure_type = [figure_types]
    figure_all = figure_json["figures"]
    if type(figure_all) is dict:
        figure_all = [figure_all]
    if len(figure_all) > 10:
        print("Too much figures at the same time")
        raise PreventUpdate
    all_figures = []
    for figure_index, figure_config in enumerate(figure_all):
        figure_type = figure_config["type"]
        figure_json_single_figure = figure_json.copy()
        figure_json_single_figure.pop("figures")
        figure_json_single_figure["panel_index"] = panel_index
        figure_json_single_figure["figure_index"] = figure_index
        figure_json_single_figure["figure_type"] = figure_type
        for k, v in figure_config.items():
            figure_json_single_figure[k] = v
        print(figure_json_single_figure)
        if figure_type == "scatter":
            figure_container = ScatterPlotDiv.generate_panel(figure_json_single_figure)
            all_figures.append(figure_container)
        # if figure_type == "continuous":
        #     figure_container = ContinuousFigurePanel.generate_panel(figure_json_single_figure)
        #     # generate_continuous_figure(figure_json)
        #     all_figures.append(figure_container)
        # elif figure_type == "categorical":
        #     figure_container = CategoricalFigurePanel.generate_panel(figure_json_single_figure)
        #     # figure_container = generate_categorical_figure(figure_json)
        #     all_figures.append(figure_container)
        elif figure_type == "higlass":
            pass
        else:
            print(f"Unknown figure type {figure_type}. This panel will not be shown")

    text_description_layout = html.Div(
        [
            dcc.Markdown("""
            **Cell Metadata Clipboard**
        """),
            # html.Pre(/id='click-data'),
            html.Pre(
                id={
                    "type": "clickdata-textarea",
                    "panel-index": panel_index,
                }
            ),
            dcc.Clipboard(
                # target_id='click-data',
                target_id={
                    "type": "clickdata-textarea",
                    "panel-index": panel_index,
                },
                title="copy",
                style={
                    "display": "inline-block",
                    "fontSize": 20,
                    "verticalAlign": "top",
                },
            ),
        ],
        className="three columns",
    )
    figure_style_template = {"display": "inline-block", "vertical-align": "top",}
    panel_wrapper = dbc.Card(
        [
            dbc.CardHeader(f"Panel {panel_index}: Data source: {figure_json['datasource']}"),
            dbc.CardBody(
                    [
                        html.Div(
                            [html.Div(figure, style=figure_style_template) for figure in all_figures],
                            style={"display":"block",
                                   "overflow-x": "auto",
                                   "overflow-y":"scroll",
                                   "white-space": "nowrap"
                            },
                        ),
                        html.Div(text_description_layout)
                    ],
                ),
        ],
    )
    return True, panel_wrapper


@callback(
    Output("figure-div", "children", allow_duplicate=True),
    Input("add-panel", "n_clicks"),
    State("new-item-input", "value"),
    prevent_initial_call=True,
)
def add_panel(n_clicks, input_string):
    """Add a figure given the input string

    Args:
    - n_clicks: used as the panel index (1-based)
    - input_string: should be in a json format
    Returns:
    - a panel of figure in a Div
    """
    if not n_clicks:
        raise PreventUpdate
    # updated_localstorage = Patch()
    # updated_localstorage['data'] = localstorage + [input_string]

    # get this div
    success, new_panel_dev = _generate_panel_dev(input_string, panel_index=n_clicks)
    updated_panel_dev = Patch()
    if success:
        updated_panel_dev.append(new_panel_dev)
    else:
        raise PreventUpdate
    return updated_panel_dev

AVAILABLE_DATASETS = ["mCG", "mCH"]

def initial_human_browser_layout():
    """Dynamically initialized the browser layout"""
    
    human_browser_layout = html.Div(
        [
            html.Div(input_div),
            html.Div(id="figure-div", children=[]),  # place to show all figures
            # TODO: how to load the localstorage when initiating the page
            # html.Div(id='hover-data', children=[])
            # html.Div([dcc.Store(id='figure-string-localstorage', storage_type='local', data='''''')]) # used to cache the panels
        ]
    )
    return human_browser_layout
