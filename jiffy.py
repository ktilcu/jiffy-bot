#todo 
#kill user
#finish him
#cmd punctuation
#what is
#mine field
#int in commands
#remove case sensitive
#secondary names
#unfriend
#auth users dump and read json



import socket
import time
import json


HOST = "irc.freenode.net" # Server to connect to
HOME_CHANNEL = "#liberatedAria" # The home channel for your bot
NICK = "Jiffy" # Your bots nick
PORT = 6667 # Port (it is normally 6667)
SYMBOL = "@" #symbol eg. if set to # commands will be #echo.
commFile = "commands.json"
funcFile = "function.json"
blank = ""
##Learning New Commands####

def learnNew(msg, cmd, CHANNEL, user, arg):
  global commandDict
  #load previous dict from file
  with open(commFile, 'r') as f:
    commandDict = json.load(f)
  
  #split keys and values on the equal sign
  value = msg.split("=")[1]
  frontHalf = msg.split("=")[0]
  key = frontHalf.split()[1]
  
  #print commandDict
  #print value

  #check for previous
  if key in commandDict:
    out = "I'm confused, I thought " + key + " meant " + commandDict.get(key)
    sendMessage("priv", CHANNEL, out)
  else:
    out = user + ": Learned " + key
    sendMessage("priv", CHANNEL, out)

  #add to dict
  commandDict[key] = value

  #write new dict to file
  with open(commFile, mode= 'w') as f:
    json.dump(commandDict, f)

def forgetCmd(msg, cmd, CHANNEL, user, arg):
  global commandDict
  if "=" in msg:
    out = "You must use the right syntax to make me forget. Usage:: @forget <command>  No \"=\" signs"
    sendMessage('priv', CHANNEL, out)
    return
  else:
    key = msg.split()[1]
    if key in commandDict:
      #print key
      out = user + ": I forgot " + key
      del commandDict[key]
      #write new dict to file
      with open(commFile, mode= 'w') as f:
        json.dump(commandDict, f)     
    else:
      out = user + ": Don't be a retard. I haven't even learned " + key
    sendMessage('priv', CHANNEL, out)


def authenticateUser(user):
  f = open("authUsers.txt")
  for line in f:
    if user in line:
      out = True
    else:
      sendMessage('priv',CHANNEL, user + " is not permitted to make that decision")
      out = False
    return out

def replyCmd(msg, user):
  if checkForLoop(msg, user):
    out = "Enough " + user + "!"
  else:
    out = commandDict[msg]
  return out

def meetNew(msg, cmd, CHANNEL, user, arg):
  if authenticateUser(user):
    user = msg.split(" ")[1]
    with open("authUsers.txt", "a") as f:
      f.write(user)
  else:
    return

def breakUpWith(msg, cmd, CHANNEL, user, arg):
  file('error.txt', 'w').writelines([l for l in file('validate.txt').readlines() if 'TRUE' not in l])
   
def ping(msg):
  s.send("PONG :"+ msg +"\r\n")

def sendMessage(irctype, channel, message):
  print (irctype + channel + message)
  if irctype == "priv":
    #print "priv true"
    s.send("PRIVMSG "+ channel +" :" + message +"\r\n")
  else:
    #print "priv false"
    s.send("PRIVMSG "+ channel +" :\x01ACTION " + message + " a\x01\r\n")

def listKnown(msg, cmd, CHANNEL, user, arg):
  if authenticateUser(user):
    out = user + ": " + " ".join(["%s" % (k) for k in commandDict.keys()])
    sendMessage('priv', CHANNEL, out)

def notHere(msg, cmd, CHANNEL, user, arg):
  sendMessage('priv', CHANNEL, "")

def bomb(user):
  s.send("PRIVMSG "+ CHANNEL +" :\x01ACTION hurls a bomb in "+ user +"'s direction.\x01\r\n")
  time.sleep(0.5)
  s.send("PRIVMSG "+ CHANNEL +" :BOOM!\n")
  s.send("PRIVMSG "+ CHANNEL +" :\x01ACTION bomb explodes.\x01\r\n")
  s.send("KICK ##aussiepowder "+ user +" Bombed\n")
  time.sleep(1.75)
  s.send("PRIVMSG "+ CHANNEL +" :and you thought you could take a bot with such awesomeness! pfft\n")

def join(chan):
  s.send("JOIN "+ chan +"\r\n")

def checkForLoop(msg, user):
  global loopCount
  if msg in loopCheck:
    loopCount+=1
  if loopCount < 5:
    loopCheck[msg] = user
    return False
  else:
    loopCount = 0
    return True

