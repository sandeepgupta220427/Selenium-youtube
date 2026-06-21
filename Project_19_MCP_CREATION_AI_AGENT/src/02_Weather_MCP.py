from fastmcp import FastMCP
import urllib.request
import json


mcp = FastMCP("Weather")

@mcp.tool()
def get_weather(city: str) -> dict:
    """Get current weather for any city. Returns temperature, condition, humidity."""
    try:
        url = f"https://wttr.in/{city}?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "MCP-Weather/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        current = data["current_condition"][0]
        return {
            "city": city,
            "temp_c": current["temp_C"],
            "temp_f": current["temp_F"],
            "condition": current["weatherDesc"][0]["value"],
            "humidity": current["humidity"] + "%",
            "wind_kmph": current["windspeedKmph"],
            "feels_like_c": current["FeelsLikeC"],
        }
    except Exception as e:
        return {"error": f"Could not fetch weather for '{city}': {str(e)}"}


if __name__ == "__main__":
    mcp.run()