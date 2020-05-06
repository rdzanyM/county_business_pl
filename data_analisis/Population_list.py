import pandas as pd 

df = pd.read_csv('Population.csv', encoding="utf-8", sep=';', dtype=str)

df['NAME'] = df['NAME'].str.replace(' ', '', regex=False).str.upper()

df.to_csv('../data/Population_list.csv', index = False)