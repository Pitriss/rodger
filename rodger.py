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
##############################################################

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#
# Posílejte patche !!
# Je potřeba trochu vylepšit koncepci, moduly by měli být oddělený, ale netušim jak to udělat.
# Na toho daemona by to možná chtělo vytvořit klasickej bash script.
# 
#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

import xmpp,sys,time,random,urllib,re,xml,os

#modul jedna - odpovědi
def responses(f,body,c):
	if body[0] == ".":
		return ""
	
	if ":" in body:
		n = body[11:]
	else:
		n = body
	
	f = open("responses.txt","r")
		
	msg_if  = []
	msg_ano = []

	for x in f.readlines():
		try:
			s = x.split(":")
			
			if s[0] == "":
				ns = ""
				i=0
				for y in s:
					if y != s[0]:
						if i != 0:
							ns += ":"
						ns += y
						i+=1
				msg_ano.append(ns)
			else:
				msg_if.append(s)
		except IndexError:
			s = []
			s[0] = ""
			s[1] = ""
	
	maybe = []
	#podmíněné reakce
	for x in msg_if:
		if x[0].strip() in n:
			ns = ""
			i = 0
			for y in x:
				if y != x[0]:
					if i != 0:
						ns += ":"
					ns += y
					i+=1
			maybe.append(ns.strip())
	
	#nepodmíněné reakce
	if len(maybe) == 0:
		maybe = msg_ano
	
	r = random.randint(0,len(maybe)-1)

	return maybe[r].strip()

# druhý modul pro nahrávání nových spojení
def write(f,body,c):
	if body[0:6] == ".learn" and ":" in body[7:]:	
		f = open("responses.txt","a")
		
		f.write("\n"+body[7:])
		
		f.close()
		
		return "???????? >>> :-|"
	else:
		return ""

#třetí modul s rss funkcemi
class rss:
	def __init__(self):
		self.t = ""
		self.i = 0
		self.out = ""
		self.count = 1

	def startE(self,name,attrs):
		if name == "item":
			self.i = 1
		
		if self.i == 1:
			self.t = name

		
	def endE(self,name):
		if self.count <= 4:
			if self.t == "title":
				self.out += "\n"
			if self.t == "link":
				self.out += "\n"
				self.count += 1
		
		self.t = ""
		
	def data(self,data):
		if self.count <= 4:
			if self.t == "title":
				self.out += data
			if self.t == "link":
				self.out += data

	def get(self,f,body,c):
		self.__init__()
		
		rss = {}
		rss["cx"]             = "http://about.bike-web.org/rss.php"
		rss["abc"]            = "http://www.abclinuxu.cz/auto/abc.rss"
		rss["abc-zpravicky"]  = "http://www.abclinuxu.cz/auto/zpravicky.rss"
		rss["abc-blogy"]      = "http://www.abclinuxu.cz/auto/blog.rss"
		rss["root"]           = "http://rss.root.cz/2/clanky/"
		rss["root-zpravicky"] = "http://rss.root.cz/2/zpravicky/"
		rss["actinet"]        = "http://www.actinet.cz/rss.xml"
		
		try:
			chanel = rss[body[5:]]
		except:
			chanel = ""
		
		if body[0:4] == ".rss" and len(chanel) > 0:
			#načteme rssko
			f = urllib.urlopen(chanel)
			r = f.read()
			f.close()
	
			#získame z něho data
			p = xml.parsers.expat.ParserCreate()

			p.StartElementHandler = self.startE
			p.EndElementHandler = self.endE
			p.CharacterDataHandler = self.data

			p.Parse(r)
			return self.out.encode("utf8")
		elif body[0:4] == ".rss":
			data = "RSS čtečka čte následující servery: "
			i=0
			for x in rss:
				if i != 0:
					data += ", "
				data += x
				i+=1
			
			return data
		else:
			return ""

crss = rss()

