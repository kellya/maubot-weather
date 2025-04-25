"""
Maubot to get weather from multiple providers and post in matrix chat
"""

from abc import ABC, abstractmethod
from re import IGNORECASE, Match, search, sub
from typing import Dict, List, Optional, Protocol, Type, Union
from urllib.parse import urlencode

from maubot import Plugin, MessageEvent
from maubot.handlers import command
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from yarl import URL

from .userprefs import UserPreferencesManager


class WeatherData:
    """Class to standardize weather data across providers"""

    def __init__(
        self,
        location: str,
        temperature: str,
        condition: str,
        humidity: str = None,
        wind: str = None,
        forecast: str = None,
        image_url: str = None,
        provider_link: str = None,
    ):
        self.location = location
        self.temperature = temperature
        self.condition = condition
        self.humidity = humidity
        self.wind = wind
        self.forecast = forecast
        self.image_url = image_url
        self.provider_link = provider_link

    def get_formatted_message(self) -> str:
        """Return a formatted message with the weather information"""
        message = f"{self.location}: {self.temperature}, {self.condition}"

        if self.humidity:
            message += f", Humidity: {self.humidity}"

        if self.wind:
            message += f", Wind: {self.wind}"

        if self.forecast:
            message += f"\nForecast: {self.forecast}"

        if self.provider_link:
            message += f" ([source]({self.provider_link}))"

        return message


class MoonPhaseData:
    """Class to standardize moon phase data across providers"""

    def __init__(self, phase: str, illumination: str, icon: str = None):
        self.phase = phase
        self.illumination = illumination
        self.icon = icon

    def get_formatted_message(self) -> str:
        """Return a formatted message with the moon phase information"""
        if self.icon:
            return f"{self.icon} {self.phase} ({self.illumination}% Illuminated)"
        return f"{self.phase} ({self.illumination}% Illuminated)"


class WeatherProvider(ABC):
    """Abstract base class for weather providers"""

    @abstractmethod
    async def get_weather(
        self, location: str, units: str = None, language: str = None
    ) -> WeatherData:
        """Get weather data for a location"""
        pass

    @abstractmethod
    async def get_weather_image(
        self, location: str, units: str = None, language: str = None
    ) -> Optional[bytes]:
        """Get weather image for a location, return None if not supported"""
        pass

    @abstractmethod
    async def get_moon_phase(self) -> MoonPhaseData:
        """Get current moon phase data"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get provider name"""
        pass

    @property
    def supports_images(self) -> bool:
        """Whether this provider supports weather images"""
        return False


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
        self, location: str, units: str = None, language: str = None
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


class TestProvider(WeatherProvider):
    """Mock weather provider for testing purposes"""

    def __init__(self, http_client):
        self.http = http_client

    @property
    def name(self) -> str:
        return "test"

    @property
    def supports_images(self) -> bool:
        return False

    async def get_weather(
        self, location: str, units: str = None, language: str = None
    ) -> WeatherData:
        """Return fake weather data for testing"""
        # Generate some simple test data
        temp_unit = "°F" if units == "u" else "°C"
        temperature = f"72{temp_unit}" if units == "u" else f"22{temp_unit}"

        # Customize messages based on language if provided
        greeting = (
            "Sunny day in" if not language or language == "en" else "Día soleado en"
        )

        return WeatherData(
            location=location or "TestCity",
            temperature=temperature,
            condition="Sunny with test clouds",
            humidity="50%",
            wind="5 mph" if units == "u" else "8 km/h",
            forecast=f"{greeting} {location or 'TestCity'}",
            provider_link="https://example.com/test-weather",
        )

    async def get_weather_image(
        self, location: str, units: str = None, language: str = None
    ) -> Optional[bytes]:
        """Test provider doesn't support images"""
        return None

    async def get_moon_phase(self) -> MoonPhaseData:
        """Return fake moon phase data for testing"""
        return MoonPhaseData(phase="Test Moon", illumination="42", icon="🌔")


