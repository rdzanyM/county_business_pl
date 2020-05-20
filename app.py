import os
import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
#from scipy.stats import zscore

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc


with open('./geo/wojewodztwa-min.geojson', 'r', encoding="utf8") as json_file:
    geojson = json.load(json_file)
v_id = pd.DataFrame([v['properties'] for v in geojson['features']])
v_id['nazwa'] = v_id['nazwa'].str.upper()

df = pd.read_csv('./data/ceidg_data_classif_removed.csv')
df['MainAddressTERC'] = df['MainAddressTERC'].fillna(0).astype(int).apply(str)
tooShortTERCCodesMask = (df['MainAddressTERC'].str.len()%2==1)
df.loc[tooShortTERCCodesMask, 'MainAddressTERC'] = '0' + df['MainAddressTERC']

data = df[['MainAddressVoivodeship', 'MainAddressCounty', 'PKDMainSection']]
#matrix = data.groupby(['MainAddressVoivodeship','PKDMainSection']).size().unstack(fill_value=0)
#matrix_proportions = matrix.div(matrix.sum(axis=1), axis=0)
#normalized = matrix_proportions.apply(zscore)
#normalized['Max'] = normalized.idxmax(axis=1)
#print(normalized['Max'])

#normalized_absolute = matrix.apply(zscore)
# mało działalności z T, więc pomijamy, bo wywala w kosmos Z Score jak już coś jest
#normalized_absolute['Max'] = normalized_absolute.iloc[:,:-1].idxmax(axis=1)

sections = pd.read_csv('./data/section_list.csv', dtype=str)
sections['name'] = sections[['symbol', 'name']].apply('-'.join, axis=1)
sections = sections.sort_values(axis=0, by='symbol')

divisions = pd.read_csv('./data/division_list.csv', dtype=str)
divisions['name'] = divisions[['symbol', 'name']].apply('-'.join, axis=1)
divisions['symbol'] = divisions['symbol'].astype('float64')
divisions = divisions.sort_values(axis=0, by='symbol')

groups = pd.read_csv('./data/group_list.csv')
groups['symbol'] = groups['symbol'].astype(str)
groups['name'] = groups[['symbol', 'name']].apply('-'.join, axis=1)
groups['symbol'] = groups['symbol'].astype('float64')
groups = groups.sort_values(axis=0, by='symbol')

classes = pd.read_csv('./data/class_list.csv')
classes['symbol'] = classes['symbol'].astype(str)
classes['name'] = classes[['symbol', 'name']].apply('-'.join, axis=1)
classes['symbol'] = classes['symbol'].astype('float64')
classes = classes.sort_values(axis=0, by='symbol')

pop = pd.read_csv('./data/Population_list.csv', dtype={'CODE' : str, 'NAME' : str, 'Total' : 'float64'})[['CODE','NAME','TOTAL']]

terc_list = pd.read_csv('./data/TERC_list.csv', dtype=str)

with open('./geo/wojewodztwa-min.geojson', 'r', encoding="utf8") as json_file:
    geojson_voivodeships = json.load(json_file)

with open('./geo/powiaty-min.geojson', 'r', encoding="utf8") as json_file:
    geojson_counties = json.load(json_file)

data = df[
    ['MainAddressVoivodeship', 'MainAddressCounty', 'MainAddressTERC', 'Sex', 'HasPolishCitizenship', 'PKDMainSection',
     'PKDMainDivision', 'PKDMainGroup', 'PKDMainClass', 'Target', 'NoOfAdditionalPlaceOfTheBusiness']]
data['MainVoivodeshipTERC'] = data['MainAddressTERC'].str.slice(start=0, stop=2)
data['MainCountyTERC'] = data['MainAddressTERC'].str.slice(start=0, stop=4)
data.drop(columns=['MainAddressTERC'])

