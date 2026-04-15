# TRMNL Canadian Weather Forecast

A TRMNL recipe showing current conditions, 24-hour hourly forecast with precipitation probability bars, and 6-day forecast. Data direct from Environment Canada API — no server needed.

![Weather](https://weather.gc.ca/weathericons/12.gif)

## Features

- **Current conditions** — temperature, condition, wind speed/direction, humidity with color weather icon
- **24-hour hourly forecast** — 3 columns x 8 rows with time, weather icon, temperature, and precipitation probability bar (blue = rain chance, yellow = dry)
- **6-day daily forecast** — day name, weather icon, high/low temperatures in aligned table
- **Color weather icons** from Environment Canada GIFs — renders on color e-ink displays (6/7-color ACeP)
- **Text symbol fallback** (☀ ⛅ 🌧 ❄ ⛈ ☾) for icon codes without GIFs
- **844 Canadian weather stations** supported — enter your station ID
- **Direct API polling** — TRMNL polls Environment Canada API directly, no GitHub Pages/Actions needed
- **Local timezone** — hourly times converted from UTC using TRMNL user offset
- **Sans-serif font** (Inter via Google Fonts)
- Refreshes **every hour**

## Layouts

### Full (800x480)
Top banner: current conditions (icon, temp, condition, wind, humidity) on the left, 6-day forecast table on the right. Below: 24-hour hourly forecast in 3 columns of 8 rows, each showing time, icon, temp, and blue/yellow precipitation bar.

### Half Horizontal (800x240)
Current conditions on the left, 7-day forecast on the right.

### Half Vertical (400x480)
Current temp at top, 12-hour forecast with precipitation bars, 7-day compact at bottom.

### Quadrant (400x240)
Current conditions and 3-day forecast.

## Setup

### 1. Create a Private Plugin on TRMNL
1. Plugins > Private Plugin
2. Strategy: **Polling**
3. Polling URL: `https://api.weather.gc.ca/collections/citypageweather-realtime/items/{{station}}?f=json&lang=en`
4. Paste `form_fields.yml` into Custom Fields
5. Enter your station ID (e.g. `bc-96` for Richmond)
6. Paste templates into markup tabs (shared, full, half horizontal, half vertical, quadrant)
7. Save and **Force Refresh**

No GitHub repo, Pages, or Actions needed. TRMNL polls the EC API directly.

### Finding your station ID

Go to [weather.gc.ca](https://weather.gc.ca), search for your city, and note the station ID.

Common station IDs:

| City | ID |
|------|-----|
| Vancouver | bc-74 |
| Richmond | bc-96 |
| Victoria | bc-85 |
| Calgary | ab-52 |
| Edmonton | ab-50 |
| Winnipeg | mb-38 |
| Toronto | on-128 |
| Ottawa | on-118 |
| Montreal | qc-147 |
| Halifax | ns-19 |
| St. John's | nl-24 |
| Whitehorse | yt-16 |
| Yellowknife | nt-24 |

## Data Source

Environment Canada GeoMet-OGC-API (`api.weather.gc.ca`). Free, anonymous, no API key required. Single endpoint returns current conditions, 24-hour hourly forecasts, and 10-day daily forecasts per station.

## Project Structure

```
trmnl-weather-ca/
├── templates/
│   ├── shared.liquid          # Inter font, CSS classes, Liquid assigns
│   ├── full.liquid            # Current + 6-day + 24-hour hourly
│   ├── half_horizontal.liquid # Current + 7-day
│   ├── half_vertical.liquid   # Current + 12-hour + 7-day
│   └── quadrant.liquid        # Current + 3-day
├── form_fields.yml            # Station ID field + author bio
├── settings.yml               # Plugin metadata
└── README.md
```

## Technical Notes

- EC API returns UTC timestamps; converted to local time via `trmnl.user.utc_offset`
- Icon codes 0-9 don't have GIFs on EC CDN; fall back to text weather symbols
- All EC GIF icons forced to uniform 30x30px via CSS (native sizes vary)
- Precipitation bars: blue (`#2266cc`) = rain probability, yellow (`#ffcc00`) = dry remainder
- Nested Liquid paths (e.g. `properties.currentConditions.temperature.value.en`) work because TRMNL exposes the full JSON response
- `{% assign %}` shortcuts in shared tab keep templates readable

## Plugin Icon

`https://weather.gc.ca/weathericons/30.gif`
