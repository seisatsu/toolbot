# Toolbot v2 - By Seisatsu
#
##	This program is free software. It comes without any warranty, to
##	the extent permitted by applicable law. You can redistribute it
##	and/or modify it under the terms of the Do What The Fuck You Want
##	To Public License, Version 2, as published by Sam Hocevar. See
##	http://sam.zoy.org/wtfpl/COPYING for more details.

import platform, os, random, subprocess, socket

def randomProxy(): #Return a random line from the proxy list
	proxylist='proxylist.txt'
	proxyfile=open(proxylist,'r')
	file_size=os.stat(proxylist)[6]
	proxyfile.seek((proxyfile.tell()+random.randint(0,file_size-1))%file_size)
	proxyfile.readline()
	proxy=proxyfile.readline()
	proxyfile.close()
	return proxy

class Toolbot_Commands:
	"""Container for Toolbot commands"""
	
	def __init__(self, cmd, rto, sender, S):
		self.cmd = cmd
		self.rto = rto
		self.sender = sender
		self.S = S
	
	def help(self, HelpDict):
		if len(self.cmd) == 1:
			self.S.send('PRIVMSG '+self.rto+' :ToolBot Commands: public[help|whois|isup|query|proxy|rnd|choose] owner[msg|join|part|nick|ctcp]\n')
		if len(self.cmd) == 2 and self.cmd[1] in HelpDict:
			self.S.send('PRIVMSG '+self.rto+' :'+HelpDict[self.cmd[1].lower()]+'\n')
	
	def whois(self):
		if platform.system()=='Windows':
			self.S.send('PRIVMSG '+self.rto+' :'+self.sender[0]+': COMMAND UNAVAILABLE\n')
		else:
			os.system('whois '+self.cmd[1]+' | wgetpaste -n ToolBot > whois.tmp')
			whoisfile=open('whois.tmp')
			whois=whoisfile.read()
			whoisfile.close()
			self.S.send('PRIVMSG '+self.rto+' :'+self.sender[0]+': '+whois[29:]+'\n')
	
	def isup(self):
		if self.cmd[1].lower()=='localhost' or self.cmd[1].lstrip('0').startswith('127.') or self.cmd[1].lstrip('0').startswith('192.168.') or self.cmd[1].lstrip('0').startswith('10.0.'):
			return
		if len(self.cmd)==2:
			uport='80'
		elif len(self.cmd)==3:
			uport=self.cmd[2]
		try: #Try to connect
			u=socket.socket()
			u.settimeout(5)
			if len(self.cmd)==2:
				u.connect((self.cmd[1], 80))
				u.close()
			elif len(self.cmd)==3:
				u.connect((self.cmd[1], int(self.cmd[2])))
				u.close()
			self.S.send('PRIVMSG '+self.rto+' :'+self.sender[0]+': Host '+self.cmd[1]+':'+uport+' is UP.\n')
		except socket.error:
			self.S.send('PRIVMSG '+self.rto+' :'+self.sender[0]+': Host '+self.cmd[1]+':'+uport+' is DOWN.\n')
		except ValueError:
			return
	
	def query(self, OptDict):
		if self.cmd[1].lower()=='os': #Return OS info
			if platform.system()=='Windows':
				self.S.send('PRIVMSG '+self.rto+' :OS: Windows '+' '.join(platform.win32_ver())+'\n')
			else:
				os.system('uname -a > query.tmp')
				queryfile=open('query.tmp')
				query=queryfile.read()
				queryfile.close()
				self.S.send('PRIVMSG '+self.rto+' :OS: '+query+'\n')
		if self.cmd[1].lower()=='owners': #Return bot owners
			self.S.send('PRIVMSG '+self.rto+' :Owners: '+', '.join(OptDict['OWNER'])+'\n')
		if self.cmd[1].lower()=='date': #Return bot's local date
			if len(self.cmd)==2:
				if platform.system()=='Windows':
					os.system('date /t > query.tmp')
				else:
					os.system('date +\'%D %r %Z\' > query.tmp')
				queryfile=open('query.tmp')
				query=queryfile.read()
				queryfile.close()
				self.S.send('PRIVMSG '+self.rto+' :Date: '+query+'\n')
	
	def proxy(self):
		goodproxy=0
		while goodproxy==0:
			proxy=randomProxy()
			proxyip=proxy.find(':')
			proxyip2=proxy[:proxyip]
			if platform.system()=='Windows':
				isup=os.system('ping -n 1 -w 2000 '+proxyip2) #Ping to test if proxy is up (windows)
			else:
				isup=os.system('ping -c1 -W2 '+proxyip2) #Ping to test if proxy is up
			if isup==0:
				p=socket.socket()
				p.settimeout(5)
				try:
					p.connect((proxy[:proxyip], int(proxy[proxyip+1:]))) #Connect to test if port is open
					p.close()
				except socket.error:
					p.close()
					continue
				goodproxy=1
				self.S.send('PRIVMSG '+self.rto+' :'+self.sender[0]+': '+proxy+'\n')
	
	def rnd(self):
		try:
			rand=random.randint(int(self.cmd[1]), int(self.cmd[2]))
			self.S.send('PRIVMSG '+self.rto+' :'+self.sender[0]+': '+str(rand)+'\n')
		except ValueError:
			pass
	
	def choose(self):
		choice=random.choice(self.cmd[1:])
		self.S.send('PRIVMSG '+self.rto+' :'+self.sender[0]+': '+choice+'\n')
	
	