possible_classification_combinations = data[
    ['PKDMainSection', 'PKDMainDivision', 'PKDMainGroup', 'PKDMainClass']].drop_duplicates().dropna()

section_list = [dict(label=row['name'], value=row['symbol']) for i, row in sections.iterrows()]

app = dash.Dash(
    __name__, external_stylesheets=[dbc.themes.BOOTSTRAP]
)

server = app.server

controls = dbc.Card([
    dbc.FormGroup(
        [
            dbc.Label("Podział"),
            dcc.Dropdown(id="Podział", value='voivodeships', options=[
                {'label': 'Województwa', 'value': 'voivodeships'}, {'label': 'Powiaty', 'value': 'counties'}
            ])
        ]
    ),
    dbc.FormGroup(
        [
            dbc.Label("Sekcja"),
            dcc.Dropdown(id="section-dropdown", options=section_list)
        ]
    ),
    dbc.FormGroup(
        [
            dbc.Label("Dział"),
            dcc.Dropdown(id="division-dropdown")
        ]
    ),
    dbc.FormGroup(
        [
            dbc.Label("Grupa"),
            dcc.Dropdown(id="group-dropdown")
        ]
    ),
    dbc.FormGroup(
        [
            dbc.Label("Klasa"),
            dcc.Dropdown(id="class-dropdown")
        ]
    ),
    html.Hr(style={"border": ""}),
    dbc.FormGroup(
        [
            dbc.Label("Rodzaj analizowanych działalności (w oparciu o zmienną Target)", style={'font-weight': 'bold'}),
            dcc.RadioItems(id='target',
                           options=[
                               {'label': 'Wszystkie działalności', 'value': 'none'},
                               {'label': 'Działalności zamknięte w przciągu roku', 'value': 'true'},
                               {'label': 'Działalności, które przetrwały rok', 'value': 'false'},
                           ],
                           value='none'
                           )
        ]
    ),
    html.Hr(style={"border": ""}),
    dbc.FormGroup(
        [
            dbc.Label("Forma prezentacji liczby działaności", style={'font-weight': 'bold'}),
            dcc.RadioItems(id='radio',
                           options=[
                               {'label': 'Całkowita liczba działalności', 'value': 'total'},
                               {'label': 'Liczba przypadająca na 1000 mieszkańców', 'value': 'per_capita'},
                           ],
                           value='total'
                           )
        ]
    )
],
    body=True)

app.layout = dbc.Container(
    [
        html.H2("Charakterystyka przestrzenna działalności gospodarczej"),
        html.Hr(style={"border": ""}),
        dbc.Row(
            [
                dbc.Col(controls, md=3),
                dbc.Col(dcc.Graph(id="graph"), md=9),
            ],
            align="left"
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Liczba działalności z podziałem na płeć", id="chart-sex-label",
                                  style={"padding-top": "2%", "text-align": "center", 'font-weight': 'bold'}),
                        dcc.Graph(id="chart-sex",
                                  figure={'data': [], 'layout': {'margin': {'b': 0, 'l': 0, 'r': 0, 't': 0}}})
                    ],
                    style={'padding': '3%'},
                    md=6
                ),
                dbc.Col(
                    [
                        dbc.Label("Liczba działalności prowadzonych przez obywateli Polski",
                                  id="chart-citizenship-label",
                                  style={"padding-top": "2%", "text-align": "center", 'font-weight': 'bold'}),
                        dcc.Graph(id="chart-citizenship",
                                  figure={'data': [], 'layout': {'margin': {'b': 0, 'l': 0, 'r': 0, 't': 0}}})
                    ],
                    style={'padding': '3%'},
                    md=6)
            ],
            align="left"
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Statystyka rozporoszenia miejsc prowadzenia działalności", id="chart-places-label",
                                  style={"padding-top": "2%", "text-align": "center", 'font-weight': 'bold'}),
                        dcc.Graph(id="chart-places",
                                  figure={'data': [], 'layout': {'margin': {'b': 0, 'l': 0, 'r': 0, 't': 0}}})
                    ],
                    md=12
                )

            ],
            style={'padding': '3%', 'align-content': 'center'},
            align="left"
        )
    ],
    style={"max-width": "90%", "margin-top": "2%"}
)


