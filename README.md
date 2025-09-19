# MCP Weather Server

A Model Context Protocol (MCP) server that provides comprehensive weather information using the Open-Meteo API. This server offers real-time weather data, forecasts, historical weather information, and location-based weather services.

## Features

- **Current Weather**: Get real-time weather conditions for any location
- **Weather Forecasts**: Multi-day weather forecasts (up to 16 days)
- **Location Search**: Find coordinates for cities worldwide
- **Weather Alerts**: Check for weather warnings and extreme conditions
- **City Weather**: Get weather by city name with automatic geocoding
- **Weather Comparison**: Compare weather between two cities
- **Historical Weather**: Access past weather data for any date

## Installation

1. Clone this repository or download the files
2. Install dependencies using uv (recommended) or pip:

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install httpx mcp[cli]
```

## Usage

### Running the Server

The server uses stdio transport for MCP communication:

```bash
python server.py
```

### Available Tools

#### 1. `get_current_weather(latitude, longitude)`
Get current weather conditions for specific coordinates.

**Parameters:**
- `latitude` (float): Latitude of the location
- `longitude` (float): Longitude of the location

**Example Response:**
```
Current Weather:
Temperature: 22.5°C
Feels like: 24.1°C
Humidity: 65%
Wind Speed: 12.5 km/h
Wind Direction: 180°
Pressure: 1013.2 hPa
Cloud Cover: 40%
Weather: Partly cloudy
```

#### 2. `search_locations(query)`
Search for locations by name to get their coordinates.

**Parameters:**
- `query` (string): Location name to search for

**Example:**
```python
search_locations("Nantes")
# Returns coordinates and details for Nantes, France
```

#### 3. `get_weather_forecast(latitude, longitude, days)`
Get weather forecast for a location.

**Parameters:**
- `latitude` (float): Latitude of the location
- `longitude` (float): Longitude of the location  
- `days` (int): Number of days to forecast (1-16, default: 7)

#### 4. `get_weather_alerts(latitude, longitude)`
Check for weather alerts and warnings.

**Parameters:**
- `latitude` (float): Latitude of the location
- `longitude` (float): Longitude of the location

**Alert Types:**
- 🔥 Heat warnings (≥35°C)
- 🥶 Cold warnings (≤-20°C)
- 💨 Wind warnings (≥60 km/h)
- 🌧️ Precipitation warnings (≥20mm)
- ⛈️ Thunderstorm warnings

#### 5. `get_weather_by_city(city_name)`
Get current weather for a city by name.

**Parameters:**
- `city_name` (string): Name of the city

**Example:**
```python
get_weather_by_city("Nantes")
# Returns current weather for Nantes, France with automatic geocoding
```

#### 6. `compare_weather_cities(city1, city2)`
Compare current weather between two cities.

**Parameters:**
- `city1` (string): Name of the first city
- `city2` (string): Name of the second city

#### 7. `get_historical_weather(latitude, longitude, date)`
Get historical weather data for a specific date.

**Parameters:**
- `latitude` (float): Latitude of the location
- `longitude` (float): Longitude of the location
- `date` (string): Date in YYYY-MM-DD format (must be in the past)

## Weather Data Sources

This server uses the [Open-Meteo API](https://open-meteo.com/), which provides:
- High-quality weather data from multiple meteorological services
- Global coverage with high resolution
- No API key required
- Free for non-commercial use

### Supported Weather Parameters

- Temperature (current, min, max, feels-like)
- Precipitation (rain, snow, total)
- Wind (speed, direction, gusts)
- Atmospheric pressure
- Humidity
- Cloud cover
- Weather conditions (clear, cloudy, rain, snow, etc.)

## Error Handling

The server includes comprehensive error handling:
- Network timeouts and connection errors
- Invalid coordinates or city names
- API rate limiting
- Invalid date formats
- Missing or incomplete data

## Dependencies

- **httpx**: For making HTTP requests to the Open-Meteo API
- **mcp**: Model Context Protocol framework
- **Python 3.13+**: Required Python version

## Configuration

The server uses these default settings:
- API timeout: 30 seconds
- User-Agent: "weather-app/1.0"
- Transport: stdio (for MCP communication)

## License

This project is open source. Please check the Open-Meteo API terms of service for data usage guidelines.

## Contributing

Feel free to submit issues and enhancement requests!

## API Limits

The Open-Meteo API has the following considerations:
- Free tier has reasonable limits for personal use
- For commercial use, consider their paid plans
- Forecast data: up to 16 days
- Historical data: available for past dates
- Multiple locations can be queried

## Examples

### Basic Weather Query
```python
# Get current weather for Nantes, France coordinates (47.2184, -1.5536)
await get_current_weather(47.2184, -1.5536)
```

### City-based Weather
```python
# Get weather by city name
await get_weather_by_city("Nantes")
```

### Weather Comparison
```python
# Compare weather between cities
await compare_weather_cities("Nantes", "Paris")
```

### Historical Data
```python
# Get historical weather for Nantes
await get_historical_weather(47.2184, -1.5536, "2024-01-15")
```
