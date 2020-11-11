import requests
import json
import pandas as pd
from datetime import datetime
from weasyprint import HTML

from database import init_db, db_session, engine
from models import Run


# request API
def request_api():
    try:
        return requests.get('https://corona.lmao.ninja/v3/covid-19/countries')
    except ConnectionError:
        print('Check network connection and try one more time')
        exit()


def json_text_to_dict(json_text: str):
    return json.loads(json_text)


# create dataframe
def df_from_dict(dict_data):
    return pd.DataFrame.from_dict(dict_data)


def add_run_to_db(status, json_data=None):
    current_run = Run(status, str(json_data))
    db_session.add(current_run)
    db_session.commit()


def get_all_from_db():
    return pd.read_sql_table('runs', engine)


def get_last_from_db():
    return pd.read_sql_query('SELECT * FROM runs ORDER BY id DESC LIMIT 1', engine)


def get_top_3_daily(df):

    df.sort_values(
        by=['todayCases'],
        ascending=False,
        inplace=True,
        ignore_index=True)

    cols = ['country', 'todayCases']
    df.index += 1
    return df[cols].head(3)


def save_html_report(df: pd.DataFrame):
    with open('report.html', 'w+') as f:
        f.write(df.to_html())
    return df.to_html()


def save_pdf_report(html):
    HTML('report.html').write_pdf('report.pdf')


def remove_milliseconds(date):
    milli_dot = date.rfind('.', 0)
    return date[0:milli_dot]

def count_days_from_last_run():
    today = datetime.now()
    last_run = get_last_from_db()
    last_run_date_str = remove_milliseconds(last_run['timestamp'][0])
    last_run_date = datetime.strptime(last_run_date_str, '%Y-%m-%d %H:%M:%S')
    diff = today - last_run_date
    return diff.days

def json_str_to_df(json_str):
    json_data = json_str
    dict_data = json_text_to_dict(json_data)
    return df_from_dict(dict_data)

def download_api_data(request):
    # data download
    df_data = json_str_to_df(request.text)
    return df_data


def get_top_3_over_week(current_json_data):

    last_run = get_last_from_db()
    json_str = last_run['data'][0]
    last_run_data = json_str_to_df(json_str)
    current_run_data = json_str_to_df(current_json_data)
    joined_data = current_run_data.join(last_run_data, rsuffix='_last')
    joined_data['percentage_increase'] = ((joined_data['cases']/joined_data['cases_last'])*100)-100

    joined_data.sort_values(
        by=['percentage_increase'],
        ascending=False,
        inplace=True,
        ignore_index=True)

    cols = ['country', 'cases', 'cases_last', 'percentage_increase']
    joined_data.index += 1
    return joined_data[cols].head(3)


def is_first_run(passed_days):
    if passed_days == 0:
        print("The report has been already generated today.")
        exit()


def choose_top_3_function(passed_days):
    passed_days = count_days_from_last_run()
    if passed_days > 7:
        return lambda json_str: get_top_3_over_week(json_str)
    return lambda json_str: get_top_3_daily(json_str)



def main():
    # database initialisation
    init_db()

    # passed days verification
    days_from_last_run = count_days_from_last_run()
    is_first_run(days_from_last_run)

    # get top 3 countries
    request = request_api()
    top_3_function = choose_top_3_function(days_from_last_run)
    top_3 = top_3_function(request.text)

    # generate pdf report
    html = save_html_report(top_3)
    save_pdf_report(html)

    # save run to database
    add_run_to_db('done', request.text)


if __name__ == '__main__':
    main()
