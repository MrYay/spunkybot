from gunfight import *

class Server:
  def __init__(self,g_gear,sv_forcegear):
    self.g_gear = g_gear	
    self.sv_forcegear = sv_forcegear	
  
  def get_cvar(self, cvar):
    if cvar == 'g_gear':
      return(self.g_gear)
    return("")

  def send_rcon(self, cmd):
    print "rcon: [%s]" % cmd
    if "set g_gear" in cmd:
      newgear = cmd.split(" ")[2]
      self.g_gear = newgear
    if "set sv_forcegear" in cmd:
      newfgear = cmd.split(" ")[2]
      self.sv_forcegear = newfgear

class VirtuaGame:
  def __init__(self, maxrounds = 15, g_gear = "", sv_forcegear = ""):
    self.maxrounds = maxrounds
    self.g_gear = g_gear
    self.sv_forcegear = sv_forcegear
    self.gunfight_loadout = sv_forcegear
    self.gunfight_presets = ""
    self.default_gear = ""
    self.roundcount = 0
    self.game = Server(g_gear,sv_forcegear)

  def Start(self):
    print("Game started!")
    print("=============")

  def Launch(self):
    self.Start()
    gunfight_next_loadout(self)
    while self.roundcount != self.maxrounds:
        self.Round()
    self.End()

  def Status(self):
    print("g_gear:[{0}]\nsv_forcegear:[{1}]".format(self.game.g_gear,self.game.sv_forcegear))

  def ActualLoadout(self):
    ggearlist = list(self.game.g_gear)
    forcegearlist = list(self.game.sv_forcegear)
    for g in ggearlist:
	for i in range(0,len(forcegearlist)):
		if forcegearlist[i] == g:
			forcegearlist[i] == 'A'
    return "".join(forcegearlist)

  def Round(self):
    self.roundcount += 1
    print "[ROUND START]"
    expected = gunfight_print_loadout(self.game.sv_forcegear,self.game.g_gear)
    actual = gunfight_print_loadout(self.ActualLoadout(),self.game.g_gear)
    print "\t\t\t\t\t=== %s ===" % expected 
    if expected != actual:
      print "[LOADOUT ERROR]" 
    print "[Round %d] " % self.roundcount,
    print "g_gear: [%s]" % self.game.g_gear
    print "[Round %d] " % self.roundcount,
    print "sv_forcegear: [%s]" % self.game.sv_forcegear
    print "[ROUND END]"
    print("----")
    if not self.roundcount % 2:
      print "[Round %d] LOADOUT CHANGE!" % self.roundcount
      gunfight_next_loadout(self)
    #print("Round {} ended".format(self.roundcount))

  def End(self):
    print("===========")
    print("Game ended!")
    print("Total rounds played: {}".format(self.roundcount))
    print("+++++++++++")
    print("+++++++++++")

if __name__ == "__main__":
    gfg = VirtuaGame(999)
    gfg.Launch()
