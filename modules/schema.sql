DROP TABLE IF EXISTS forecast;

CREATE TABLE forecast (
    rec_id SERIAL PRIMARY KEY,
    rec_type text,
    city text NOT NULL,
    country text NOT NULL,
    city_population int,
    coord json NOT NULL,
    dt text NOT NULL,
    tz text NOT NULL,
    sunrise text NOT NULL,
    sunset text NOT NULL,
    weather text NOT NULL,
    temp json NOT NULL,
    cloudiness real ,
    wind json NOT NULL,
    visibility int NOT NULL,
    rain_volume_3h real,
    snow_volume_3h real
);

DROP TABLE IF EXISTS metrics;
CREATE TABLE metrics(
    mid SERIAL PRIMARY KEY,
    duration text NOT NULL,
    real_temp_mean real NOT NULL,
    feels_like_mean real NOT NULL,
    min_temp_mean real NOT NULL,
    max_temp_mean real NOT NULL,
    pressure_mean real NOT NULL,
    humidity_mean real NOT NULL,
    wind_degrees_mean real NOT NULL,
    wind_gust_mean real NOT NULL,
    wind_speed_mean real NOT NULL

);