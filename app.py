
from flask import Flask, render_template, request
import requests

app = Flask(__name__)


# Convert weather code into weather condition
def get_condition(code):

    if code == 0:
        return "Clear Sky ☀️"

    elif code == 1:
        return "Mainly Clear 🌤️"

    elif code == 2:
        return "Partly Cloudy ⛅"

    elif code == 3:
        return "Overcast ☁️"

    elif code in [45, 48]:
        return "Fog 🌫️"

    elif code in [51, 53, 55, 56, 57]:
        return "Drizzle 🌦️"

    elif code in [61, 63, 65, 66, 67, 80, 81, 82]:
        return "Rain 🌧️"

    elif code in [71, 73, 75, 77, 85, 86]:
        return "Snow ❄️"

    elif code in [95, 96, 99]:
        return "Thunderstorm ⛈️"

    else:
        return "Unknown"


# Home page
@app.route("/", methods=["GET", "POST"])
def home():

    weather = None
    forecast = []
    error = None

    if request.method == "POST":

        city = request.form["city"].strip()

        try:

            # Find city coordinates
            geo_url = "https://geocoding-api.open-meteo.com/v1/search"

            geo_response = requests.get(
                geo_url,
                params={
                    "name": city,
                    "count": 1
                },
                timeout=10
            )

            geo_response.raise_for_status()

            geo_data = geo_response.json()

            if not geo_data.get("results"):

                error = "City not found!"

            else:

                location = geo_data["results"][0]

                latitude = location["latitude"]
                longitude = location["longitude"]

                # Get current and 7-day weather
                weather_url = "https://api.open-meteo.com/v1/forecast"

                weather_response = requests.get(
                    weather_url,
                    params={
                        "latitude": latitude,
                        "longitude": longitude,
                        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
                        "forecast_days": 7,
                        "timezone": "auto"
                    },
                    timeout=10
                )

                weather_response.raise_for_status()

                weather_data = weather_response.json()

                # Current weather details
                current = weather_data["current"]

                weather = {
                    "city": location["name"],
                    "temperature": current["temperature_2m"],
                    "humidity": current["relative_humidity_2m"],
                    "wind": current["wind_speed_10m"],
                    "condition": get_condition(current["weather_code"])
                }

                # Seven-day forecast
                daily = weather_data["daily"]

                for i in range(len(daily["time"])):

                    day = {
                        "date": daily["time"][i],
                        "condition": get_condition(
                            daily["weather_code"][i]
                        ),
                        "max_temp": daily["temperature_2m_max"][i],
                        "min_temp": daily["temperature_2m_min"][i]
                    }

                    forecast.append(day)

        except requests.RequestException:

            error = "Unable to connect to the weather service."

        except (KeyError, IndexError, TypeError):

            error = "Unable to get weather information."

    return render_template(
        "index.html",
        weather=weather,
        forecast=forecast,
        error=error
    )


# Run application
if __name__ == "__main__":
    app.run(debug=True)
