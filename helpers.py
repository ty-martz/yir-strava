import pandas as pd
import base64
import io
from file_transformer import transform_strava_upload

## Variables ##

high_five_emoji = '\U0001F64C'
clap_emoji = "\U0001F44F"
run_emoji = "\U0001F3C3"
singlet_emoji = "\U0001F3BD"
shoe_emoji = "\U0001F45F"
watch_emoji = "\U0000231A"
clock_emoji = "\U000023F1"
bolt_emoji = "\U000026A1"
footprint_emoji = "\U0001F463"
calendar_emoji = "\U0001F4C5"

def startup_procedure(uploaded=None):
    '''
    Creates the startup procedure given the starting input data
    The `uploaded` variable is used in callbacks to use a new uploaded file instead of the starting data
    '''
    
    # Load and transform data for 2 years and get the activity types
    df, df_2022 = transform_strava_upload(uploaded=uploaded)
    activity_types = df['type'].unique()

    #elevation and distance grouped data by month
    grp_df_elev = df.groupby('month')['total_elevation_gain'].sum().reset_index()
    grp_df_dist = df.groupby(['month', 'type'])['distance'].sum().reset_index()

    table_data = [
        {"metric": f'Days Active {calendar_emoji}', "2023": f"{len(df['start_date_local'].unique())} days", "2022": f"{len(df_2022['start_date_local'].unique())} days"},
        {"metric": f'Average Speed {shoe_emoji}', "2023": f"{df['average_speed_mph'].mean():,.2f} mph", "2022": f"{df_2022['average_speed_mph'].mean():,.2f} mph"},
        {"metric": f'Max Speed {bolt_emoji}', "2023": f"{df['max_speed_mph'].mean():,.2f} mph", "2022": f"{df_2022['max_speed_mph'].mean():,.2f} mph"},
        {"metric": f'Longest Activity Time {watch_emoji}', "2023": f"{df['elapsed_time'].max() / 3600:,.2f} hours", "2022": f"{df_2022['elapsed_time'].max() / 3600:,.2f} hours"},
        {"metric": f'Longest Activity Distance {run_emoji}', "2023": f"{df['distance'].max() * 0.000621371:,.2f} miles", "2022": f"{df_2022['distance'].max() * 0.000621371:,.2f} miles"},
        {"metric": f'Total Time Spent {clock_emoji}', "2023": f"{df['elapsed_time'].sum() / 3600:,.2f} hours", "2022": f"{df_2022['elapsed_time'].sum() / 3600:,.2f} hours"},
        {"metric": f'Total Steps Taken {footprint_emoji}', "2023": f"{int(df['Total Steps'].sum())} steps", "2022": f"{int(df_2022['Total Steps'].sum())} steps"},
    ]
    td_copy = table_data.copy()
    
    return df, df_2022, activity_types, grp_df_elev, grp_df_dist, td_copy, table_data


def parse_contents(contents):
    # Assuming CSV format for simplicity
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    
    analysis_result = f"Analyzing {len(df)} activities"
    
    return analysis_result, df