##########################
##Making the connection###
##########################
def connect(NICK, HOST, PORT, HOME_CHANNEL):
  global s
  s = socket.socket( )
  s.connect((HOST, PORT))
  s.send("USER "+ NICK +" "+ NICK +" "+ NICK +" :bot\n")
  s.send("NICK "+ NICK +"\r\n")
  s.send("JOIN "+ HOME_CHANNEL +"\r\n")

connect(NICK, HOST, PORT, HOME_CHANNEL)
#Loading Commands from last session

with open(commFile, 'r') as f:
  commandDict = json.load(f)

#Loading Function Commands
funcDict = { "@learn": learnNew, "@forget": forgetCmd, "@befriend": meetNew, "@list": listKnown, "@unfriend": breakUpWith}
loopCheck = {}
loopCount = 0
#start the loop to listen for info

while 1:
  line = s.recv(2048)
  line = line.strip("\r\n")
  print (line)
  stoperror = line.split(" ")
  if ("PING :" in line):
    pingcmd = line.split(":", 1)
    pingmsg = pingcmd[1]
    ping(pingmsg)
  elif "KICK " + HOME_CHANNEL + " " + NICK in line:
    join(HOME_CHANNEL)
  elif "PRIVMSG" in line:
    if len(line) < 30:
      print (blank)
    elif len(stoperror) < 4:
      print (blank)

      #parse the info once we get a valid line
    else:
      complete = line.split(":", 2)
      info = complete[1]
      msg = line.split(":", 2)[2] ##the thing that was said
      cmd = msg.split(" ")[0]
      CHANNEL = info.split(" ")[2] ##channel from which it was said
      user = line.split(":")[1].split("!")[0] ## the person that said the thing
      arg = msg.split(" ")
      #check to see if message matches any functions then commands
      if cmd in funcDict:
        funcDict[cmd](msg, cmd, CHANNEL, user, arg)
      elif cmd in commandDict:
        out = replyCmd(cmd, user)
        sendMessage("priv", CHANNEL, out)



##        if "hello " + NICK ==cmd:
##          hello(user)
##          print "recieved hello"
##        elif "hey " + NICK ==cmd:
##          hello(user)
##          "print recieved hello"
##        elif "hi " + NICK ==cmd:
##          hello(user)
##          "print recieved hello"
##        elif SYMBOL + "join"==cmd and len(arg) > 1:
##          x = line.split(" ", 4)
##          newchannel = x[4]
##          joinchan(newchannel)
##        elif SYMBOL + "leave"==cmd and len(arg) > 1:
##          x = line.split(" ", 4)
##          newchannel = x[4]
##          partchan(newchannel)
##        elif SYMBOL + "quit"==cmd:
##          quitIRC()
##        elif SYMBOL + "coke"==cmd and len(arg) > 1:
##          x = line.split(" ")
##          recvr = x[4]
##          coke(recvr)
##        elif SYMBOL + "pepsi"==cmd and len(arg) > 1:
##          x = line.split(" ")
##          recvr = x[4]
##          pepsi(recvr)
##        elif SYMBOL + "fish"==cmd and len(arg) > 1:
##          x = line.split(" ")
##          recvr = x[4]
##          fish(recvr)
##        elif SYMBOL + "bomb"==cmd and len(arg) > 1:
##          x = line.split(" ")
##          recvr = x[4]
##          bomb(recvr)
##        elif SYMBOL + "fish"==cmd:
##          sandwich(user)
##        elif SYMBOL + "cake"==cmd:
##          cake(user)
##        elif SYMBOL + "echo"==cmd:
##          x = msg.split(" ", 1)[1]
##          echo(x)
##        elif "ask"==cmd:
##          ask(user)
##        
##        elif line.find(""+ SYMBOL +"load") != -1:
##          plugin = msg.split(" ")[1]
##          load(plugin)
##       
##        elif line.find(""+ SYMBOL +"unload") != -1:
##          plugin = msg.split(" ")[1]
##          unload(plugin)
##       
##        elif SYMBOL in cmd:
##          fail()














