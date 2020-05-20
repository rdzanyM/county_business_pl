import pandas as pd
import json
import numpy as np

def read_from_json(filename):
    with open(filename, encoding="utf-8") as json_file:
        data = json.load(json_file)
    return data

def replace_duplicated_values(file_with_values, column_name, file_with_abbreviations, dependent_column):
    values_to_be_replaced = read_from_json(file_with_values)
    abbreviations = read_from_json(file_with_abbreviations)
    for val in values_to_be_replaced:
        if (df[column_name] == val).any():
            df.loc[df[column_name] == val, str(column_name)] = df.loc[df[column_name] == val].apply(lambda x : x[column_name] if x[dependent_column] != x[dependent_column] else x[column_name] + ' (' + abbreviations[x[dependent_column]] + ')', axis=1)

v_main = 'MainAddressVoivodeship'
c_main = 'MainAddressCounty'
v_corresp = 'CorrespondenceAddressVoivodeship'
c_corresp = 'CorrespondenceAddressCounty'
all_units = [v_main, c_main, v_corresp, c_corresp]


df = pd.read_csv('./data/ceidg_data_classif_cleaned.csv', encoding="utf-8", dtype=str)

replace_duplicated_values('duplicated_counties.json', c_main, 'voiv_abbreviations.json', v_main)
replace_duplicated_values('duplicated_counties.json', c_corresp, 'voiv_abbreviations.json', v_corresp)

df.to_csv("./data/ceidg_data_classif_cleaned2.csv")