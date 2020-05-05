import pandas as pd 

df = pd.read_csv('TERC_Urzedowy_2020-05-05.csv', encoding="utf-8", sep=';', dtype=str)

names = ['województwo', 'powiat', 'miasto na prawach powiatu', 'miasto stołeczne, na prawach powiatu']

df = df[df['NAZWA_DOD'].apply(lambda x: True if x in names else False)][['WOJ', 'POW', 'NAZWA']]
df['NAZWA'] = df['NAZWA'].str.upper()
df['WOJ'] = df['WOJ']
df['POW'] = df['POW'].fillna('')
df['CODE'] = df['WOJ'].str.cat(df['POW'])

df.to_csv('../data/TERC_list.csv', index = False)