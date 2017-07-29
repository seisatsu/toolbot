# Toolbot v2 - By Seisatsu
#
##	This program is free software. It comes without any warranty, to
##	the extent permitted by applicable law. You can redistribute it
##	and/or modify it under the terms of the Do What The Fuck You Want
##	To Public License, Version 2, as published by Sam Hocevar. See
##	http://sam.zoy.org/wtfpl/COPYING for more details.

import platform, os, random, subprocess, socket, time, hashlib, binascii

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
			self.S.send('PRIVMSG '+self.rto+' :ToolBot Commands: public[help|sigil|rnd|choose] owner[msg|action|join|part|nick|ctcp|owner|quit]\n')
		if len(self.cmd) == 2 and self.cmd[1] in HelpDict:
			self.S.send('PRIVMSG '+self.rto+' :'+HelpDict[self.cmd[1].lower()]+'\n')
	
	def sigil(self):
		try:
			chars = "(){}[]|\\/<>*^v-=+~"

			phrase = ' '.join(self.cmd[1:]).encode()

			m = hashlib.sha256()
			m.update(phrase)
			m.update(str(int(time.time())).encode())
			dig = m.digest()

			sgl = ""

			for byte in dig:
				char = int(binascii.b2a_hex(byte), 16) % len(chars)
				sgl += chars[char]

			self.S.send('PRIVMSG '+self.rto+' :'+self.sender[0]+': '+sgl+'\n')
			
		except ValueError:
			pass
	
	def rnd(self):
		try:
			rand=random.randint(int(self.cmd[1]), int(self.cmd[2]))
			self.S.send('PRIVMSG '+self.rto+' :'+self.sender[0]+': '+str(rand)+'\n')
		except ValueError:
			pass
	
	def choose(self):
		choice=random.choice(self.cmd[1:])
		self.S.send('PRIVMSG '+self.rto+' :'+self.sender[0]+': '+choice+'\n')
	
	