@app.callback(Output("graph", "figure"), [
    Input("section-dropdown", "value"),
    Input("division-dropdown", "value"),
    Input("group-dropdown", "value"),
    Input("class-dropdown", "value"),
    Input("Podział", "value"),
    Input("radio", "value"),
    Input("target", "value")
])
def make_figure(section, division, group, _class, area_division, radio, target):
    if section is None:
        v_size = data
    elif division is None:
        v_size = data[data['PKDMainSection'] == section]
    elif group is None:
        v_size = data[data['PKDMainDivision'] == division]
    elif _class is None:
        v_size = data[data['PKDMainGroup'] == group]
    else:
        v_size = data[data['PKDMainClass'] == _class]

    if target == "true":
        v_size = v_size[v_size['Target'] == True]
    elif target == "false":
        v_size = v_size[v_size['Target'] == False]

    if area_division is None or area_division == "voivodeships":
        v_size = v_size.groupby(['MainAddressVoivodeship', 'MainVoivodeshipTERC']).size().to_frame('size').reset_index()

        if (radio == 'per_capita'):
            v_size['size'] = 1e3 * v_size['size'] / v_size.join(pop.set_index('CODE'), on='MainVoivodeshipTERC')[
                'TOTAL']
        geojson = geojson_voivodeships
        v_id = pd.DataFrame([v['properties'] for v in geojson['features']])
        v_id['nazwa'] = v_id['nazwa'].str.upper()
        map_data = pd.merge(v_size, v_id.set_index('nazwa'), how='right', left_on='MainAddressVoivodeship',
                            right_index=True)
        map_data['size'].fillna(0, inplace=True)
        tt = 'liczba firm' if radio == 'total' else 'liczba firm na 1000 mieszkańców'
        fig = px.choropleth(map_data, geojson=geojson, color="size", locations="id", featureidkey="properties.id",
                            projection="mercator", color_continuous_scale="peach",
                            labels={'size': tt}, hover_name="MainAddressVoivodeship",
                            custom_data=['MainVoivodeshipTERC'],
                            height=800)
    else:
        v_size = v_size.groupby(['MainAddressCounty', 'MainCountyTERC']).size().to_frame('size').reset_index()

        if (radio == 'per_capita'):
            v_size['size'] = 1e3 * v_size['size'] / v_size.join(pop.set_index('CODE'), on='MainCountyTERC')['TOTAL']
        geojson = geojson_counties
        v_id = pd.DataFrame([v['properties'] for v in geojson_counties['features']])
        v_id['nazwa'] = v_id['nazwa'].str[7:]
        v_id['nazwa'] = v_id['nazwa'].str.upper()
        map_data = pd.merge(v_size, v_id.set_index('nazwa'), how='right', left_on='MainAddressCounty', right_index=True)
        map_data['size'].fillna(0, inplace=True)
        tt = 'liczba firm' if radio == 'total' else 'liczba firm na 1000 mieszkańców'
        fig = px.choropleth(map_data, geojson=geojson, color="size", locations="id", featureidkey="properties.id",
                            projection="mercator", color_continuous_scale="peach",
                            labels={'size': tt}, hover_name="MainAddressCounty", custom_data=['MainCountyTERC'],
                            height=800)
    fig.update_geos(fitbounds="locations", visible=False, lataxis_range=[50, 60], lonaxis_range=[5, 30])
    return fig