#modul 5 - počasí
def weather(f,body,c):
	if body[0:7] == ".pocasi":
		f = urllib.urlopen("http://www.e-pocasi.cz/")
		r = f.read()
		f.close()
		r = r.decode("iso-8859-2")

		#vysekáme info o počasí
		p = re.compile("\<div class\=\"right\-forecast\"\>.{20,450}\<div class\=\"clear\"\>\<\/div\>",re.S)
		g = p.findall(r)
		data = []
	
		#ještě více detaijlněji rozsekáme
		for x in g:
			temp = {}
			try:
				p = re.compile("\<div class\=\"right\-forecast\-head\"\>.*\<\/div\>")
				temp["date"]  = p.findall(x)[0][33:-6]
				p = re.compile("Den\: \<span class\=\"orange\"\>.{3,10}\&deg\;\<\/span\>",re.S)
				temp["day"]   = p.findall(x)[0][26:-12]
				p = re.compile("Noc\: \<span class\=\"orange\"\>.{3,10}\&deg\;\<\/span\>",re.S)
				temp["night"] = p.findall(x)[0][26:-12]
			except IndexError:
				return u"Chyba v regulárním výrazu."
			data.append(temp)

		#složíme text
		text = ""
		for x in data:
			text += x["date"]+":"+" "+x["day"]+u"°C ve dne a "+x["night"]+u"°C v noci\n"
		
		text += "www.e-pocasi.cz"
		
		return text.encode("utf8")
	
	return ""

#modul 4 - autorizace
def autorize(f,body,c):
	if body[0:5] == ".auth":
		jid = body[6:]
		if len(jid) == 0:
			return ""
		
		c.send(xmpp.protocol.Presence(to=jid, typ='subscribed'))
		return "User autorizován"
		
	elif body[0:7] == ".deauth":
		jid = body[0:8]
		if len(jid) == 0:
			return ""
		
		c.send(xmpp.protocol.Presence(to=jid, typ='unsubscribed'))
		return "User odautorizován"

	return ""

#modul 6 - kernely
def kernels(f,body,c):
	if body[0:8] == ".kernels":
		f = urllib.urlopen("http://kernel.org/")
		r = f.read()
		f.close()

		p = re.compile("\>([0-9]{1,2}[\.\-][0-9]{1,2}[\.\-][0-9]{1,2}[a-z0-9\-\.]{0,20})",re.S)
		g = p.findall(r)

		text = "Aktuální jádra: "
		prvx = ""
		for x in g:
			if x != prvx:
				text += x+", "
				prvx = x

		return text[:-2]
	
	return ""

