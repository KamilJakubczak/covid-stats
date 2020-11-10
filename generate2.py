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
        add_run_to_db(status='error')
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


def check_run():
    today = datetime.now()
    last_run = get_last_from_db()
    last_run_date_str = remove_milliseconds(last_run['timestamp'][0])
    last_run_date = datetime.strptime(last_run_date_str, '%Y-%m-%d %H:%M:%S')
    diff = today - last_run_date
    print(diff.days)
    print(last_run_date_str)
    pass


def main():
    # print(get_last_from_db())
    # exit()
    init_db()

    check_run()
    exit()
    request = request_api()
    json_data = request.text
    dict_data = json_text_to_dict(json_data)
    df_data = df_from_dict(dict_data)
    top3 = get_top_3_daily(df_data)
    html = save_html_report(top3)
    save_pdf_report(html)
    add_run_to_db('done', request.text)
    pass


if __name__ == '__main__':
    main()
