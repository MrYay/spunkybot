# What is this?

This is a lightweight server script for enabling [gunfight-like](https://callofduty.fandom.com/wiki/Gunfight#Overview) gamemode on an [Urban Terror](http://www.urbanterror.info) game server.
Based off [Spunky Bot](https://github.com/SpunkyBot/spunkybot) stripped of its administration functions, meaning it will not react to in-game commands.

When the Gunfight modifier is enabled, every player spawns with the same loadout, generated randomly or predefined by the server admin.
Loadouts used can change periodically, at a rate that can be configured.
Only gamemodes with no respawn are supported (Team Survivor, Bomb Mode, Freeze Tag and Last Man Standing).

An Urban Terror server binary with `sv_forcegear` functionality is required. For example https://github.com/MrYay/ioq3-for-UrbanTerror-4

[![License](https://img.shields.io/github/license/SpunkyBot/spunkybot)](https://github.com/SpunkyBot/spunkybot/blob/develop/LICENSE)
[![Release](https://img.shields.io/github/v/release/SpunkyBot/spunkybot.svg?color=orange)](https://github.com/SpunkyBot/spunkybot/releases)
[![PyPI version](https://img.shields.io/pypi/v/spunkybot.svg)](https://pypi.python.org/pypi/spunkybot)
[![Python version](https://img.shields.io/pypi/pyversions/spunkybot?color=yellow)](https://pypi.org/project/spunkybot)

## Features

* Gunfight gamemode modification with fully randomized loadouts or presets
* Match point system
* Randomized mapcycle

## Environment

* Urban Terror 4.1.1 / 4.2.023 / 4.3.4
* Python 2.6 / 2.7
* Cross-platform (tested on Debian 6 / 7 / 8 / 9, Ubuntu 12 / 14 / 16 / 18, CentOS 6 / 7, macOS 10.13, Windows 7 / 10)
* Supporting 32-bit and 64-bit operating systems

## Quickstart

The setup is similar to [Spunky Bot quickstart instructions](https://github.com/SpunkyBot/spunkybot#quickstart) without the `!iamgod` command

### Configuration

* Modify the Urban Terror server config file as follows:

```
seta g_logsync "1"
```

* Restart your Urban Terror server
* Modify the configuration file `/conf/settings.conf` and set game server port and RCON password
* Run the application manually: `python spunky.py`
* Or use the provided systemd or sysVinit script to run Spunky Bot as daemon

### Game modifiers
The game modifiers can be enabled by editing `/conf/settings.conf` before running the bot.

Under the `[gamemode]` section:
#### Gunfight
* set `gunfight = 1` to enable gunfight mode
* set `gunfight_presets` to a comma-separated list of loadouts if you want to use [predefined loadouts](https://www.urbanterror.info/support/120-gears/#D). If this option is not set, loadouts are generated on the fly.
* set `gunfight_banned_items` to a string containing [gear](https://www.urbanterror.info/support/120-gears/#C) you do not want to appear in loadouts
* set `gunfight_banned_loadouts` to a comma-separated list of loadouts you want to prevent from being generated.
* set `gunfight_loadout_rounds` to the number of rounds to play before a new loadout is generated. Default is `2`
* set `gunfight_loadout_probs` to a comma-separated list of probabilities for each loadout type to be generated, in the format `<type>:<probability>`. 
loadout types can be the following:
  
`p_K` knife only, `p_G` grenade only, `p_PSPs` primary+secondary+pistol, `p_PS` primary+secondary (no pistol),
`p_PPs` primary+pistol, `p_PO` primary only, `p_SPs` secondary+pistol, `p_SO` secondary only, `p_PsO` pistol only

for example, to have all loadout types generated with equal probabilities except for knife only: `p_K:0,p_G:0.11,p_PSPs:0.11,p_PS:0.11,p_PPs:0.11,p_PO:0.11,p_SPs:0.11,p_SO:0.11,p_PsO:0.11`

#### Match Point system
* set `use_match_point = 1` to enable the match point system. If enabled, the match ends as soon as a team's score reaches more than half the value of `g_maxrounds`

#### Randomized mapcycle
Under the `[mapcycle]` section:
* set `mapcycle_file` to the path of your server's mapcycle, for example `/home/urt/server/q3ut4/mapcycle.txt`
* set `mapcycle_randomize = 1` to enable mapcycle randomization. If enabled, the ordering of the maps in the mapcycle will be randomly shuffled.

## Contributing

By contributing code to this project in any form, including sending a pull request via GitHub, a code fragment or patch via mail or public discussion groups, you agree to release your code under the terms of the MIT license that you can find in the [LICENSE](https://github.com/SpunkyBot/spunkybot/blob/develop/LICENSE) file included in this source distribution.

## License

The code of Spunky Bot is released under the MIT License. See the [LICENSE](https://github.com/SpunkyBot/spunkybot/blob/develop/LICENSE) file for the full license text.

### Third Party Libraries

* RCON: [pyquake3.py](https://github.com/urthub/pyquake3)
  * The library has been modified to fix some error handling issues and fulfill the PEP8 conformance. This file is released under the GNU General Public License.
* GeoIP: [pygeoip.py](https://github.com/urthub/pygeoip)
  * The library has been extended with the list `GeoIP_country_name` to support full country names (e.g. Germany for country_code DE). This file is released under the MIT License.
* GeoLite database: [www.maxmind.com](http://www.maxmind.com)
  * The GeoLite databases created by MaxMind are distributed under the Creative Commons Attribution-ShareAlike 4.0 International License and the MaxMind Open Data License.
* Schedule: [schedule.py](https://github.com/dbader/schedule)
  * This file is released under the MIT License.

Urban Terror® and FrozenSand™ are trademarks, or registered trademarks of Frozensand Games Limited.
