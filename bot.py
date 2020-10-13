import telebot 
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import InlineQueryResultArticle, InputTextMessageContent
import sqlite3
from sqlite3 import Error as Error_sqlite3
import logging
from telehelper import MessageDistributer, MessageController, Message_mc, TelePoker_message_request
from time import time, sleep
import threading
from copy import copy

TMP = None

class PartyMessage():

	class Timer():
		num_dict = {
		'0':'0️⃣','1':'1️⃣','2':'2️⃣','3':'3️⃣',
		'4':'4️⃣','5':'5️⃣','6':'6️⃣','7':'7️⃣',
		'8':'8️⃣','9':'9️⃣'}

		def __init__(self,num):
			self.val = int(num)

		def __str__(self):
			return self.emj_val()

		def to_emj(self, num):
			if num > 0:
				_str = str(num)
				ans = ''
				for digit in _str:
					ans += self.__class__.num_dict[digit] + ' '
				return ans
			else :
				return self.__class__.num_dict['0'] + ' '
		def emj_val(self):
			if self.val > 0:
				_min = self.val // 60
				_sec = self.val % 60
				if _sec < 10:
					return self.to_emj(_min) + ':' + '0️⃣ '+ self.to_emj(_sec)
				else:
					return self.to_emj(_min) + ':' + self.to_emj(_sec)
			else:
				return 'FINISHED'
		
	def __init__(self,mc):
		#super(PartyMessage, self).__init__()
		self.type = 'txt'
		self.mc = mc
		self.data = 'empty space'
		self.file = None
		self.mrkp = None
		share_link = f"http://t.me/share/url?url={self.mc.encounter.link}"
		join_bttn = InlineKeyboardButton('JoinTheFight',url = share_link )
		#join_bttn = InlineKeyboardButton('JoinTheFight', switch_inline_query = self.mc.encounter.link )
		mark_bttn = InlineKeyboardButton('MarkMe!', callback_data = 'markme')

		self._mrkp_full = InlineKeyboardMarkup(row_width = 2)
		self._mrkp_full.add(join_bttn, mark_bttn)
		self._mrkp_jn = InlineKeyboardMarkup(row_width = 1)
		self._mrkp_jn.add(join_bttn)
		#self.mc.player = player
		#self.party_list = [self.mc.encounter.calling_player]
		#self.mid_lvl = mid_lvl
		#self.mob_str = mob_str
		#self.start_time = start_time
		if self.mc.encounter.type == 'ambush':
			self.time_till_fight = 300
			self.max_party_size = 5
		elif self.mc.encounter.type == 'mobs':
			self.time_till_fight = 180
			self.max_party_size = 2

		self.timer = self.__class__.Timer(self.time_till_fight)

		self.case_dict = {'init': self._countdown, 'countdown':self._countdown, 'finished':self._finish}
		
	def build(self):
		

		row1 = self.case_dict[self.mc.status]() #get 1st row according to mc.status

		#row2 = '\n'.join(self.mc.encounter.mob_str) + '\n\n'
		row2 = f'Mobs mid level : {self.mc.encounter.mid_lvl}\n\n'
		row3 = f'Participating Players[mid lvl : {self.players_mid_lvl()}]\n'
		print([_.username for _ in self.mc.party_list])
		#for pl in self.mc.party_list:
		#	row3 += f"{str(pl.lvl)} : {pl.gamename}\n"
		row3 = self._party()

		self.data = row1 + row2 + row3

		if len(self.mc.party_list) < self.max_party_size and self.mc.status != 'finished':
			self.mrkp = self._mrkp_full
		elif len(self.mc.party_list) >= self.max_party_size and self.mc.status != 'finished':
			self.mrkp = self._mrkp_jn
		elif self.mc.status == 'finished':
			self.mrkp = None

	def _countdown(self):
		self.timer.val = self.time_till_fight - int(time() - self.mc.encounter.start_time)
		return f'======|{str(self.timer)}|======\n'
	def _finish(self):
		return '======|FINISHED|======\n'
	def _party(self): 							#return party string with  numered rows
		_nums = ('1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣')
		ans = ''
		for i in range(self.mc.encounter.max_party_size):
			_pl = ''
			if i  < len(self.mc.party_list):
				_ = self.mc.party_list[i]
				_pl = f"({_.lvl}):{_.gamename}"
			_str = _nums[i] + '#' + _pl + '\n'
			ans += _str
		return ans



	def players_mid_lvl(self):
		_party = copy(self.mc.party_list)
		sum_lvl = 0
		for pl in _party:
			sum_lvl += pl.lvl
		return sum_lvl//len(_party)


	'''
	def build(self):
		#print('building party message')
		if self.mc.status == 'countdown':
			self.timer.val = self.time_till_fight - int(time() - self.mc.encounter.start_time)
			row1 = f'======|{str(self.timer)}|======\n'
		elif self.mc.status == 'init':
			self.timer.val = self.time_till_fight
			row1 = f'=====|{str(self.timer)}|======\n'
		elif self.mc.status == 'finished':
			row1 = '======|FINISHED|======\n'
		#print(f'mob_str {self.mc.encounter.mob_str}')
		row2 = '\n'.join(self.mc.encounter.mob_str) + '\n'
		row3 = 'Participating Players\n'
		for pl in self.mc.party_list:
			row3 += f"{str(pl.lvl)} : {pl.gamename}\n"

		self.data = row1 + row2 + row3

		if len(self.mc.party_list) < self.max_party_size:
			self.mrkp = self._mrkp
		else:
			self.mrkp = None
	'''