##def joinchan(channel):
##  s.send("PRIVMSG "+ CHANNEL +" :Joining "+ channel +"\r\n")
##  s.send("JOIN "+ channel +"\r\n")
##def partchan(channel):
##  s.send("PRIVMSG "+ CHANNEL +" :Leaving "+ channel +"\r\n")
##  s.send("PART "+ channel +"\r\n")
##def hello(user):
##  s.send("PRIVMSG "+ CHANNEL +" :G'day "+ nick +"!\n")
##def quitIRC():
##  s.send("QUIT "+ CHANNEL +"\n")
##def kickme(target, reason):
##  s.send("KICK "+ CHANNEL +" "+ target +" "+ reason + "\n")
##def fail():
##  s.send("PRIVMSG "+ CHANNEL +" :Either you do not have the permission to do that, or that is not a valid command.\n")
##def fish(user):
##  s.send("PRIVMSG "+ CHANNEL +" :\x01ACTION slaps "+ user +" with a wet sloppy tuna fish.\x01\r\n")
##  time.sleep(1)
##  s.send("PRIVMSG "+ CHANNEL +" :take that bitch\n")
##def sandwich(sender):
##  if food == True:
##     s.send("PRIVMSG "+ CHANNEL +" :\x01ACTION is making "+ sender +" a sandwich\x01\r\n")
##     time.sleep(10)
##     s.send("PRIVMSG "+ CHANNEL +" :\x01ACTION has finished making "+ sender +"'s sandwhich\x01\r\n")
##     time.sleep(1)
##     s.send("PRIVMSG "+ CHANNEL +" :Here you go "+ sender +"! I hope you enjoy it!\r\n")
##  else:
##     s.send("PRIVMSG "+ CHANNEL +" :Command not loaded\r\n")
##def makeitem(nick, item):
##  s.send("PRIVMSG "+ CHANNEL +" :\x01ACTION is making "+ nick +" a "+ item +"\x01\r\n")
##  time.sleep(10)
##  s.send("PRIVMSG "+ CHANNEL +" :\x01ACTION has finished making "+ nick +"'s "+ item +"\x01\r\n")
##  time.sleep(1)
##  s.send("PRIVMSG "+ CHANNEL +" :Here you go "+ nick +"! I hope you enjoy it!\r\n")
##def bomb(user):
##  s.send("PRIVMSG "+ CHANNEL +" :\x01ACTION hurls a bomb in "+ user +"'s direction.\x01\r\n")
##  time.sleep(0.5)
##  s.send("PRIVMSG "+ CHANNEL +" :BOOM!\n")
##  s.send("PRIVMSG "+ CHANNEL +" :\x01ACTION bomb explodes.\x01\r\n")
##  s.send("KICK ##aussiepowder "+ user +" Bombed\n")
##  time.sleep(1.75)
##  s.send("PRIVMSG "+ CHANNEL +" :and you thought you could take a bot with such awesomeness! pfft\n")
##def cake(sender):
##   if food == True: 
##     s.send("PRIVMSG "+ CHANNEL +" :\x01ACTION is making "+ sender +" a cake\x01\r\n")
##     time.sleep(10)
##     s.send("PRIVMSG "+ CHANNEL +" :\x01ACTION has finished making "+ sender +"'s cake\x01\r\n")
##     time.sleep(1)
##     s.send("PRIVMSG "+ CHANNEL +" :Here you go "+ sender +"! I hope you enjoy it!\r\n")
##   else:
##     s.send("PRIVMSG "+ CHANNEL +" :Command not loaded\r\n")
##
##def ask(sender):
##  s.send("PRIVMSG "+ CHANNEL +" :Do not ask if you can ask a question but instead just ask it\r\n")
##def echo(message):
##  s.send("PRIVMSG "+ CHANNEL +" :"+ message +"\r\n") 
##def pepsi(user):
##  if food == True:
##     s.send("PRIVMSG "+ CHANNEL +" :\x01ACTION dispenses a can of Pepsi for "+ user +"\x01\r\n")
##  else:
##     s.send("PRIVMSG "+ CHANNEL +" :Command not loaded\r\n")
##def coke(user):
##  if food == True:
##     s.send("PRIVMSG "+ CHANNEL +" :\x01ACTION dispenses a can of Coke for "+ user +"\x01\r\n")
##  else:
##     s.send("PRIVMSG "+ CHANNEL +" :Command not loaded\r\n")
##def load(plugin):
##  if plugin =="food":
##     global food
##     food = True
##     s.send("PRIVMSG "+ CHANNEL +" :LOADED the FOOD plugin\r\n")
##  else:
##      s.send("PRIVMSG "+ CHANNEL +" :UNKNOWN plugin\r\n")
##     
##def unload(plugin):
##  if plugin =="food":
##     global food
##     food = False
##     s.send("PRIVMSG "+ CHANNEL +" :UNLOADED the FOOD plugin\r\n")
##  else:
##     s.send("PRIVMSG "+ CHANNEL +" :UNKNOWN plugin\r\n")
##
