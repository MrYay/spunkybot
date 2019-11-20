import random
import collections
from numpy.random import choice as nchoice

g_gear_itemsonly = "KLeMiNZacHjhIJkFfGl"

gear_list = { "F":"Beretta",
            "f":"Glock",
            "g":"Colt1911",
            "G":"DE",
            "l":"Magnum",
            "H":"SPAS12",
            "j":"Benelli",
            "h":"Mac11",
            "I":"MP5K",
            "J":"UMP45",
            "k":"P90",
            "K":"HK69",
            "L":"LR300",
            "e":"M4",
            "M":"G36",
            "i":"FR-F1",
            "N":"PSG1",
            "Z":"SR8",
            "a":"AK103",
            "c":"Negev",
            "O":"HE",
            "Q":"Smoke",
            "R":"Vest",
            "S":"Tac",
            "T":"Medkit",
            "U":"Silencer",
            "V":"Laser",
            "W":"Helmet",
            "X":"Ammo"}

gear_type = collections.OrderedDict(sorted({
        "grenade":"O",
        "item":"UV",
        "primary":"KLeMiNZac",
        "secondary":"HjhIJk",
        "sidearm":"FfGl"
	}.items()))

def gunfight_can_use_laser(loadout):
    for e in loadout:
        if e in "FfgGIJLea":
            return True
    return False

def gunfight_can_use_silencer(loadout):
    for e in loadout:
        if e in "FfghIJkLeMiNac":
            return True
    return False

def gunfight_loadout_generate(loadouts=""):

        if loadouts != "":
            return random.choice(loadouts.split(','))

        gearstring = list("AAAARWA")

        loadout_type_weights = [0.1,0.1,0.2,0.3,0.3]
	#loadout_type_weights = [0.4,0.5,0.03,0.03,0.04]
        loadout_type = nchoice(gear_type.keys(),p=loadout_type_weights)

        pick_nade = random.randint(0,1)
        pick_item = random.randint(0,1)
        if loadout_type in ("sidearm","primary","secondary"):
            gearstring[0] = random.choice(gear_type["sidearm"])
        if loadout_type == "primary":
            gearstring[1] = random.choice(gear_type["primary"])
        if loadout_type == "secondary":
            gearstring[2] = random.choice(gear_type["secondary"])
        if loadout_type != "item":
            if loadout_type == "grenade" or (pick_nade and (gearstring.count('A') != 2)):
                gearstring[3] = random.choice(gear_type["grenade"])
        if loadout_type not in ("grenade","item"):
            if pick_item and (gearstring.count('A') != 2):
                item = random.choice(gear_type["item"])
                if (gunfight_can_use_laser(gearstring) and item == "V") or (gunfight_can_use_silencer(gearstring) and item == "U"):
                    gearstring[6] = item
        return("".join(gearstring))

def gunfight_print_loadout(gearstring,g_gear=""):
    textlist = []
    if g_gear == g_gear_itemsonly:
        gearstring = "AA"+gearstring[2:]
    if gearstring[0:4].count('A') >= 3:
        textlist.append("^1")
    if gearstring[0:4].count('A') == 4:
        textlist.append("KNIFE")
    for e in gearstring:
        if e in gear_list.keys() and e not in "RW":
            textlist.append(gear_list[e])
    if textlist[0] == "^1":
        textlist.append("ONLY!")
    return(" ".join(textlist))

def gunfight_next_loadout(spunky):
    current_loadout = spunky.gunfight_round_loadout
    while current_loadout == spunky.gunfight_round_loadout:
        spunky.gunfight_round_loadout = gunfight_loadout_generate(spunky.gunfight_presets)
    spunky.game.rcon_bigtext("^2New Loadout: %s" % gunfight_print_loadout(spunky.gunfight_round_loadout))
    if spunky.gunfight_round_loadout[0:3] == "AAA":
        gunfight_workaround = spunky.gunfight_round_loadout
        spunky.game.send_rcon("set g_gear %s" % g_gear_itemsonly)
        if spunky.gunfight_round_loadout[3] == "O":
            gunfight_workaround = "GL" + spunky.gunfight_round_loadout[2:]
        spunky.game.send_rcon("set sv_forcegear %s" % gunfight_workaround)
    else:
        if spunky.game.get_cvar('g_gear') == g_gear_itemsonly:
            spunky.game.send_rcon("set g_gear '%s'" % spunky.default_gear)
        spunky.game.send_rcon("set sv_forcegear %s" % spunky.gunfight_round_loadout)