class CallingMessage():
	def __init__(self, mc):
		#super(CallingMessage, self).__init__()
		print('CALLING MSG INIT')
		self.type = 'txt'
		self.mc = mc
		self.data = None
		self.file = None
		self.mrkp = None
		#ping requared users
		row1 = '📣📣📣\n'
		row2 = ''
		for pl in self.mc.encounter.players_to_call:
			row2 += f"@{pl}\n"
		self.data = row1 + row2 
		print(self.data)
	def build(self):
		if self.mc.status == 'finished':
			self.mc.send_to_distributer('DeleteMessage', 1)

class CallingMessageController(MessageController):

	"""
	class CallingMessage(Message.Msg):
		def __init__(self, mc):
			super(CallingMessage, self).__init__()
			self.type = 'txt'
			#ping requared users
			row1 = 'Aaaaaaaaaaaaaaa!(c)\n'
			row2 = ''
			for pl in self.mc.encounter.players_to_call:
				row2 += f'@{pl}\n'
			self.data = row1 + row2 

	class PartyMessage(Message.Msg):
		
		def __init__(self,mc):
			super(PartyMessage, self).__init__()
			self.type = 'txt'
			self.mc = mc

			join_bttn = InlineKeyboardButton('JoinTheFight', switch_inline_query = self.mc.encounter.link )
			mark_bttn = InlineKeyboardButton('MarkMe!', callback_data = 'markme')

			self._mrkp = InlineKeyboardMarkup(row_width = 2)
			self._mrkp.add(join_bttn, mark_bttn)
			#self.mc.player = player
			#self.party_list = [self.mc.encounter.calling_player]
			#self.mid_lvl = mid_lvl
			#self.mob_str = mob_str
			#self.start_time = start_time
			if self.mc.encounter.type == 'ambush':
				self.time_till_fight = 300
				self.max_party_size = 5
			elif self.mc.encounter.type == 'mobs':
				self.time_till_fight = 180
				self.max_party_size = 2

			self.timer = self.__class__.Timer()

		def build(self):
			if self.mc.status == 'countdown':
				self.timer.val = self.time_till_fight - int(time - self.mc.encounter.start_time)
				row1 = f'======|{str(self.timer)}|======\n'
			elif self.mc.status == 'init':
				self.timer.val = self.time_till_fight
				row1 = f'=====|{str(self.timer)}|======\n'
			elif self.mc.status == 'finished':
				row1 = '======|FINISHED|======\n'
			row2 = self.mc.encounter.mob_str + '\n'
			row3 = 'Participating Players\n'
			for pl in party_list:
				row3 += f"{str(pl.lvl)} : {pl.gamename}\n"

			self.data = row1 + row2 + row3

			if len(self.mc.party_list) < self.max_party_size:
				self.mrkp = self._mrkp
			else:
				self.mrkp = None
	"""
	class CountdownThread(threading.Thread):

		def __init__(self, mc):
			super(CallingMessageController.CountdownThread, self).__init__()
			self.mc = mc
			self.timer = mc.messages[0].msg.timer
		def run(self):
			self.start_countdown()
		def start_countdown(self):
			while self.timer.val > 0 and self.mc.status == 'countdown' and self.mc.bot.running:
				sleep(4)
				self.mc.build()
				self.mc.send_to_distributer('UpdateMessage',0)
			print(f'countdown while finish')
			self.mc.status = 'finished'


			#self.mc.send_to_distributer('DeleteMessage',1)
			#self.bot.del_mc(self)
			#del self
			self.mc.build()


	def __init__(self, bot, chat_id, md, encounter):
		print(f"{'='*20}\n mc init")

		super(CallingMessageController, self).__init__(chat_id, md)
		self.status = 'init'
		self.type = 'CallingMessageController'
		self.encounter = encounter
		self.bot = bot
		self.party_list = [self.encounter.calling_player]
		_party_msg = PartyMessage(self)
		_calling_msg = CallingMessage(self)

		if time() - self.encounter.start_time >= self.encounter.time_till_fight:
			self.messages = [Message_mc(_party_msg)]
			self.status = 'finished'
		else:
			self.messages = [Message_mc(_party_msg), Message_mc(_calling_msg)]
			self.status = 'countdown'
		print(f'mc status {self.status}')

		self.bot.add_mc(self)
		print('mc added to bot.messages')
		self.build()
		print('build done')
		self.send_to_distributer('SendMessage')
		sleep(1.5)
		
		self.countdown = self.CountdownThread(self)
		self.countdown.start()
		print('end of mc init')


		#self.start_time = start_time
		#self.calling_player = calling_player
		#self.players_to_call = players_to_call
		#self.encounter_time = encounter_time
		#self.player = player
		#self.mid_lvl = mid_lvl
		#self.mob_str = mob_str

	def build(self):

		if len(self.party_list) >= self.encounter.max_party_size:
			self.status = 'finished'

		for _m in self.messages:
			_m.build()

