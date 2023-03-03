""" maubot to get the weather from wttr.in and post in matrix chat """

from typing import Type
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


class WeatherBot(Plugin):
    """maubot plugin class to get the weather and respond in a chat"""

    async def start(self) -> None:
        await super().start()
        self.config.load_and_update()

    @classmethod
    def get_config_class(cls) -> Type[BaseProxyConfig]:
        return Config

    def get_location(self, location=None) -> str:
        """Return a cleaned-up location name"""
        if not location:
            location = self.config["default_location"]
        location = location.replace(", ", "_")
        location = location.replace(" ", "+")
        return location

    @command.new(
        name="weather", help="Get weather info",
        arg_fallthrough=False, require_subcommand=False
    )
    @command.argument("location", pass_raw=True)
    async def weather_handler(self, evt: MessageEvent, location=None) -> None:
        """Listens for `!weather` and returns a message with the result of
        a call to wttr.in for the location specified by `!weather <location>`
        or by the config file if no location is given"""
        units = ""  # default to nothing so that response works even if default is unset

        if self.config["default_units"]:
            # If units are specified in the config, use them
            units = f"&{self.config['default_units']}"
        if "u:" in location:
            # If the location has units specified, attempt to use them
            location, custom_unit = location.split("u:")
            if custom_unit in ["u", "m", "M"]:
                units = f"&{custom_unit}"
        location = self.get_location(location.strip())

        resp = await self.http.get(f"http://wttr.in/{location}?format=3{units}")
        weather = await resp.text()
        message = weather
        if self.config["show_link"]:
            link = f'[(wttr.in)]({URL("https://wttr.in") / location})'
            message += link
        if weather.startswith("Unknown location; please try"):
            message += (
                " | Note: "
                "An 'unknown location' likely indicates "
                "an issue with wttr.in obtaining geolocation information. "
                "This issue will probably resolve itself, so sit "
                "tight and look out the window until it does"
            )
        await evt.respond(message)
        if self.config["show_image"]:
            wttr_url = "http://wttr.in"
            wttr = URL(f"{wttr_url}/{location}.png?{units}")
            resp = await self.http.get(wttr)
            if resp.status == 200:
                data = await resp.read()
                filename = "weather.png"
                uri = await self.client.upload_media(
                    data, mime_type="image/png", filename="filename"
                )
                await self.client.send_image(
                    evt.room_id,
                    url=uri,
                    file_name=filename,
                )
            else:
                await evt.respond(f"error getting location {location}")

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

        resp = await self.http.get(URL(f"http://wttr.in/{self.get_location}?format=j1"))
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