#modul 8 - multi action modul - pro více jednoduchých akcí
def multi(f,body,c):
	if body[0:5] == ".help":
		f = open("help","r")
		r = f.read()
		f.close()

		return r
	#kdo má dneska svátek
	elif body[0:7] == ".svatek":
		svatky = []
		svatky.append(["Nový rok","Karina","Radmila","Diana","Dalimil","Tři králové","Vilma","Čestmír","Vladan","Břetislav","Bohdana","Pravoslav","Edita","Radovan","Alice","Ctirad","Drahoslav","Vladislav","Doubravka","Ilona","Běla","Slavomír","Zdeněk","Milena","Miloš","Zora","Ingrid","Otýlie","Zdislava","Robin","Marika"])
		svatky.append(["Hynek","Nela a Hromnice","Blažej","Jarmila","Dobromila","Vanda","Veronika","Milada","Apolena","Mojmír","Božena","Slavěna","Věnceslav","Valentýn","Jiřina","Ljuba","Miloslav","Gizela","Patrik","Oldřich","Lenka","Petr","Svatopluk","Matěj","Liliana","Dorota","Alexandr","Lumír","Horymír a Rufin"])
		svatky.append(["Bedřich","Anežka","Kamil","Stela","Kazimír","Miroslav","Tomáš","Gabriela","Františka","Viktorie","Anděla","Řehoř","Růžena","Růt","Ida","Elena","Vlastimil","Eduard","Josef","Světlana","Radek","Leona","Ivona","Gabriel","Marián","Emanuel","Dita","Soňa","Taťána","Arnošt","Kvido"])
		svatky.append(["Hugo","Erika","Richard","Ivana","Miroslava","Vendula","Heřman","Ema","Dušan","Darja","Izabela","Julius","Aleš","Vincenc","Anastázie","Irena","Rudolf","Valérie","Rostislava","Marcela","Alexandra","Evžénie","Vojtěch","Jiří","Marek","Oto","Jaroslav","Vlastislav","Robert","Blahoslav"])
		svatky.append(["Svátek práce","Zikmund","Alexej","Květoslav","Klaudie","Radoslav","Stanislav","Státní svátek","Ctibor","Blažena","Svatava","Pankrác","Servác","Bonifác","Žofie","Přemysl","Aneta","Nataša","Ivo","Zbyšek","Monika","Emil","Vladimír","Jana","Viola","Filip","Valdemar","Vilém","Maxmilián","Ferdinand","Kamila"])
		svatky.append(["Laura","Jarmil","Tamara","Dalibor","Dobroslav","Norbert","Iveta","Medard","Stanislava","Otta","Bruno","Antonie","Antonín","Roland","Vít","Zbyněk","Adolf","Milan","Leoš","Květa","Alois","Pavla","Zdeňka","Jan","Ivan","Adriana","Ladislav","Lubomír","Petr a Pavel","Šárka"])
		svatky.append(["Jaroslava","Patricie","Radomír","Prokop","Cyril a Metoděj","Mistr Jan Hus","Bohuslava","Nora","Drahoslava","Libuše","Olga","Bořek","Markéta","Karolína","Jindřich","Luboš","Martina","Drahomíra","Čeněk","Ilja","Vítězslav","Magdaléna","Libor","Kristýna","Jakub","Anna","Věroslav","Viktor","Marta","Bořivoj","Ignác"])
		svatky.append(["Oskar","Gustav","Miluše","Dominik","Kristián a Milivoj","Oldřiška","Lada","Soběslav","Roman","Vavřinec","Zuzana","Klára","Alena","Alan a Sylva","Hana","Jáchym","Petra","Helena","Ludvík","Bernard","Johana","Bohuslav","Sandra","Bartoloměj","Radim","Luděk","Otakar","Augustýn","Evelína","Vladěna","Pavlína"])
		svatky.append(["Linda","Adéla","Bronislav","Jindřiška","Boris","Boleslav","Regina","Mariana","Daniela","Irma","Denisa","Marie","Lubor","Radka","Jolana","Ludmila","Naděžda","Kryštof","Zita","Oleg","Matouš","Darina","Berta","Jaromír","Zlata","Andrea","Jonáš","Václav","Michal","Jeroným"])
		svatky.append(["Igor","Olivie","Bohumil","František","Eliška","Hanuš","Justýna","Věra","Štefan","Marina","Andrej","Marcel","Renáta","Agáta","Tereza","Havel","Hedvika","Lukáš","Michaela","Vendelín","Brigita","Sabina","Teodor","Nina","Beáta","Erik","Šarlota","Státní svátek","Silvie","Tadeáš","Štěpánka"])
		svatky.append(["Felix","Památka zesnulých","Hubert","Karel","Miriam","Liběna","Saskie","Bohumír","Bohdan","Evžen","Martin","Benedikt","Tibor","Sáva","Leopold","Otmar","Mahulena","Romana","Alžběta","Nikola","Albert","Cecílie","Klement","Emílie","Kateřina","Artur","Xenie","René","Zina","Ondřej"])
		svatky.append(["Iva","Blanka","Svatoslav","Barbora","Jitka","Mikuláš","Ambrož","Květoslava","Vratislav","Julie","Dana","Simona","Lucie","Lýdie","Radana","Albína","Daniel","Miloslav","Ester","Dagmar","Natálie","Šimon","Vlasta","Adam a Eva","1. svátek vánoční","Štěpán","Žaneta","Bohumila","Judita","David","Silvestr"])
		
		date = body[8:]
		
		if "." in date:
			e = date.split(".")
			try:
				d = int(e[0])
				m = int(e[1])
			except IndexError:
				return ""
			
			try:
				text = "Toto datum má svátek "+svatky[m-1][d-1]
			except:
				return ""
		
		else:
			m = int(time.strftime("%m"))
			d = int(time.strftime("%d"))
			
			text = "Svátek má dnes "+svatky[m-1][d-1]

		return text
		
	#spočítá hlášky v komunikační databázi	
	elif body[0:7] == ".hlasky":
		f = open("responses.txt","r")
		r = f.read()
		r = r.split("\n")
		f.close()
	
		return "Už umím "+str(len(r))+" hlášek a reakcí."
	
	#topka
	elif body[0:4] == ".top":
		f = open("top","r")
		r = f.readlines()
		f.close()
		
		user = body[5:]

		users = []
		bods = []
	
		for x in r:
			if x.strip() != "":
				e = x.strip().split(":")
				e[1] = int(e[1])
				e[2] = float(e[2])
				users.append(e)
				bods.append(e[2])


		bods.sort()
		bods.reverse()

		if len(user) == 0:
			text = "\nTabulka nejdrsnějších spamerů:\n"
		else:
			text = ""

		#vypíšeme 10 prvním userů
		if len(user) == 0:
			i=1
			for x in bods:
				for y in users:
					if y[2] == x:
						text += str(i)+". "+y[0]+" napsal "+str(y[1])+" zpráv a dostal za ně "+str(y[2])+" bodů. ("+str(round(y[2]/y[1],2))+" na jednu zprávu)\n"
						i+=1
	
				if i > 10:
					break
		#pokud hledáme konkrétní nick
		else:
			i=1
			for x in bods:
				for y in users:
					if y[0] == user and y[2] == x:
						text += str(i)+". "+y[0]+" napsal "+str(y[1])+" zpráv a dostal za ně "+str(y[2])+" bodů. ("+str(round(y[2]/y[1],2))+" na jednu zprávu)\n"
					if y[2] == x:
						i+=1

				if len(text) > 0:
					break

		return text[:-1]
	#zakázaná slova
	elif body[0:4] == ".bad":
		f = open("badwords","r")
		r = f.read()
		f.close()
		
		words = r.strip().split(",")
		
		text = "Seznam špatných slov (za špatné slovo 10 bodů dolů):\n"
		for x in words:
			text += x+","
		
		return text[:-1]
		
	elif body[0:5] == ".news":
		f = open("news","r")
		r = f.read()
		f.close()
		
		return r
	
	return ""