class OneMessageController(MessageController):
	
	class OneTimeMsg():

		def __init__(self, mc):
			self.mc = mc
			self.data = self.mc._guild_list()
			self.type = 'txt'
			self.mrkp = None


	def __init__(self, bot, chat_id, md, msg_type):


		super(OneMessageController, self).__init__(chat_id, md)
		self._templates = {'show_guild_list' : self._guild_list}

		self.status = 'init'

		self.type = 'OneMessageController'
		self.bot = bot

		self.messages = [Message_mc(self.__class__.OneTimeMsg(self))]

		self.data = self._templates[msg_type]()
		self.send_to_distributer('SendMessage' )

	def _guild_list(self):

		_list = self.bot.db.get_all_players_in_table(self.chat_id)

		ans = ''
		for i, _pl in enumerate(_list):
			ans += f'{i+1}. {_pl[2]}\n'
		return ans


class OldCampBot(telebot.TeleBot):

	class Encounter():
		'''
		Class container for encounter data
		'''
		def __init__(self, _type, start_time, calling_player, mid_lvl, players_to_call, mob_str, link):
			self.type = _type 						# 'ambush' / 'mobs'
			self.start_time = start_time			# time of encounter countdown start
			self.calling_player = calling_player	# OldCampBot.Player that initiated encounter
			self.mid_lvl = mid_lvl					# medium level of monsters in encounter
			self.players_to_call = players_to_call	# list of players in db that in 10 levels range from self.mid_lvl
			self.mob_str = mob_str					# string from cw encounter message
			self.link = link 						# cw link for entering the encounter

			if self.type == 'ambush':
				self.time_till_fight = 300
				self.max_party_size = 5
			elif self.type == 'mobs':
				self.time_till_fight = 180
				self.max_party_size = 2

	class db_interface():
		db = 'camp.db'
		def __init__(self, bot):

			self.bot = bot
			_conn, _c = self.conn() #create db or connect to 
			_conn.close()

		def conn(self):
			'''
			conect to db, return connection and cursor
			'''
			try:
				_conn = sqlite3.connect(self.__class__.db)
				_c = _conn.cursor()
				print('Connection succesfull')
				return _conn, _c
			except Exception as e:
				self.bot.log.warning(e)

		def add_chat(self, chat_id):
			'''
			add table chat_id to db
			'''
			_conn, _c = self.conn()
			try:
				_c.execute(self._table_init_cmd(chat_id))
				_conn.commit()
				print('table created')

			except Exception as e:
				self.bot.log.warning(e)
				print(f'add_chat fail\n{e}')

			_conn.close()

		def update_player(self, player):
			'''
			check player in db. if its new player -> add player to db, 
			if not -> update player in db 
			'''
			_conn, _c = self.conn()
			_pl = None

			try:
				_c.execute(self._select_player_cmd(player.chat_id, player.user_id))
				_pl = _c.fetchone()
				if _pl:
					print(f'player in table:{_pl[1]}')
			except Error_sqlite3 as e:
				self.bot.log.warning(e)
				print('update_player cant fetch player')

			if _pl:

				try:
					_c.execute(self._update_player_cmd(player))
					_conn.commit()
					self.bot.log.debug(f"player {player.username} was updated")	
				except Error_sqlite3 as e:
					self.bot.log.warning(e)
					print('update_player failed to update player')

			else:
				try:
					_c.execute(self._add_player_cmd(player))
					_conn.commit()
					self.bot.log.debug(f"player {player.username} was initiated ")	
				except Error_sqlite3 as e:
					self.bot.log.warning(f"cant init player {player.username}\n" + str(e))
					print('update_player failed to init player')

			_conn.close()

		def get_players(self, chat_id, mid_lvl):
			_conn, _c = self.conn()
			_players = None
			try:
				_c.execute(self._select_players_lvl_cmd(mid_lvl, chat_id))
				_players = _c.fetchall()
				print(_players)
				print(f'get_players \n {_players}')
				_conn.close()
				return _players
			except Error_sqlite3 as e:
				self.bot.log.warning(e)
				print('get_players failed to get players')
			finally:
				_conn.close()
			return _players

		def get_player(self, chat_id, user_id):
			_conn, _c = self.conn()
			try:
				_c.execute(self._select_player_cmd(chat_id, user_id))
				_pl = _c.fetchone()
				_conn.close()
				return OldCampBot.Player(_pl[0], _pl[1], _pl[2], _pl[3], chat_id)
			except Error_sqlite3 as e:
				self.bot.log.warning(e)
				print('get_player failed to get player')
			finally:
				_conn.close()

		def get_all_players_in_table(self, chat_id):
			_conn, _c = self.conn()
			try:
				_c.execute(self._select_all_players_cmd(chat_id))
				_pl = _c.fetchall()
				_conn.close()
				return _pl
			except Error_sqlite3 as e:
				self.bot.log.warning(e)
				print('get_player failed to get player')
			finally:
				_conn.close()

		def _table_init_cmd(self, chat_id):
			print(chat_id)
			_str = f'''
				CREATE TABLE {self.t_name(chat_id)}(
				user_id INTEGER PRIMARY KEY,
				username TEXT NOT NULL,
				gamename TEXT NOT NULL,
				lvl INTEGER NOT NULL
				);'''
			return _str

		def _update_player_cmd(self, player):
			_str = f"""
				UPDATE {self.t_name(player.chat_id)}
				SET username = '{player.username}',
					gamename = '{player.gamename}',
					lvl = {player.lvl}
				WHERE user_id = {player.user_id};"""
			return _str

		def _add_player_cmd(self, player):
			_str = f"""
				INSERT INTO {self.t_name(player.chat_id)} (user_id, username, gamename, lvl)
				VALUES ({player.user_id},  '{player.username}', '{player.gamename}', {player.lvl});"""
			return _str

		def _select_player_cmd(self, chat_id, user_id):
			_str = f'''
				SELECT user_id, username, gamename, lvl
				FROM {self.t_name(chat_id)}
				WHERE user_id = {user_id} ;'''
			return _str

		def _select_players_lvl_cmd(self, mid_lvl, chat_id):
			_str = f'''
				SELECT user_id, username, gamename, lvl
				FROM {self.t_name(chat_id)}
				WHERE lvl BETWEEN {mid_lvl - 10} AND {mid_lvl + 10};'''
			return _str

		def _select_all_players_cmd(self, chat_id):
			_str = f'SELECT * FROM {self.t_name(chat_id)}'
			return _str

		def t_name(self, chat_id):
			if type(chat_id) == int:
				return 'c' + str(abs(chat_id))
			else:
				return chat_id

	class Player():
		'''
		Class container for Player data
		'''
		def __init__(self, user_id, username, gamename, lvl, chat_id):
			self.user_id = user_id								#telegram user id
			self.username = username							#telegram username
			self.gamename = self.prep_gamename(gamename)		#cw name
			self.lvl = lvl 										#cw player lvl
			self.chat_id = chat_id								#telegram chat id

		def prep_gamename(self, _name):				# return game name witout castle logo, guild, 
			i = 0
			if ']' in _name:
				for _num, letter in enumerate(_name):
					if letter == ']':
						i = _num + 1

			return(_name[i:])


	
	
	def __init__(self, token):
		super(OldCampBot, self).__init__(token, num_threads = 1)

		self.running = True
		self.pin_mobs = True  #on True bot init calling messages in response to Encounter message in chats

		self.admin_id = []

		self.players = {}


		self.db = self.__class__.db_interface(self)
		
		self.mc = []							 #message controllers

		self.log = logging.getLogger('OldCampBot_Loger')
		self.log.setLevel(logging.DEBUG) 
		formatter = logging.Formatter('%(asctime)s:%(threadName)s\n%(message)s')
		file_handler = logging.FileHandler('dbg.log') 
		file_handler.setFormatter(formatter)
		self.log.addHandler(file_handler)

		self.logger = self.log


		self.md = MessageDistributer(bot = self, log = self.log) #message distributer

		self.log.debug('OldCampBot init')
		

		@self.message_handler(commands = ['start_chat'],
				func = lambda message : message.chat.id < 0 )
		def _start_camp(message):
			'''
			check for table <chat_id>, if no, init table
			'''
			print('starting chat')
			self.db.add_chat(message.chat.id)

		@self.message_handler(regexp = ('Ты заметил враждебных существ'))
		def pin_party(message):
			'''
			find sutable party for enconter, and ping them
			'''
			print('pin_party start')
			def get_data(msg):
				_ = msg.text

				link = _.split('\n\n')[-1]
				mob_str = _.split('\n\n')[0].split('\n')[1:]
				lvl = mob_lvl(mob_str)
				chat_id = msg.chat.id
				user_id = msg.from_user.id

				if 'Ambush' in _:
					_type = 'ambush'
				else:
					_type = 'mobs'
				start_time = msg.forward_date
				print(f'forward time {start_time}')	

				username = getattr(msg.from_user, 'username')
				if not username:
					username = getattr(msg.from_user, 'first_name')	

				return link, lvl, chat_id, user_id, mob_str, _type, start_time, username

			def mob_lvl(_str):
				mobs_qty = 0
				sum_lvl = 0

				for row in _str:
					
					_ = row.split(' ')
					
					if _[-1][:3] == 'lvl':
						num = 1
						lvl = 0
						try:
							num = int(_[0])
						except Exception as e:
							print(e)
						try:
							lvl = int(_[-1][4:])
						except Exception as e:
							print(e)

						if lvl != 0:
							sum_lvl += lvl * num
							mobs_qty += num
				#print(f'mid lvl = {sum_lvl // mobs_qty}')
				return sum_lvl // mobs_qty

			#link, lvl, chat_id, user_id, mob_str = get_data(message)
			#players = self.db.get_players(chat_id, lvl)

			#self.send_call(chat_id, players, user_id, mob_str)
			if time() - message.date < 300 and self.pin_mobs:		#use messages that was sendt less than 5 min ago
				self.log.debug(message)
				link, lvl, chat_id, user_id, mob_str, _type, start_time, username = get_data(message)
				self.send_call(link, lvl, chat_id, user_id, mob_str, _type, start_time, username)
				print('end of pin_party')
				self.log.debug(message.text)

		@self.message_handler(regexp = ('Твои результаты в бою'))
		def update_player(message):
			'''
			check for player in guild table. if got difference -> update db 
			if no player in db -> add to db
			'''
			def get_data(msg):
				_ = msg.text.split('\n')[0]
				_lvl = _.split('Lvl: ')[-1]
				_gamename = _.split(' ⚔')[0]
				
				_username = msg.from_user.username
				user_id = msg.from_user.id
				return OldCampBot.Player(
					user_id = user_id,
					username = _username,
					gamename = _gamename,
					lvl = _lvl,
					chat_id = msg.chat.id
					)
			_pl = get_data(message)
			if _pl:
				self.db.update_player(_pl)

			self.log.debug(message.text)

		@self.callback_query_handler(lambda query: query.data == 'markme')
		def add_pl_to_list(callback_query):
			chat_id = callback_query.message.chat.id
			msg_id = callback_query.message.message_id
			user_id = callback_query.from_user.id
			pl = self.db.get_player(chat_id, user_id)
			print(f'user {pl.username} pressed MarkMe')

			if not pl:
				user = callback_query.from_user
				pl = OldCampBot.Player(user.id, user.username, user.username, 'n/a')

			for c in self.mc:
				if c.chat_id == chat_id and c.messages[0].message_id == msg_id:
					#pl = self.db.get_player(chat_id, user_id)
					not_in_party_flag = True
					for _player in c.party_list:
						print(c.party_list)
						if _player.user_id == user_id:
							not_in_party_flag = False 

					if not_in_party_flag and len(c.party_list) < c.encounter.max_party_size: 
						c.party_list.append(pl)
						c.build()
						c.send_to_distributer('UpdateMessage',0)
						self.log.debug(f'Player {pl.username} enter party')

		@self.message_handler(commands = ['guild_list'])
		def _get_guild_list(message):
			_ = OneMessageController(self, message.chat.id, self.md, 'show_guild_list' )



		@self.message_handler(commands = ['try_me'])
		def try_msg(message):
			print(f'got msg in chat {message.chat.id}')
			m_str = ['Ты заметил враждебных существ. Будь осторожен:\n2 x Forbidden Alchemist lvl.53']
			link = '/fight_MX9yddGXpUyKMWed5gfR'
			self.send_call(
				link = link,
				lvl = 55,
				chat_id = message.chat.id,
				user_id = 30,
				mob_str = m_str,
				_type = 'mobs',
				start_time = time() - 150,
				username = 'SomeGuy')
		
		@self.message_handler(func = lambda message : message.forward_from )
		def echo_msg(message):
			print(message.date)

		self.t_players = [self.Player(i * 10, f'Player{str(i)}', f'GamePlayer{str(i)}', i * 5 + 30, 123) for i in range(10)]

	def add_mc(self, mc):
		self.mc.append(mc)

	def del_mc(self, mc):
		for i, _mc in enumerate(self.mc):
			if _mc.status == 'finished':
				self.mc.pop(i)

		
	def send_call(self, link, lvl, chat_id, user_id, mob_str, _type, start_time, username):
		global TMP
		pl_list = self.db.get_players(chat_id, lvl)
		print(pl_list)
		
		players_to_call = [] 
		calling_player = None
		for i, pl in enumerate(pl_list):		#exclude player that calling for help from calling list
			if pl[0] == user_id:
				calling_player = self.__class__.Player(user_id, pl[1], pl[2], pl[3], chat_id)
				#print(f'{pl_list}\nis {type(pl_list)} type')
				#TMP = pl_list
				#pl_list.pop[i]
			else:
				players_to_call.append(pl[1])
		#if players_to_call == []:
		#	players_to_call = [p.username for p in self.t_players]

		if not calling_player:
			calling_player = self.__class__.Player(user_id, username, username, 0, chat_id)

		print('players_to_call',players_to_call)

		encounter = self.__class__.Encounter(_type, start_time, calling_player, lvl, players_to_call, mob_str, link )
		#self, _type, start_time, calling_player, mid_lvl, players_to_call, mob_str, link

				
		#start_time = 100
		print('start mc')
		mc = CallingMessageController(self, chat_id, self.md, encounter)
		
		#mc.send_to_distributer('SendMessage')


_b = None


def main():
	global _b
	token = 'TOKEN' #Telegram bot token
	bot = OldCampBot(token)
	_b = bot

	bot.md.start() #start message distributer
	print('md on!')

	try:
		print('starting polling ')
		bot.polling()
	except Exception as e:
		bot.running = False
		bot.stop_polling()
		print(e)
BOT = None
def test_me():
	global BOT
	token = 'TOKEN' #Telegram bot token
	bot = OldCampBot(token)
	players = []
	BOT = bot
	

	for i in range(20):
		players.append(bot.Player(i * 3, f'Name_{i}', f'gname{i}', 50 + i, 'C111'))
	print([(i.user_id, i.username, i.lvl) for i in players])

	bot.db.add_chat('C111')

	print('start update of players')

	for pl in players:
		bot.db.update_player(pl)

	print('start geting party ')
	party = bot.db.get_players(chat_id = 'C111', mid_lvl = 55)
	print(party)












