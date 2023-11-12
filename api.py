import os
from dotenv import load_dotenv
import requests
import pandas as pd

load_dotenv()
auth_token = os.getenv('API_KEY')

headers = {
    'Authorization': f'Bearer {auth_token}',
    'Content-Type': 'application/json',
}

def get_timeseries(str_):
    """

    :param str_:
    :return:
    """
    res = requests.get(str_, headers=headers)
    if res.status_code == 200:
        print('got data')
        df = parse_response(res)
    else:
        raise LookupError

    return df

def parse_response(response):
    """

    :param response:
    :return:
    """
    dict_ = response.json()
    list_ = dict_['point_samples']
    df = pd.DataFrame(list_)
    df.index = df.pop('time')
    df.drop(columns='name', inplace=True)

    return df



