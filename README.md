# Weahter API

## Stack
| Functionality  | Tool  |
|---|---|
| Backend  | Python Flask |
|  Database | PostgreSQL (dockerized)  |

## Setting up
- Download Code
```shell
$ git clone https://github.com/radistoubalidis/weatherApp.git
```
- Install Dependencies (from a python venv)
```shell
$ pip install flask pandas psycopg2 requests flask_cors
```
- Setup Dockerized PostgresSQL
  - If docker is not install on you machine follow [this guide](https://docs.docker.com/get-docker/)
  - From you terminal:
  ```shell
  $ cd weatherApp
  $ docker-compose up --build -d
- Initialize Database
    ```shell
    $ docker cp modules/schema.sql weatherapp_database_1:/
    $ docker exec -it weatherapp_database_1 psql -U postgres -f schema.sql
- Setup Flask development environment
    - In linux machines (for windows replace `expose` with `set`):
    ```shell
    $ expose FLASK_APP=server.py
    $ expose FLASK_ENV=development
    $ expose FLASK_DEBUG=True
    $ flask run
    ```

# API Endpoints
The app fetches data from the [openWeather API](https://openweathermap.org/api)

## 5-day Weather Forecast Prediction `/prediction`
- Fetches the 5-day forecast from openWeather (based on coordinates from the form-data)
- Returns a json opbject with the weather forecast record for a specific timestamp (date and time) from the 5-day forecast

#### URL Format:    
```
localhost:5000/prediction?date={date}&time={time}
```
**Params Example**

We want to fetch forecast for `2022-10-04 18:00:00` the final URL would be:
- `http://localhost:5000/prediction?date=20221004&?time=180000`

<sub> Constraint: {time} param should be in the future</sub>

#### Example response format
```json
{
        "city": "Thessaloniki",
    "cloudiness": 18.0,
    "coordinates": {
        "lat": 40.63,
        "lon": 22.94
    },
    "country": "GR",
    "date": "2022-10-04 18:00:00",
    "population": null,
    "sunrise": "2022-10-03 04:26:19",
    "sunset": "2022-10-03 16:08:10",
    "temp": {
        "atm_pressure": 1021,
        "feels_like": 289.83,
        "feels_like_Celcius": 16.68,
        "feels_like_Farenheit": 62.02,
        "humidity": 38,
        "real_temp": 291,
        "real_temp_Celcius": 17.85,
        "real_temp_Farenheit": 64.13,
        "temp_max": 291,
        "temp_max_Celcius": 17.85,
        "temp_max_Farenheit": 64.13,
        "temp_min": 291,
        "temp_min_Celcius": 17.85,
        "temp_min_Farenheit": 64.13
    },
    "timezone": "03:00",
    "type": "prediction",
    "visibility": 10000,
    "weather": "few clouds",
    "wind": {
        "deg": 5,
        "gust": 9.61,
        "speed": 5.15
    }
}
```


## Today's weather forecast `/forecast`
Returns a json object with today's weather forecast:
#### URL Format:
```
localhost:5000/forecast?lat={lat}&lon={lon}
```
**Params Example**
We want to fetch data with coors: `lat=40.63 ,lon=22.94`, the final URL would be:
- `http://localhost:5000/forecast?lat=40.63&lon=22.94`
  
#### Example response format
```json
{
    "data": {
        "city": "Thessaloniki",
        "cloudiness": 20,
        "coordinates": {
            "lat": 40.63,
            "lon": 22.94
        },
        "country": "GR",
        "date": "2022-10-04 14:14:41",
        "population": null,
        "sunrise": "2022-10-04 04:27:19",
        "sunset": "2022-10-04 16:06:31",
        "temp": {
            "atm_pressure": 1020,
            "feels_like": 294.97,
            "feels_like_Celcius": 21.82,
            "feels_like_Farenheit": 71.28,
            "humidity": 37,
            "real_temp": 295.69,
            "real_temp_Celcius": 22.54,
            "real_temp_Farenheit": 72.57,
            "temp_max": 297.36,
            "temp_max_Celcius": 24.21,
            "temp_max_Farenheit": 75.58,
            "temp_min": 293.84,
            "temp_min_Celcius": 20.69,
            "temp_min_Farenheit": 69.24
        },
        "timezone": "UTC +03:00",
        "type": "current",
        "visibility": 10000,
        "weather": "few clouds",
        "wind": {
            "deg": 320,
            "speed": 6.17
        }
    },
    "msg": "Fetched and stored todays weather forecast."
}
```

## Metrics `/metrics`
From the records regarding the 5-day forecast, the mean values for
temperature, wind, atmospheric pressure and humidity metrics

#### URL Format:

- `http://localhost:5000/metrics`


#### Example response format
```json
{
    "duration": "For the next 4 days and  21:00:00 hours",
    "feels_like_mean": 291.45,
    "humidity_mean": 45.39,
    "max_temp_mean": 292.29,
    "min_temp_mean": 292.18,
    "pressure_mean": 1022.98,
    "real_temp_mean": 292.29,
    "wind_degrees_mean": 233.8,
    "wind_gust_mean": 2.27,
    "wind_speed_mean": 1.8
}
```