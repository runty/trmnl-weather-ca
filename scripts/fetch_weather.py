#!/usr/bin/env python3
"""Fetch Canadian weather data from Environment Canada API for TRMNL."""

import json
import math
import os
import sys
from datetime import datetime, timezone
from urllib.error import URLError
from urllib.request import Request, urlopen

EC_BASE = "https://api.weather.gc.ca/collections/citypageweather-realtime/items"

# Weather icon codes to text symbols
# https://weather.gc.ca/weathericons/
ICON_MAP = {
    0: "☀", 1: "☀", 2: "⛅", 3: "⛅", 4: "⛅",    # sunny, mostly sunny, partly cloudy
    5: "⛅", 6: "☁", 7: "⛅", 8: "⛅", 9: "🌧",     # cloudy mix, overcast, showers
    10: "☁", 11: "🌧", 12: "🌧", 13: "🌧",           # cloudy, rain, rain/drizzle
    14: "🌧", 15: "🌧", 16: "❄", 17: "❄", 18: "❄",  # freezing rain, snow
    19: "⛈", 20: "☁", 21: "☁", 22: "⛅", 23: "☁",   # thunderstorm, haze, fog
    24: "❄", 25: "❄", 26: "❄", 27: "🌧", 28: "🌧",  # blowing snow, ice, drizzle
    29: "☁", 30: "☾", 31: "☾", 32: "☾", 33: "☾",    # not used, clear night, cloudy night
    34: "☾", 35: "☾", 36: "🌧", 37: "🌧", 38: "🌧",  # night showers, night rain
    39: "⛈", 40: "❄", 41: "⛈", 42: "⛈", 43: "⛈",   # night thunder, tornado, hurricane
    44: "💨",                                           # windy/funnel
}


def fetch_json(url):
    req = Request(url, headers={"User-Agent": "TRMNL-Weather-CA/1.0"})
    with urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def icon_symbol(code):
    """Convert EC icon code to a text weather symbol."""
    try:
        return ICON_MAP.get(int(code), "?")
    except (ValueError, TypeError):
        return "?"


def icon_url(code):
    """Get the EC weather icon GIF URL for color displays."""
    try:
        c = int(code)
        if 10 <= c <= 44:
            return f"https://weather.gc.ca/weathericons/{c}.gif"
    except (ValueError, TypeError):
        pass
    return ""


def parse_current(cc):
    """Parse current conditions."""
    temp_val = cc.get("temperature", {}).get("value", {}).get("en")
    temp = round(temp_val) if temp_val is not None else None

    wind_chill = cc.get("windChill", {}).get("value", {}).get("en")
    humidex = cc.get("humidex", {}).get("value", {}).get("en")
    # Only use wind chill if temp is below 10, only use humidex if temp is above 20
    if wind_chill is not None and temp_val is not None and temp_val <= 10:
        feels_like = wind_chill
    elif humidex is not None and temp_val is not None and temp_val >= 20:
        feels_like = humidex
    else:
        feels_like = None

    return {
        "temp": temp,
        "temp_raw": temp_val,
        "condition": cc.get("condition", {}).get("en", ""),
        "icon": icon_symbol(cc.get("iconCode", {}).get("value")),
        "icon_img": icon_url(cc.get("iconCode", {}).get("value")),
        "icon_code": cc.get("iconCode", {}).get("value"),
        "humidity": cc.get("relativeHumidity", {}).get("value", {}).get("en"),
        "wind_speed": cc.get("wind", {}).get("speed", {}).get("value", {}).get("en"),
        "wind_dir": cc.get("wind", {}).get("direction", {}).get("value", {}).get("en", ""),
        "wind_gust": cc.get("wind", {}).get("gust", {}).get("value", {}).get("en"),
        "pressure": cc.get("pressure", {}).get("value", {}).get("en"),
        "feels_like": round(feels_like) if feels_like is not None else None,
        "dewpoint": cc.get("dewpoint", {}).get("value", {}).get("en"),
    }


def parse_hourly(hfg):
    """Parse hourly forecasts."""
    hours = []
    for h in hfg.get("hourlyForecasts", [])[:24]:
        ts = h.get("timestamp", "")
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            hour_label = dt.strftime("%-I%p").lower()
        except (ValueError, AttributeError):
            hour_label = ""

        temp = h.get("temperature", {}).get("value", {}).get("en")
        lop = h.get("lop", {}).get("value", {}).get("en", 0)

        hours.append({
            "time": hour_label,
            "hour": dt.hour if dt else 0,
            "temp": temp,
            "condition": h.get("condition", {}).get("en", ""),
            "icon": icon_symbol(h.get("iconCode", {}).get("value")),
            "icon_img": icon_url(h.get("iconCode", {}).get("value")),
            "pop": lop if lop else 0,
            "pop_height": min(max(int(lop or 0), 0), 100),
            "wind_speed": h.get("wind", {}).get("speed", {}).get("value", {}).get("en"),
            "wind_dir": h.get("wind", {}).get("direction", {}).get("value", {}).get("en", ""),
        })
    return hours