class Config(BaseProxyConfig):
    """Configuration class"""

    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("show_link")
        helper.copy("default_location")
        helper.copy("show_image")
        helper.copy("default_units")
        helper.copy("default_language")
        helper.copy("weather_provider")  # Add this new config option


class WeatherBot(Plugin):
    """Maubot plugin class to get the weather and respond in a chat."""

    _providers: Dict[str, WeatherProvider]
    _current_provider: WeatherProvider
    _stored_language: str
    _stored_location: str
    _stored_units: str
    _userprefs: UserPreferencesManager

    async def start(self) -> None:
        await super().start()
        self.config.load_and_update()

        # Initialize providers
        self._providers = {
            "wttr.in": WttrInProvider(self.http),
            "test": TestProvider(self.http),
            # Add more providers as they're implemented
            # "openweathermap": OpenWeatherMapProvider(self.http, api_key),
            # "weatherapi": WeatherAPIProvider(self.http, api_key),
        }

        # Set up user preferences manager
        self._userprefs = UserPreferencesManager(self.database, self.log)
        await self._userprefs.init_db()

        # Set current provider from config (will be overridden per-user)
        provider_name = self.config.get("weather_provider", "wttr.in")
        self._current_provider = self._providers.get(
            provider_name, self._providers["wttr.in"]
        )

    @classmethod
    def get_config_class(cls) -> Type[BaseProxyConfig]:
        return Config

    @command.new(
        name="weather",
        help="Get the weather",
        arg_fallthrough=False,
        require_subcommand=False,
    )
    @command.argument("location", pass_raw=True)
    async def weather_handler(self, evt: MessageEvent, location: str) -> None:
        """Listens for `!weather` and returns a message with the weather for the location"""
        self._reset_stored_values()
        user_id = evt.sender
        prefs = await self._userprefs.load_preferences_with_defaults(user_id, self.config, self._providers)
        parsed_location = self._parse_location(location or prefs['location'])
        # Use per-user or default provider
        provider_name = prefs['provider']
        self._current_provider = self._providers.get(provider_name, self._providers["wttr.in"])
        self._stored_units = prefs['units']
        self._stored_language = prefs['language']
        try:
            weather_data = await self._current_provider.get_weather(
                parsed_location,
                units=self._stored_units,
                language=self._stored_language,
            )
            await evt.respond(weather_data.get_formatted_message())
            # Send weather image if enabled and supported
            if (
                prefs['show_image']
                and self._current_provider.supports_images
                and parsed_location
            ):
                await self._send_weather_image(evt, parsed_location)
        except Exception as e:
            await evt.respond(f"Error getting weather: {str(e)}")

    @weather_handler.subcommand("provider", help="Set or view current weather provider")
    @command.argument("provider_name", required=False)
    async def set_provider(self, evt: MessageEvent, provider_name: str = None) -> None:
        """Set or view the current weather provider"""
        user_id = evt.sender
        if not provider_name:
            # List available providers
            providers_list = ", ".join(self._providers.keys())
            current = self._current_provider.name
            await evt.respond(
                f"Current provider: {current}\nAvailable providers: {providers_list}"
            )
            return
        if provider_name not in self._providers:
            await evt.respond(
                f"Unknown provider: {provider_name}. Available providers: {', '.join(self._providers.keys())}"
            )
            return
        self._current_provider = self._providers[provider_name]
        await self._userprefs.save_preference(user_id, 'provider', provider_name)
        await evt.respond(f"Weather provider set to {provider_name} for you.")

    @weather_handler.subcommand("help", help="Usage instructions")
    async def help(self, evt: MessageEvent) -> None:
        """Return help message."""
        await evt.respond(
            "Get information about the weather.\n\n"
            "If the location is not specified, the default location or IP address will be used.\\\n"
            "Otherwise, location can be specified by name:\\\n"
            "`!weather Chicago`\\\n"
            "or by Airport Code:\\\n"
            "`!weather SFO`\n\n"
            "Units may be specified by adding `u:<unit>` at the end of the "
            "location like:\\\n"
            "`!weather Chicago u:m`\\\n"
            "where `<unit>` is one of:"
            "\n\n"
            "* `m`: metric;\n"
            "* `u`: US;\n"
            "* `M`: metric, but wind speed unit is m/s."
            "\n\n"
            "Forecast language can be specified by adding `l:<language-code>` "
            "at the end of the location like:\\\n"
            "`!weather Chicago l:es`.\\\n"
            "\n\n"
            "Options can be combined: `!weather Chicago l:es u:M`."
            "\n\n"
            "To change the weather provider, use: `!weather provider <name>`\n"
            "To see available providers, use: `!weather provider`\n"
            "To set your own preferences, use: `!weather pref <option> <value>`\n"
            "To view your preferences, use: `!weather pref`\n"
            "To clear your preferences, use: `!weather pref clear`\n"
        )

    @command.new(name="moon", help="Get the moon phase")
    async def moon_phase_handler(self, evt: MessageEvent) -> None:
        """Get the lunar phase and respond in chat"""
        try:
            moon_data = await self._current_provider.get_moon_phase()
            await evt.respond(moon_data.get_formatted_message())
        except Exception as e:
            await evt.respond(f"Error getting moon phase: {str(e)}")

    def _parse_location(self, location: str = "") -> str:
        """Parse location string and extract units and language"""
        # This function is now called with already merged user preference as fallback
        if not location:
            return ""
        # Parse units from location
        if "u:" in location:
            match = search(r"(\bu: *(?!l:)(\S+))", location, IGNORECASE)
            if match:
                matches = match.groups()
                unit = matches[1]
                if unit in ("u", "m", "M"):
                    self._stored_units = unit
                location = location.replace(matches[0], "").strip()
        # Parse language from location
        if "l:" in location:
            match = search(r"(\bl: *(?!u:)(\S+))", location, IGNORECASE)
            if match:
                matches = match.groups()
                self._stored_language = matches[1]
                location = location.replace(matches[0], "").strip()
        self._stored_location = location.strip()
        return self._stored_location

    async def _send_weather_image(self, evt: MessageEvent, location: str) -> None:
        """Send weather image to chat if available"""
        image_data = await self._current_provider.get_weather_image(
            location, units=self._stored_units, language=self._stored_language
        )

        if image_data:
            filename = f"{location}.png"
            uri = await self.client.upload_media(
                image_data, mime_type="image/png", filename=filename
            )
            await self.client.send_image(evt.room_id, url=uri, file_name=filename)

    def _config_value(self, name: str) -> str:
        """Get a configuration value with empty string fallback (legacy)"""
        return self.config[name].strip() if self.config[name] is not None else ""

    @weather_handler.subcommand("pref", help="Set, view, or clear your weather preferences")
    @command.argument("option", required=False)
    @command.argument("value", required=False)
    async def user_pref_handler(self, evt: MessageEvent, option: str = None, value: str = None) -> None:
        """Set, view, or clear user preferences."""
        user_id = evt.sender
        valid_options = ["location", "units", "language", "show_image", "provider"]
        if option is None:
            prefs = await self._userprefs.load_preferences_with_defaults(user_id, self.config, self._providers)
            msg = "Your preferences (including defaults):\n" + "\n".join(f"{k}: {v}" for k, v in prefs.items())
            await evt.respond(msg)
            return
        if option == "clear":
            await self._userprefs.clear_preferences(user_id)
            await evt.respond("Your weather preferences have been cleared (server defaults will be used).")
            return
        if option not in valid_options:
            await evt.respond(f"Unknown preference '{option}'. Valid options: {', '.join(valid_options)}")
            return
        if value is None:
            await evt.respond(f"Please provide a value for '{option}'.")
            return
        # Type conversion for booleans
        if option == "show_image":
            value = value.lower() in ("1", "true", "yes", "on")
        await self._userprefs.save_preference(user_id, option, value)
        await evt.respond(f"Preference '{option}' set to '{value}' for you.")

    def _reset_stored_values(self) -> None:
        """Reset stored location, units and language"""
        self._stored_language = ""
        self._stored_location = ""
        self._stored_units = ""
