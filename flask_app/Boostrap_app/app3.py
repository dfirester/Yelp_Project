""" flask_example.py

    Required packages:
    - flask
    - folium

    Usage:

    Start the flask server by running:

        $ python flask_example.py

    And then head to http://127.0.0.1:5000/ in your browser to see the map displayed

"""

from flask import Flask, render_template,url_for, request
import folium
import numpy as np
from folium.plugins import HeatMap
from folium.plugins import MarkerCluster

import geopandas
import pandas as pd


app = Flask(__name__)

@app.route('/')
def index():
   return render_template('index.html')



@app.route('/map/<foodtype>')
def map(foodtype):
    name = foodtype + '.csv'
    tacos = pd.read_csv(name)
    gdf = geopandas.GeoDataFrame(tacos, geometry=geopandas.points_from_xy(tacos.longitude, tacos.latitude))
    gdf.crs = {'init' :'epsg:4326'}
    # Get x and y coordinates for each point
    gdf["x"] = gdf["geometry"].apply(lambda geom: geom.x)
    gdf["y"] = gdf["geometry"].apply(lambda geom: geom.y)

    #  Create a list of coordinate pairs
    locations_with_weights = list(zip(gdf["y"], gdf["x"],np.exp(5*(gdf['Weighted taco score 2']-.3))))
    locations = list(zip(gdf["y"], gdf["x"]))

    html = """Resturant Name: <td>{}</td><br> Food Score: <td>{}</td>""".format


    m = folium.Map(location=[43.65,-79.38], tiles = 'cartodbpositron', zoom_start=11, control_scale=True)

    width, height = 300,50
    popups, locations = [], []
    for idx, row in gdf.iterrows():
        locations.append([row['geometry'].y, row['geometry'].x])
        name = row['name']
    
        iframe = folium.IFrame(html(name,row['Weighted taco score 2']), width=width, height=height)
        popups.append(folium.Popup(iframe))


    h = folium.FeatureGroup(name='Resturant')

    h.add_child(MarkerCluster(locations=locations, popups=popups))
    m.add_child(h)


    points_gjson = folium.features.GeoJson(gdf, name="Good Tacos")
    HeatMap(locations_with_weights).add_to(m)
    m.save('templates/map.html')
    return render_template('map.html')

if __name__ == '__main__':
    app.run(debug=False)