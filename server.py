from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from datetime import datetime, timedelta
import json

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
OPENMETEO_API_BASE = "https://api.open-meteo.com/v1"
GEOCODING_API_BASE = "https://geocoding-api.open-meteo.com/v1"
USER_AGENT = "weather-app/1.0"

# Weather code mappings for better descriptions
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

# Helper function to make a request to the Open-Meteo API
async def make_openmeteo_request(url: str) -> dict[str, Any] | None:
    """Make a request to the Open-Meteo API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

@mcp.tool()
async def get_current_weather(latitude: float, longitude: float) -> str:
    """Get current weather for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    
    url = f"{OPENMETEO_API_BASE}/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,is_day,showers,cloud_cover,wind_speed_10m,wind_direction_10m,pressure_msl,snowfall,precipitation,relative_humidity_2m,apparent_temperature,rain,weather_code,surface_pressure,wind_gusts_10m"
    
    data = await make_openmeteo_request(url)

    if not data:
        return "Unable to fetch current weather data for this location."

    # Format the weather data as a readable string
    current = data.get('current', {})
    
    weather_report = f"""Current Weather:
Temperature: {current.get('temperature_2m', 'N/A')}°C
Feels like: {current.get('apparent_temperature', 'N/A')}°C
Humidity: {current.get('relative_humidity_2m', 'N/A')}%
Wind Speed: {current.get('wind_speed_10m', 'N/A')} km/h
Wind Direction: {current.get('wind_direction_10m', 'N/A')}°
Pressure: {current.get('pressure_msl', 'N/A')} hPa
Cloud Cover: {current.get('cloud_cover', 'N/A')}%
Precipitation: {current.get('precipitation', 'N/A')} mm
Rain: {current.get('rain', 'N/A')} mm
Snow: {current.get('snowfall', 'N/A')} mm
Weather: {WEATHER_CODES.get(current.get('weather_code'), 'Unknown')}"""

    return weather_report


@mcp.tool()
async def search_locations(query: str) -> str:
    """Search for locations by name to get coordinates.
    
    Args:
        query: Location name to search for (e.g., "Paris", "New York", "Tokyo")
    """
    url = f"{GEOCODING_API_BASE}/search?name={query}&count=5&language=en&format=json"
    
    data = await make_openmeteo_request(url)
    if not data or not data.get('results'):
        return f"No locations found for '{query}'"
    
    locations = []
    for result in data['results']:
        name = result.get('name', 'Unknown')
        country = result.get('country', 'Unknown')
        admin1 = result.get('admin1', '')
        lat = result.get('latitude', 0)
        lon = result.get('longitude', 0)
        
        location_str = f"{name}"
        if admin1:
            location_str += f", {admin1}"
        location_str += f", {country} (Lat: {lat:.4f}, Lon: {lon:.4f})"
        locations.append(location_str)
    
    return "Found locations:\n" + "\n".join(locations)


@mcp.tool()
async def get_weather_forecast(latitude: float, longitude: float, days: int = 7) -> str:
    """Get weather forecast for a location.
    
    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
        days: Number of days to forecast (1-16, default: 7)
    """
    days = max(1, min(days, 16))  # Limit to valid range
    
    url = f"{OPENMETEO_API_BASE}/forecast?latitude={latitude}&longitude={longitude}&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,wind_direction_10m_dominant&forecast_days={days}&timezone=auto"
    
    data = await make_openmeteo_request(url)
    if not data:
        return "Unable to fetch forecast data for this location."
    
    daily = data.get('daily', {})
    dates = daily.get('time', [])
    
    forecast_lines = [f"Weather Forecast for {days} days:"]
    
    for i in range(len(dates)):
        date = dates[i]
        weather_code = daily.get('weather_code', [])[i] if i < len(daily.get('weather_code', [])) else None
        temp_max = daily.get('temperature_2m_max', [])[i] if i < len(daily.get('temperature_2m_max', [])) else 'N/A'
        temp_min = daily.get('temperature_2m_min', [])[i] if i < len(daily.get('temperature_2m_min', [])) else 'N/A'
        precipitation = daily.get('precipitation_sum', [])[i] if i < len(daily.get('precipitation_sum', [])) else 'N/A'
        wind_speed = daily.get('wind_speed_10m_max', [])[i] if i < len(daily.get('wind_speed_10m_max', [])) else 'N/A'
        
        weather_desc = WEATHER_CODES.get(weather_code, 'Unknown') if weather_code else 'Unknown'
        
        forecast_lines.append(f"{date}: {weather_desc}, {temp_min}°C - {temp_max}°C, Rain: {precipitation}mm, Wind: {wind_speed}km/h")
    
    return "\n".join(forecast_lines)


