"""
Maubot to get weather from multiple providers and post in matrix chat
"""

from re import IGNORECASE, Match, search, sub
from typing import Dict, List, Optional, Protocol, Type, Union

from maubot import Plugin, MessageEvent
from maubot.handlers import command
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper

from .models import WeatherData, MoonPhaseData
from .providers import WeatherProvider, WttrInProvider, TestProvider
from .userprefs import UserPreferencesManager





class Config(BaseProxyConfig):
    """Configuration class"""

    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("show_link")
        helper.copy("default_location")
        helper.copy("show_image")
        helper.copy("default_units")
        helper.copy("default_language")
        helper.copy("weather_provider")
        helper.copy("show_plus_sign")  # Option to show + sign in temperature


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
        # Only use prefs if not set by command
        if not self._stored_units:
            self._stored_units = prefs['units']
        if not self._stored_language:
            self._stored_language = prefs['language']
        try:
            weather_data = await self._current_provider.get_weather(
                parsed_location,
                units=self._stored_units,
                language=self._stored_language,
                show_plus_sign=prefs.get('show_plus_sign', False),
            )
            # Remove provider_link if user doesn't want to show it
            if not prefs.get('show_link', False):
                weather_data.provider_link = None
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
            "To change the weather provider, use: `!weather provider <name>`\n\n"
            "To see available providers, use: `!weather provider`\n\n"
            "To set your own preferences, use: `!weather pref <option> <value>`\n\n"
            "To view your preferences, use: `!weather pref`\n\n"
            "To clear your preferences, use: `!weather pref clear`\n\n"
        )

    @command.new(name="moon", help="Get the moon phase")
    async def moon_phase_handler(self, evt: MessageEvent) -> None:
        """Get the lunar phase and respond in chat, respecting user preferences."""
        user_id = evt.sender
        prefs = await self._userprefs.load_preferences_with_defaults(user_id, self.config, self._providers)
        provider_name = prefs.get('provider', 'wttr.in')
        self._current_provider = self._providers.get(provider_name, self._providers['wttr.in'])
        self._stored_language = prefs.get('language', '')
        self._stored_units = prefs.get('units', '')
        try:
            # If future providers support language/units for moon, pass them here
            moon_data = await self._current_provider.get_moon_phase()
            await evt.respond(moon_data.get_formatted_message())
        except Exception as e:
            await evt.respond(f"Error getting moon phase: {str(e)}")

    def _parse_location(self, location: str = "") -> str:
        """Parse location string and extract units and language (robustly)"""
        if not location:
            return ""
            
        original_location = location
        has_only_options = True
            
        # Extract units (u:m, u:M, u:u)
        # More flexible pattern to match different formats users might use
        unit_match = search(r"\b[uU]:\s*([mMu])\b|\b[uU]([mMu])\b", location)
        if unit_match:
            # Use the first non-None group
            self._stored_units = unit_match.group(1) if unit_match.group(1) else unit_match.group(2)
            # Remove the unit specification with a more flexible pattern
            location = sub(r"\b[uU]:\s*[mMu]\b|\b[uU][mMu]\b", "", location)
            
        # Extract language (l:xx, l:xx-yy)
        # More flexible pattern to match different formats users might use
        lang_match = search(r"\b[lL]:\s*([a-zA-Z\-]+)\b|\b[lL]([a-zA-Z\-]+)\b", location)
        if lang_match:
            # Use the first non-None group
            self._stored_language = lang_match.group(1) if lang_match.group(1) else lang_match.group(2)
            # Remove the language specification with a more flexible pattern
            location = sub(r"\b[lL]:\s*[a-zA-Z\-]+\b|\b[lL][a-zA-Z\-]+\b", "", location)
            
        # Remove extra spaces and commas at ends
        location = location.strip(" ,")
        
        # Check if the original input contained only options (units/language) and no actual location
        if location == "" and original_location != "":
            # If we had input but it's now empty after removing options, return empty string
            # to signal that we should use the default location
            return ""
            
        self._stored_location = location
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
        valid_options = ["location", "units", "language", "show_image", "show_link", "show_plus_sign", "provider"]
        if option is None or (isinstance(option, str) and option.strip() == ""):
            prefs = await self._userprefs.load_preferences_with_defaults(user_id, self.config, self._providers)
            user_row = await self._userprefs.get_preferences(user_id)
            user_set = set()
            if user_row:
                if user_row.location: user_set.add('location')
                if user_row.units: user_set.add('units')
                if user_row.language: user_set.add('language')
                if user_row.show_image is not None: user_set.add('show_image')
                if user_row.show_link is not None: user_set.add('show_link')
                if user_row.show_plus_sign is not None: user_set.add('show_plus_sign')
                if user_row.provider: user_set.add('provider')
            msg_lines = ["Your preferences (including defaults):\n"]
            for k, v in prefs.items():
                if k in user_set:
                    msg_lines.append(f"**{k}: {v}** (set by you)")
                else:
                    msg_lines.append(f"{k}: {v} (server default)")
            msg = "\n\n".join(msg_lines)
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
        if option in ("show_image", "show_link", "show_plus_sign"):
            value = value.lower() in ("1", "true", "yes", "on")
        await self._userprefs.save_preference(user_id, option, value)
        await evt.respond(f"Preference '{option}' set to '{value}' for you.")


    def _reset_stored_values(self) -> None:
        """Reset stored location, units and language"""
        self._stored_language = ""
        self._stored_location = ""
        self._stored_units = ""
