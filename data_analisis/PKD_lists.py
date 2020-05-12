import pandas as pd 
import xml.etree.ElementTree as et

tree = et.parse("./data_analisis/pkd2007.xml")
root = tree.getroot()

columns = ["level", "symbol", "name", "parent"]
df = pd.DataFrame(columns = columns)

uuid = {}
for node in tree.findall('poziom'):
    level = node.find('nazwaPoziomu').text
    for elem in node.findall('element'):
        symbol = elem.find('symbol').text
        uuid[elem.find('uuid').text] = symbol
        parent = ''
        parentUUID = elem.find('elementNadrzednyUuid')
        if parentUUID != None:
            parent = uuid[parentUUID.text]
            
        name = elem.find('nazwa').text

        df = df.append(pd.Series([level, symbol, name, parent], index = columns), ignore_index = True)

section_df = df.loc[df['level'] == 'sekcja'][["symbol", "name", "parent"]]
section_df.to_csv('./data/section_list.csv', encoding = "utf-8", index = False)

division_df = df.loc[df['level'] == 'dział'][["symbol", "name", "parent"]]
division_df.to_csv('./data/division_list.csv', encoding = "utf-8", index = False)

group_df = df.loc[df['level'] == 'grupa'][["symbol", "name", "parent"]]
group_df["symbol"] = group_df["symbol"].str.replace('.', '', regex=False)
group_df.to_csv('./data/group_list.csv', encoding = "utf-8", index = False)

class_df = df.loc[df['level'] == 'klasa'][["symbol", "name", "parent"]]
class_df["symbol"] = class_df["symbol"].str.replace('.', '', regex=False)
class_df.to_csv('./data/class_list.csv', encoding = "utf-8", index = False)