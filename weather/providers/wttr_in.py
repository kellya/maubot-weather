"""
Weather provider implementation for wttr.in
"""

from re import search, sub
from typing import Dict, Optional, Union
from urllib.parse import urlencode

from yarl import URL

from .base import WeatherProvider
from ..weather import WeatherData, MoonPhaseData


class WttrInProvider(WeatherProvider):
    """Weather provider implementation for wttr.in"""

    def __init__(self, http_client):
        self.http = http_client
        self._service_url = "https://wttr.in"

    @property
    def name(self) -> str:
        return "wttr.in"

    @property
    def supports_images(self) -> bool:
        return True

    def _build_url(
        self, location: str, options: Dict[str, Union[int, str]] = None
    ) -> URL:
        """Build URL for wttr.in API"""
        base_url = URL(self._service_url).with_path(location)
        if not options:
            return base_url

        querystring = sub(r"=(?:(?=&)|$)", "", urlencode(options))
        return base_url.update_query(querystring)

    async def get_weather(
        self, location: str, units: str = None, language: str = None, show_plus_sign: bool = False
    ) -> WeatherData:
        """Get weather data from wttr.in"""
        options = {}
        if language:
            options["lang"] = language
        if units:
            options[units] = ""

        # Add format=3 for one-line output
        query_options = options.copy()
        query_options["format"] = 3

        url = self._build_url(location, query_options)
        response = await self.http.get(url)
        content = await response.text()

        # Parse the response from wttr.in
        location_match = search(r"^(.+):", content)
        extracted_location = location_match.group(1) if location_match else location

        # Remove the location prefix for the condition text
        condition_text = content.replace(f"{extracted_location}:", "").strip()
        
        # Process + signs in temperature data based on preference
        # Handle wttr.in format which is typically "+XX°C, condition" or "-XX°C, condition"
        condition_parts = condition_text.split(',', 1)  # Split at first comma
        
        if len(condition_parts) >= 1 and '+' in condition_parts[0] and not show_plus_sign:
            # Replace '+' in the temperature part only if show_plus_sign is False
            cleaned_temp = condition_parts[0].replace('+', '')
            
            if len(condition_parts) > 1:
                # Re-join with the rest of the condition text
                cleaned_condition = f"{cleaned_temp},{condition_parts[1]}"
            else:
                cleaned_condition = cleaned_temp
                
            # Use the cleaned condition text
            condition_text = cleaned_condition
            
        # Ensure there are no leading commas in the condition text

        provider_link = str(self._build_url(location, options))

        return WeatherData(
            location=extracted_location,
            temperature="",  # wttr.in format=3 combines temp with condition
            condition=condition_text,
            provider_link=provider_link,
        )

    async def get_weather_image(
        self, location: str, units: str = None, language: str = None
    ) -> Optional[bytes]:
        """Get weather image from wttr.in"""
        options = {}
        if language:
            options["lang"] = language
        if units:
            options[units] = ""

        image_url = self._build_url(f"{location}.png", options)
        response = await self.http.get(image_url)

        if response.status == 200:
            return await response.read()
        return None

    async def get_moon_phase(self) -> MoonPhaseData:
        """Get moon phase data from wttr.in"""
        # Associate the utf-8 character with the name of the phase
        phase_char = {
            "new moon": "🌑",
            "waxing crescent": "🌒",
            "first quarter": "🌓",
            "waxing gibbous": "🌔",
            "full moon": "🌕",
            "waning gibbous": "🌖",
            "last quarter": "🌗",
            "waning crescent": "🌘",
        }

        url = URL(self._service_url).update_query({"format": "j1"})
        response = await self.http.get(url)

        # get the JSON data
        moon_phase_json = await response.json()

        # pull out the "moon_phase"
        moon_phase = moon_phase_json["weather"][0]["astronomy"][0]["moon_phase"]
        moon_phase_illum = moon_phase_json["weather"][0]["astronomy"][0][
            "moon_illumination"
        ]

        # get the character associated with the current phase
        moon_phase_char = phase_char.get(moon_phase.lower(), "")

        return MoonPhaseData(
            phase=moon_phase, illumination=moon_phase_illum, icon=moon_phase_char
        )
