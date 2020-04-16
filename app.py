from flask import Flask, render_template
import requests as rq
import pandas
import json
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/Details/<country>')
def detail_data(country):
    covid_data_url = "https://pomber.github.io/covid19/timeseries.json"
    res_value = rq.get(covid_data_url, verify=False)
    data_res = res_value.json()
    if country in data_res:
        data_df = pandas.DataFrame.from_dict(data_res[country])
        data_df['date1'] = pandas.to_datetime(data_df['date'])
        data_df = data_df.sort_values(by='date1', ascending=False)
        json_data = data_df.to_json(orient='records')
        json_object = json.loads(json_data)
        return render_template('Index.html', len=len(json_object), items=json_object)
    else:
        return "Countries you can search for " + get_all_countries()


@app.route('/Graph/<country>')
def graph_data(country):
    covid_data_url = "https://pomber.github.io/covid19/timeseries.json"
    res_value = rq.get(covid_data_url, verify=False)
    data_res = res_value.json()
    if country in data_res:
        data_df = pandas.DataFrame.from_dict(data_res[country])
        confirmed_df = data_df['confirmed']
        data_df['Previous_Day_Diff'] = confirmed_df.diff()
        data_df['Previous_Day_Diff'] = data_df['Previous_Day_Diff'].fillna(0)
        label_values= data_df['date'].tolist()
        confirmed = data_df['Previous_Day_Diff'].tolist()
        labels = []
        labels.append('January')
        labels.append('February')
        labels.append('March')
        labels.append('April')
        labels.append('May')
        labels.append('June')
        labels.append('July')
        labels.append('August')
        values = [10, 9, 8, 7, 6, 4, 7, 8]
        return render_template('Graph.html', values=confirmed, labels=label_values)
    else:
        return "Countries you can search for " + get_all_countries()


def get_all_countries():
    covid_data_url = "https://pomber.github.io/covid19/timeseries.json"
    res_value = rq.get(covid_data_url, verify=False)
    data_res = res_value.json()
    lst_country = []
    for single_key in data_res.keys():
        lst_country.append(single_key)
    return ",".join(lst_country)


if __name__ == '__main__':
    app.run()
