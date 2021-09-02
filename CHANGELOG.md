# Changelog

## v0.2.3 (2021-08-30)

#### Fixes

* wrap all url calls with yarl.URL to sanitize the URLs passed
#### Refactorings

* move location to a fuction
#### Docs

* fix image urls in the examples section
* add some examples to the readme
#### Others

* correct issue with the move into a subdir
* remove __pycache__ from git

Full set of changes: [`v0.2.2...v0.2.3`](https://github.com/kellya/maubot-weather/compare/v0.2.2...v0.2.3)

## v0.2.2 (2021-08-30)

#### Fixes

* rewrite the moon phase to only make one call to get json and generate the correct character instaed of making 2 calls
#### Others

* add changelog to auto-publish to github release
* update changelog
* add build status to badges
* add build status to badges
* add some badges to the doc page

Full set of changes: [`v0.2.1...v0.2.2`](https://github.com/kellya/maubot-weather/compare/v0.2.1...v0.2.2)

## v0.2.1 (2021-08-29)

#### Fixes

* correct space to plus in location

Full set of changes: [`v0.2.0...v0.2.1`](https://github.com/kellya/maubot-weather/compare/v0.2.0...v0.2.1)

## v0.2.0 (2021-08-29)

#### New Features

* add command to get the lunar phase
#### Refactorings

* move weather into its own module to clean up basedir and make future expansion easier

Full set of changes: [`v0.1.0...v0.2.0`](https://github.com/kellya/maubot-weather/compare/v0.1.0...v0.2.0)

## v0.1.0 (2021-08-29)

#### New Features

* add ability to display the png forecast version of the weather
#### Refactorings

* clean up redundant logic for location given or not
#### Others

* add pylint to makefile
* Updated makefile to check tags to determine release
* fix default location format as it seems to not quite work right
* make show_image default to false
* clean up some docstrings and the error note, added show_image helper.copy()

Full set of changes: [`v0.0.16...v0.1.0`](https://github.com/kellya/maubot-weather/compare/v0.0.16...v0.1.0)

## v0.0.16 (2021-08-28)

#### Fixes

* added a check for the 'unknown location' to show a message if that occurs
#### Others

* Setup all the dev stuff in poetry

Full set of changes: [`v0.0.15...v0.0.16`](https://github.com/kellya/maubot-weather/compare/v0.0.15...v0.0.16)

## v0.0.15 (2021-07-14)


Full set of changes: [`v0.0.14...v0.0.15`](https://github.com/kellya/maubot-weather/compare/v0.0.14...v0.0.15)

## v0.0.14 (2021-02-24)


Full set of changes: [`v0.0.13...v0.0.14`](https://github.com/kellya/maubot-weather/compare/v0.0.13...v0.0.14)

## v0.0.13 (2021-01-20)


Full set of changes: [`v0.0.9...v0.0.13`](https://github.com/kellya/maubot-weather/compare/v0.0.9...v0.0.13)

## v0.0.9 (2021-01-20)


Full set of changes: [`v0.0.8...v0.0.9`](https://github.com/kellya/maubot-weather/compare/v0.0.8...v0.0.9)

## v0.0.8 (2021-01-20)

