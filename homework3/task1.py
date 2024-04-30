import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import os.path

ltude = {'Moscow': (55.7522, 37.6156), 'London': (51.5085, -0.1257), 'Madrid': (40.4165, -3.7026)}


def load_temp_data(city: str, file: str):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": ltude[city][0],
        "longitude": ltude[city][1],
        "start_date": "2024-03-28",
        "end_date": "2024-04-28",
        "daily": "temperature_2m_mean"
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_temperature_2m_mean = daily.Variables(0).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left"
    )}
    daily_data["temperature_2m_mean"] = daily_temperature_2m_mean
    daily_data["city"] = city

    df = pd.DataFrame(data=daily_data)
    print(df)

    if not os.path.exists(file):
        df.to_csv(file)
    else:
        df.to_csv(file, mode='a', header=False)


cities = ['Moscow', 'London', 'Madrid']
file = 'temperature.csv'

for city in cities:
    load_temp_data(city, file)
