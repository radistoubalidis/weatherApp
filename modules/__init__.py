import psycopg2
import requests
from datetime import datetime
import json
import pandas as pd




"""
This class can be assumed as a Model
as well as a Controller for the Database entity `forecast`.
"""
class WeatherForecast:
    def __init__(self,dt,sunrise, sunset, weather, temp, cloudiness,
    wind, visibility, tz=None, rec_type=None, city=None, country=None,coord=None,
    city_population=None, rain_vol_3h=None, snow_vol_3h=None) -> None:
        self.db = Database()
        self.rec_type = rec_type
        self.city = city
        self.coord = coord
        self.country = country
        self.dt = dt
        self.tz = tz
        self.sunrise = sunrise
        self.sunset = sunset
        self.weather = weather
        self.temp = temp
        self.cloudiness = cloudiness
        self.wind = wind
        self.visibility = visibility
        self.city_population = city_population
        self.rain_vol_3h = rain_vol_3h
        self.snow_vol_3h = snow_vol_3h
        
# The _toDict() methods prepare queries' outputs
# into json formats for endpoint outputs
    def toDict(self):
        # Add Celcious and Farehneit
        tmp = DataOperations.add_C_F(self.temp)
        if self.rec_type == 'Current':
            output= {
                "type":self.rec_type,
                'city':self.city,
                'country':self.country,
                'date':DataOperations.convertDates(self.dt),
                'timezone':DataOperations.convertDates(self.tz),
                'coordinates':self.coord,
                'sunrise':DataOperations.convertDates(self.sunrise),
                'sunset':DataOperations.convertDates(self.sunset),
                'weather':self.weather,
                'temp':tmp,
                'cloudiness':self.cloudiness,
                'wind':self.wind,
                'visibility':self.visibility,
            }
        else:
            output= {
                "type":self.rec_type,
                'city':self.city,
                'population':self.city_population,
                'country':self.country,
                'date':self.dt,
                'timezone':self.tz,
                'coordinates':self.coord,
                'sunrise':self.sunrise,
                'sunset':self.sunset,
                'weather':self.weather,
                'temp':self.temp,
                'cloudiness':self.cloudiness,
                'wind':self.wind,
                'visibility':self.visibility,
            }
            if self.rain_vol_3h is not None:
                output['rain_volume_3h'] = self.rain_vol_3h
            if self.snow_vol_3h is not None:
                output['snow_volume_3h'] = self.snow_vol_3h
        return output

# Organizes the data data to calculate mean values
    def metricsDict(self):
        # Add Celcious and Farehneit
        tmp = DataOperations.add_C_F(self.temp)
        output =  {
            'dt':self.dt,
            'sunrise':self.sunrise,
            'sunset':self.sunset,
            'weather':self.weather,
            'temp':tmp,
            'cloudiness':self.cloudiness,
            'wind':self.wind,
            'visibility':self.visibility,
            'rain_volume_3h':self.rain_vol_3h,
            'snow_volume_3h':self.snow_vol_3h
        }
        if self.rain_vol_3h is not None:
                output['rain_volume_3h'] = self.rain_vol_3h
        if self.snow_vol_3h is not None:
            output['snow_volume_3h'] = self.snow_vol_3h
        return output

# Inserts today's forecast to db
    def add_current(self):
        try:    
            conn = self.db.connect()
            cursor = conn.cursor()
            query = """INSERT INTO forecast(rec_type,city,country,coord,
                        dt,tz,sunrise,sunset,weather,temp,cloudiness,wind,visibility) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        RETURNING rec_id;"""

            cursor.execute(query,(
                                self.rec_type,self.city,self.country,json.dumps(self.coord),
                                self.dt,self.tz,self.sunrise,self.sunset,self.weather,json.dumps(self.temp),
                                self.cloudiness,json.dumps(self.wind),self.visibility
                            ))

            rec_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            return rec_id
        except (Exception, psycopg2.Error) as error:
            print("Error while storing data to PostgreSQL", error)

# Insert one weather record from the 5-day forecast
    def add_prediction(self):
        try:    
            conn = self.db.connect()
            cursor = conn.cursor()
            query = """INSERT INTO forecast(rec_type,city,country,coord,
                        dt,tz,sunrise,sunset,weather,temp,cloudiness,wind,visibility,
                        rain_volume_3h,snow_volume_3h) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        RETURNING rec_id;"""

            cursor.execute(query,(
                                self.rec_type,self.city,self.country,json.dumps(self.coord),
                                self.dt,self.tz,self.sunrise,self.sunset,self.weather,json.dumps(self.temp),
                                self.cloudiness,json.dumps(self.wind),
                                self.visibility,self.rain_vol_3h,self.snow_vol_3h
                            ))

            rec_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            return rec_id
        except (Exception, psycopg2.Error) as error:
            print("Error while storing data to PostgreSQL", error)

