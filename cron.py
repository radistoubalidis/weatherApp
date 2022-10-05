import requests
import json

def fetchData():
    response = requests.get(
        'http://localhost:5000/prediction',
        data={'lat':40.63,'lon':22.94},
        params={'date':20221005,'time':210000}
        )
    return response

def fetchMetrics():
    response = requests.get('http://localhost:5000/metrics')
    return response

if __name__ == '__main__':
    init_server = fetchData()
    if init_server is None:
        print('oops')
    else:
        response = fetchMetrics()
        with open('cron_response.json','w') as f:
            json.dump(response.json(),f)