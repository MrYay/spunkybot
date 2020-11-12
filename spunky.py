#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Spunky Bot - An automated game server bot
http://www.spunkybot.de
Author: Alexander Kress

This program is released under the MIT License. See LICENSE for more details.

## About ##
Spunky Bot is a lightweight game server administration bot and RCON tool,
inspired by the eb2k9 bot by Shawn Haggard.
The purpose of Spunky Bot is to administrate an Urban Terror 4.1 / 4.2 / 4.3
server and provide statistics data for players.

## Configuration ##
Modify the UrT server config as follows:
 * seta g_logsync "1"
 * seta g_loghits "1"
Modify the files '/conf/settings.conf' and '/conf/rules.conf'
Run the bot: python spunky.py
"""

__version__ = '1.11.0'


### IMPORTS
import os
import time
import math
import textwrap
import urllib
import urllib2
import platform
import random
import ConfigParser
import logging.handlers
import lib.schedule as schedule

from lib.pyquake3 import PyQuake3
from Queue import Queue
from threading import Thread
from threading import RLock
from gunfight import *


# Get an instance of a logger
logger = logging.getLogger('spunkybot')
logger.setLevel(logging.DEBUG)
logger.propagate = False

# Bot player number
BOT_PLAYER_NUM = 1022

# RCON Delay in seconds, recommended range: 0.18 - 0.33
RCON_DELAY = 0.2

### CLASS Log Parser ###
class LogParser(object):
    """
    log file parser
    """
    def __init__(self, config_file):
        """
        create a new instance of LogParser

        @param config_file: The full path of the bot configuration file
        @type  config_file: String
        """

        self.config_file = config_file
        config = ConfigParser.ConfigParser()
        config.read(config_file)

        # enable/disable debug output
        verbose = config.getboolean('bot', 'verbose') if config.has_option('bot', 'verbose') else False
        # logging format
        formatter = logging.Formatter('[%(asctime)s] %(levelname)-8s %(message)s', datefmt='%d.%m.%Y %H:%M:%S')
        # console logging
        console = logging.StreamHandler()
        if not verbose:
            console.setLevel(logging.INFO)
        console.setFormatter(formatter)

        # devel.log file
        devel_log = logging.handlers.RotatingFileHandler(filename='devel.log', maxBytes=2097152, backupCount=1, encoding='utf8')
        devel_log.setLevel(logging.INFO)
        if verbose:
		devel_log.setLevel(logging.DEBUG)
        devel_log.setFormatter(formatter)

        # add logging handler
        logger.addHandler(console)
        logger.addHandler(devel_log)

        logger.info("*** Spunky Bot v%s : www.spunkybot.de ***", __version__)
        logger.info("Starting logging      : OK")
        logger.info("Loading config file   : %s", config_file)

        games_log = config.get('server', 'log_file')

        self.ffa_lms_gametype = False
        self.ctf_gametype = False
        self.ts_gametype = False
        self.tdm_gametype = False
        self.bomb_gametype = False
        self.freeze_gametype = False
        self.gunfight_gametype = False
        self.urt_modversion = None
        self.game = None
        self.default_gear = ''
        self.round_count = 0
        self.blue_score = 0
        self.red_score = 0
        self.fraglimit = 0
        self.use_match_point = True
        self.match_point = False
        self.gunfight_old_maxrounds = 0
        self.gunfight_presets = []
        self.gunfight_loadout = ''
        self.gunfight_banned_items = ''
        self.gunfight_loadout_rounds = 2
        self.gunfight_swapped_roles = True
        self.gunfight_maxrounds = 0

        # Gameplay mods
        if config.has_option('gamemode','use_match_point') and config.getboolean('gamemode','use_match_point'):
            logger.debug("Using Match Point!")
            self.use_match_point = True
        logger.debug("Checking for GUNFIGHT variable...")
        if config.has_option('gamemode','gunfight') and config.getboolean('gamemode','gunfight'):
            logger.debug("GUNFIGHT mode active!")
            self.gunfight_gametype = True
	    gunfight_presets_string = config.get('gamemode','gunfight_presets') if config.has_option('gamemode','gunfight_presets') else ""
	    self.gunfight_presets = filter(lambda s: s is not '', gunfight_presets_string.split(','))
	    self.gunfight_banned_items = config.get('gamemode','gunfight_banned_items') if config.has_option('gamemode','gunfight_banned_items') else ""
        self.gunfight_loadout_rounds = config.getint('gamemode','gunfight_loadout_rounds') if config.has_option('gamemode','gunfight_loadout_rounds') else 2
        logger.info("Configuration loaded  : OK")
        server_port = config.get('server', 'server_port') if config.has_option('server', 'server_port') else "27960"
        self.uptime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        # Parse Game log file
        try:
            # open game log file
            self.log_file = open(games_log, 'r')
        except IOError:
            logger.error("ERROR: The Gamelog file '%s' has not been found", games_log)
            logger.error("*** Aborting Spunky Bot ***")
        else:
            # go to the end of the file
            self.log_file.seek(0, 2)
            # start parsing the games logfile
            logger.info("Parsing Gamelog file  : %s", games_log)
            self.read_log()

    def find_game_start(self):
        """
        find InitGame start
        """
        seek_amount = 768
        # search within the specified range for the InitGame message
        start_pos = self.log_file.tell() - seek_amount
        end_pos = start_pos + seek_amount
        try:
            self.log_file.seek(start_pos)
        except IOError:
            logger.error("ERROR: The games.log file is empty, ignoring game type and start")
            # go to the end of the file
            self.log_file.seek(0, 2)
            game_start = True
        else:
            game_start = False
        while not game_start:
            while self.log_file:
                line = self.log_file.readline()
                tmp = line.split()
                if len(tmp) > 1 and tmp[1] == "InitGame:":
                    game_start = True
                    if 'g_gametype\\0\\' in line or 'g_gametype\\1\\' in line or 'g_gametype\\9\\' in line or 'g_gametype\\11\\' in line:
                        # disable teamkill event and some commands for FFA (0), LMS (1), Jump (9), Gun (11)
                        self.ffa_lms_gametype = True
                    elif 'g_gametype\\7\\' in line:
                        self.ctf_gametype = True
                    elif 'g_gametype\\4\\' in line or 'g_gametype\\5\\' in line:
                        self.ts_gametype = True
                    elif 'g_gametype\\3\\' in line:
                        self.tdm_gametype = True
                    elif 'g_gametype\\8\\' in line:
                        self.bomb_gametype = True
                    elif 'g_gametype\\10\\' in line:
                        self.freeze_gametype = True

                    # get default g_gear value
                    self.default_gear = line.split('g_gear\\')[-1].split('\\')[0] if 'g_gear\\' in line else "%s" % '' if self.urt_modversion > 41 else '0'

                    # get default fraglimit value
                    self.fraglimit = line.split('fraglimit\\')[-1].split('\\')[0] if 'fraglimit\\' in line else "%s" % '' if self.urt_modversion > 41 else '0'
                if self.log_file.tell() > end_pos:

                    break
                elif not line:
                    break
            if self.log_file.tell() < seek_amount:
                self.log_file.seek(0, 0)
            else:
                cur_pos = start_pos - seek_amount
                end_pos = start_pos
                start_pos = cur_pos
                if start_pos < 0:
                    start_pos = 0
                self.log_file.seek(start_pos)

    def read_log(self):
        """
        read the logfile
        """

        self.find_game_start()

        # create instance of Game
        self.game = Game(self.config_file, self.urt_modversion)

        self.log_file.seek(0, 2)
        while self.log_file:
            line = self.log_file.readline()
            if line:
                self.parse_line(line)
            else:
                if not self.game.live:
                    self.game.go_live()
                time.sleep(.125)

    def parse_line(self, string):
        """
        parse the logfile and search for specific action
        """
        line = string[7:]
        tmp = line.split(":", 1)
        line = tmp[1].strip() if len(tmp) > 1 else tmp[0].strip()
        option = {'InitGame': self.new_game, 'Warmup': self.handle_warmup, 'InitRound': self.handle_initround,
                  'Exit': self.handle_exit, 
                  'SurvivorWinner': self.handle_teams_ts_mode, 'AssassinWinner': self.handle_teams_ftl_mode,
                  }

        try:
            action = tmp[0].strip()
            if action in option:
                option[action](line)
        except (IndexError, KeyError):
            pass
        except Exception as err:
            logger.error(err, exc_info=True)

    def new_game(self, line):
        """
        set-up a new game
        """
        self.ffa_lms_gametype = True if ('g_gametype\\0\\' in line or 'g_gametype\\1\\' in line or 'g_gametype\\9\\' in line or 'g_gametype\\11\\' in line) else False
        self.ctf_gametype = True if 'g_gametype\\7\\' in line else False
        self.ts_gametype = True if ('g_gametype\\4\\' in line or 'g_gametype\\5\\' in line) else False
        self.tdm_gametype = True if 'g_gametype\\3\\' in line else False
        self.bomb_gametype = True if 'g_gametype\\8\\' in line else False
        self.freeze_gametype = True if 'g_gametype\\10\\' in line else False
        logger.debug("InitGame: Starting game...")
        self.game.rcon_clear()

        # gunfight_gametype 
        self.gunfight_maxrounds = int(self.game.get_cvar('g_maxrounds'))
        if self.gunfight_gametype:
            self.gunfight_swapped_roles = False if 'g_swaproles\\1\\' in line else True
            if self.ts_gametype or self.bomb_gametype or self.freeze_gametype:
	        self.game.send_rcon("set g_gear \"\"")
                self.gunfight_loadout = gunfight_next_loadout(self.gunfight_loadout, self.gunfight_presets, self.game, self.gunfight_banned_items)
                logger.debug("new_game: New GUNFIGHT Loadout! [%s]", self.gunfight_loadout)
            else:
                self.gunfight_gametype = False
                logger.debug("GUNFIGHT disabled because of unsupported gametype")

    def handle_warmup(self, line):
        """
        handle warmup
        """
        logger.debug("Warmup... %s", line)
        self.match_point = False
        self.round_count = 0

    def handle_initround(self, _):
        """
        handle Init Round
        """
        logger.debug("InitRound: Round started...")
        self.round_count += 1
        if self.gunfight_gametype:
            logger.debug("InitRound: GUNFIGHT Round started...")
            logger.debug("InitRound: Round number %d...", self.round_count)
	    if self.use_match_point and self.match_point:
                logger.debug("MATCH POINT!")
                self.game.rcon_say("^1[  MATCH POINT!  ]")
            self.game.rcon_bigtext("^2%s" % gunfight_print_loadout(self.gunfight_loadout))

    def handle_exit(self, line):
        """
        handle Exit of a match, show Awards, store user score in database and reset statistics
        """
        logger.debug("Exit: %s", line)
        self.blue_score = 0
        self.red_score = 0
    	self.round_count = 0
        if self.gunfight_gametype:
            logger.debug("Exit: GUNFIGHT match end...")
 	    if self.use_match_point and self.match_point:
		self.match_point = False
		self.game.send_rcon("fraglimit %s" % str(self.fraglimit))
            #if self.game.get_cvar('g_gear') != self.default_gear:
                #self.game.send_rcon("set g_gear %s" % self.default_gear)
	    if self.gunfight_swapped_roles:
	        self.game.send_rcon("set g_gear \"\"")
                self.game.send_rcon("set sv_forcegear \"\"")
	    if self.game.get_cvar('g_swaproles') == '1':
	        self.gunfight_swapped_roles = not self.gunfight_swapped_roles

    def check_match_point(self):
	"""
	setup matchpoint if enabled
	"""
        rcon_players = self.game.get_rcon_output('players')
        teams_scores = rcon_players[1].split('\n')[3].split(' ')[-2:]
        half_point = self.gunfight_maxrounds/2
        self.blue_score = int(teams_scores[1].split(':')[1])
        self.red_score = int(teams_scores[0].split(':')[1])
        if ((self.blue_score+1 > half_point) or \
           (self.red_score+1 > half_point)) and not self.match_point:
            self.match_point = True
        if self.match_point and (self.blue_score > half_point or self.red_score > half_point):
            self.game.send_rcon("fraglimit %s" % str(half_point))	

    def handle_teams_ts_mode(self, line):
        """
        handle team balance in Team Survivor mode
        """
        logger.debug("SurvivorWinner: %s", line)
        self.game.send_rcon("%s%s ^7team wins" % ('^1' if line == 'Red' else '^4', line) if 'Draw' not in line else "^7Draw")
	if self.use_match_point:
		self.check_match_point()
        if self.gunfight_gametype:
            self.gunfight_round_end()

    def handle_teams_ftl_mode(self, line):
        """
        handle team balance in Follow The Leader mode
        """
        logger.debug("AssassinWinner: %s", line)
        self.game.send_rcon("%s%s ^7team wins" % ('^1' if line == 'Red' else '^4', line) if 'Draw' not in line else "^7Draw")
	if self.use_match_point:
		self.check_match_point()
        if self.gunfight_gametype:
            self.gunfight_round_end()

    def gunfight_round_end(self):
        """
        handle gunfight loadout cycle
        """
        if (not self.round_count % self.gunfight_loadout_rounds) or (not self.gunfight_swapped_roles and self.round_count == self.gunfight_maxrounds):
            self.gunfight_loadout = gunfight_next_loadout(self.gunfight_loadout, self.gunfight_presets, self.game, self.gunfight_banned_items)
            logger.debug("New GUNFIGHT Loadout! [%s]", self.gunfight_loadout)
            self.game.rcon_bigtext("^2Weapons change next round!")

### CLASS Game ###
class Game(object):
    """
    Game class
    """
    def __init__(self, config_file, urt_modversion):
        """
        create a new instance of Game

        @param config_file: The full path of the bot configuration file
        @type  config_file: String
        """
        self.players = {}
        self.live = False
        self.urt_modversion = urt_modversion
        self.game_cfg = ConfigParser.ConfigParser()
        self.game_cfg.read(config_file)
        self.quake = PyQuake3("%s:%s" % (self.game_cfg.get('server', 'server_ip'), self.game_cfg.get('server', 'server_port')), self.game_cfg.get('server', 'rcon_password'))
        self.queue = Queue()
        self.rcon_lock = RLock()
        self.thread_rcon()
        logger.info("Opening RCON socket   : OK")
        logger.info("Activating the Bot    : OK")
        logger.info("Startup completed     : Let's get ready to rumble!")
        logger.info("Spunky Bot is running until you are closing this session or pressing CTRL + C to abort this process.")
        logger.info("*** Note: Use the provided initscript to run Spunky Bot as daemon ***")

        # gunfight
        self.gunfight_on = self.game_cfg.has_option('gamemode','gunfight') and self.game_cfg.getboolean('gamemode','gunfight')
        gunfight_presets_string = self.game_cfg.get('gamemode','gunfight_presets') if self.game_cfg.has_option('gamemode','gunfight_presets') else ""
        self.gunfight_banned_items = self.game_cfg.get('gamemode','gunfight_banned_items') if self.game_cfg.has_option('gamemode','gunfight_banned_items') else ""
        self.gunfight_presets = list(set(filter(lambda s: s is not '', gunfight_presets_string.split(','))))

    def thread_rcon(self):
        """
        Thread process for starting method rcon_process
        """
        # start Thread
        processor = Thread(target=self.rcon_process)
        processor.setDaemon(True)
        processor.start()

    def rcon_process(self):
        """
        Thread process
        """
        while 1:
            if not self.queue.empty():
                if self.live:
                    with self.rcon_lock:
                        try:
                            command = self.queue.get()
                            if command != 'status':
                                self.quake.rcon(command)
                            else:
                                self.quake.rcon_update()
                        except Exception as err:
                            logger.error(err, exc_info=True)
            time.sleep(RCON_DELAY)

    def get_quake_value(self, value):
        """
        get Quake3 value

        @param value: The Quake3 value
        @type  value: String
        """
        if self.live:
            with self.rcon_lock:
                self.quake.update()
                return self.quake.values[value]

    def get_rcon_output(self, value):
        """
        get RCON output for value

        @param value: The RCON output for value
        @type  value: String
        """
        if self.live:
            with self.rcon_lock:
                return self.quake.rcon(value)

    def get_cvar(self, value):
        """
        get CVAR value

        @param value: The CVAR value
        @type  value: String
        """
        if self.live:
            with self.rcon_lock:
                try:
                    ret_val = self.quake.rcon(value)[1].split(':')[1].split('^7')[0].lstrip('"')
                except IndexError:
                    ret_val = None
                time.sleep(RCON_DELAY)
                return ret_val

    def get_number_players(self):
        """
        get the number of online players
        """
        return len(self.players) - 1  # bot is counted as player

    def send_rcon(self, command):
        """
        send RCON command

        @param command: The RCON command
        @type  command: String
        """
        if self.live:
            with self.rcon_lock:
                self.queue.put(command)

    def rcon_say(self, msg):
        """
        display message in global chat

        @param msg: The message to display in global chat
        @type  msg: String
        """
        # wrap long messages into shorter list elements
        lines = textwrap.wrap(msg, 140)
        for line in lines:
            self.send_rcon('say %s' % line)

    def rcon_tell(self, player_num, msg, pm_tag=True):
        """
        tell message to a specific player

        @param player_num: The player number
        @type  player_num: Integer
        @param msg: The message to display in private chat
        @type  msg: String
        @param pm_tag: Display '[pm]' (private message) in front of the message
        @type  pm_tag: bool
        """
        lines = textwrap.wrap(msg, 128)
        prefix = "^4[pm] "
        for line in lines:
            if pm_tag:
                self.send_rcon('tell %d %s%s' % (player_num, prefix, line))
                prefix = ""
            else:
                self.send_rcon('tell %d %s' % (player_num, line))

    def rcon_bigtext(self, msg):
        """
        display bigtext message

        @param msg: The message to display in global chat
        @type  msg: String
        """
        self.send_rcon('bigtext "%s"' % msg)

    def rcon_forceteam(self, player_num, team):
        """
        force player to given team

        @param player_num: The player number
        @type  player_num: Integer
        @param team: The team (red, blue, spectator)
        @type  team: String
        """
        self.send_rcon('forceteam %d %s' % (player_num, team))

    def rcon_clear(self):
        """
        clear RCON queue
        """
        self.queue.queue.clear()

    def go_live(self):
        """
        go live
        """
        self.live = True
        self.rcon_say("^7Powered by ^8[Spunky Bot %s] ^1[www.spunkybot.de]" % __version__)
        logger.info("Server CVAR g_logsync : %s", self.get_cvar('g_logsync'))
        logger.info("Server CVAR g_loghits : %s", self.get_cvar('g_loghits'))
        # gunfight
        if self.get_cvar('g_gametype') in ("4","8","10","1","5"):
            if self.gunfight_on and self.get_cvar('sv_forcegear') == "":
                logger.debug("[go_live] GUNFIGHT ENABLED")
		gunfight_init = gunfight_next_loadout("",self.gunfight_presets,self, self.gunfight_banned_items)
                logger.debug("[go_live] GUNFIGHT INIT: %s", gunfight_init)
                logger.debug("[go_live] sv_forcegear set to [%s]", self.get_cvar('sv_forcegear'))
        else:
            logger.debug("GUNFIGHT not initiated because of unsupported gametype")
            self.gunfight_on = False
            
    def add_player(self, player):
        """
        add a player to the game

        @param player: The instance of the player
        @type  player: Instance
        """
        self.players[player.get_player_num()] = player

    def get_gamestats(self):
        """
        get number of players in red team, blue team and spectator
        """
        game_data = {Player.teams[1]: 0, Player.teams[2]: 0, Player.teams[3]: -1}
        for player in self.players.itervalues():
            game_data[Player.teams[player.get_team()]] += 1
        return game_data


### Main ###
if __name__ == "__main__":
    # get full path of spunky.py
    HOME = os.path.dirname(os.path.realpath(__file__))
    # create instance of LogParser
    LogParser(os.path.join(HOME, 'conf', 'settings.conf'))
