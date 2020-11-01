#################################################################################
#                                IMPORTATIONS                                   #  
#################################################################################

from PIL import Image
import PIL.ExifTags

import folium
from folium import plugins
from folium import IFrame 

import ipywidgets
import numpy as np
import pandas as pd
import base64
import os

import geopy
from geopy import*

#################################################################################
#                                DONNEES EXIFS                                  #
#################################################################################


#extraction des données exif
image = Image.open("chat.jpg")
exif_data_PIL = image._getexif()
exif_data = {}

for k, v, in PIL.ExifTags.TAGS.items():
    if k in exif_data_PIL:
        value = exif_data_PIL[k]
    else:
        value = None  
    exif_data[v] = {"tag": k, "raw": value,"processed": value}
image.close()

#conversion en décimal
degre=exif_data['GPSInfo']['processed'][2][0]
minute=exif_data['GPSInfo']['processed'][2][1]
seconde=exif_data['GPSInfo']['processed'][2][2]
latitude = degre + minute/60 + seconde/3600

degre=exif_data['GPSInfo']['processed'][4][0]
minute=exif_data['GPSInfo']['processed'][4][1]
seconde=exif_data['GPSInfo']['processed'][4][2]
longitude  = degre + minute/60 + seconde/3600

#prise en compte des références cardinales et inversion du signe des coordonnées
# si les références ne sont pas N ou W.
if exif_data['GPSInfo']['processed'][1]=='S': latitude=-latitude
if exif_data['GPSInfo']['processed'][3]=='E': longitude=-longitude
    
gps = (latitude, longitude)


#################################################################################
#                                    MAP                                        #
#################################################################################


# la map
map_layer_control = folium.Map(gps, zoom_start=5)

# ajouter différents types de map
folium.raster_layers.TileLayer('Open Street Map').add_to(map_layer_control)
folium.raster_layers.TileLayer('Stamen Terrain').add_to(map_layer_control)
folium.raster_layers.TileLayer('Stamen Toner').add_to(map_layer_control)
folium.raster_layers.TileLayer('Stamen Watercolor').add_to(map_layer_control)
folium.raster_layers.TileLayer('CartoDB Positron').add_to(map_layer_control)
folium.raster_layers.TileLayer('CartoDB Dark_Matter').add_to(map_layer_control)


# ajouter la photo sur le popup 
tooltip = "Clique pour voir la photo / Double clique pour zoomer"
encoded = base64.b64encode(open( 'chat.jpg','rb').read()).decode()
html = '<figure>'
html += '<img src="data:image/jpeg;base64,{}"width="124" height="166">'.format(encoded)
#ajouter la date et l'heure
date=exif_data['DateTime']['processed'][8:10] + '/' + exif_data['DateTime']['processed'][5:7] + '/' + exif_data['DateTime']['processed'][0:4]
heure= exif_data['DateTime']['processed'][11:16]
html += '<br><b> date: </b>'+ date+'<br> <b> heure: </b>'+ heure
#ajouter l'adresse
locator = Nominatim(user_agent="myGeocoder")   
location = locator.reverse(gps) 
html += '<br><b> lieu: </b>'+ location.address 
# afficher dans le popup
popup = folium.Popup(html, max_width=166)
# ajouter un icon
icon=folium.Icon(color='red', icon='camera') 
# ajouter le tout à la map 
folium.Marker(gps, tooltip=tooltip, popup=popup, icon=icon).add_to(map_layer_control)

# ajouter le layer control pour montrer les differentes maps 
folium.LayerControl().add_to(map_layer_control)

# afficher la map
map_layer_control

#sauvegarder
map_layer_control.save(os.path.join('/Users/admin/Documents/NSI/GPS/map.html'))

