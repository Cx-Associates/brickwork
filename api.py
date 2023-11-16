import os
from dotenv import load_dotenv
import requests
import pandas as pd
import yaml


env_filepath = 'env.yml'

def get_timeseries(str_):
    """

    :param str_:
    :return:
    """
    with open(env_filepath, 'r') as file:
        config = yaml.safe_load(file)
        url = config['DATABASE_URL']
        str_ = url + str_
        auth_token = config['API_KEY']
        headers = {
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json',
        }
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
    df.index = pd.to_datetime(df.pop('time'))
    df.drop(columns='name', inplace=True)
    #ToDo: really need to keep parsing to get the number out of this string

    return df



