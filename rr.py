#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################
#                                                            #
#         Tento program je šířen pod licencí GNU/GPLv2.      #
#         Může sním být naloženo podle této licence.         #
#         Autor nenese žádnou zodpovědnost za škody          #
#         způsobené tímto programem. Plně znění              #
#         licence je dodáno společně se zdrojovými           #
#         kódy programu v anglické i české verzi.            #
#                                                            #
#         Autor: Adam Štrauch                                #
#         jabber: cx@jabber.cz                               #
#         email: creckx@gmail.com                            #
#                                                            #
###########################################################

import os,signal,sys

pid = 0

try:
	f = open("pid","r")
	pid = int(f.read().strip())
	f.close()
except:
	print "Nepodařilo se otevřít soubor s PID. :("

if pid > 0:
	os.kill(pid,signal.SIGTERM)
	os.system("python rodger.py")
	sys.exit()
else:
	print "PID neexistuje."