@app.callback(Output('chart-sex', 'figure'), [
    Input('graph', 'clickData'),
    Input("Podział", "value"),
    Input("section-dropdown", "value"),
    Input("division-dropdown", "value"),
    Input("group-dropdown", "value"),
    Input("class-dropdown", "value")
])
def printData_sex(clickData, area_division, section, division, group, _class):
    if section is None:
        chart_data = data
    elif division is None:
        chart_data = data[(data['PKDMainSection'] == section)]
    elif group is None:
        chart_data = data[(data['PKDMainSection'] == section) & (data['PKDMainDivision'] == division)]
    elif _class is None:
        chart_data = data[(data['PKDMainSection'] == section) & (data['PKDMainDivision'] == division) & (
                    data['PKDMainGroup'] == group)]
    else:
        chart_data = data[(data['PKDMainSection'] == section) & (data['PKDMainDivision'] == division) & (
                    data['PKDMainGroup'] == group) & (data['PKDMainClass'] == _class)]

    if clickData is not None:
        terc = clickData['points'][0]['customdata'][0]
        name = terc_list[terc_list['CODE'] == terc]['NAZWA'].values[0]
        if area_division == 'counties':
            chart_data = chart_data[chart_data['MainCountyTERC'] == terc]
            title = "POW. " + name
        else:
            chart_data = chart_data[chart_data['MainVoivodeshipTERC'] == terc]
            title = "WOJ. " + name
    else:
        title = "POLSKA"

    chart_data = chart_data.groupby('Sex').size().to_frame('Liczba firm').reset_index()
    chart_data = chart_data.rename(columns={'Sex': 'Płeć'})
    chart_data['Płeć'] = chart_data['Płeć'].apply(lambda x: 'Mężczyzna' if x == 'M' else "Kobieta")

    fig = px.pie(chart_data, values='Liczba firm', names='Płeć', color='Płeć',
                 color_discrete_map={'Mężczyzna': 'skyblue', 'Kobieta': 'pink'}, title=title)
    return fig


@app.callback(Output('chart-citizenship', 'figure'), [
    Input('graph', 'clickData'),
    Input("Podział", "value"),
    Input("section-dropdown", "value"),
    Input("division-dropdown", "value"),
    Input("group-dropdown", "value"),
    Input("class-dropdown", "value")
])
def printData_citizenship(clickData, area_division, section, division, group, _class):
    if section is None:
        chart_data = data
    elif division is None:
        chart_data = data[(data['PKDMainSection'] == section)]
    elif group is None:
        chart_data = data[(data['PKDMainSection'] == section) & (data['PKDMainDivision'] == division)]
    elif _class is None:
        chart_data = data[(data['PKDMainSection'] == section) & (data['PKDMainDivision'] == division) & (
                    data['PKDMainGroup'] == group)]
    else:
        chart_data = data[(data['PKDMainSection'] == section) & (data['PKDMainDivision'] == division) & (
                    data['PKDMainGroup'] == group) & (data['PKDMainClass'] == _class)]

    if clickData is not None:
        terc = clickData['points'][0]['customdata'][0]
        name = terc_list[terc_list['CODE'] == terc]['NAZWA'].values[0]
        if area_division == 'counties':
            chart_data = chart_data[chart_data['MainCountyTERC'] == terc]
            title = "POW. " + name
        else:
            chart_data = chart_data[chart_data['MainVoivodeshipTERC'] == terc]
            title = "WOJ. " + name
    else:
        title = "POLSKA"

    chart_data = chart_data.groupby('HasPolishCitizenship').size().to_frame('Liczba firm').reset_index()
    chart_data = chart_data.rename(columns={'HasPolishCitizenship': 'Obywatelstwo polskie'})
    chart_data['Obywatelstwo polskie'] = chart_data['Obywatelstwo polskie'].apply(
        lambda x: 'Tak' if x == True else 'Nie')

    fig = px.pie(chart_data, values='Liczba firm', names='Obywatelstwo polskie', color='Obywatelstwo polskie',
                 color_discrete_map={'Tak': 'yellowgreen', 'Nie': 'indianred'}, title=title)
    return fig