#modul 9 - topka
def top(f,body,c):
	if f == "Ubuntik[X]":
		return 0
	
	#otevřeme soubor
	try:
		fi = open("top","r")
		r = fi.readlines()
		fi.close()
	except IOError:
		r = []
	
	#vypočteme počet bodů
	bods = float(0.2)+(float(len(body))/100)
	
	#zakázaná slova
	f_bad = open("badwords","r")
	r_mess = f_bad.read()
	f_bad.close()
		
	words = r_mess.strip().split(",")
	for x in words:
		if x.lower() in body.lower():
			bods -= float(10)
	
	#zapíšeme data do paměti
	users = []
	
	for x in r:
		if x.strip() != "":
			e = x.strip().split(":")
			e[1] = int(e[1])
			e[2] = float(e[2])
			users.append(e)
	
	i = 0
	ch = 0
	for x in users:
		if x[0] == f:
			users[i][1] += 1
			users[i][2] += bods
			ch = 1
		i+=1
	
	if ch == 0:
		new_user = []
		new_user.append(f)
		new_user.append(1)
		new_user.append(bods)
		users.append(new_user)
	
	#vgenerujeme nový soubor
	fi = open("top","w")
	
	for x in users:
		fi.write(str(x[0])+":"+str(x[1])+":"+str(x[2])+"\n")
	
	fi.close()
	
	return ""

