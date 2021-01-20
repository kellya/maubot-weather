# weather
A simple [maubot](https://github.com/maubdlkfjalsdkfjt/maubot) (which was copied from the echobot) that gets the weather from [wttr.in](http://wttr.in) and returns the text to the chat
## Usage
* `!weather` - Reply with the weather based on the server's location
* `!weather <location>` - Reply with the location for the specified <location> where
<location> can be an airport code, or a city

## Requirements
Make sure the environment you are running this in has requests installed.  This can usually be accomplished by running `pip install requests`.  If you don't, maubot will output "ModuleNotFoundError: No module named 'requests'" and your bot server will die