# Fetches a weather record from the 5-day forecast
    @classmethod
    def getPredByDate(self,date):
        try:
            db = Database()
            conn = db.connect()
            cursor = conn.cursor()
            query = f"""SELECT *
                    FROM forecast
                    WHERE forecast.dt IN('{date}')"""
            cursor.execute(query)
            res = cursor.fetchall()[0]
            conn.commit()
            cursor.close()
            pretty = DataOperations.prepare_output_by_date(res)
            return pretty
        except(Exception, psycopg2.Error) as error:
            print('Something went wrong while fetching data',error)

# Fetches appropriate columns from all 5-day forecast records
    @classmethod
    def fetchMetrics(self):
        try:
            db = Database()
            conn = db.connect()
            cursor = conn.cursor()
            query = f"""SELECT dt,sunrise,sunset,weather,temp,cloudiness,wind,visibility,rain_volume_3h,snow_volume_3h
                    FROM forecast
                    WHERE rec_type='prediction'
                    ORDER BY dt"""
            cursor.execute(query)
            res = cursor.fetchall()
            pretty = []
            for row in res:
                pretty.append(DataOperations.prepareMean(row))
            return pd.DataFrame(pretty)
        except(Exception, psycopg2.Error) as error:
            print('Something went wrong while fetching data',error)


class Metrics:
    def __init__(self,duration,real_temp_mean,feels_like_mean, min_temp_mean,
    max_temp_mean, pressure_mean, humidity_mean, wind_degrees_mean,
    wind_gust_mean, wind_speed_mean) -> None:
        self.duration = duration
        self.real_temp_mean = real_temp_mean
        self.feels_like_mean = feels_like_mean
        self.min_temp_mean = min_temp_mean
        self.max_temp_mean = max_temp_mean
        self.pressure_mean = pressure_mean
        self.humidity_mean = humidity_mean
        self.wind_degrees_mean = wind_degrees_mean
        self.wind_gust_mean = wind_gust_mean
        self.wind_speed_mean = wind_speed_mean
    
# prepares 
    def toDict(self):
        real_temp_imperial, real_temp_celcius = DataOperations.kelvin2celsius2Imperial(self.real_temp_mean)
        feels_like_imperial, feels_like_celcius = DataOperations.kelvin2celsius2Imperial(self.feels_like_mean)
        min_temp_imperial, min_temp_celcius = DataOperations.kelvin2celsius2Imperial(self.min_temp_mean)
        max_temp_imperial, max_temp_celcius = DataOperations.kelvin2celsius2Imperial(self.max_temp_mean)
        output = {
            'duration':f"{self.duration}",
            'real_temp_mean':round(self.real_temp_mean,2),
            'real_temp_mean_Celcius':round(real_temp_celcius,2),
            'real_temp_mean_Farehneit':round(real_temp_imperial,2),
            'feels_like_mean':round(self.feels_like_mean,2),
            'feels_like_mean_Celcius':round(feels_like_celcius,2),
            'feels_like_mean_Farehneit':round(feels_like_imperial,2),
            'min_temp_mean':round(self.min_temp_mean,2),
            'min_temp_mean_Celcius':round(min_temp_celcius,2),
            'min_temp_mean_Farehneit':round(min_temp_imperial,2),
            'max_temp_mean':round(self.max_temp_mean,2),
            'max_temp_mean_Celcius':round(max_temp_celcius,2),
            'max_temp_mean_Farehneit':round(max_temp_imperial,2),
            'pressure_mean':round(self.pressure_mean,2),
            'humidity_mean':round(self.humidity_mean,2),
            'wind_degrees_mean':round(self.wind_degrees_mean,2),
            'wind_gust_mean':round(self.wind_gust_mean,2),
            'wind_speed_mean':round(self.wind_speed_mean,2)
        }
        return output

