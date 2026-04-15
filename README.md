# TRMNL Canadian Weather Forecast

A TRMNL recipe showing current conditions, 24-hour hourly forecast with precipitation probability bars, and 7-day forecast. Data from Environment Canada.

## Features

- **Current conditions** — temperature, condition, feels-like, wind, humidity
- **24-hour hourly forecast** — two rows of 12 hours with temps, weather icons, and precipitation probability bars
- **7-day daily forecast** — day name, weather icon, high/low temps
- **Color weather icons** from Environment Canada (renders on color e-ink displays)
- **Text symbol fallback** for monochrome displays
- **Coordinate-based** — finds nearest Environment Canada weather station
- Updated **every hour** via GitHub Actions

## Layouts

### Full (800x480)
Current conditions banner at top. 24-hour forecast in two rows with precipitation bars. 7-day forecast at bottom.

### Half Horizontal (800x240)
Current conditions on the left. 7-day forecast on the right.

### Half Vertical (400x480)
Current temp at top. 12-hour forecast with precipitation bars. 7-day compact at bottom.

### Quadrant (400x240)
Current conditions and 3-day forecast.

## Setup

### 1. Fork this repository

### 2. Set your coordinates
Edit `.github/workflows/update-data.yml` and change `WEATHER_LAT` and `WEATHER_LON` to your location:
```yaml
env:
  WEATHER_LAT: "43.65"    # Your latitude
  WEATHER_LON: "-79.38"   # Your longitude
```

### 3. Enable GitHub Pages
Settings > Pages > Source: **GitHub Actions**

### 4. Run the data fetch
Actions > "Update Weather Data" > Run workflow

### 5. Create a Private Plugin on TRMNL
1. Plugins > Private Plugin
2. Strategy: **Polling**
3. Polling URL: `https://YOUR_USERNAME.github.io/trmnl-weather-ca/weather.json`
4. Paste `form_fields.yml` into Custom Fields
5. Paste templates into markup tabs
6. Save and **Force Refresh**

## Data Source

Environment Canada GeoMet-OGC-API (`api.weather.gc.ca`). Free, anonymous, no API key required. Provides city page weather data including current conditions, 24-hour hourly forecasts, and 10-day daily forecasts.

## Plugin Icon

`https://weather.gc.ca/weathericons/30.gif`
