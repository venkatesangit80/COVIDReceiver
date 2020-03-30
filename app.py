from flask import Flask
import requests as rq
import pandas

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/Details/<country>')
def detail_data(country):
    covid_data_url = "https://pomber.github.io/covid19/timeseries.json"
    res_value = rq.get(covid_data_url, verify=False)
    data_res = res_value.json()
    data_df = pandas.DataFrame.from_dict(data_res[country])
    print(data_df.head(3))
    json_data = data_df.to_json(orient='records')
    return json_data


if __name__ == '__main__':
    app.run()
