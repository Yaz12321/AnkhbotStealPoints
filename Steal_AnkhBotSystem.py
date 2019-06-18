#---------------------------------------
#	Import Libraries
#---------------------------------------
import clr, sys, json, os, codecs
clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")
import random

#---------------------------------------
#	[Required]	Script Information
#---------------------------------------
ScriptName = "Steal"
Website = ""
Creator = "Yaz12321"
Version = "1.1"
Description = "Viewers can try to steal points from others, they can succeed, fail, get caught, or go to prison (timeout)"

settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")

#---------------------------------------
#   Version Information
#---------------------------------------

# Version:
# > 1.1 <
    # Bug fixed
# > 1.0 <
    # First Release

class Settings:
    # Tries to load settings from file if given 
    # The 'default' variable names need to match UI_Config
    def __init__(self, settingsFile = None):
        if settingsFile is not None and os.path.isfile(settingsFile):
            with codecs.open(settingsFile, encoding='utf-8-sig',mode='r') as f:
                self.__dict__ = json.load(f, encoding='utf-8-sig') 
        else: #set variables if no settings file
            self.OnlyLive = False
            self.Command = "!steal"
            self.Permission = "Everyone"
            self.PermissionInfo = ""
            self.UseCD = True
            self.Cooldown = 0
            self.OnCooldown = "{0} the command is still on cooldown for {1} seconds!"
            self.UserCooldown = 10
            self.OnUserCooldown = "{0} the command is still on user cooldown for {1} seconds!"
            self.BaseResponsewin = "{0} has succeeded in stealing {2} {3} from {1}."
            self.BaseResponselose = "{0} was caught trying to steal from {1}!! {1} agreed to settle for {2} {3} to not call one of the mods!"
            self.BaseResponsefail = "{0} has failed to steal from {1}, but {0} was never caught in the attempt!"
            self.BaseResponsetimeout = "{0} was caught trying to steal from {1}!! {1} refused to settle, and called one of the mods! {0} was timedout for {2} seconds! RIP!"
            self.NotEnoughResponse = "{0} or {1} do not have {4} {2} to attempt stealing!"
            self.Steal = 30
            self.Timeout = 60

            
    # Reload settings on save through UI
    def ReloadSettings(self, data):
        self.__dict__ = json.loads(data, encoding='utf-8-sig')
        return

    # Save settings to files (json and js)
    def SaveSettings(self, settingsFile):
        with codecs.open(settingsFile,  encoding='utf-8-sig',mode='w+') as f:
            json.dump(self.__dict__, f, encoding='utf-8-sig')
        with codecs.open(settingsFile.replace("json", "js"), encoding='utf-8-sig',mode='w+') as f:
            f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8-sig')))
        return


#---------------------------------------
# Initialize Data on Load
#---------------------------------------
def Init():
    # Globals
    global MySettings

    # Load in saved settings
    MySettings = Settings(settingsFile)

    # End of Init
    return

#---------------------------------------
# Reload Settings on Save
#---------------------------------------
def ReloadSettings(jsonData):
    # Globals
    global MySettings

    # Reload saved settings
    MySettings.ReloadSettings(jsonData)

    # End of ReloadSettings
    return

def Execute(data):
    if data.IsChatMessage() and data.GetParam(0).lower() == MySettings.Command:
       
        #check if command is in "live only mode"
        if MySettings.OnlyLive:

            #set run permission
            startCheck = data.IsLive() and Parent.HasPermission(data.User, MySettings.Permission, MySettings.PermissionInfo)
            
        else: #set run permission
            startCheck = True
        
        #check if user has permission
        if startCheck and  Parent.HasPermission(data.User, MySettings.Permission, MySettings.PermissionInfo):
            
            #check if command is on cooldown
            if Parent.IsOnCooldown(ScriptName,MySettings.Command) or Parent.IsOnUserCooldown(ScriptName,MySettings.Command,data.User):
               
                #check if cooldown message is enabled
                if MySettings.UseCD: 
                    
                    #set variables for cooldown
                    cooldownDuration = Parent.GetCooldownDuration(ScriptName,MySettings.Command)
                    usercooldownDuration = Parent.GetUserCooldownDuration(ScriptName,MySettings.Command,data.User)
                    
                    #check for the longest CD!
                    if cooldownDuration > usercooldownDuration:
                    
                        #set cd remaining
                        m_CooldownRemaining = cooldownDuration
                        
                        #send cooldown message
                        Parent.SendTwitchMessage(MySettings.OnCooldown.format(data.User,m_CooldownRemaining))
                        
                        
                    else: #set cd remaining
                        m_CooldownRemaining = Parent.GetUserCooldownDuration(ScriptName,MySettings.Command,data.User)
                        
                        #send usercooldown message
                        Parent.SendTwitchMessage(MySettings.OnUserCooldown.format(data.User,m_CooldownRemaining))
            
            else: #check if user got enough points

                              
                if MySettings.Steal <= Parent.GetPoints(data.User) and MySettings.Steal <= Parent.GetPoints(data.GetParam(1)):

                    options = ['lose','win','fail','timeout']
                    result = random.choice(options)
                    payout = Parent.GetRandom(0,MySettings.Steal+1)

                    if result == "lose":
                        Parent.RemovePoints(data.User, data.UserName, payout)
                        Parent.AddPoints(data.GetParam(1),data.GetParam(1),payout)
                        Parent.SendTwitchMessage(MySettings.BaseResponselose.format(data.UserName,data.GetParam(1),payout,Parent.GetCurrencyName()))

                    if result == "win":
                        Parent.AddPoints(data.User, data.UserName, payout)
                        Parent.RemovePoints(data.GetParam(1),data.GetParam(1),payout)
                        Parent.SendTwitchMessage(MySettings.BaseResponsewin.format(data.UserName,data.GetParam(1),payout,Parent.GetCurrencyName()))

                    if result == "fail":
                        Parent.SendTwitchMessage(MySettings.BaseResponsefail.format(data.UserName,data.GetParam(1)))

                    if result == "timeout":
                        Parent.SendTwitchMessage(MySettings.BaseResponsetimeout.format(data.UserName,data.GetParam(1),MySettings.Timeout))
                        timeoutuser = "/timeout {} {}".format(data.User,MySettings.Timeout) 
                        Parent.SendTwitchMessage(timeoutuser)                  

                    # add cooldowns
                    Parent.AddUserCooldown(ScriptName,MySettings.Command,data.User,MySettings.UserCooldown)
                    Parent.AddCooldown(ScriptName,MySettings.Command,MySettings.Cooldown)
                
                else:
                    #send not enough currency response
                    Parent.SendTwitchMessage(MySettings.NotEnoughResponse.format(data.UserName,data.GetParam(1),Parent.GetCurrencyName(),MySettings.Command,MySettings.Steal))
    return

def Tick():
    return

def UpdateSettings():
    with open(m_ConfigFile) as ConfigFile:
        MySettings.__dict__ = json.load(ConfigFile)
    return
