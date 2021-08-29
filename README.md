![build status](https://build.arachnitech.com/badges/maubot-weather.png) ![latest Release](https://img.shields.io/github/v/release/kellya/maubot-weather) ![Latest in dev](https://img.shields.io/github/v/tag/kellya/maubot-weather?label=latest%20%28dev%29)

# weather
A simple [maubot](https://github.com/maubot/maubot) (which was based on the echobot) that gets the weather from [wttr.in](http://wttr.in) and returns the text to the chat

## Installation

1. Download the current `com.arachnitech.weather-vX.X.X.mbp` file from the
   [Releases](https://github.com/kellya/maubot-weather/releases) page.
2. Follow the [Maubot](https://docs.mau.fi/maubot/usage/basic.html) instructions
   which boils down to:

   1. In your maubot manager, click the plus sign next to plugins
   2. Upload the plugin you downloaded from step 1 above

## Usage
* `!weather` - Reply with the weather based on the default config value
* `!weather <location>` - Reply with the location for the specified <location> where
<location> can be an airport code, or a city
* `!moon` - Display lunar phase information

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
