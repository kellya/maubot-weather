[![build status](https://build.arachnitech.com/badges/maubot-weather.png)](https://build.arachnitech.com/#/builders/2) [![latest Release](https://img.shields.io/github/v/release/kellya/maubot-weather)](https://github.com/kellya/maubot-weather/releases) [![Latest in dev](https://img.shields.io/github/v/tag/kellya/maubot-weather?label=latest%20%28dev%29)](https://github.com/kellya/maubot-weather/tree/develop)

# weather
A simple [maubot](https://github.com/maubot/maubot) (which was based on the echobot) that gets the weather from [wttr.in](http://wttr.in) and returns the text to the chat

## Usage
* `!weather` - Reply with the weather based on the default config value
* `!weather <location>` - Reply with the location for the specified <location> where
<location> can be an airport code, or a city
* `!weather <location> u:[u|m|M]` - As above, but specify unit of measure (see
    below)
* `!moon` - Display lunar phase information

### Units
The unit is directly passed to the wttr.in, so the option specified must match
what wttr.in expects.

Valid units are as follows:

u  - USCS (used by default in US)
m  - metric (SI) (used by default everywhere except US)
M  - metric (SI), but show wind speed in m/s

(taken from https://github.com/chubin/wttr.in)


## Examples

### !weather
Entering `!weather` in the chat will display the default server location setting
and display the single-line version of the weather from wttr.in.
   
![oneline](https://raw.githubusercontent.com/kellya/maubot-weather/develop/docs/images/weather_oneline.png)

If the `show_image` setting is `true` in the settings, the bot will return the
png image of the current weather with the forecast

![image_weather_oneline](https://raw.githubusercontent.com/kellya/maubot-weather/develop/docs/images/show_image_true.png)

### !moon
Entering the `!moon` command in the chat will display a oneline version of the
lunar phase:

![image_moon](https://raw.githubusercontent.com/kellya/maubot-weather/develop/docs/images/moon.png)


## Installation

1. Download the current `com.arachnitech.weather-vX.Y.Z.mbp` file from the
   [Releases](https://github.com/kellya/maubot-weather/releases) page.
2. Follow the [Maubot](https://docs.mau.fi/maubot/usage/basic.html) instructions
   which boils down to:

   1. In your maubot manager, click the plus sign next to plugins
   2. Upload the plugin you downloaded from step 1 above

## Upgrading

Basically the same as the Installation, except since you already have it
installed:

1. Click on the `com.arachnitech.weather` under the plugins
2. Upload the new version

## Development

If you would like to mess with the source code to add your own stuff, or clean
up some python atrocity I have committed, please clone/fork this repo and have at it.

I have built everything using poetry, so the easiest path is:
1. clone/fork the repo
2. run `poetry shell`
3. run `poetry install` to add all the dependent packages
4. Make changes.

## Chat

[![chat](https://shields.io/matrix/maubot-weather:arachnitech.com.svg?server_fqdn=matrix.arachnitech.com)](https://matrix.to/#/#maubot-weather:arachnitech.com)

I have created a dedicated [#maubot-weather:arachnitech.com](https://matrix.to/#/#maubot-weather:arachnitech.com) channel.  I also follow the #maubot:maubot.xyz channel.
