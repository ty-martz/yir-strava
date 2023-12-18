import pandas as pd
import json

def transform_csv_export(data, year=2023, uploaded=None):
    if uploaded is not None:
        data = uploaded
    data['start_date'] = pd.to_datetime(data['Activity Date'], format='%b %d, %Y, %I:%M:%S %p')
    df = data[data.start_date.dt.year == year].reset_index(drop=True).copy()
    
    df['start_date_local'] = pd.to_datetime(df['start_date'])
    df.sort_values('start_date_local', inplace=True)

    # Create a new column for month
    df['month'] = df['start_date_local'].dt.month
    df['start_date_local_comp'] = df['start_date_local'] + pd.offsets.DateOffset(years=1)

    # Calculate cumulative distance in miles
    df['cumulative_distance'] = (df['Distance.1'].astype(float) * 0.000621371).cumsum()
    df['average_speed_mph'] = df['Average Speed'] * 2.237
    df['max_speed_mph'] = df['Max Speed'] * 2.237

    # CSV SPECIFIC
    df['type'] = df['Activity Type']
    df['total_elevation_gain'] = df['Elevation Gain']
    df['elapsed_time'] = df['Elapsed Time']
    df['distance'] = df['Distance.1'].astype(float)

    # get HR zones
    df['zone1_time'] = df['Elapsed Time'] * ((df['Average Heart Rate'] >= 96) & (df['Average Heart Rate'] <= 115))
    df['zone2_time'] = df['Elapsed Time'] * ((df['Average Heart Rate'] > 115) & (df['Average Heart Rate'] <= 134))
    df['zone3_time'] = df['Elapsed Time'] * ((df['Average Heart Rate'] > 134) & (df['Average Heart Rate'] <= 154))
    df['zone4_time'] = df['Elapsed Time'] * ((df['Average Heart Rate'] > 154) & (df['Average Heart Rate'] <= 173))
    df['zone5_time'] = df['Elapsed Time'] * ((df['Average Heart Rate'] > 173) & (df['Average Heart Rate'] <= 200))
    
    return df


def transform_json_api(data, year=2023):
    data['start_date'] = pd.to_datetime(data['start_date'])
    df = data[data.start_date.dt.year == year].reset_index(drop=True).copy()

    # Convert 'start_date_local' to datetime and sort by date
    df['start_date_local'] = pd.to_datetime(df['start_date_local'])
    df.sort_values('start_date_local', inplace=True)

    # Create a new column for month
    df['month'] = df['start_date_local'].dt.month
    df['start_date_local_comp'] = df['start_date_local'] + pd.offsets.DateOffset(years=1)

    # Calculate cumulative distance in miles
    df['cumulative_distance'] = (df['distance'] * 0.000621371).cumsum()
    df['average_speed_mph'] = df['average_speed'] * 2.237
    df['max_speed_mph'] = df['max_speed'] * 2.237

    df['zone1_time'] = df['elapsed_time'] * ((df['average_heartrate'] >= 96) & (df['average_heartrate'] <= 115))
    df['zone2_time'] = df['elapsed_time'] * ((df['average_heartrate'] > 115) & (df['average_heartrate'] <= 134))
    df['zone3_time'] = df['elapsed_time'] * ((df['average_heartrate'] > 134) & (df['average_heartrate'] <= 154))
    df['zone4_time'] = df['elapsed_time'] * ((df['average_heartrate'] > 154) & (df['average_heartrate'] <= 173))
    df['zone5_time'] = df['elapsed_time'] * ((df['average_heartrate'] > 173) & (df['average_heartrate'] <= 200))
    
    return df


def transform_strava(file_loc, json_count, year1=2023, year2=2022, uploaded=None):
    
    raw = None
    if isinstance(uploaded, pd.DataFrame):
        df = transform_csv_export(raw, year1, uploaded)
        df_2022 = transform_csv_export(raw, year2, uploaded)
    elif file_loc[-4:] != '.csv':
        data_files = []
        for f in range(1,json_count+1):
            with open(f'{file_loc}/activities_{f}.json', 'r') as file:
                data = json.load(file)
                data_files.append(data)
                file.close()
        dfs = [pd.DataFrame(d) for d in data_files]
        raw = pd.concat(dfs)
        df = transform_json_api(data=raw, year=year1)
        df_2022 = transform_json_api(data=raw, year=year2)
        
    elif file_loc[-4:] == '.csv':
        raw = pd.read_csv(file_loc)
        df = transform_csv_export(raw, year1)
        df_2022 = transform_csv_export(raw, year2)
        
    else:
        assert raw != None, f'file_loc = {file_loc} variable must be csv file or a folder with json files where each is named "activities_n.json" where n is a number unique to that file starting from 1 and ending with json count variable'
        
    return df, df_2022
    

def transform_strava_upload(uploaded=None, year1=2023, year2=2022):
    
    raw = None
    if isinstance(uploaded, pd.DataFrame):
        df = transform_csv_export(raw, year1, uploaded)
        df_2022 = transform_csv_export(raw, year2, uploaded)
        
    else:
        assert raw != None, f'upload seems to have failed, try again'
        
    return df, df_2022