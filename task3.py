"""
map of twitter fllowing locations
"""
import ssl
import requests
import folium
import certifi
import os
from flask import Flask, render_template, request
import geopy.geocoders
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from folium.plugins import MarkerCluster

def info_request(user_name):
    """
    requests info about user's twitter friends
    """
    load_dotenv('bt.env')
    key=os.environ.get('BEARER')
    headers = {'Authorization': f'Bearer {key}'}
    params = {'screen_name': user_name, 'count': 100}
    response = requests.get('https://api.twitter.com/1.1/friends/list.json',
                            headers=headers,
                            params=params)
    ctx = ssl.create_default_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ctx
    geolocator = Nominatim(user_agent="task3.py", scheme = 'http')
    for elem in response.json()['users']:
        nam, loc = elem["screen_name"], elem["location"]
        if loc != '':
            location = geolocator.geocode(loc, timeout=None)
            if location is not None:
                yield (nam, (location.latitude, location.longitude))

def map_creation(usrname):
    """
    creates a map file
    """
    mapp = folium.Map(location = [49.83826, 24.02324], zoom_start = 2, control_scale = True)
    markers_group = folium.FeatureGroup(name = "Followings")
    locations = [i for i in info_request(usrname)]
    # print(locations)
    marker_cluster = MarkerCluster([i[1] for i in locations], name = "Markers of distanse")
    mapp.add_child(markers_group)
    mapp.add_child(marker_cluster)
    for usr in locations:
        iframe = folium.IFrame(usr[0], width = 200, height = 100)
        markers_group.add_child(folium.Marker(location=usr[1], popup=folium.Popup(iframe)))
    mapp.add_child(folium.LayerControl())
    mapp.save('templates/map_of_locations.html')

app = Flask(__name__)

@app.route("/")

def start():
    """
    opens website
    """
    return render_template('welcome.html')

@app.route("/where", methods = ["POST"])

def run_tudududu_tudududu():
    """
    gets username and creates map
    """
    username = request.form['name']
    map_creation(username)
    return render_template('map_of_locations.html')

app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.after_request

def add_header(response):
    """
    helps to create new map
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

if __name__ == "__main__":
    app.run(debug=True)
