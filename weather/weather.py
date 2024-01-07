""" Maubot to get the weather from wttr.in and post in matrix chat """

from re import IGNORECASE, Match, search, sub
from typing import Dict, Optional, Type, Union
from urllib.parse import urlencode

from maubot import Plugin, MessageEvent
from maubot.handlers import command
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from yarl import URL


class Config(BaseProxyConfig):
    """Configuration class"""

    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("show_link")
        helper.copy("default_location")
        helper.copy("show_image")
        helper.copy("default_units")
        helper.copy("default_language")


class WeatherBot(Plugin):
    """Maubot plugin class to get the weather and respond in a chat."""

    _service_url: str = "https://wttr.in"
    _stored_language: str
    _stored_location: str
    _stored_units: str

    async def start(self) -> None:
        await super().start()
        self.config.load_and_update()

    @classmethod
    def get_config_class(cls) -> Type[BaseProxyConfig]:
        return Config

    @command.new(
        name="weather", help="Get the weather",
        arg_fallthrough=False, require_subcommand=False
    )
    @command.argument("location", pass_raw=True)
    async def weather_handler(self, evt: MessageEvent, location: str) -> None:
        """Listens for `!weather` and returns a message with the result of
        a call to wttr.in for the location specified by `!weather <location>`
        or by the config file if no location is given"""
        self._reset_stored_values()
        self._location(location)
        response = await self.http.get(self._url({"format": 4}))
        await evt.respond(self._message(await response.text()))
        await self._image(evt)

    @weather_handler.subcommand("help", help="Usage instructions")
    async def help(self, evt: MessageEvent) -> None:
        """Return help message."""
        await evt.respond(
            "Get information about the weather from "
            "[wttr.in](https://wttr.in).\n\n"
            "If the location is not specified, the IP address will be used by "
            "the server to figure out what the location is.\\\n"
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
            "Available languages are listed on <https://wttr.in/:translation>."
            "\n\n"
            "Options can be combined: `!weather Chicago l:es u:M`."
        )

    @command.new(name="moon", help="Get the moon phase")
    async def moon_phase_handler(
        self,
        evt: MessageEvent,
    ) -> None:
        """Get the lunar phase from wttr.in json and respond in chat"""
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
        self._reset_stored_values()
        resp = await self.http.get(
            self._base_url().update_query({"format": "j1"})
        )
        # get the JSON data
        moon_phase_json = await resp.json()
        # pull out the "moon_phase"
        moon_phase = moon_phase_json["weather"][0]["astronomy"][0]["moon_phase"]
        # get the character associated with the current phase
        moon_phase_char = phase_char[moon_phase.lower()]
        moon_phase_illum = moon_phase_json["weather"][0]["astronomy"][0][
            "moon_illumination"
        ]
        await evt.respond(
            f"{moon_phase_char} {moon_phase} ({moon_phase_illum}% Illuminated)"
        )

    def _base_url(self) -> URL:
        return URL(self._service_url).with_path(self._location())

    def _config_value(self, name: str) -> str:
        return (
            self.config[name].strip()
            if self.config[name] is not None
            else ""
        )

    async def _image(self, event: MessageEvent) -> None:
        if self.config["show_image"] and self._stored_location:
            response = await self.http.get(
                URL(f"{self._base_url()}.png")
                .update_query(self._options_querystring())
            )

            if response.status == 200:
                data = await response.read()
                filename = f"{self._stored_location}.png"
                uri = await self.client.upload_media(
                    data, mime_type="image/png", filename="filename"
                )
                await self.client.send_image(
                    event.room_id, url=uri, file_name=filename
                )
            else:
                await event.respond(
                    f"error getting location {self._stored_location}"
                )

    def _language(self) -> str:
        if self._stored_language == "":
            language = self._config_value("default_language")
            location = self._stored_location

            if "l:" in location:
                match: Optional["Match[str]"] = search(
                    r"(\bl: *(?!u:)(\S+))", location, IGNORECASE
                )

                if match is not None:
                    matches = match.groups()
                    language = matches[1]
                    location = location.replace(matches[0], "")

            self._stored_language = language.strip()
            self._stored_location = location.strip()

        return self._stored_language

    def _location(self, location: str = "") -> str:
        """Return a cleaned-up location name"""
        if self._stored_location == "":
            location = location.strip()
            self._stored_location = (
                location
                if location
                else self._config_value("default_location")
            ).strip()
            self._units()
            self._language()

        return self._stored_location

    def _message(self, content: str) -> str:
        message: str = content
        location_match: Optional["Match[str]"] = search(r'^(.+):', message)

        if self.config["show_link"]:
            message += f"([wttr.in]({self._url()}))"

        if content.startswith("Unknown location; please try"):
            message += (
                " | Note: "
                "An 'unknown location' likely indicates "
                "an issue with wttr.in obtaining geolocation information. "
                "This issue will probably resolve itself, so sit "
                "tight and look out the window until it does"
            )
        elif not self._stored_location and location_match is not None:
            self._stored_location = location_match[1]

        return message

    def _options(self) -> Dict[str, Union[int, str]]:
        options: Dict[str, Union[int, str]] = {}

        if self._stored_language:
            options["lang"] = self._stored_language

        if self._stored_units:
            options[self._stored_units] = ""

        return options

    def _options_querystring(
        self, custom_options: Optional[Dict[str, Union[int, str]]] = None
    ) -> str:
        options = self._options()
        options.update(custom_options if custom_options else {})

        return sub(r'=(?:(?=&)|$)', '', urlencode(options))

    def _reset_stored_values(self) -> None:
        self._stored_language = ''
        self._stored_location = ''
        self._stored_units = ''

    def _units(self) -> str:
        if self._stored_units == "":
            units = self._config_value("default_units")
            location = self._stored_location

            if "u:" in location:
                match: Optional["Match[str]"] = search(
                    r"(\bu: *(?!l:)(\S+))", location, IGNORECASE
                )

                if match is not None:
                    matches = match.groups()
                    custom_unit = matches[1]
                    units = (
                        custom_unit
                        if custom_unit in ("u", "m", "M")
                        else units
                    )
                    location = location.replace(matches[0], "").strip()

            self._stored_location = location.strip()
            self._stored_units = units.strip()

        return self._stored_units

    def _url(
        self, custom_options: Optional[Dict[str, Union[int, str]]] = None
    ) -> str:
        querystring = self._options_querystring(custom_options)

        return (
            f"{self._base_url()}" + (f"?{querystring}" if querystring else "")
        )
