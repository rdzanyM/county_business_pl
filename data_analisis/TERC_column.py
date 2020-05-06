import pandas as pd
import numpy as np


def read_data(sample: bool):
    ceidg_sample = "100_CEIDG_classification_sample.csv"
    ceidg = "ceidg_data_classif_cleaned.csv"

    if sample is True:
        data = pd.read_csv(f"../data/{ceidg_sample}")
    else:
        data = pd.read_csv(f"../data/{ceidg}")
    return data


df = read_data(sample=False)
df = df.replace(np.nan, "", regex=True)

TERC_list = pd.read_csv('../data/TERC_list.csv')

for index, row in df.iterrows():

    if row['MainAddressCounty'] not in ['', None]:
        df.at[index, 'ShortMainTERC'] = TERC_list.loc[TERC_list['NAZWA'] == row['MainAddressCounty']].iloc[0]['CODE']
    elif row['MainAddressVoivodeship'] not in ['', None]:
        df.at[index, 'ShortMainTERC'] = TERC_list.loc[TERC_list['NAZWA'] == row['MainAddressVoivodeship']].iloc[0]['CODE']
    else:
        df.at[index, 'ShortMainTERC'] = pd.NA

    if row['CorrespondenceAddressCounty'] not in ['', None]:
        df.at[index, 'ShortCorrespondenceTERC'] = TERC_list.loc[TERC_list['NAZWA'] == row['CorrespondenceAddressCounty']].iloc[0]['CODE']
    elif row['CorrespondenceAddressVoivodeship'] not in ['', None]:
        df.at[index, 'ShortCorrespondenceTERC'] = TERC_list.loc[TERC_list['NAZWA'] == row['CorrespondenceAddressVoivodeship']].iloc[0]['CODE']
    else:
        df.at[index, 'ShortCorrespondenceTERC'] = pd.NA


df.to_csv("../data/ceidg_data_classif_cleaned.csv", index = False)