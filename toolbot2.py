# Toolbot v2 - By Seisatsu
#
##	This program is free software. It comes without any warranty, to
##	the extent permitted by applicable law. You can redistribute it
##	and/or modify it under the terms of the Do What The Fuck You Want
##	To Public License, Version 2, as published by Sam Hocevar. See
##	http://sam.zoy.org/wtfpl/COPYING for more details.

import sys, socket, string, os, sys, subprocess, time
from toolbot_commands import *
from optparse import OptionParser

#Begin Function Definitions

def ParseOpts(OptDict):
	"""Parse options from command line"""
	
	parser = OptionParser(usage='%prog [OPTIONS]\n	   %prog [-h|--help]') #Parse command line arguments
	
	parser.add_option('-H', '--host', dest='HOST', help='server to connect to <REQUIRED>', action='store', 
	type='string', metavar='HOST')
	
	parser.add_option('-p', '--port', dest='PORT', help='port to use', action='store', 
	type='int', metavar='PORT', default=6667)
	
	parser.add_option('-n', '--nick', dest='NICK', help='set nickname', action='store', 
	type='string', metavar='NICK', default='ToolBot')
	
	parser.add_option('-u', '--username', dest='USERNAME', help='set username', action='store', 
	type='string', metavar='USER', default='toolbot')
	
	parser.add_option('-r', '--realname', dest='REALNAME', help='set real name', action='store', 
	type='string', metavar='REALNAME', default='toolbot')
	
	parser.add_option('-i', '--identify', dest='NICKPASS', help='password to identify with nickserv', action='store', 
	type='string', metavar='PASS', default='')
	
	parser.add_option('-o', '--owner', dest='OWNER', help='list of owner nicks, comma delimited <REQUIRED>', action='store', 
	type='string', metavar='OWNER')
	
	parser.add_option('-c', '--channel', dest='CHANNELINIT', help='channel to join', action='store', 
	type='string', metavar='CHANNEL', default='')
	
	parser.add_option('-l', '--logfile', dest='LOGFILE', help='write log to file', action='store', 
	type='string', metavar='LOGFILE', default='')
	
	(options, args) = parser.parse_args()
	
	if not options.HOST or not options.OWNER:
		parser.error('host and owner options are required')
	
	#Populate Option Dictionary
	OptDict['HOST'] = options.HOST
	OptDict['PORT'] = options.PORT
	OptDict['NICK'] = options.NICK
	OptDict['USERNAME'] = options.USERNAME
	OptDict['REALNAME'] = options.REALNAME
	OptDict['NICKPASS'] = options.NICKPASS
	OWNER = options.OWNER.split(',')
	OptDict['OWNER'] = []
	for i in range(len(OWNER)):
		OptDict['OWNER'].append((OWNER[i]+'@'+OptDict['HOST']))
	OptDict['CHANNELINIT'] = options.CHANNELINIT
	if options.LOGFILE:
		OptDict['LOGFILE'] = open(options.LOGFILE, 'a')
	else:
		OptDict['LOGFILE'] = False

def Connect(S, OptDict):
	"""Perform initial IRC connection"""
	
	S.connect((OptDict['HOST'], OptDict['PORT'])) #Connect to server
	S.setblocking(0)
	S.send('NICK '+OptDict['NICK']+'\n') #Send the nick to server
	S.send('USER '+OptDict['USERNAME']+' '+OptDict['HOST']+' bla :'+OptDict['REALNAME']+'\n') #Identify to server
	if len(OptDict['NICKPASS']) > 0:
		S.send('PRIVMSG NICKSERV :IDENTIFY '+OptDict['NICKPASS']+'\n') #Identify with nickserv

def LogMsg(lmsg, OptDict):
	"""Print a message to standard out; write to logfile if logging enabled"""
	
	print lmsg
	if OptDict['LOGFILE']:
		OptDict['LOGFILE'].write(lmsg+'\n')

