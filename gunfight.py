import random
import collections

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
            "Q":"Smokes",
            "R":"Vest",
            "S":"Tac",
            "T":"Medkit",
            "U":"Silencer",
            "V":"Laser",
            "W":"Helmet",
            "X":"Ammo"}

gear_type = collections.OrderedDict(sorted({
        "grenade":"OQ",
        "item":"UV",
        "primary":"KLeMiNZac",
        "secondary":"HjhIJk",
        "sidearm":"FfgGl"
	}.items()))

def gunfight_can_use_laser(loadout):
    for e in loadout:
        if e in "FfgGIJLea":
            return True
    return False

def gunfight_can_use_silencer(loadout):
    for e in loadout:
        if e in "FfghIJkLeMNac":
            return True
    return False

def gunfight_loadout_generate(loadouts=[]):

        if loadouts != []:
            return random.choice(loadouts)

        gearstring = list("AAAARWA")

        pick_primary = random.randint(0,1)
        pick_secondary = random.randint(0,1)
        pick_sidearm = pick_nade = pick_item = 0
        if not (pick_primary and pick_secondary):
            pick_sidearm = random.randint(0,1)
            pick_nade = random.randint(0,1)
            pick_item = random.randint(0,1) if not (pick_nade and (pick_primary or pick_secondary)) else 0

	if pick_sidearm:
            gearstring[0] = random.choice(gear_type["sidearm"])
	if pick_primary:
            gearstring[1] = random.choice(gear_type["primary"]+gear_type["secondary"])
	if pick_secondary and (gearstring[1] is not 'c'):
            gearstring[2] = random.choice(gear_type["secondary"])
	    while gearstring[2] == gearstring[1]:
              gearstring[2] = random.choice(gear_type["secondary"])
	if pick_nade:
            gearstring[3] = random.choice(gear_type["grenade"])
	if pick_item:
            item = random.choice(gear_type["item"]) if not (pick_secondary and pick_primary) else 'A'
            if (gunfight_can_use_laser(gearstring) and item == "V") or (gunfight_can_use_silencer(gearstring) and item == "U"):
                gearstring[6] = item
			
        return("".join(gearstring))

def gunfight_print_loadout(gearstring,g_gear=""):
    textlist = []

    if gear_type["sidearm"] in g_gear:
	 gl = list(gearstring)
	 gl[0] = 'A'
	 gearstring = "".join(gl)
    if gear_type["primary"] in g_gear:
	 gl = list(gearstring)
	 gl[1] = 'A'
	 gearstring = "".join(gl)
    if gear_type["secondary"] in g_gear:
	 gl = list(gearstring)
	 gl[2] = 'A'
	 gearstring = "".join(gl)

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

def gunfight_next_loadout(current, presets, rcon):
    g_sidearm = gear_type["sidearm"]
    g_primary = gear_type["primary"]
    g_secondary = gear_type["secondary"]

    new_loadout = gunfight_loadout_generate(presets)
    while current == new_loadout and not len(presets) == 1:
	    new_loadout = gunfight_loadout_generate(presets)
    og_loadout = new_loadout
    new_g_gear = ""
    if new_loadout[1] == 'A':
        new_g_gear += g_primary
    if new_loadout[2] == 'A' and new_loadout[1] not in g_secondary:
        new_g_gear += g_secondary
    if new_loadout[0] == 'A':
        new_g_gear += g_sidearm
        new_loadout = "G" + new_loadout[1:]
        if new_loadout[0:3].count('A') == 3:
          if new_loadout[3] in gear_type["grenade"]:
            new_loadout = "GL" + new_loadout[2:]
    rcon.send_rcon("set g_gear \"%s\"" % new_g_gear)
    rcon.send_rcon("set sv_forcegear %s" % new_loadout)
    return og_loadout