def parse_daily(fg):
    """Parse daily forecasts into day pairs (day/night)."""
    raw = fg.get("forecasts", [])
    days = []
    i = 0
    while i < len(raw) and len(days) < 7:
        fc = raw[i]
        period_name = fc.get("period", {}).get("textForecastName", {}).get("en", "")
        temps = fc.get("temperatures", {}).get("temperature", [])

        high = None
        low = None
        for t in temps:
            cls = t.get("class", {})
            cls_en = cls.get("en", cls) if isinstance(cls, dict) else cls
            val = t.get("value", {}).get("en")
            if cls_en == "high":
                high = val
            elif cls_en == "low":
                low = val

        abbr = fc.get("abbreviatedForecast", {})
        condition = abbr.get("textSummary", {}).get("en", "")
        icon_code = abbr.get("icon", {}).get("value", abbr.get("iconCode", {}).get("value"))
        pop = abbr.get("pop", {}).get("value", {}).get("en", "")

        # Determine day name
        day_name = period_name.replace(" night", "").replace("Tonight", "Tonight")
        # Get short day name (Mon, Tue, etc.)
        short_name = day_name[:3] if len(day_name) > 3 else day_name

        # Check if next entry is the night counterpart
        if "night" not in period_name.lower() and "tonight" not in period_name.lower():
            # This is a daytime forecast, check for night pair
            if i + 1 < len(raw):
                night_fc = raw[i + 1]
                night_temps = night_fc.get("temperatures", {}).get("temperature", [])
                for t in night_temps:
                    cls = t.get("class", {})
                    cls_en = cls.get("en", cls) if isinstance(cls, dict) else cls
                    if cls_en == "low":
                        low = t.get("value", {}).get("en")
                i += 2
            else:
                i += 1
        else:
            # Night-only entry (e.g., "Tonight")
            i += 1

        days.append({
            "name": period_name,
            "short": short_name,
            "high": high,
            "low": low,
            "condition": condition,
            "icon": icon_symbol(icon_code),
            "icon_img": icon_url(icon_code),
            "pop": pop if pop else "",
        })

    return days


def fetch_weather(lat, lon):
    """Fetch weather for the nearest city page station to given coordinates."""
    # Try progressively wider search until we find stations
    for radius in [0.3, 0.5, 1.0, 2.0]:
        bbox = f"{lon-radius},{lat-radius},{lon+radius},{lat+radius}"
        url = f"{EC_BASE}?f=json&lang=en&limit=10&bbox={bbox}"
        data = fetch_json(url)
        if data.get("features"):
            break
    data = fetch_json(url)

    features = data.get("features", []) if data else []
    if not features:
        raise ValueError(f"No weather stations found near {lat},{lon}")

    # Find nearest station
    best = None
    best_dist = float("inf")
    for f in features:
        coords = f.get("geometry", {}).get("coordinates", [0, 0])
        dist = math.sqrt((coords[0] - lon) ** 2 + (coords[1] - lat) ** 2)
        if dist < best_dist:
            best_dist = dist
            best = f

    props = best["properties"]
    coords = best["geometry"]["coordinates"]

    return {
        "location": {
            "name": props.get("name", {}).get("en", ""),
            "region": props.get("region", {}).get("en", ""),
            "identifier": props.get("identifier", ""),
            "lat": coords[1],
            "lon": coords[0],
        },
        "current": parse_current(props.get("currentConditions", {})),
        "hourly": parse_hourly(props.get("hourlyForecastGroup", {})),
        "daily": parse_daily(props.get("forecastGroup", {})),
        "sunrise": props.get("riseSet", {}).get("sunrise", {}).get("en", ""),
        "sunset": props.get("riseSet", {}).get("sunset", {}).get("en", ""),
        "warnings": [w.get("description", {}).get("en", "") for w in props.get("warnings", [])],
        "updated": props.get("lastUpdated", ""),
    }


def main():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "api")
    os.makedirs(out_dir, exist_ok=True)

    # Default coordinates - can be overridden by environment variables
    lat = float(os.environ.get("WEATHER_LAT", "43.65"))
    lon = float(os.environ.get("WEATHER_LON", "-79.38"))

    try:
        result = fetch_weather(lat, lon)
        loc = result["location"]
        cur = result["current"]
        print(f"Location: {loc['name']}, {loc['region']}")
        print(f"Current: {cur['temp']}°C {cur['condition']}")
        print(f"Hourly: {len(result['hourly'])} hours")
        print(f"Daily: {len(result['daily'])} days")
    except Exception as e:
        print(f"ERR: {e}", file=sys.stderr)
        sys.exit(1)

    path = os.path.join(out_dir, "weather.json")
    with open(path, "w") as f:
        json.dump(result, f, separators=(",", ":"))

    print(f"Done. Written to {path}")


if __name__ == "__main__":
    main()
