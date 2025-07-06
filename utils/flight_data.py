import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

def fetch_flight_data():
    url = "http://api.aviationstack.com/v1/flights"
    params = {
        'access_key': API_KEY,
        'limit': 100
    }
    response = requests.get(url, params=params)
    return response.json()

def process_data(flight_json):
    data = []
    for flight in flight_json.get('data', []):
        data.append({
            'airline': flight['airline']['name'],
            'departure': flight['departure']['airport'],
            'arrival': flight['arrival']['airport'],
            'date': flight['departure']['estimated']
        })

    df = pd.DataFrame(data)

    # Convert to datetime and drop rows with missing/invalid dates
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df.dropna(subset=['date'], inplace=True)

    # Log a few rows for debugging
    print("✅ Valid flights with dates:")
    print(df[['departure', 'arrival', 'date']].head(10))

    return df


def fetch_and_process_flights(from_filter=None, to_filter=None):
    raw = fetch_flight_data()
    df = process_data(raw)

    if from_filter:
        df = df[df['departure'].str.contains(from_filter, case=False, na=False)]
    if to_filter:
        df = df[df['arrival'].str.contains(to_filter, case=False, na=False)]

    if df.empty:
        print("⚠️ No data found after filtering.")
        return df, [], []

    # Log how many flights per date (for trend chart)
    print("📊 Flights per day:")
    print(df['date'].dt.date.value_counts().sort_index())

    route_data = (
        df.groupby(['departure', 'arrival'])
        .size().reset_index(name='count')
        .to_dict(orient='records')
    )

    trend_data = (
        df.groupby(df['date'].dt.date)
        .size().reset_index(name='count')
        .rename(columns={'date': 'date'})
        .to_dict(orient='records')
    )

    return df, route_data, trend_data

