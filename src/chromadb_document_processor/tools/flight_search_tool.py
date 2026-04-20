import json
import os
import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class FlightSearchInput(BaseModel):
    origin: str = Field(description="Departure airport IATA code (e.g., JFK)")
    destination: str = Field(description="Arrival airport IATA code (e.g., LAX)")
    outbound_date: str = Field(description="Departure date in YYYY-MM-DD format")
    return_date: str = Field(default="", description="Return date in YYYY-MM-DD format; leave empty for one-way")


_AIRLINE_FLAGS: dict[str, str] = {
    "japan airlines": "🇯🇵", "all nippon airways": "🇯🇵", "ana": "🇯🇵",
    "singapore airlines": "🇸🇬", "cathay pacific": "🇭🇰",
    "emirates": "🇦🇪", "lufthansa": "🇩🇪", "iberia": "🇪🇸",
    "icelandair": "🇮🇸", "latam airlines": "🇨🇱", "aegean airlines": "🇬🇷",
    "sri lankan airlines": "🇱🇰", "olympic air": "🇬🇷",
}


def _badge(airline: str) -> str:
    return _AIRLINE_FLAGS.get(airline.lower(), "✈️")


def _minutes_to_duration(minutes) -> str:
    if not isinstance(minutes, (int, float)):
        return str(minutes)
    h, m = divmod(int(minutes), 60)
    return f"{h}h {m:02d}m"


class FlightSearchTool(BaseTool):
    name: str = "Flight Search"
    description: str = (
        "Search for flights via SerpAPI Google Flights. "
        "Provide IATA airport codes and dates in YYYY-MM-DD format. "
        "Returns a JSON object with a 'flights' array."
    )
    args_schema: type[BaseModel] = FlightSearchInput

    def _run(self, origin: str, destination: str, outbound_date: str, return_date: str = "") -> str:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return json.dumps({"error": "SERPAPI_API_KEY not set.", "flights": []})

        params = {
            "engine": "google_flights",
            "departure_id": origin.upper(),
            "arrival_id": destination.upper(),
            "outbound_date": outbound_date,
            "currency": "USD",
            "hl": "en",
            "api_key": api_key,
            "type": "1" if return_date else "2",
        }
        if return_date:
            params["return_date"] = return_date

        try:
            response = requests.get("https://serpapi.com/search", params=params, timeout=15)
            data = response.json()
        except Exception as e:
            return json.dumps({"error": f"Request failed: {e}", "flights": []})

        if "error" in data:
            return json.dumps({"error": f"SerpAPI error: {data['error']}", "flights": []})

        options = data.get("best_flights", []) or data.get("other_flights", [])
        if not options:
            return json.dumps({"flights": []})

        flights = []
        for i, option in enumerate(options[:5], 1):
            legs = option.get("flights", [])
            if not legs:
                continue

            first_leg = legs[0]
            last_leg = legs[-1]
            airline = first_leg.get("airline", "Unknown")
            dep = first_leg.get("departure_airport", {})
            arr = last_leg.get("arrival_airport", {})

            stops_count = len(legs) - 1
            if stops_count == 0:
                stops_label = "Nonstop"
            else:
                via = ", ".join(
                    leg.get("arrival_airport", {}).get("id", "")
                    for leg in legs[:-1]
                    if leg.get("arrival_airport", {}).get("id")
                )
                stops_label = f"{stops_count} stop · {via}" if via else f"{stops_count} stop"

            flights.append({
                "id": f"live-{i}",
                "airline": airline,
                "badge": _badge(airline),
                "flightNumber": first_leg.get("flight_number", ""),
                "from": dep.get("id", origin.upper()),
                "to": arr.get("id", destination.upper()),
                "departure": dep.get("time", ""),
                "arrival": arr.get("time", ""),
                "duration": _minutes_to_duration(option.get("total_duration")),
                "stops": stops_label,
                "price": option.get("price", 0),
                "class": first_leg.get("travel_class", "Economy"),
                "perks": [],
            })

        return json.dumps({"flights": flights})
