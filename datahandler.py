import pandas as pd
import sqlite3
from pandasql import sqldf

import pandas_datareader as web
import bs4 as bs

import datetime as dt
from datetime import timedelta
import matplotlib.pyplot as plt
from matplotlib import style

import pickle
import requests
import numpy as np


# data sources
# cases:        https://github.com/CSSEGISandData/COVID-19
# test data:    https://ourworldindata.org/grapher/full-list-total-tests-for-covid-19
# https://github.com/owid/covid-19-data/tree/master/public/data/


# Call SQL query
def pysqldf(q):
    return sqldf(q, globals())


def compile_data(df, target, save=True, verbose=True):
    """
    Aggregate data on target column
    :param df: source df
    :param target: target column to join on
    :param save: bool save as csv
    :param verbose: bool print debug
    :return: joined dataframe
    """

    main_df = pd.DataFrame()

    for count, ticker in enumerate(df.columns):
        try:
            df.rename(columns={target: ticker}, inplace=True)
            df.drop(df.columns.difference([ticker]), 1, inplace=True)

            if main_df.empty:
                main_df = df
            else:
                main_df = main_df.join(df, how='outer')
        except Exception as e:
            print('{}: Skipping {}'.format(e, ticker))

        if verbose:
            if count % 1 == 0:
                print(count)

    if save:
        main_df.to_csv('joined_{}.csv'.format(target))

    return main_df


# Load test per day data
dftests = pd.read_csv('full-list-covid-19-tests-per-day.csv',
                      header=0, names=['country', 'code', 'tests'],
                      dtype={'country': str, 'code': str, 'tests': float},
                      index_col=2, parse_dates=True)
print(dftests.head())

# Load mobility report
dfmobility = pd.read_csv('Global_Mobility_Report.csv',
                         header=0, names=['country_region_code',
                                          'country_region',
                                          'sub_region_1',
                                          'sub_region_2',
                                          'retail_and_recreation_percent_change_from_baseline',
                                          'grocery_and_pharmacy_percent_change_from_baseline',
                                          'parks_percent_change_from_baseline',
                                          'transit_stations_percent_change_from_baseline',
                                          'workplaces_percent_change_from_baseline',
                                          'residential_percent_change_from_baseline'],
                         dtype={'country_region_code': str,
                                'country_region': str,
                                'sub_region_1': str,
                                'sub_region_2': str,
                                'retail_and_recreation_percent_change_from_baseline': float,
                                'grocery_and_pharmacy_percent_change_from_baseline': float,
                                'parks_percent_change_from_baseline': float,
                                'transit_stations_percent_change_from_baseline': float,
                                'workplaces_percent_change_from_baseline': float,
                                'residential_percent_change_from_baseline': float},
                         index_col=4, parse_dates=True)
print(dfmobility.head())

dfconfirmed_global = pd.read_csv('time_series_covid19_confirmed_global.csv')

# joined_test = compile_data(dftests, target='tests', save=True, verbose=True)
# print(joined_test.head())
# print(dftests.groupby(dftests['country']).sum())
q = """
    SELECT country, SUM(tests) as 'sum'
    FROM dftests
    GROUP BY country
    """
df_sum_tests = pysqldf(q)
df_sum_tests.plot.bar(x='country',y='sum')

q = """
    SELECT country from df_sum_tests
    """
print(pysqldf(q)['country'].values)

plt.show()
