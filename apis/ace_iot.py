import os
from dotenv import load_dotenv
import requests
import pandas as pd
import yaml

env_filename = 'api_keys.yml'
# grandparent_dir = os.path.dirname(os.path.dirname(os.getcwd()))
# env_filepath = os.path.join(grandparent_dir, env_filename)
f_drive_path = 'F:/PROJECTS/1715 Main Street Landing EMIS Pilot/API keys'
env_filepath = os.path.join(f_drive_path, env_filename)

def get_timeseries(
        str_,
        timezone='US/Eastern'
):
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
            print(f'Got data! From: \n {str_} \n')
            df = parse_response(res)
            df.index = df.index.tz_localize('UTC').tz_convert(timezone)
        else:
            msg = f'API request from ACE was unsuccessful. \n {res.reason} \n {res.content}'
            raise Exception(msg)
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
    df['value'] = pd.to_numeric(df['value'])

    return df