@app.callback(Output('chart-places', 'figure'), [
    Input('graph', 'clickData'),
    Input("Podział", "value"),
    Input("section-dropdown", "value"),
    Input("division-dropdown", "value"),
    Input("group-dropdown", "value"),
    Input("class-dropdown", "value")
])
def printData_places(clickData, area_division, section, division, group, _class):
    if section is None:
        chart_data = data
    elif division is None:
        chart_data = data[(data['PKDMainSection'] == section)]
    elif group is None:
        chart_data = data[(data['PKDMainSection'] == section) & (data['PKDMainDivision'] == division)]
    elif _class is None:
        chart_data = data[(data['PKDMainSection'] == section) & (data['PKDMainDivision'] == division) & (
                    data['PKDMainGroup'] == group)]
    else:
        chart_data = data[(data['PKDMainSection'] == section) & (data['PKDMainDivision'] == division) & (
                    data['PKDMainGroup'] == group) & (data['PKDMainClass'] == _class)]

    if clickData is not None:
        terc = clickData['points'][0]['customdata'][0]
        name = terc_list[terc_list['CODE'] == terc]['NAZWA'].values[0]
        if area_division == 'counties':
            chart_data = chart_data[chart_data['MainCountyTERC'] == terc]
            title = "POW. " + name
        else:
            chart_data = chart_data[chart_data['MainVoivodeshipTERC'] == terc]
            title = "WOJ. " + name
    else:
        title = "POLSKA"

    chart_data = chart_data.groupby('NoOfAdditionalPlaceOfTheBusiness').size().to_frame('Liczba firm').reset_index()
    chart_data = chart_data.rename(
        columns={'NoOfAdditionalPlaceOfTheBusiness': 'Liczba dodatkowych miejsc działalności'})

    fig = px.bar(chart_data, x='Liczba dodatkowych miejsc działalności', y='Liczba firm', title=title)
    fig.update_layout(yaxis_type="log", plot_bgcolor='rgba(0,0,0,0)')
    fig.update_yaxes(title_text='Liczba firm (skala logarytmiczna)')
    fig.update_traces(marker_color='coral')
    return fig


@app.callback(Output("division-dropdown", "options"), [Input("section-dropdown", "value")])
def get_division_options(section):
    divisions_from_section = divisions[divisions['parent'] == section]
    division_list = [dict(label=row['name'], value=row['symbol']) for i, row in divisions_from_section.iterrows()]
    return division_list


@app.callback(Output("division-dropdown", "value"), [Input("section-dropdown", "value")])
def reset_division_value_on_section_change(section):
    return None


@app.callback(Output("group-dropdown", "options"), [Input("division-dropdown", "value")])
def get_group_options(division):
    groups_from_section = groups[groups['parent'] == division]
    group_list = [dict(label=row['name'], value=row['symbol']) for i, row in groups_from_section.iterrows()]
    return group_list


@app.callback(Output("group-dropdown", "value"),
              [Input("section-dropdown", "value"), Input("division-dropdown", "value")])
def reset_group_value_on_section_or_division_change(section, division):
    return None


@app.callback(Output("class-dropdown", "options"), [Input("group-dropdown", "value")])
def get_division_options(group):
    classes_from_section = classes[classes['parent'] == group]
    class_list = [dict(label=row['name'], value=row['symbol']) for i, row in classes_from_section.iterrows()]
    return class_list


@app.callback(Output("class-dropdown", "value"), [
    Input("section-dropdown", "value"),
    Input("division-dropdown", "value"),
    Input("group-dropdown", "value")])
def reset_class_value_on_section_or_division_or_group_change(section, division, group):
    return None


@app.callback(Output('graph', 'clickData'), [Input('Podział', 'value')])
def reset_clickData_on_map_change(area_division):
    return None

if __name__ == '__main__':
    app.run_server(debug=True)