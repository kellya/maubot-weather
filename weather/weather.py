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
        # using yarl kind of made this function useless, but I'm leaving it
        # for now.
        if not location:
            location = self.config["default_location"]
        return location

    async def post_image(self, location, evt):
        wttr_url = "http://wttr.in"
        wttr = URL(f"{wttr_url}/{location}.png")
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
            await evt.respond("error getting location " + wttr)

    @command.new(
        name="weather",
        help="Get the weather",
        require_subcommand=False,
        arg_fallthrough=False,
    )
    @command.argument("location", pass_raw=True)
    async def weather_handler(self, evt: MessageEvent, location=None) -> None:
        """Listens for !weather and returns a message with the result of
        a call to wttr.in for the location specified by !weather <location>
        or by the config file if no location is given"""
        location = self.get_location(location)

        resp = await self.http.get(f"http://wttr.in/{location}?format=3")
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
            self.post_image(location, evt)

    @weather_handler.subcommand(name="help", help="display help text")
    async def show_help(self, evt: MessageEvent) -> None:
        """Display general help information"""
        await evt.respond(
            """
Uses wttr.in to get the weather and respond. If you don't specify a
location, it will use the server setting for `default_location`

Otherwise, you may specify the location by name:

!weather Chicago

or by Airport Code

!weather SFO

You may also get the lunar phase information by sending

!moon
                          """
        )

    @weather_handler.subcommand(name="show_default", help="show the default location")
    async def get_default_location(self, evt: MessageEvent) -> None:
        """Respond with the value of the default_location setting"""
        await evt.respond(self.config["default_location"])

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
