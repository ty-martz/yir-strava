#############
## IMPORTS ##
#############
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from datetime import datetime
from dash import dash_table

from helpers import startup_procedure, parse_contents

singlet_emoji = "\U0001F3BD"

##############
## Dash App ##
##############

# Initiate
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.Link( # add favicon with saved link asset
        rel='icon',
        href='assets/favicon.ico',
        type='image/x-icon'
    ),
    
    # Add title and subtitle (to ask for an upload)
    html.H1(f"2023 Strava Year in Sport {singlet_emoji}", style={'textAlign': 'center'}),
    html.H3("Upload and Analyze Data", style={'textAlign': 'center'}),

    # File Upload Handler
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '50%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '8px',
            'margin': '20px auto',
            'textAlign': 'center'
        },
        multiple=False
    ),

    # Output for upload success and quick info along with link to exporting
    html.Div(id='output-analysis', 
             children=['Upload an `activities.csv` file from your Strava account to populate your Year in Sport!'],
             style={'textAlign': 'center'}
            ),
    html.Div(id='link-out', 
             children=[html.A("How to Bulk Export you Data", href="https://support.strava.com/hc/en-us/articles/216918437-Exporting-your-Data-and-Bulk-Export#h_01GG58HC4F1BGQ9PQZZVANN6WF")],
             style={'textAlign': 'center', 'font-size': '10px'}
            ),

    # Main content Div
    html.Div(
            style={'border': '2px solid #FFA500', 'padding': '20px', 'border-radius': '15px', 'margin': '10px'},
            children=[
                
                # Total Activity Counts and Distances Table
                dcc.Graph(
                    id='total-stats-table',
                 ),
                
                # Filter on Activities
                html.Label("Filter Activities", style={'margin-left': '185px'}),
                dcc.Dropdown(
                    id='activity-filter',
                    multi=True,
                    value=['Run'],  # Default to 'Run'
                    style={
                        'width': '65%',
                        'margin': '20px auto',
                        'backgroundColor': '#f8f9fa',
                        'borderRadius': '8px',
                        'border': '1px solid #ced4da',
                        'color': '#495057',
                    },
                    placeholder='Select activity types...',
                    clearable=True,  # Allow clearing the selected values
                ),
                # Total Distance Bar Chart by Month
                 dcc.Graph(
                     id='total-distance-by-month',
                 ),

                 # Cumulative Distance Graph with 2022 Comparison Line
                 dcc.Graph(
                     id='cumulative-distance',
                 ),

                 # Total Elevation Bar Chart by Month
                 dcc.Graph(
                     id='total-elevation-by-month',
                 ),
                 
                 html.H3('Key Stats'),
                 
                 # Additional Statistics Table for 2023
                 dash_table.DataTable(
                     id='stats-table',
                     columns=[
                         {"name": 'Metric', "id": 'metric'},
                         {"name": '2023', "id": '2023'},
                         {"name": '2022', "id": '2022'}
                     ],
                     #data=table_data,
                     style_table={'border': '1px solid black'},
                 ),
             ]),
], style={'maxWidth': '800px', 'margin': 'auto'})


###############
## CALLBACKS ##
###############

## 1. On upload, handle file and display analysis results ##
@app.callback(
    Output('output-analysis', 'children', allow_duplicate=True),
    Output('total-stats-table', 'figure', allow_duplicate=True),
    Output('activity-filter', 'options', allow_duplicate=True),
    Output('activity-filter', 'value', allow_duplicate=True),
    Output('total-distance-by-month', 'figure', allow_duplicate=True),
    Output('cumulative-distance', 'figure', allow_duplicate=True),
    Output('total-elevation-by-month', 'figure', allow_duplicate=True),
    Output('stats-table', 'data', allow_duplicate=True),
    [Input('upload-data', 'contents')],#, Input('activity-filter', 'value')],
    prevent_initial_call=True
)

