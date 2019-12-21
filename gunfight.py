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
    
    N = 15 #number of rounds
    E_knife = 1.5 #desired avg numbers of knife only per map
    
    p_MSP = 0.33/4
    p_MS = 0.33/4
    p_MP = 0.33/4
    p_M = 0.33/4
    p_SP = 0.33/2
    p_S = 0.33/2
    p_P = 0.33
    
    p_nades = 0.5
    
    def f(x, N, E):
        return x*N*(x+1)**(N-1) - E
    
    p_knife = fsolve(f, 0.5, args=(N, E_knife))[0]
    
    if not(random.randint(1,100) <= p_knife*100):
        #not knife only
        pick = random.choice([0]*(int)(p_MSP*1000) + [1]*(int)(p_MS*1000) + [2]*(int)(p_MP*1000) + [3]*(int)(p_M*1000) + [4]*(int)(p_SP*1000) + [5]*(int)(p_S*1000) + [6]*(int)(p_P*1000))
        if (pick == 0): #main, secondary, pistol
            gearstring[0] = random.choice(gear_type["sidearm"])
            gearstring[1] = random.choice(gear_type["primary"])
            while (gearstring[1] == 'c'): # no negev
                gearstring[1] = random.choice(gear_type["primary"])
            gearstring[2] = random.choice(gear_type["secondary"])
            while gearstring[2] == gearstring[1]:
                gearstring[2] = random.choice(gear_type["secondary"])
        elif (pick == 1): #main, secondary
            gearstring[1] = random.choice(gear_type["primary"])
            while (gearstring[1] == 'c'): # no negev
                gearstring[1] = random.choice(gear_type["primary"])
            gearstring[2] = random.choice(gear_type["secondary"])
        elif (pick == 2): # main, pistol
            gearstring[0] = random.choice(gear_type["sidearm"])
            gearstring[1] = random.choice(gear_type["primary"])
        elif (pick == 3): # main
            gearstring[1] = random.choice(gear_type["primary"])
        elif (pick == 4): #secondary, pistol
            gearstring[0] = random.choice(gear_type["sidearm"])
            gearstring[2] = random.choice(gear_type["secondary"])
        elif (pick == 5): # secondary
            gearstring[2] = random.choice(gear_type["secondary"])
        else: #(pick == 6) # pistol
            gearstring[0] = random.choice(gear_type["sidearm"])       
    
    if (random.randint(1,100) <= p_nades*100):
        gearstring[3] = random.choice(['O']*80 + ['Q']*20) # 80% chance for HE
        
    if (gunfight_can_use_laser(gearstring)):
        if (gunfight_can_use_silencer(gearstring)):
            if random.randint(0,1):
                gearstring[6] = 'U' #silencer
            elif random.randint(0,1):
                gearstring[6] = 'V' #laser
        else:
            if random.randint(0,1):
                gearstring[6] = 'V'
        
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
