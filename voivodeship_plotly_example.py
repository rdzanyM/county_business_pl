from urllib.request import urlopen
import plotly.express as px
import pandas as pd
import numpy as np
import json

df = pd.DataFrame(np.array([range(1, 17)]).T, columns=['ids'])
with urlopen(
        'https://raw.githubusercontent.com/ppatrzyk/polska-geojson/master/wojewodztwa/wojewodztwa-min.geojson') as response:
    geojson = json.load(response)

fig = px.choropleth(df, geojson=geojson, color="ids", locations="ids", featureidkey="properties.id",
                    projection="mercator")
fig.update_geos(fitbounds="locations", visible=False, lataxis_range=[50, 60], lonaxis_range=[0, 30])
fig.write_html("voivodeships.html")