# Inserts the calculated mean values to the metrics entity
    def addMetrics(self):
        try:
            db = Database()
            conn = db.connect()
            cursor = conn.cursor()
            query = """INSERT INTO metrics(duration,real_temp_mean,feels_like_mean,min_temp_mean,
            max_temp_mean,pressure_mean,humidity_mean,wind_degrees_mean,wind_gust_mean,wind_speed_mean) 
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING mid;
            """
            cursor.execute(query,(self.duration,
            self.real_temp_mean,self.feels_like_mean,self.min_temp_mean,
            self.max_temp_mean,self.pressure_mean,self.humidity_mean,
            self.wind_degrees_mean, self.wind_gust_mean, self.wind_speed_mean
            ))
            mid = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            return mid
        except(Exception, psycopg2.Error) as error:
            print('Something went wrong while storing data',error)



"""
Database serves as an interface to connect to Postgres docker container
"""
class Database:
    def __init__(self):
        self.link = 'postgres://postgres:postgres@localhost:6543/postgres'

    def connect(self):
        conn = psycopg2.connect(self.link)
        return conn


"""
ExternalData serves as an interface for
fetching data from openWeatherAPI
"""
class ExternalData:
    def __init__(self):
        self.EXTERNAL_SOURCE = 'https://api.openweathermap.org/data/2.5'
        self.KEY = '3f9fb726b84a13e7cf9355378e1f08c9'

    def getForecast(self,lon,lat):
        params = f'weather?lat={lat}&lon={lon}&appid={self.KEY}'
        url = f'{self.EXTERNAL_SOURCE}/{params}'
        res = requests.get(url)
        data = res.json()
        prepared = self.prepareWeather(data)
        return prepared

    def getPrediction(self,lon,lat):
        params = f'forecast?lat={lat}&lon={lon}&appid={self.KEY}'
        url = f"{self.EXTERNAL_SOURCE}/{params}"
        res = requests.get(url)
        data = res.json()
        prepared = self.preparePrediction(data)
        return prepared

    def prepareWeather(self,data):
        tzone=f"UTC +0{data['timezone'] // 3600}:00" if data['timezone']>0 else f"UTC -0{data['timezone'] // 3600}:00"
        tmp = {
                'real_temp':data['main']['temp'],
                'feels_like':data['main']['feels_like'],
                'temp_min':data['main']['temp_min'],
                'temp_max':data['main']['temp_max'],
                'atm_pressure':data['main']['pressure'],
                'humidity':data['main']['humidity'],
            }
        wf = WeatherForecast(
            rec_type='current',
            city=data['name'],
            country=data['sys']['country'],
            coord=data['coord'],
            dt=str(datetime.utcfromtimestamp(data['dt']).strftime('%Y-%m-%d %H:%M:%S')),
            tz=tzone,
            sunrise=str(datetime.utcfromtimestamp(data['sys']['sunrise']).strftime('%Y-%m-%d %H:%M:%S')),
            sunset=str(datetime.utcfromtimestamp(data['sys']['sunset']).strftime('%Y-%m-%d %H:%M:%S')),
            weather=data['weather'][0]['description'],
            temp=tmp,
            cloudiness=data['clouds']['all'],
            wind=data['wind'],
            visibility=data['visibility']
        )
        # Check if "Ground level pressure key exists"
        if 'grnd_level' in data['main']:
            wf.temp['grnd_atm_pressure'] = data['main']['grnd_level']
        return wf
    
    def preparePrediction(self,data):
        records_list=data['list']
        dump=[]
        for rec in records_list:
            tmp = {
                'real_temp':rec['main']['temp'],
                'feels_like':rec['main']['feels_like'],
                'temp_min':rec['main']['temp_min'],
                'temp_max':rec['main']['temp_max'],
                'atm_pressure':rec['main']['pressure'],
                'humidity':rec['main']['humidity'],
            }
            wf = WeatherForecast(
                rec_type='prediction',
                city=data['city']['name'],
                city_population=data['city']['population'],
                country=data['city']['country'],
                coord=data['city']['coord'],
                dt=str(datetime.utcfromtimestamp(rec['dt']).strftime('%Y-%m-%d %H:%M:%S')),
                tz=f"0{data['city']['timezone'] // 3600}:00",
                sunrise=str(datetime.utcfromtimestamp(data['city']['sunrise']).strftime('%Y-%m-%d %H:%M:%S')),
                sunset=str(datetime.utcfromtimestamp(data['city']['sunset']).strftime('%Y-%m-%d %H:%M:%S')),
                weather=rec['weather'][0]['description'],
                temp=tmp,
                cloudiness=rec['clouds']['all'],
                wind=rec['wind'],
                visibility=rec['visibility'],
                rain_vol_3h=rec['rain']['3h'] if 'rain' in rec.keys() else None,
                snow_vol_3h=rec['snow']['3h'] if 'snow' in rec.keys() else None
            )
            dump.append(wf)
        return dump
              