def update_analysis(contents):
    # parse uploaded file
    quick_info, upload = parse_contents(contents)
    if contents is None:
        return "Upload an 'activities.csv' file to see analysis results."
    
    # get activity types and transform data
    all_types = upload['Activity Type'].unique()
    df, df_2022, activity_types, grp_df_elev, grp_df_dist, table_dat, td_og = startup_procedure(upload)
    
    # activity_bar
    type_fig = px.bar(df.groupby('type').size().reset_index(name='Total Activities'),
                                   x='type', y='Total Activities', text='Total Activities',
                                   labels={'type': 'Activity Type', 'Total Activities': 'Total Activities'},
                                   title='Total Activities by Type',
                                   color_discrete_sequence=['#FFA500']
                                   )
    # activity_filter
    filt = [{'label': activity_type, 'value': activity_type} for activity_type in activity_types]
    
    # monthly distances
    dist_month = px.bar(grp_df_dist, x='month', y='distance', title='Total Elevation Gain by Month',
            labels={'month': 'Month', 'total_elevation_gain': 'Total Elevation Gain (meters)'},
            color='type'
            #color_discrete_sequence=['#FFA500'],
            )
    
    # cumulative distance
    cdist = {
        'data': [
            {'x': df['start_date_local'], 'y': df['cumulative_distance'], 'type': 'scatter', 'mode': 'lines', 'name': '2023'},
            {'x': df_2022['start_date_local_comp'], 'y': df_2022['cumulative_distance'], 'type': 'scatter', 'mode': 'lines', 'name': '2022'},
        ],
        'layout': {
            'title': 'Cumulative Distance Over Time (2023 vs. 2022)',
            'xaxis': {'title': 'Date'},
            'yaxis': {'title': 'Cumulative Distance (miles)'}
        }
    }
    
    #elevation
    elev = px.bar(grp_df_elev, x='month', y='total_elevation_gain', title='Total Elevation Gain by Month',
            labels={'month': 'Month', 'total_elevation_gain': 'Total Elevation Gain (meters)'},
            color_discrete_sequence=['#FFA500'],
            )
    
    # stats table
    td = table_dat
    
    return quick_info, type_fig, filt, all_types, dist_month, cdist, elev, td


## 2. Update on Filter Change ##
@app.callback(
    Output('total-distance-by-month', 'figure'),
    Output('cumulative-distance', 'figure'),
    Output('total-elevation-by-month', 'figure'),
    Output('stats-table', 'data'),
    [Input('activity-filter', 'value'), Input('upload-data', 'contents')]
)


def update_activity_graph(selected_activity_types, contents):
    quick_info, upload = parse_contents(contents)
    if contents is None:
        return "Upload an 'activities.csv' file to see analysis results."
    
    upload_filt = upload[upload['Activity Type'].isin(selected_activity_types)].copy()
    
    df, df_2022, activity_types, grp_df_elev, grp_df_dist, table_dat, td_og = startup_procedure(upload_filt)
    
    dist_month = px.bar(grp_df_dist, x='month', y='distance', title='Total Elevation Gain by Month',
            labels={'month': 'Month', 'total_elevation_gain': 'Total Elevation Gain (meters)'},
            color='type'
            )

    # update the cumulative distance chart
    cdist = {
        'data': [
            {'x': df['start_date_local'], 'y': df['cumulative_distance'], 'type': 'scatter', 'mode': 'lines', 'name': '2023'},
            {'x': df_2022['start_date_local_comp'], 'y': df_2022['cumulative_distance'], 'type': 'scatter', 'mode': 'lines', 'name': '2022'},
        ],
        'layout': {
            'title': 'Cumulative Distance Over Time (2023 vs. 2022)',
            'xaxis': {'title': 'Date'},
            'yaxis': {'title': 'Cumulative Distance (miles)'}
        }
    }
    
    # update elevation chart
    elev = px.bar(grp_df_elev, x='month', y='total_elevation_gain', title='Total Elevation Gain by Month',
            labels={'month': 'Month', 'total_elevation_gain': 'Total Elevation Gain (meters)'},
            color_discrete_sequence=['#FFA500'],
            )
    
    # update stats table
    td = table_dat
    
    return dist_month, cdist, elev, td


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)






