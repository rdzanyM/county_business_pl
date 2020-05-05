import pandas as pd 
import xml.etree.ElementTree as et

tree = et.parse("pkd2007.xml")

columns = ["level", "symbol", "name"]
df = pd.DataFrame(columns = columns)

for node in tree.findall('poziom'):
    level = node.find('nazwaPoziomu').text
    for elem in node.findall('element'):
        symbol = elem.find('symbol').text
        name = elem.find('nazwa').text

        df = df.append(pd.Series([level, symbol, name], index = columns), ignore_index = True)

section_df = df.loc[df['level'] == 'sekcja'][["symbol", "name"]]
section_df.to_csv('../data/section_list.csv', encoding = "utf-8", index = False)

division_df = df.loc[df['level'] == 'dział'][["symbol", "name"]]
division_df.to_csv('../data/division_list.csv', encoding = "utf-8", index = False)

group_df = df.loc[df['level'] == 'grupa'][["symbol", "name"]]
group_df["symbol"] = group_df["symbol"].str.replace('.', '', regex=False)
group_df.to_csv('../data/group_list.csv', encoding = "utf-8", index = False)

class_df = df.loc[df['level'] == 'klasa'][["symbol", "name"]]
class_df["symbol"] = class_df["symbol"].str.replace('.', '', regex=False)
class_df.to_csv('../data/class_list.csv', encoding = "utf-8", index = False)