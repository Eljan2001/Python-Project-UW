{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "5d4aa06c",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      " * Serving Flask app '__main__'\n",
      " * Debug mode: on\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.\n",
      " * Running on http://127.0.0.1:5000\n",
      "Press CTRL+C to quit\n"
     ]
    }
   ],
   "source": [
    "import folium\n",
    "import requests\n",
    "from flask import Flask, render_template, request\n",
    "\n",
    "app = Flask(__name__)\n",
    "\n",
    "YOUR_API_KEY = 'kgftgJ5E83XWr8BSC6VcXR8r0lNI3xjD'  # TomTom API key\n",
    "WEATHER_API_KEY = 'e36ba1d01c70152cb5a016d0a8b6fc80'  # OpenWeatherMap API key\n",
    "\n",
    "# Function to get weather information\n",
    "def get_weather(lat, lon):\n",
    "    url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric'\n",
    "    response = requests.get(url)\n",
    "    data = response.json()\n",
    "    if response.status_code == 200:\n",
    "        temp = data['main']['temp']\n",
    "        description = data['weather'][0]['description']\n",
    "        return f\"{temp}°C, {description}\"\n",
    "    else:\n",
    "        return \"Weather data not available\"\n",
    "\n",
    "# Route for the home page\n",
    "@app.route('/')\n",
    "def index():\n",
    "    return render_template('index.html')  # Renders the input form\n",
    "\n",
    "# Route to handle the form submission and display the map\n",
    "@app.route('/get_map', methods=['POST'])\n",
    "def get_map():\n",
    "    # Get coordinates from the user input\n",
    "    start_lat = float(request.form['start_lat'])\n",
    "    start_lon = float(request.form['start_lon'])\n",
    "    end_lat = float(request.form['end_lat'])\n",
    "    end_lon = float(request.form['end_lon'])\n",
    "\n",
    "    # Get weather data for start and end locations\n",
    "    start_weather = get_weather(start_lat, start_lon)\n",
    "    end_weather = get_weather(end_lat, end_lon)\n",
    "\n",
    "    # TomTom API request for route data\n",
    "    url = f'https://api.tomtom.com/routing/1/calculateRoute/{start_lat},{start_lon}:{end_lat},{end_lon}/json'\n",
    "    params = {'key': YOUR_API_KEY, 'avoid': 'motorways', 'traffic': 'true', 'instructionsType': 'text', 'routeType': 'fastest'}\n",
    "    response = requests.get(url, params=params)\n",
    "\n",
    "    if response.status_code == 200:\n",
    "        data = response.json()\n",
    "        route_points = [(point['latitude'], point['longitude']) for point in data['routes'][0]['legs'][0]['points']]\n",
    "        \n",
    "        # Create the map centered around the start location\n",
    "        my_map = folium.Map(location=[start_lat, start_lon], zoom_start=6)\n",
    "\n",
    "        # Add markers with weather info\n",
    "        folium.Marker([start_lat, start_lon], tooltip=f\"Start: Weather: {start_weather}\").add_to(my_map)\n",
    "        folium.Marker([end_lat, end_lon], tooltip=f\"End: Weather: {end_weather}\").add_to(my_map)\n",
    "\n",
    "        # Add polyline for the route\n",
    "        folium.PolyLine(route_points, color=\"blue\", weight=5, opacity=0.7).add_to(my_map)\n",
    "\n",
    "        # Save the map to the templates folder\n",
    "        my_map.save(\"templates/map.html\")\n",
    "\n",
    "        return render_template('map.html')\n",
    "    else:\n",
    "        return \"Error in fetching route data\"\n",
    "\n",
    "# Allow Flask to work in Jupyter Notebook\n",
    "import nest_asyncio\n",
    "nest_asyncio.apply()\n",
    "\n",
    "if __name__ == '__main__':\n",
    "    app.run(debug=True, use_reloader=False)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "3491d0df",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.4"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
