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

def gunfight_loadout_is_full(loadout):
    # consider pistol slot is always occupied 
    max_weight = 4
    weight = 0

    for slot in loadout[1:]:
        if slot == 'A':
            continue
        weight += 2 if slot == 'c' else 1
    return (weight >= max_weight)
		
def gunfight_loadout_generate(loadouts=[], banned_gear=""):

    if loadouts != []:
        return random.choice(loadouts)

    gearstring = list("AAAARWA")

    p_knife = 0.00
    p_nades = 0.0
    
    p_PSPs = 0.11
    p_PS = 0.11
    p_PPs = 0.11
    p_PO = 0.11
    p_SPs = 0.11
    p_SO = 0.11
    p_PsO = 0.11
    
    primary_secondary_pistol = 0
    primary_secondary = 1
    primary_pistol = 2
    primary_only = 3
    secondary_pistol = 4
    secondary_only = 5 
    pistol_only = 6
    pick = -1

    if not(random.randint(1,100) <= p_knife*100):
        #not knife only
        pick = random.choice(
		  [primary_secondary_pistol] *(int)(p_PSPs*100) \
		+ [primary_secondary]	     *(int)(p_PS*100) \
		+ [primary_pistol]           *(int)(p_PPs*100) \
		+ [primary_only]             *(int)(p_PO*100) \
		+ [secondary_pistol]         *(int)(p_SPs*100) \
		+ [secondary_only]           *(int)(p_SO*100) \
		+ [pistol_only]              *(int)(p_PsO*100)
	)

    weapstack = []
    pistolstack = []
    grenadestack = []
    if pick in {primary_secondary,secondary_pistol,secondary_only,primary_secondary_pistol}:
        weapstack += list(filter(lambda i: i not in banned_gear, gear_type["secondary"]))
    if pick in {primary_secondary,primary_pistol,primary_only,primary_secondary_pistol}:
        weapstack += list(filter(lambda i: i not in banned_gear, gear_type["primary"]))
    if pick == primary_secondary:
        weapstack.remove('c')
    if pick in {primary_pistol,primary_secondary_pistol,pistol_only}:
        pistolstack = list(filter(lambda i: i not in banned_gear, gear_type["sidearm"]))
    if random.randint(1,100) <= p_nades*100:
        grenadestack = list(filter(lambda i: i not in banned_gear, gear_type["grenade"]))
    itemstack = list(filter(lambda i: i not in banned_gear, gear_type["item"]))
    for stack in [pistolstack,weapstack,grenadestack,itemstack]: 
        random.shuffle(stack)

    gearstring[0] = pistolstack.pop() if len(pistolstack) else 'A' # ! always occupied
    gearstring[1] = weapstack.pop() if len(weapstack) else 'A'
    weapstack = [w for w in weapstack if w not in gear_type["primary"]]
    if not gunfight_loadout_is_full(gearstring) and not pick == secondary_only:
        gearstring[2] = weapstack.pop() if len(weapstack) else 'A'
    if not gunfight_loadout_is_full(gearstring) or gearstring[1] == 'c':
        gearstring[3] = grenadestack.pop() if len(grenadestack) else 'A'
    if not gunfight_loadout_is_full(gearstring) or (gearstring[1] == 'c' and gearstring[3] == 'A'):
        gearstring[6] = itemstack.pop() if len(itemstack) else 'A'
    if not gunfight_can_use_silencer(gearstring) and 'U' in gearstring:
        gearstring[gearstring.index('U')] = 'A'
    if not gunfight_can_use_laser(gearstring) and 'V' in gearstring: 
        gearstring[gearstring.index('V')] = 'A'

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

def gunfight_next_loadout(current, presets, rcon, banned_gear):
    g_sidearm = gear_type["sidearm"]
    g_primary = gear_type["primary"]
    g_secondary = gear_type["secondary"]

    new_loadout = gunfight_loadout_generate(presets, banned_gear)
    while current == new_loadout and not len(presets) == 1:
	    new_loadout = gunfight_loadout_generate(presets, banned_gear)
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
