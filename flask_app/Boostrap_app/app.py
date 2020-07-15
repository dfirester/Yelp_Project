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
    tacos['Weighted taco score 2'] = (tacos['Weighted taco score'] - min(tacos['Weighted taco score']))/(max(tacos['Weighted taco score']) - min(tacos['Weighted taco score']))
    toptacos = tacos[:10]
    othertacos = tacos[10:]
    gdf_top = geopandas.GeoDataFrame(toptacos, geometry=geopandas.points_from_xy(toptacos.longitude, toptacos.latitude))
    gdf_top.crs = {'init' :'epsg:4326'}
    
    # Get x and y coordinates for each point
    gdf_top["x"] = gdf_top["geometry"].apply(lambda geom: geom.x)
    gdf_top["y"] = gdf_top["geometry"].apply(lambda geom: geom.y)


    gdf_other = geopandas.GeoDataFrame(othertacos, geometry=geopandas.points_from_xy(othertacos.longitude, othertacos.latitude))
    gdf_other.crs = {'init' :'epsg:4326'}
    
    # Get x and y coordinates for each point
    gdf_other["x"] = gdf_other["geometry"].apply(lambda geom: geom.x)
    gdf_other["y"] = gdf_other["geometry"].apply(lambda geom: geom.y)
    
    #First we deal with the not highly rated resturants

      
    gdf_all = geopandas.GeoDataFrame(tacos, geometry=geopandas.points_from_xy(tacos.longitude, tacos.latitude))
    gdf_all.crs = {'init' :'epsg:4326'}
    
    # Get x and y coordinates for each point
    gdf_all["x"] = gdf_all["geometry"].apply(lambda geom: geom.x)
    gdf_all["y"] = gdf_all["geometry"].apply(lambda geom: geom.y)
    
    # Create a list of coordinate pairs
    locations_with_weights = list(zip(gdf_all["y"], gdf_all["x"],np.exp((5*gdf_other['Weighted taco score 2'] - .3))))
    
    locations = list(zip(gdf_other["y"], gdf_other["x"]))

   
    m = folium.Map(location=[43.65,-79.38], tiles = 'cartodbpositron', zoom_start=11, control_scale=True)
    html = """Resturant Name: <td>{}</td><br> Food Score: <td>{}</td>""".format

    width, height = 300,50
    popups, locations,icons = [], [],[]

    for idx, row in gdf_other.iterrows():
        locations.append([row['geometry'].y, row['geometry'].x])
        name = row['name']
    
        iframe = folium.IFrame(html(name,round(row['Weighted taco score'],3)), width=width, height=height)
        popups.append(folium.Popup(iframe))
        icons.append(folium.Icon(icon='info',prefix='fa'))
    
    h = folium.FeatureGroup(name='Resturant')

    h.add_child(MarkerCluster(locations=locations,icons=icons, popups=popups))
    m.add_child(h)


    points_gjson = folium.features.GeoJson(gdf_other, name="Tacos")
    HeatMap(locations_with_weights,min_opacity=.3).add_to(m)
    
    
    #Now we deal with the highly rated resturants
    locations = list(zip(gdf_top["y"], gdf_top["x"]))
    
    popups, locations,icons = [], [],[]

    for idx, row in gdf_top.iterrows():
        locations.append([row['geometry'].y, row['geometry'].x])
        name = row['name']
    
        iframe = folium.IFrame(html(name,round(row['Weighted taco score'],3)), width=width, height=height)
        popups.append(folium.Popup(iframe))
        icons.append(folium.Icon(color='lightred',icon='thumbs-up',prefix='fa'))
    
    h2 = folium.FeatureGroup(name='Top Resturant')
    for i in range(len(icons)):
        h2.add_child(folium.Marker(location=locations[i],icon=icons[i],popup=popups[i]))

    m.add_child(h2)
    #m.save('templates/map.html')
    f = folium.Figure(width=1000, height=500)
    m.add_to(f)
    return f._repr_html_()

if __name__ == '__main__':
    app.run(debug=False)