def ParseMsg(msg, S, authowner, HelpDict, OptDict):
	"""Parse a message from IRC"""
	
	complete = msg[1:].split(':',1) #Split message into sections
	info = complete[0].split(' ')
	try:
		msgpart=complete[1]
	except IndexError:
		return
	sender = info[0].split('!')
	if len(sender)>=2: #Prevent a bizarre error I haven't figured out yet
		if not sender[1] in authowner and (sender[0]+'@'+OptDict['HOST']).lower() in OptDict['OWNER']: #Authenticate owner's hostname by first message
				authowner.append(sender[1])
				LogMsg('Owner '+sender[0]+' bound to hostname '+sender[1], OptDict)
	
	if len(msgpart) > 0:
		if msgpart[0] == '^': #Public Commands
			cmd = msgpart[1:].rstrip().split(' ')
			if info[2] == OptDict['NICK']:
				rto = sender[0]
			else:
				rto = info[2]
				
			TB_Cmd = Toolbot_Commands(cmd, rto, sender, S)
			
			#Begin public command calls
			if cmd[0].lower() == 'help': #Help command
				TB_Cmd.help(HelpDict)
			
			if cmd[0].lower() == 'whois' and len(cmd) == 2: #Whois command
				TB_Cmd.whois()
			
			if cmd[0].lower() == 'isup' and (len(cmd) == 2 or len(cmd) == 3): #Isup command
				TB_Cmd.isup()
			
			if cmd[0].lower() == 'query' and len(cmd) == 2: #Query command
				TB_Cmd.query(OptDict)
			
			if cmd[0].lower() == 'proxy': #Proxy command
				TB_Cmd.proxy()
			
			if cmd[0].lower() == 'rnd' and len(cmd) == 3: #Rnd command
				TB_Cmd.rnd()
			
			if cmd[0].lower() == 'choose' and len(cmd) >= 3: #Choose command
				TB_Cmd.choose()
			
		if msgpart[0] == '^' and sender[1] in authowner: #Owner Commands
			if cmd[0].lower() == 'msg' and len(cmd) >= 3: #Send message
				S.send('PRIVMSG '+cmd[1]+' :'+' '.join(cmd[2:])+'\n')
			
			if cmd[0].lower() == 'join' and len(cmd) == 2: #Make ToolBot join a channel
				S.send('JOIN '+cmd[1]+'\n')
			
			if cmd[0].lower() == 'part' and len(cmd) == 2: #Make ToolBot part from a channel
				S.send('PART '+cmd[1]+'\n')
			
			if cmd[0].lower() == 'nick' and len(cmd) == 2: #Change nick
				S.send('NICK '+cmd[1]+'\n')
			
			if cmd[0].lower() == 'ctcp' and len(cmd) >= 2: #Send CTCP command
				S.send('PRIVMSG '+cmd[1]+' :'+u'\u0001'+' '.join(cmd[2:])+u'\u0001'+'\n')
			
			if cmd[0].lower() == 'owner' and len(cmd) >= 3: #Add/remove owner
				if cmd[1].lower() == 'add':
					for nick in cmd[2:]:
						OptDict['OWNER'].append(nick)
				if cmd[1].lower() == 'remove':
					for nick in cmd[2:]:
						if nick in OptDict['OWNER']:
							OptDict['OWNER'].remove(nick)
		
		if msgpart[0] == '_' and sender[1] in authowner: #Treat msgs with _ as explicit command to send to server
			cmd = msgpart[1:]
			S.send(cmd+'\n')
			if cmd.lower() == 'quit':
				S.close()
				sys.exit(0)

def main():
	"""Main loop"""
	
	linebuf = []
	line = ''
	OptDict = {}
	authowner = []
	HelpDict = { #Dictionary of help info
		'help':		'PUBLIC; Prints help information. Usage: ^help [command]',
		'whois':	'PUBLIC; Performs whois on specified domain. Usage: ^whois <domain>',
		'isup':		'PUBLIC; Checks if host is up. Usage: ^isup <host> [port]',
		'query':	'PUBLIC; Query ToolBot for information. Usage: ^query <os|owners|date>',
		'proxy':	'PUBLIC; Return a working proxy from the list. Usage: ^proxy',
		'rnd':		'PUBLIC; Return a random integer. Usage: ^rnd <min> <max>',
		'choose':	'PUBLIC; Choose one item from a list of choices. Usage: ^choose <a> <b> [c] ...',
		'msg':		'OWNER; Sends a message to nick or channel. Usage: ^msg <nick|channel>',
		'join':		'OWNER; Tells ToolBot to join a channel. Usage: ^join <channel>',
		'part':		'OWNER; Tells ToolBot to part from a channel. Usage: ^part <channel>',
		'nick':		'OWNER; Changes ToolBot\'s nickname. Usage: ^nick <nick>',
		'ctcp':		'OWNER; Send a CTCP command. Usage: ^ctcp <dest> <command> [args]',
		'owner':	'OWNER; Add/remove nick(s) from owner list. Usage: ^owner <add/remove> <nick 1> [nick 2] ...'
	}
	
	S = socket.socket()
	ParseOpts(OptDict)
	Connect(S, OptDict)
	
	while 1:
		try:
			linebuf.extend(S.recv(500).split('\r\n')) #buffer server messages
		except socket.error: #If nothing was received
			lines = 0
		if len(linebuf) > 0:
			if len(linebuf[0]) > 0:
				line = linebuf.pop(0)
				lines = 1
			else:
				linebuf = linebuf[1:]
				if len(linebuf) > 0:
					line = linebuf.pop(0)
					lines = 1
		if len(line) > 0 and lines == 1:
			LogMsg(line+'\n', OptDict) #server message is output
			if line.find('Welcome to') != -1 and OptDict['CHANNELINIT'] != '': #This is crap, but it works.
				S.send('JOIN '+OptDict['CHANNELINIT']+'\n') #Join a channel
			if line.find('PRIVMSG') != -1: #Call a parsing function
				ParseMsg(line, S, authowner, HelpDict, OptDict)
			if line.startswith('PING'): #If server pings then pong
				S.send('PONG '+line[5:]+'\n')
				LogMsg('PONG '+line[5:]+'\n', OptDict)
		else:
			time.sleep(0.001) #Don't eat up cpu time
			continue

#BEGIN
main()