#modul 10 - statistika
def stat(f,body,c):
	if body[0:5] != ".stat":
		return ""
	
	#topka
	f = open("top","r")
	r = f.readlines()
	f.close()
		
	data = []
	points = float(0)
	messages = float(0)
	lpoints = []
	for x in r:
		e = x.strip().split(":")
			
		odata = {}
		odata["Nick"]      = e[0]
		odata["CMessages"] = int(e[1])
		odata["Points"]    = float(e[2])
		lpoints.append(float(e[2]))
		points += float(e[2])
		messages += int(e[1])
		data.append(odata)
	
	lpoints.sort()
	lpoints.reverse()
	
	who = ""
	for x in data:
		if x["Points"] == lpoints[0]:
			who = x["Nick"]
			break

	#výstup
	text = "\n"
	text += "---------------------------------------\n"
	text += "|      Statistika bota na linjabu     |\n"
	text += "---------------------------------------\n"
	text += "Nejvetší spamer: "+who+"\n"
	text += "Počet příspěvků: "+str(messages)+"\n"
	text += "Počet bodů: "+str(points)+"\n"
	text += "Celkový počet lidí: "+str(len(r))+"\n"
	text += "Aktuální čas: "+str(time.strftime("%H:%M:%S %d.%m.%Y"))+"\n"
	#text += "---------------------------------------\n"
	text += ""
	
	return text

class rg:
	#připojení
	def __init__(self):	
		jid=xmpp.protocol.JID("rodger@example.com")

		self.c = xmpp.Client(jid.getDomain(),debug=[])

		self.c.connect()
		self.c.auth(jid.getNode(),"heslo")
		
		self.c.RegisterHandler('presence',self.presenceH)
		self.c.RegisterHandler('iq',self.iqH)
		self.c.RegisterHandler('message',self.messageH)
	
		self.c.sendInitPresence()
		
		self.conGCH()
		
		self.conTS = time.time()
	
	#přihlášení do groupechatu
	def conGCH(self):
		self.c.send(xmpp.protocol.Presence(to="ubuntu@chat.example.com/Ubuntik[X]"))
	
	def disConGCH(self):
		self.c.send(xmpp.protocol.Presence(to="ubuntu@chat.example.com/Ubuntik[X]",typ="unavailable"))
	
	#postaráme se o zprávu
	def messageH(self,conn,mess_node):
		t = mess_node.getType()
		
		if t == "chat":
			f = str(mess_node.getFrom())
			n = str(mess_node.getFrom().getNode())
			#print "Z chatu - "+mess_node.getBody();
			
			fm = [responses,multi,weather,kernels,write,crss.get,autorize,stat]
		elif t == "groupchat":
			f = str(mess_node.getFrom().getNode())+"@"+str(mess_node.getFrom().getDomain())
			n = str(mess_node.getFrom().getResource())
			#print "Z group chatu - "+mess_node.getBody();
			
			fm = [responses,multi,weather,top,kernels,write,crss.get,autorize,stat]
		else:
			#print t
			fm = [responses,multi,weather,kernels,write,crss.get,autorize,stat]
		
		#zpracování messgaů
		if self.conTS+10 < time.time():
			for x in fm:
				s = x(n,mess_node.getBody().encode("utf8"),conn)
				if ((mess_node.getBody()[0:10] == "Ubuntik[X]" and t == "groupchat") or t == "chat" or mess_node.getBody()[0] == ".") and len(s) > 0:
					self.c.send(xmpp.protocol.Message(to=f,typ=mess_node.getType(),body=n+": "+s))
	
	def iqH(self,conn,iq_node):
		pass
	
	def presenceH(self,conn,presence_node):
		pass

	def process(self):
		while 1:
			try:
				self.c.Process(1)
			except KeyboardInterrupt:
				self.disConGCH()
				#print "Konec."
				sys.exit(0)

#daemon - moc tomu nerozumim, hlavně proč se tvořej dva forky, je to trochu složitější :)
#Vytvoříme první fork
try:
	pid = os.fork()
	if pid > 0:
		#a původní zabijeme
		sys.exit(0)
except OSError, e:
	print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror) 
	sys.exit(1)

#tímhle oddělíme forky od sebe
os.chdir("/home/cx/rodger")
os.setsid() 
os.umask(0) 

#vytvoříme další fork
try:
	pid = os.fork() 
	if pid > 0:
	#zabijeme první fork a vrátíme pid damemona
		print "Daemon PID %d" % pid
		
		#zapíšeme PID daemona
		f = open("pid","w")
		f.write(str(pid))
		f.close()
		
		sys.exit(0)
except OSError, e:
	print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror)
	sys.exit(1)

r = rg()
r.process()