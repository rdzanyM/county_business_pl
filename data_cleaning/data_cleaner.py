import pandas as pd
import json
import numpy as np


def read_data(sample: bool):
    ceidg_sample = "100_CEIDG_classification_sample.csv"
    ceidg = "ceidg_data_classif.csv"

    if sample is True:
        data = pd.read_csv(f"../data/{ceidg_sample}")
    else:
        data = pd.read_csv(f"../data/{ceidg}", dtype={"MainAddressTERC" : str})
    return data


def read_from_json(filename):
    with open(filename, encoding="utf-8") as json_file:
        data = json.load(json_file)
    return data


def empty_field_converter(x):
    if x == "":
        return "N/A"
    return x


def fill_empty_fields(*args):
    for arg in args:
        df[arg] = df[arg].apply(empty_field_converter)


def uppercase_converter(x):
    return x.upper()


def uppercase_columns(*args):
    for arg in args:
        df[arg] = df[arg].apply(uppercase_converter)


def prefixes_remover(city, prefixes):
    for prefix in prefixes:
        if city.startswith(prefix):
            return city[len(prefix):]
    return city


def delete_county_prefixes(*args):
    prefixes = read_from_json('prefixes_to_be_deleted.json')
    for arg in args:
        df[arg] = df[arg].apply(prefixes_remover, args=(prefixes,))


def replace_values_in_column(column_name, values):
    for key in values:
        df[column_name] = df[column_name].replace(key, values[key])


def replace_values(file_with_values, *args):
    values_to_be_replaced = read_from_json(file_with_values)
    for arg in args:
        replace_values_in_column(arg, values_to_be_replaced)

def replace_duplicated_values(file_with_values, column_name, file_with_abbreviations, dependent_column):
    values_to_be_replaced = read_from_json(file_with_values)
    abbreviations = read_from_json(file_with_abbreviations)
    for val in values_to_be_replaced:
        if (df[column_name] == val).any():
            df.loc[df[column_name] == val, str(column_name)] = df.loc[df[column_name] == val].apply(lambda x : x[column_name] if x[dependent_column] != x[dependent_column] else x[column_name] + ' (' + abbreviations[x[dependent_column]] + ')', axis=1)

def count_by_businesses(*args):
    for arg in args:
        business_counted_by_arg = df[arg].value_counts()
        business_counted_by_arg.to_csv(f"../data/{arg.lower()}_count_by.csv", header=True)

def partial_TERC_fill(data, terc):
   for index, row in data.iterrows():
        V = row['MainAddressVoivodeship']
        C = row['MainAddressCounty']
        
        if C == 'RADOM':
            data.at[index, 'MainAddressVoivodeship'] = 'MAZOWIECKIE'
            V = 'MAZOWIECKIE'
        if C == 'LUBLIN':
            data.at[index, 'MainAddressVoivodeship'] = 'LUBELSKIE'
            V = 'LUBELSKIE'

        code = ""
        if V not in ["", None, "N/A", 'EMPTYFIELD']:
            code = terc[terc['NAZWA'] == V]['CODE']

        if C not in ["", None, "N/A", 'EMPTYFIELD']:
            if V not in ["", None, "N/A"]:
                code = terc[(terc['NAZWA'] == C) & (terc['WOJ'] == code.values[0])]['CODE']
            else:
                code = terc[terc['NAZWA'] == C]['CODE']
        
        if type(code) == pd.Series:
            data.at[index, 'MainAddressTERC'] = code.values[0]
        else:
            data.at[index, 'MainAddressTERC'] = ""


df = read_data(sample=False)     
df = df.replace(np.nan, "", regex=True)

v_main = 'MainAddressVoivodeship'
c_main = 'MainAddressCounty'
v_corresp = 'CorrespondenceAddressVoivodeship'
c_corresp = 'CorrespondenceAddressCounty'
all_units = [v_main, c_main, v_corresp, c_corresp]

fill_empty_fields(*all_units)
uppercase_columns(*all_units)
delete_county_prefixes(c_main, c_corresp)
replace_values('voiv_to_be_replaced.json', v_main, v_corresp)
replace_values('county_to_be_replaced.json', c_main, c_corresp)

terc = pd.read_csv('../data/TERC_list.csv', encoding="utf-8", dtype=str)

partial_TERC_fill(df, terc)

replace_duplicated_values('duplicated_counties.json', c_main, 'voiv_abbreviations.json', v_main)
replace_duplicated_values('duplicated_counties.json', c_corresp, 'voiv_abbreviations.json', v_corresp)

df.to_csv("./data/ceidg_data_classif_cleaned.csv")

# count_by_businesses(*all_units)
