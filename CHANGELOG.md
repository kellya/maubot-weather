# CHANGELOG


## v0.6.1 (2025-04-25)


## v0.6.0 (2025-04-25)


## v0.5.0 (2025-04-25)


## v0.4.2 (2025-04-25)

### Bug Fixes

- Cleanup formatting to remove + on positive temps
  ([`e628a69`](https://github.com/kellya/maubot-weather/commit/e628a69536ccef3f0deba5a426531090bd296ce5))

- Cleanup leading comma on output
  ([`0a1abbc`](https://github.com/kellya/maubot-weather/commit/0a1abbc69bd6588fae613e92894cd40496f41ae8))

### Features

- Add user prefs db
  ([`9648282`](https://github.com/kellya/maubot-weather/commit/9648282883b05ddcacbb4a9438ef78ab51e27f29))


## v0.4.1 (2023-05-01)


## v0.4.0 (2023-03-11)

### Build System

- Fix build requirements
  ([`9f4f932`](https://github.com/kellya/maubot-weather/commit/9f4f932c06db026b1f61bd0a076e12d1d9167da1))

- Fix missing dep for markupsafe
  ([`1f9e12b`](https://github.com/kellya/maubot-weather/commit/1f9e12be37c042a2083641b3519fc0a136feacf1))

### Refactoring

- Clean-up long line in help output
  ([`6fec749`](https://github.com/kellya/maubot-weather/commit/6fec74997358b6f63277ec5b892f17072f362de6))


## v0.3.1 (2022-03-04)

### Bug Fixes

- Correct the missing unit on image generation
  ([`1285de4`](https://github.com/kellya/maubot-weather/commit/1285de4549bfa88da6204d4a648dd98982262bbd))

### Documentation

- Add linebreaks for units section
  ([`89cb55c`](https://github.com/kellya/maubot-weather/commit/89cb55ce69b9fb85932d5fb5b1edc8d3f47a6656))

- Update changelog
  ([`a114358`](https://github.com/kellya/maubot-weather/commit/a1143583b366c4c4b0d95bc7cce831e12dafc839))

- Update readme with units info
  ([`dd84a39`](https://github.com/kellya/maubot-weather/commit/dd84a39520da04deb13ef224c607406ae84c3137))


## v0.3.0 (2022-03-04)

### Features

- Allow changing units of measure for reporting
  ([`8c7c74e`](https://github.com/kellya/maubot-weather/commit/8c7c74e1efddfe289147fd7129e046639ece7028))

Added "default_units" to the config file. This globally overrides/forces the setting which can be:
  metric(m) US(u) or metric except wind(M).

These values may also be specified at the end of a `!weather location` call from a chat prefixed by
  'u:" to indicate you are specifying the unit to use. So you can do something like:

!weather Chicago, Il u:m

To get the weather in Chicago reported in Celcius.

closes #3


## v0.2.4 (2022-02-18)

### Bug Fixes

- Correct issue with location error response
  ([`5916469`](https://github.com/kellya/maubot-weather/commit/59164698d3931bd863f3593d0a26e72ce960f6a9))

### Documentation

- Update changelong vor 0.2.3
  ([`fa268df`](https://github.com/kellya/maubot-weather/commit/fa268dfa23c7cb4c225d4ed0b987fa938ecac689))


## v0.2.3 (2021-08-30)

### Bug Fixes

- Wrap all url calls with yarl.URL to sanitize the URLs passed
  ([`885045c`](https://github.com/kellya/maubot-weather/commit/885045cdccee9f2580c7e7bda68c5be454868908))

### Build System

- Correct issue with the move into a subdir
  ([`db7de27`](https://github.com/kellya/maubot-weather/commit/db7de27dd8c840780045089af816ad3805fe5961))

### Chores

- Remove __pycache__ from git
  ([`d48c23e`](https://github.com/kellya/maubot-weather/commit/d48c23e6867038949374ff7e206605e1a9d4e2ab))

### Documentation

- Add some examples to the readme
  ([`af6e199`](https://github.com/kellya/maubot-weather/commit/af6e19943db059cdcdab2f197672de36c983416f))

- Fix image urls in the examples section
  ([`ca9705e`](https://github.com/kellya/maubot-weather/commit/ca9705e43eb300035f8f23e2ec8683c22e9dcda5))

### Refactoring

- Move location to a fuction
  ([`fb2cf6c`](https://github.com/kellya/maubot-weather/commit/fb2cf6c19b888ec658bc15b17558343bffe51f50))


## v0.2.2 (2021-08-30)

### Bug Fixes

- Rewrite the moon phase to only make one call to get json and generate the correct character
  instaed of making 2 calls
  ([`543f670`](https://github.com/kellya/maubot-weather/commit/543f670a07a835d48924b1c5299d7dbece154278))

### Build System

- Add changelog to auto-publish to github release
  ([`cf3cc0c`](https://github.com/kellya/maubot-weather/commit/cf3cc0cf5bdca6ea8e9f25b0c57530f3876d3f74))

doc: add chat section to README.md

### Chores

- Add build status to badges
  ([`79256d5`](https://github.com/kellya/maubot-weather/commit/79256d5f7c9ecd583be73ad8a67246487930735e))

- Add build status to badges
  ([`4631faf`](https://github.com/kellya/maubot-weather/commit/4631fafa0040b117c3bc838d75fada87460742e1))

- Add some badges to the doc page
  ([`3f4582b`](https://github.com/kellya/maubot-weather/commit/3f4582b64522f3f8bb2184d262f83cc508e72b44))

- Update changelog
  ([`ed318f8`](https://github.com/kellya/maubot-weather/commit/ed318f8cea027321ae631dfc0b6438a1f9bf1531))


## v0.2.1 (2021-08-29)

### Bug Fixes

- Correct space to plus in location
  ([`2cdbee2`](https://github.com/kellya/maubot-weather/commit/2cdbee2138e59a0f3024cf369c2d51be81e1fd09))

feat: add more details to moon information line


## v0.2.0 (2021-08-29)

### Features

- Add command to get the lunar phase
  ([`70087a3`](https://github.com/kellya/maubot-weather/commit/70087a38181274f5d94a2874dbcfb11356bdb6a8))

refactor: consistently used resp (instead of a few places that were rsp) for response

### Refactoring

- Move weather into its own module to clean up basedir and make future expansion easier
  ([`090c60d`](https://github.com/kellya/maubot-weather/commit/090c60db3f9aaacd1407756989daa69f14b654af))


## v0.1.0 (2021-08-29)

### Build System

- Add pylint to makefile
  ([`3ea4e17`](https://github.com/kellya/maubot-weather/commit/3ea4e17d65152d43704aeb44b69c0fb8715c57f7))

style: add recommended pylint clean-ups

- Updated makefile to check tags to determine release
  ([`d1f7773`](https://github.com/kellya/maubot-weather/commit/d1f777381951117dfaa2ab1cb15c9b4706bb6f5d))

### Chores

- Fix default location format as it seems to not quite work right
  ([`35e56f0`](https://github.com/kellya/maubot-weather/commit/35e56f041fa518e0747ffb4c7c73576270237e53))

- Make show_image default to false
  ([`2bb43d4`](https://github.com/kellya/maubot-weather/commit/2bb43d419ce61950f1ccb985ac17b3839885677b))

### Code Style

- Clean up some docstrings and the error note, added show_image helper.copy()
  ([`2f9e032`](https://github.com/kellya/maubot-weather/commit/2f9e032cecf74cecae0272e7576797ea6013ebd9))

### Features

- Add ability to display the png forecast version of the weather
  ([`a164030`](https://github.com/kellya/maubot-weather/commit/a1640309b3b049b45dd90b8019ecef0a89712377))

### Refactoring

- Clean up redundant logic for location given or not
  ([`0a6d483`](https://github.com/kellya/maubot-weather/commit/0a6d483407d2ccc88092737314ba5f6fb0d58523))

refactor: moved link variable under the if that it is referenced so it doesn't pointlessly build a
  link for nothing

chore: add default show_image value to base-config


## v0.0.16 (2021-08-28)

### Bug Fixes

- Added a check for the 'unknown location' to show a message if that occurs
  ([`c42e2c1`](https://github.com/kellya/maubot-weather/commit/c42e2c15f483d2dbd4b511f8f91adc44634d71d3))

### Chores

- Setup all the dev stuff in poetry
  ([`475f19a`](https://github.com/kellya/maubot-weather/commit/475f19af46eef581b96420f1cb7c420e71b84ebe))

test: corrected makefile


## v0.0.15 (2021-07-14)


## v0.0.14 (2021-02-24)


## v0.0.13 (2021-01-20)


## v0.0.9 (2021-01-20)


## v0.0.8 (2021-01-20)
