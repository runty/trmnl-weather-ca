# TRMNL Canadian Weather Forecast

A TRMNL recipe showing current conditions, 24-hour hourly forecast with precipitation probability bars, and 7-day forecast. Data direct from Environment Canada API — no server or GitHub Actions needed.

## Features

- **Current conditions** — temperature, condition, wind, humidity with color weather icon
- **24-hour hourly forecast** — two rows of 12 hours with temps, weather icons, and precipitation probability bars
- **7-day daily forecast** — day name, weather icon, high/low temps
- **Color weather icons** from Environment Canada GIFs (blue rain, yellow sun — renders on color e-ink)
- **844 Canadian weather stations** supported — just enter your station ID
- **Direct API polling** — no GitHub Pages/Actions needed, TRMNL polls EC API directly
- Refreshes **every hour**

## Setup

### 1. Create a Private Plugin on TRMNL
1. Plugins > Private Plugin
2. Strategy: **Polling**
3. Polling URL: `https://api.weather.gc.ca/collections/citypageweather-realtime/items/{{station}}?f=json&lang=en`
4. Paste `form_fields.yml` into Custom Fields
5. Enter your station ID (e.g. `bc-96` for Richmond)
6. Paste templates into markup tabs (shared, full, half horizontal, half vertical, quadrant)
7. Save and **Force Refresh**

### Finding your station ID
1. Go to [weather.gc.ca](https://weather.gc.ca)
2. Search for your city
3. The station ID is in the URL — e.g. `weather.gc.ca/en/location/index.html?coords=49.15,-123.16` → look up the ID in the API

Common station IDs:
| City | ID |
|------|-----|
| Vancouver | bc-74 |
| Richmond | bc-96 |
| Toronto | on-128 |
| Montreal | qc-147 |
| Calgary | ab-52 |
| Edmonton | ab-50 |
| Ottawa | on-118 |
| Winnipeg | mb-38 |
| Halifax | ns-19 |

## Layouts

### Full (800x480)
Current conditions banner. 24-hour forecast in two rows with precipitation bars. 7-day forecast at bottom.

### Half Horizontal (800x240)
Current conditions left. 7-day forecast right.

### Half Vertical (400x480)
Current temp top. 12-hour forecast with precipitation bars. 7-day compact bottom.

### Quadrant (400x240)
Current conditions and 3-day forecast.

## Data Source

Environment Canada GeoMet-OGC-API (`api.weather.gc.ca`). Free, anonymous, no API key required. TRMNL polls the API directly — no intermediary server needed.

## Plugin Icon

Use the current condition icon from the title bar, or: `https://weather.gc.ca/weathericons/30.gif`