@mcp.tool()
async def get_weather_alerts(latitude: float, longitude: float) -> str:
    """Check for weather alerts and warnings for a location.
    
    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # Get current and forecast data to analyze for potential alerts
    url = f"{OPENMETEO_API_BASE}/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m,precipitation,weather_code&hourly=temperature_2m,precipitation,wind_speed_10m&forecast_days=2&timezone=auto"
    
    data = await make_openmeteo_request(url)
    if not data:
        return "Unable to fetch weather alert data for this location."
    
    alerts = []
    current = data.get('current', {})
    
    # Check current conditions for alerts
    temp = current.get('temperature_2m')
    wind_speed = current.get('wind_speed_10m')
    precipitation = current.get('precipitation')
    weather_code = current.get('weather_code')
    
    if temp is not None:
        if temp >= 35:
            alerts.append("🔥 HEAT WARNING: Extreme temperature detected")
        elif temp <= -20:
            alerts.append("🥶 COLD WARNING: Extreme cold temperature detected")
    
    if wind_speed is not None and wind_speed >= 60:
        alerts.append("💨 WIND WARNING: High wind speeds detected")
    
    if precipitation is not None and precipitation >= 20:
        alerts.append("🌧️ PRECIPITATION WARNING: Heavy precipitation detected")
    
    if weather_code in [95, 96, 99]:
        alerts.append("⛈️ THUNDERSTORM WARNING: Thunderstorm conditions detected")
    
    if not alerts:
        return "✅ No weather alerts or warnings for this location."
    
    return "Weather Alerts:\n" + "\n".join(alerts)


@mcp.tool()
async def get_weather_by_city(city_name: str) -> str:
    """Get current weather for a city by name.
    
    Args:
        city_name: Name of the city (e.g., "Paris", "New York", "Tokyo")
    """
    # First, search for the city to get coordinates
    geocoding_url = f"{GEOCODING_API_BASE}/search?name={city_name}&count=1&language=en&format=json"
    
    location_data = await make_openmeteo_request(geocoding_url)
    if not location_data or not location_data.get('results'):
        return f"City '{city_name}' not found. Please check the spelling and try again."
    
    # Get the first result
    location = location_data['results'][0]
    latitude = location.get('latitude')
    longitude = location.get('longitude')
    name = location.get('name')
    country = location.get('country')
    
    if latitude is None or longitude is None:
        return f"Could not get coordinates for '{city_name}'"
    
    # Get weather data
    weather_url = f"{OPENMETEO_API_BASE}/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,is_day,cloud_cover,wind_speed_10m,wind_direction_10m,pressure_msl,precipitation,relative_humidity_2m,apparent_temperature,weather_code"
    
    weather_data = await make_openmeteo_request(weather_url)
    if not weather_data:
        return f"Unable to fetch weather data for {name}, {country}."
    
    current = weather_data.get('current', {})
    weather_code = current.get('weather_code')
    weather_desc = WEATHER_CODES.get(weather_code, 'Unknown') if weather_code else 'Unknown'
    
    weather_report = f"""Weather in {name}, {country}:
Weather: {weather_desc}
Temperature: {current.get('temperature_2m', 'N/A')}°C
Feels like: {current.get('apparent_temperature', 'N/A')}°C
Humidity: {current.get('relative_humidity_2m', 'N/A')}%
Wind Speed: {current.get('wind_speed_10m', 'N/A')} km/h
Wind Direction: {current.get('wind_direction_10m', 'N/A')}°
Pressure: {current.get('pressure_msl', 'N/A')} hPa
Cloud Cover: {current.get('cloud_cover', 'N/A')}%
Precipitation: {current.get('precipitation', 'N/A')} mm"""

    return weather_report


@mcp.tool()
async def compare_weather_cities(city1: str, city2: str) -> str:
    """Compare current weather between two cities.
    
    Args:
        city1: Name of the first city
        city2: Name of the second city
    """
    # Get weather for both cities
    weather1 = await get_weather_by_city(city1)
    weather2 = await get_weather_by_city(city2)
    
    if "not found" in weather1.lower() or "unable to fetch" in weather1.lower():
        return f"Could not get weather data for {city1}: {weather1}"
    
    if "not found" in weather2.lower() or "unable to fetch" in weather2.lower():
        return f"Could not get weather data for {city2}: {weather2}"
    
    comparison = f"""Weather Comparison:

📍 {city1.upper()}:
{weather1}

📍 {city2.upper()}:
{weather2}"""

    return comparison


@mcp.tool()
async def get_historical_weather(latitude: float, longitude: float, date: str) -> str:
    """Get historical weather data for a specific date.
    
    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
        date: Date in YYYY-MM-DD format (must be in the past)
    """
    try:
        # Validate date format
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD format."
    
    # Check if date is in the past
    today = datetime.now().date()
    request_date = datetime.strptime(date, '%Y-%m-%d').date()
    
    if request_date >= today:
        return "Historical weather data is only available for past dates."
    
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={latitude}&longitude={longitude}&start_date={date}&end_date={date}&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max&timezone=auto"
    
    data = await make_openmeteo_request(url)
    if not data:
        return f"Unable to fetch historical weather data for {date}."
    
    daily = data.get('daily', {})
    if not daily.get('time'):
        return f"No historical data available for {date}."
    
    weather_code = daily.get('weather_code', [None])[0]
    temp_max = daily.get('temperature_2m_max', ['N/A'])[0]
    temp_min = daily.get('temperature_2m_min', ['N/A'])[0]
    precipitation = daily.get('precipitation_sum', ['N/A'])[0]
    wind_speed = daily.get('wind_speed_10m_max', ['N/A'])[0]
    
    weather_desc = WEATHER_CODES.get(weather_code, 'Unknown') if weather_code else 'Unknown'
    
    historical_report = f"""Historical Weather for {date}:
Weather: {weather_desc}
Temperature: {temp_min}°C - {temp_max}°C
Precipitation: {precipitation} mm
Max Wind Speed: {wind_speed} km/h"""

    return historical_report


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')