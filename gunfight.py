import random
import collections

gear_list = {"F": "Beretta",
             "f": "Glock",
             "g": "Colt1911",
             "G": "DE",
             "l": "Magnum",
             "H": "SPAS12",
             "j": "Benelli",
             "h": "Mac11",
             "I": "MP5K",
             "J": "UMP45",
             "k": "P90",
             "K": "HK69",
             "L": "LR300",
             "e": "M4",
             "M": "G36",
             "i": "FR-F1",
             "N": "PSG1",
             "Z": "SR8",
             "a": "AK103",
             "c": "Negev",
             "O": "HE",
             "Q": "Smokes",
             "R": "Vest",
             "S": "Tac",
             "T": "Medkit",
             "U": "Silencer",
             "V": "Laser",
             "W": "Helmet",
             "X": "Ammo"}

gear_type = collections.OrderedDict(sorted({
                                               "grenade": "OQ",
                                               "item": "UV",
                                               "primary": "KLeMiNZac",
                                               "secondary": "HjhIJk",
                                               "sidearm": "FfgGl"
                                           }.items()))

class GunfightGame(object):
    """
    gunfight game variables
    """
    def __init__(self, banned_items, banned_loadouts, loadouts_presets, loadouts_probabilities, loadout_rounds, config_g_gear=""):
        self.config_g_gear = config_g_gear
        self.g_gear = ""
        self.banned_items = banned_items
        self.banned_loadouts = banned_loadouts
        self.loadouts_presets = loadouts_presets
        self.loadouts_probabilities = loadouts_probabilities
        self.current_loadout = ""
        self.loadout_announcement = ""
        self.loadout_rounds = loadout_rounds
        self.swapped_roles = True

    def can_use_laser(self, loadout):
        for e in loadout:
            if e in "FfgGIJLea":
                return True
        return False

    def can_use_silencer(self, loadout):
        for e in loadout:
            if e in "FfghIJkLeMNac":
                return True
        return False

    def loadout_is_full(self, loadout):
        # consider pistol slot is always occupied
        max_weight = 4
        weight = 0

        for slot in loadout[1:]:
            if slot == 'A':
                continue
            weight += 2 if slot == 'c' else 1
        return (weight >= max_weight)

    def loadout_to_msg(self, gearstring):
        msg = []

        if gear_type["sidearm"] in self.g_gear:
            gl = list(gearstring)
            gl[0] = 'A'
            gearstring = "".join(gl)
        if gear_type["primary"] in self.g_gear:
            gl = list(gearstring)
            gl[1] = 'A'
            gearstring = "".join(gl)
        if gear_type["secondary"] in self.g_gear:
            gl = list(gearstring)
            gl[2] = 'A'
            gearstring = "".join(gl)

        if gearstring[0:4].count('A') >= 3:
            msg.append("^1")
            if gearstring[0:4].count('A') == 4:
                msg.append("KNIFE")
        for e in gearstring:
            if e in gear_list.keys() and e not in "RW":
                msg.append(gear_list[e])
        if msg[0] == "^1":
            msg.append("ONLY!")
        return " ".join(msg)

    def _loadout_generate(self):
        if len(self.loadouts_presets):
            return random.choice(self.loadouts_presets)

        gearstring = list("AAAARWA")

        p_knife = self.loadouts_probabilities.get("p_K", 0)
        p_nades = self.loadouts_probabilities.get("p_G", 0)
        p_PSPs = self.loadouts_probabilities.get("p_PSPs", 0)
        p_PS = self.loadouts_probabilities.get("p_PS", 0)
        p_PPs = self.loadouts_probabilities.get("p_PPs", 0)
        p_PO = self.loadouts_probabilities.get("p_PO", 0)
        p_SPs = self.loadouts_probabilities.get("p_SPs", 0)
        p_SO = self.loadouts_probabilities.get("p_SO", 0)
        p_PsO = self.loadouts_probabilities.get("p_PsO", 0)

        primary_secondary_pistol = 0
        primary_secondary = 1
        primary_pistol = 2
        primary_only = 3
        secondary_pistol = 4
        secondary_only = 5
        pistol_only = 6
        pick = -1

        if not (random.randint(1, 100) <= p_knife * 100):
            # not knife only
            pick = random.choice(
                [primary_secondary_pistol] * (int)(p_PSPs * 100) \
                + [primary_secondary] * (int)(p_PS * 100) \
                + [primary_pistol] * (int)(p_PPs * 100) \
                + [primary_only] * (int)(p_PO * 100) \
                + [secondary_pistol] * (int)(p_SPs * 100) \
                + [secondary_only] * (int)(p_SO * 100) \
                + [pistol_only] * (int)(p_PsO * 100)
            )

        weapstack = []
        pistolstack = []
        grenadestack = []
        if pick in {primary_secondary, secondary_pistol, secondary_only, primary_secondary_pistol}:
            weapstack += list(filter(lambda i: i not in self.banned_items+self.config_g_gear, gear_type["secondary"]))
        if pick in {primary_secondary, primary_pistol, primary_only, primary_secondary_pistol}:
            weapstack += list(filter(lambda i: i not in self.banned_items+self.config_g_gear, gear_type["primary"]))
        if pick == primary_secondary:
            weapstack.remove('c')
        if pick in {primary_pistol, primary_secondary_pistol, pistol_only}:
            pistolstack = list(filter(lambda i: i not in self.banned_items+self.config_g_gear, gear_type["sidearm"]))
        if random.randint(1, 100) <= p_nades * 100:
            grenadestack = list(filter(lambda i: i not in self.banned_items+self.config_g_gear, gear_type["grenade"]))
        itemstack = list(filter(lambda i: i not in self.banned_items+self.config_g_gear, gear_type["item"]))
        for stack in [pistolstack, weapstack, grenadestack, itemstack]:
            random.shuffle(stack)

        gearstring[0] = pistolstack.pop() if len(pistolstack) else 'A'  # ! always occupied
        gearstring[1] = weapstack.pop() if len(weapstack) else 'A'
        weapstack = [w for w in weapstack if w not in gear_type["primary"]]
        if not self.loadout_is_full(gearstring) and not pick == secondary_only:
            gearstring[2] = weapstack.pop() if len(weapstack) else 'A'
        if not self.loadout_is_full(gearstring) or gearstring[1] == 'c':
            gearstring[3] = grenadestack.pop() if len(grenadestack) else 'A'
        if not self.loadout_is_full(gearstring) or (gearstring[1] == 'c' and gearstring[3] == 'A'):
            gearstring[6] = itemstack.pop() if len(itemstack) else 'A'
        if not self.can_use_silencer(gearstring) and 'U' in gearstring:
            gearstring[gearstring.index('U')] = 'A'
        if not self.can_use_laser(gearstring) and 'V' in gearstring:
            gearstring[gearstring.index('V')] = 'A'

        return "".join(gearstring)

    def loadout_cycle(self):
        old_loadout = self.current_loadout
        self.current_loadout = self._loadout_generate()
        while (self.current_loadout == old_loadout or self.current_loadout in self.banned_loadouts) and not len(self.loadouts_presets) == 1:
            self.current_loadout = self._loadout_generate()
        # workaround to produce a valid gear string for sv_forcegear
        self.g_gear = ""
        if self.current_loadout[1] == 'A':
            self.g_gear += gear_type["primary"]
        if self.current_loadout[2] == 'A' and self.current_loadout[1] not in gear_type["secondary"]:
            self.g_gear += gear_type["secondary"]
        if self.current_loadout[0] == 'A':
            self.g_gear += gear_type["sidearm"]
            self.current_loadout = "G" + self.current_loadout[1:]
            if self.current_loadout[0:3].count('A') == 3:
                if self.current_loadout[3] in gear_type["grenade"]:
                    self.current_loadout = "GL" + self.current_loadout[2:]
        self.loadout_announcement = self.loadout_to_msg(self.current_loadout)
