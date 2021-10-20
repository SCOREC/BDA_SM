import argparse
import requests
import json
import pandas as pd

'''
    Reads data from csv file
'''

data_file='mutation_data.csv'
data_df= pd.read_csv(data_file)

data_df
data_df = data_df.astype(str)
print(data_df)
print(data_df.dtypes)

def do_split(full_df, column_no):
    df_new = full_df.iloc[:,[0,column_no]].copy()
    df_new['status'] = pd.Series([1 for x in range(len(df_new.index))])
    df_new = df_new.astype(str)
    return df_new

def get_data(): return data_df