import openmeteo_requests
import db
from datetime import date,timedelta, datetime

import requests_cache
import pandas as pd
from retry_requests import retry

con = db.pool.connect()

def PastSitesData(long,lat,start_date,end_date):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": long,
        "start_date": "%s-%s-%s"%(start_date.year,str(start_date.month).zfill(2),str(start_date.day).zfill(2)),
        "end_date": "%s-%s-%s"%(end_date.year,str(end_date.month).zfill(2),str(end_date.day).zfill(2)),
        "daily": ["temperature_2m_mean","rain_sum"]
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_temperature_2m_mean = daily.Variables(0).ValuesAsNumpy()
    daily_rain_sum = daily.Variables(1).ValuesAsNumpy()

    daily_data = {"Month": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}
    daily_data["Temperature"] = daily_temperature_2m_mean
    daily_data["Rain"] = daily_rain_sum

    daily_dataframe = pd.DataFrame(data = daily_data)
    return(daily_dataframe)

def UploadData():
    ListSite = con.execute("""SELECT DISTINCT Sites.Id_Site FROM Sites 
                            INNER JOIN DailySales ON DailySales.Id_Site = Sites.Id_Site
                            WHERE Platform <> 'Dead' AND Longitude is NOT NULL 
                            AND Latitude is NOT NULL """).fetchall()
    Site = [i[0] for i in ListSite]
    print(Site)
    wait = input("go")
    for id in (Site):
        Coordonnate = con.execute("SELECT Longitude,Latitude FROM Sites WHERE Id_Site = %s",id).fetchall()
        start_date = date(2024,1,1)
        end_date = date(2024,5,15)
        Weather_data = PastSitesData(Coordonnate[0][0],Coordonnate[0][1],start_date,end_date)
        print(id)
        for index, row in Weather_data.iterrows():
            day = row['Month'].date()
            temperature = row['Temperature'] 
            rain = row['Rain']
            print(day,temperature,rain)
            # Exécutez la requête SQL pour mettre à jour la table
            query = "UPDATE DailySales SET Temperature=%s,Rain =%s WHERE Day=%s AND Id_Site = %s"
            values = (temperature,rain, day,id)
            con.execute(query, values)