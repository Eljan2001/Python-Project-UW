import requests
import folium
import nest_asyncio
import logging
from folium.plugins import HeatMap
from geopy import *
from flask import Flask, render_template, request

# Apply nest_asyncio to allow Flask to run inside Jupyter
nest_asyncio.apply()

app = Flask(__name__)

MAP_API_KEY = 'kgftgJ5E83XWr8BSC6VcXR8r0lNI3xjD'  # TomTom API key
WEATHER_API_KEY = 'e36ba1d01c70152cb5a016d0a8b6fc80'  # OpenWeatherMap API key

# Function to get weather information
def get_weather(lat, lon):
    url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric'
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200:
        temp = data['main']['temp']
        description = data['weather'][0]['description']
        return f"{temp}°C, {description}"
    else:
        return "Weather data not available"


# Function to convert the name of place to longitude and latitude
def get_coordinates(place_name):
    try:
        # Initialize the geolocator
        geolocator = Nominatim(user_agent="geo_locator")
        
        # Get location information
        location = geolocator.geocode(place_name)
        if location:
            return location.latitude, location.longitude
        else:
            return "Place not found. Please check the name and try again."
    except Exception as e:
        return f"An error occurred: {e}"


# Route for the home page
@app.route('/')
def index():
    return render_template('index.html') 


# Route to handle the form submission and display the map
@app.route('/get_map', methods=['POST'])
def get_map():
    # Get the names of the start and end location
    start_place_name = request.form['start_place_name']
    end_place_name = request.form['end_place_name']
    try:
        start_lat, start_lon = get_coordinates(start_place_name)
        end_lat, end_lon = get_coordinates(end_place_name)
    except Exception as e:
        return render_template('index.html', error_message="Incorrect location")

    # Get the weather data for start and end location
    start_weather = get_weather(start_lat, start_lon)
    end_weather = get_weather(end_lat, end_lon)

    # Fetch route data from TomTom API
    url = f'https://api.tomtom.com/routing/1/calculateRoute/{start_lat},{start_lon}:{end_lat},{end_lon}/json'
    params = {
        'key': MAP_API_KEY,
        'avoid': 'motorways',
        'traffic': 'true',
        'instructionsType': 'text',
        'routeType': 'fastest'
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        try:
            data = response.json()

            # Extract route points and details
            if 'routes' in data and len(data['routes']) > 0:
                route_points = [
                    (point['latitude'], point['longitude'])
                    for point in data['routes'][0]['legs'][0]['points']
                ]
                # Extract distance (in meters) and convert to kilometers
                route_distance = data['routes'][0]['summary']['lengthInMeters'] / 1000  # in kilometers
            else:
                return "No route data available."

            # Create the map centered at the start location
            my_map = folium.Map(location=[start_lat, start_lon], zoom_start=6)

            # Add start and end markers with weather information
            folium.Marker(
                [start_lat, start_lon],
                tooltip=f"Start: {start_weather}",
                popup=f"Starting Point: {start_place_name}<br>Weather: {start_weather}",
                icon=folium.Icon(color="green")
            ).add_to(my_map)

            folium.Marker(
                [end_lat, end_lon],
                tooltip=f"End: {end_weather}",
                popup=f"Destination: {end_place_name}<br>Weather: {end_weather}",
                icon=folium.Icon(color="red")
            ).add_to(my_map)

            # Add polyline for the route
            folium.PolyLine(
                route_points,
                color="blue",
                weight=5,
                opacity=0.7,
                tooltip="Route"
            ).add_to(my_map)

            # Adjust zoom to fit both start and end points
            my_map.fit_bounds([[start_lat, start_lon], [end_lat, end_lon]])

            # Add a heatmap to visualize start and end points
            HeatMap(
                data=[[start_lat, start_lon], [end_lat, end_lon]],
                radius=10
            ).add_to(my_map)

            # Add new location button
            button_html = '''
            <form action='/' method="GET">
            <div style="position: absolute; top: 10px; right: 10px; z-index:9999; background-color:white; padding:10px; border:1px solid black; border-radius:5px;">
                <button style="padding: 5px 10px; font-size: 14px;" type='submit'>New Location!</button>
            </div>
            </form>
            '''
            my_map.get_root().html.add_child(folium.Element(button_html))

            # Create legend
            legend_html = f"""
            <div style="position: fixed; bottom: 50px; left: 50px; width: 300px; height: 200px; 
                        background-color: rgba(255, 255, 255, 0.7); z-index:9999; font-size:14px; 
                        border:1px solid black; padding: 10px;">
                <b>Legend</b><br>
                <i style="background:green; width:10px; height:10px; display:inline-block;"></i> Start: {start_place_name}
                <i style="background:green; display:inline-block; padding-left: 10px;">Weather: {start_weather}</i><br>
                <i style="background:red; width:10px; height:10px; display:inline-block;"></i> End: {end_place_name}
                <i style="background:red; display:inline-block; padding-left: 10px;">Weather: {end_weather}</i><br>
                <i style="background:blue; width:10px; height:10px; display:inline-block;"></i> Route<br>
                <b>Distance:</b> {route_distance:.2f} km
            </div>
            """
            my_map.get_root().html.add_child(folium.Element(legend_html))

            # Save the map to the templates folder
            my_map.save("templates/map.html")

            return render_template('map.html')

        except Exception as e:
            return f"Error processing route data: {str(e)}"
    else:
        return f"Error fetching route data: HTTP {response.status_code} - {response.reason}"


# Run Flask without the reloader
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", use_reloader=False)
