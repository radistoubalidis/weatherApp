from flask import Flask,request,Response
from flask_cors import CORS
from modules import DataOperations, Database,WeatherForecast,ExternalData,Metrics
import json



app = Flask(__name__)
CORS(app)

def get_file(name):
    try:
        return open(name).read()
    except(IOError) as exc:
        return (str(exc))

# home endpoint: when its called it fetches the 5-day forecast from openWeather and stores is to postgres
# form-data : lat, lon
@app.route('/',methods=['GET'])
def index():
    return "Home"

# endpoint for today's weather forecast
@app.route('/forecast',methods=['GET'])
def forecast():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    rec_id, wf = prepareRequests.prepareForecastRequest(lat,lon)
    if rec_id is None:
        return 'Something went wrong while fetching data from openWeather and storing to PostgreSQL'
    else:
        return {
            'msg':f'Fetched and stored todays weather forecast.',
            'data':wf.toDict()
            }

# endpoint for fetching the 5-day forecast from open weather
# and returning one record from it based on params
# params : 
# - int ,date in format : yyyymmdd
# - int ,time in format : hhmmss
# form-data:
# - int lat,lon
@app.route('/prediction',methods=['GET'])
def predictionDate():
    lat = request.form.get('lat')
    lon = request.form.get('lon')
    content = prepareRequests.preparePredictionRequest(lat,lon)
    if content is None:
        return 'Somthing went wrong while fetch 5-day forecast from openWeather'
    else:
        date = str(request.args.get('date'))
        time = str(request.args.get('time'))
        date = date[:4] + '-' + date[4:6] + '-' + date[6:]
        time = time[:2] + ':' + time[2:4] + ':' + time[4:]
        complete = date + ' ' + time
        res = WeatherForecast.getPredByDate(complete)
        print(res)
        return res

# endpoint for fetching the metrics entity from the database
@app.route('/metrics',methods=['GET','POST'])
def metrics():
    # Retrieve required data from db to calculate metrics
    metrics_df = WeatherForecast.fetchMetrics()
    # Calculate metrics and return them as a dataframe
    metrics_obj = DataOperations.prepareMetrics(metrics_df=metrics_df)
    # insert calculated metrics to db
    mid = metrics_obj.addMetrics()
    if mid is None:
        return 'Something went wrong while storing metrics data to Database'
    else:
        output = metrics_obj.toDict()
        print(output)
        return output

@app.route('/shutdown',methods=['GET'])
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


# prepareRequests serves as an interface
# for creating the requests to fetch data from openWeather
class prepareRequests:
    def prepareForecastRequest(lat,lon):
        ed = ExternalData()
        wf = ed.getForecast(lat=lat, lon=lon)
        res = wf.add_current()
        return res,wf

    def preparePredictionRequest(lat,lon):
        ed = ExternalData()
        records_list = ed.getPrediction(lat=lat,lon=lon)
        rec_ids = []
        for wf in records_list:
            rec_id = wf.add_prediction()
            if rec_id is None:
                msg = 'Something went wrong while fetching data from openWeather and storing in PostgreSQL'
                pass
            else:
                rec_ids.append(rec_id)
        if len(rec_ids) == len(records_list):
            msg = "Stored Prediction Weather Records."
        return msg
            




if (__name__ == '__main__'):
    from waitress import serve
    serve(app, host="127.0.0.1", port=5000)