"""
DataOperations serves as an interface to apply some modifications
or changes to a WeatherForecast object's attributes
"""
class DataOperations:
    def kelvin2celsius2Imperial(kelvin):
        imperial = kelvin * 1.8 - 459.67
        celsius = kelvin - 273.15
        return imperial, celsius

# Converts a date from a seconds timestamp to YYYY-mm-dd hh:mm:ss format
    def convertDates(date):
        return str(datetime.utcfromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S'))
# Prepares the response from getByDate for the endpoint
    def prepare_output_by_date(response):
        wf = WeatherForecast(
            rec_type=response[1],
            city=response[2],
            country=response[3],
            city_population=response[4],
            coord=response[5],
            dt=response[6],
            tz=response[7],
            sunrise=response[8],
            sunset=response[9],
            weather=response[10],
            temp=response[11],
            cloudiness=response[12],
            wind=response[13],
            visibility=response[14],
            rain_vol_3h=response[15],
            snow_vol_3h=response[16]
        )
        return wf.toDict()

# Prepares the response from fetchMetrics for the /metrics endpoint 
    def prepareMean(response):
        wf = WeatherForecast(
            dt=response[0],
            sunrise=response[1],
            sunset=response[2],
            weather=response[3],
            temp=response[4],
            cloudiness=response[5],
            wind=response[6],
            visibility=response[7],
            rain_vol_3h=response[8],
            snow_vol_3h=response[9]
        )
        return wf.metricsDict()

# Calculates mean values for temperature,windf,atm pressure and humidity metrics for all 5-day forecast records
    def prepareMetrics(metrics_df):
        # Calculate date duration
        dt_max = metrics_df['dt'].max()
        dt_min = metrics_df['dt'].min()
        dt_max = datetime.strptime(dt_max,'%Y-%m-%d %H:%M:%S')
        dt_min = datetime.strptime(dt_min,'%Y-%m-%d %H:%M:%S')
        duration = dt_max - dt_min
        # Calculate temp metrics
        temp = metrics_df['temp']
        temp.reset_index()
        temp = temp.tolist()
        temp = pd.DataFrame(temp)
        real_temp_mean = temp['real_temp'].mean()
        feels_like_mean = temp['feels_like'].mean()
        min_temp_mean = temp['temp_min'].mean()
        max_temp_mean = temp['temp_max'].mean()
        pressure_mean = temp['atm_pressure'].mean()
        humidity_mean = temp['humidity'].mean()
        # Calculate wind metrics
        wind = metrics_df['wind']
        wind.reset_index()
        wind = wind.tolist()
        wind = pd.DataFrame(wind)
        wind_degrees_mean = wind['deg'].mean()
        wind_gust_mean = wind['gust'].mean()
        wind_speed_mean = wind['speed'].mean()
        metrics_obj = Metrics(
            duration=duration,
            real_temp_mean=real_temp_mean,
            feels_like_mean=feels_like_mean,
            min_temp_mean=min_temp_mean,
            max_temp_mean=max_temp_mean,
            pressure_mean=pressure_mean,
            humidity_mean=humidity_mean,
            wind_degrees_mean=wind_degrees_mean,
            wind_gust_mean=wind_gust_mean,
            wind_speed_mean=wind_speed_mean
        )
        return metrics_obj

# Add celcius and Farehneit values to temp dictionary
    def add_C_F(temp):
        imperial ,celcius = DataOperations.kelvin2celsius2Imperial(temp['feels_like'])
        temp['feels_like_Celcius'] = round(celcius,2)
        temp['feels_like_Farenheit'] = round(imperial,2)

        imperial ,celcius = DataOperations.kelvin2celsius2Imperial(temp['real_temp'])
        temp['real_temp_Celcius'] = round(celcius,2)
        temp['real_temp_Farenheit'] = round(imperial,2)

        imperial ,celcius = DataOperations.kelvin2celsius2Imperial(temp['temp_max'])
        temp['temp_max_Celcius'] = round(celcius,2)
        temp['temp_max_Farenheit'] = round(imperial,2)

        imperial ,celcius = DataOperations.kelvin2celsius2Imperial(temp['temp_min'])
        temp['temp_min_Celcius'] = round(celcius,2)
        temp['temp_min_Farenheit'] = round(imperial,2)
        return temp
