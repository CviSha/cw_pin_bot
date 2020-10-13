from time import sleep, time
import threading 
import logging
from telebot.types import InputMediaPhoto
from copy import copy

class TelePoker_message_request():
	'''
	message sends and edits for telegram
	'''
	def SendMessage(mc, bot, msg_indx):
		_m = mc.messages[msg_indx]
		print(f'SEnding msg #{msg_indx}')
		#bot.logger.debug(f'TelePoker_message_request.SendMessage executed\n sending {_m.msg.type} to {mc.chat_id}')			#LOG

		

		#if _m.msg.type == 'pic' and mc.messages[msg_indx]:  
		if _m.msg and _m.msg.type == 'pic':    #send pic message
			#bot.logger.debug('TelePoker_message_request.SendMessage\npic condition passed')				#LOG

			_msg = bot.send_photo(
				chat_id = mc.chat_id,
				photo = _m.msg.file,
				reply_markup = _m.msg.mrkp)

			if _msg:
				#bot.logger.debug(f'TelePoker_message_request.SendMessage\nsuccess msg#{_msg.message_id}')			#LOG
				_m.new_message_id(_msg.message_id)
				_m.update_last()
				_m.updating = False

				return _msg

		#elif msg_type == 'txt' and mc.txt: 		
		elif _m.msg and _m.msg.type == 'txt': #send text message
			#bot.logger.debug(f'TelePoker_message_request.SendMessage\ntxt condition passed')		#LOG
			_msg = bot.send_message(
				chat_id = mc.chat_id,
				text = _m.msg.data,
				reply_markup = _m.msg.mrkp)

			if _msg:
				#bot.logger.debug(f'TelePoker_message_request.SendMessage\nsuccess msg#{_msg.message_id}')		#LOG
				_m.new_message_id(_msg.message_id)
				_m.update_last()
				mc.messages[msg_indx].updating = False

				return _msg

	def UpdateMessage(mc, bot, msg_indx):
		_m = mc.messages[msg_indx]

		if not mc.messages[msg_indx].message_id: 					#if no message to update, send message
			msg = TelePoker_message_request.SendMessage(mc, bot, msg_indx)
			return msg

		#bot.logger.debug(f'\n{"*" * 30}\nTelePoker_message_request.UpdateMessage executed')
		if _m.msg.type == 'pic':
			#bot.logger.debug('TelePoker_message_request.UpdateMessage\nmsg.type == "pic"')
			#bot.logger.debug(f'mc.pic : {_.msg}\nmc.pic.menu == mc.last_pic - {_m.msg.data == _m.last_data}')

			if _m.msg and _m.msg.data != _m.last_data:
				#bot.logger.debug('TelePoker_message_request.UpdateMessage\npic condition passed')

				_msg = bot.edit_message_media(
					media = InputMediaPhoto(_m.msg.file),
					chat_id = mc.chat_id,
					message_id = _m.message_id,
					reply_markup = _m.msg.mrkp)

				if _msg:
					#bot.logger.debug(f'TelePoker_message_request.UpdateMessage\nmsg#{_msg.message_id} was updated')
					_m.update_last()
					_m.updating = False
					return _msg

			
			elif _m.msg and _m.msg.mrkp != _m.last_markup:
				#bot.logger.debug('TelePoker_message_request.UpdateMessage\nupdating markup of pic messgae')
				_msg = bot.edit_message_reply_markup(
					chat_id = mc.chat_id,
					message_id = _m.message_id,
					reply_markup = _m.msg.mrkp)

				if _msg:
					#bot.logger.debug('pic markup was updated')
					_m.update_last()
					_m.updating = False
					return _msg

			elif _m.msg and _m.msg.data == _m.last_data and _m.msg.mrkp == _m.last_markup:
				_m.updating = False


		elif _m.msg.type == 'txt':
			#bot.logger.debug('TelePoker_message_request.UpdateMessage\nmsg_type == "txt"')
			#bot.logger.debug(f'mc.txt - {_m.msg.data}\nmc.txt.text == mc.last_txt - {_m.msg.data == _m.last_data}')
			
			if _m.msg and _m.msg.data != _m.last_data:
				#bot.logger.debug('TelePoker_message_request.UpdateMessage\ntxt condition passed')

				_msg = bot.edit_message_text(
						text = _m.msg.data,
						chat_id = mc.chat_id,
						message_id = _m.message_id,
						reply_markup = _m.msg.mrkp)
				if _msg:
					#bot.logger.debug(f'TelePoker_message_request.UpdateMessage\nmsg#{_m.message_id} was updated')
					_m.update_last()
					_m.updating = False
					return _msg

			elif _m.msg and _m.msg.mrkp != _m.last_markup:
				#bot.logger.debug('UpdateMarkup of txt message')
				_msg = bot.edit_message_reply_markup(
					chat_id = mc.chat_id,
					message_id = _m.message_id,
					reply_markup = _m.msg.mrkp)

				if _msg:
					#bot.logger.debug('txt markup was updated')
					_m.update_last()
					_m.updating = False
					return _msg

			elif _m.msg and _m.msg.data == _m.last_data and _m.msg.mrkp == _m.last_markup:
				_m.updating = False

		#bot.logger.debug(f'TelePoker_message_request.UpdateMessage end\n{"*" * 30}')

	def DeleteMessage(mc, bot, msg_indx):
		_m = mc.messages[msg_indx]
		print(f'deliting message {msg_indx}')

		if _m.message_id:
			_msg = bot.delete_message(
				chat_id = mc.chat_id,
				message_id = _m.message_id)

			_m.message_id = None
			return _msg 

	def UpdateMarkup(mc, bot, msg_type):
		'''
		old version
		'''

		if msg_type == 'pic':
			msg = mc.pic
			msg_id = mc.pic_message_id
			msg_last_mrkp = mc.last_pic_markup
		elif msg_type == 'txt':
			msg = mc.txt
			msg_id = mc.txt_message_id
			msg_last_mrkp = mc.last_txt_markup

		if msg_id and not msg.mrkp == msg_last_mrkp : 
			print('#'*10 + '\n cond 111 passed')
			_msg = bot.edit_message_reply_markup(
					chat_id = mc.chat_id,
					message_id = msg.message_id,
					reply_markup = msg.mrkp)

			if _msg and msg_type == 'pic':
				mc.last_pic_markup = msg.mrkp
			elif _msg and msg_type == 'txt':
				mc.last_txt_markup = msg.mrkp
			return _msg

	req_dict = {
	'SendMessage':SendMessage,
	'UpdateMessage':UpdateMessage,
	'DeleteMessage':DeleteMessage,
	'UpdateMarkup':UpdateMarkup}

	def __init__(self,mc , command, msg_indx):    # mc - message_controller
		self.mc = mc
		self.command = command
		self.msg_indx = msg_indx

		self.request = self.__class__.req_dict[self.command]
	def __repr__(self):
		return self.command + str(self.msg_indx)
	
	def _execute(self,bot):
		if hasattr(bot, 'log'):
			bot.log.debug(f'starting execution of request from {self.mc.type}')			#LOG
		return self.request(self.mc, bot, self.msg_indx)

class MessageDistributer(threading.Thread):
	'''
	Thread that distribute message requests to telegram, acording to it time limitations 

	'''

	class Line():
		def __init__(self):
			self.commands = []			#(MessageController, <str command for  >)
			self.last_update = time()

	def __init__(self,bot,log = None):
		super(MessageDistributer, self).__init__()
		self.name = 'MessageDistributerThread'
		self.bot = bot
		self.chats = {}
		self.requests_que = []
		self.running = False
		self.log = log

	def run(self):
		self.running = True
		if self.log:
			self.log.debug('MessageDistributer is running')
		
		self.loop()

	def add_chat(self, chat_id):
		self.chats[chat_id] = self.__class__.Line()

	def close_chat(self, chat_id):
		del self.chats[chat_id]

	def update_lines(self):
		while len(self.requests_que) > 0:
			_req = self.requests_que.pop(0)

			if not _req.mc.chat_id in self.chats:
				self.add_chat(_req.mc.chat_id)

			self.chats[_req.mc.chat_id].commands.append(_req)

	def loop(self):
		'''
		checks for new requests in chat lines and execute them 
		meet the telegram send message limits 
		'''
		_chat_cooldown = 1.05
		_all_cooldown = .2

		last_update = time()
		print('md loop starts')
		while self.running and self.bot.running:
			_chats = self.chats.copy()
			for _id in _chats:

				_log = ''

				if self.chats[_id].commands != []:
					print(f'comands in line :{self.chats[_id].commands}')


				if len(self.chats[_id].commands) > 0 and time() - self.chats[_id].last_update > _chat_cooldown:
					_log = f'chat {_id}\ngot {len(self.chats[_id].commands)} commands in line '
					
					_dtime = time() - last_update
					_log += f'\nlast update was {round(_dtime)} sec ago'
					
					if _dtime < _all_cooldown:
						_log = '\nwaitng for global cooldown'
						#print('_all_cooldown condition')
						sleep(_all_cooldown - _dtime)
						_dtime = time() - last_update
						#print(f'new _dtime : {_dtime}')

					_req = self.chats[_id].commands.pop(0)
					_log += f'\nrequest to execution\n{_req}'

					try:
						#_log += (f'try to execute _req : {_req.command}\nchat id : {_req.mc.chat_id}\nmsg type : {_req.msg_type}')
						_ans = _req._execute(self.bot)
						if _ans:
							_log += (f'\nreq was executed')
							#_log += (f'\nreq was executed\n{_ans}')
							#_rec.mc.messages[_req.msg_indx].
							last_update = time()
							self.chats[_id].last_update = time()

					except Exception as e:
							_log += (f'\nExeption in sending to telegram\n{e}')
							print(e)
							#print('some shit in sending to telegram')
							#print(e)

				elif time() - self.chats[_id].last_update > 2000:
					self.close_chat(_id)
					print(f'md Chat {_id} was closed')

				if _log != '':
					_log = '-' * 30 + '\n' + _log + '\n' + '-' * 30
					if self.log:
						self.log.debug(_log)
				sleep(.3)

			self.update_lines()
			sleep(1)

class Message_mc():
	'''
	class Msg():
		def __init__(self):
			self.data = None
			self.type = None
			self.file = None
			self.mrkp = None
		def build(self):
			#build Msg.data according to your needs is inherting class
			pass
	'''

	def __init__(self, msg):
		self.msg = msg
		self.message_id = None
		self.last_data = None
		self.last_markup = None
		self.updating = False

	def build(self):
		'''
		fill 
		'''
		#print('mc build!')
		self.msg.build()


	def update_last(self):
		if self.last_data != self.msg.data:
			self.last_data = copy(self.msg.data)
		if self.last_markup != self.msg.mrkp:
			self.last_markup = copy(self.msg.mrkp)

	def new_message_id(self, new_id):
		self.message_id = new_id

class MessageController():
	'''
	object controlling flow of messages and menu builds on different stages of bot scenario 
	'''

	def __init__(self,chat_id, md): 
		self.md = md #MessageDistributer 
		self.chat_id = chat_id
		self.type = None

		self.messages = []
		
		
		
	def send_to_distributer(self, command, message_indx = 'all'):

		#self.md.requests_que.append( TelePoker_message_request((self, command, message_type)))
		if message_indx == 'all':
		#	for i, msg in enumerate(self.messages):
			for i in range(len(self.messages)):
				self.md.requests_que.append( TelePoker_message_request(self, command, i))
				print(f'req sendt {command}, {i}')
		else:
			self.md.requests_que.append( TelePoker_message_request(self, command, message_indx))


	def new_send_to_distributer(self):
		pass

	def send_to_chat(self): #Send or replace pic and txt messages to chat
		#self.md.bot.logger.debug(f'{"#" * 30}\nMessageController.send_to_chat start\nchat_id {self.chat_id} ')		#LOG
		if not self.chat_id in self.md.chats:
			self.md.add_chat(self.chat_id)
		
		if self.pic and self.pic.message_id:
			self.send_to_distributer('DeleteMessage', 'pic')
			
		if self.txt and self.txt.message_id:
			self.send_to_distributer('DeleteMessage', 'txt')
			
		self.build()
		self.pic_updating = True
		self.txt_updating = True 

		self.send_to_distributer('SendMessage', 'pic')
		self.send_to_distributer('SendMessage', 'txt')
		self.md.bot.logger.debug(f'MessageController.send_to_chat end\n{"#" * 30}')		#LOG

	def update_msg(self): #Update 'pic' or 'txt' message
		'''
		check curent pic/txt and they markups with last_pic/txt/markup
		if they not the same - edit requered message and update last_pic/txt/markup
		'''
		_log = f'{"#" * 30}\nMessageController.update_msg start\nchat id : {self.chat_id}'


		if not self.chat_id in self.md.chats:
			self.md.add_chat(self.chat_id)
			_log += f'\n- New chat was created at MessageDistributer\nchat_id:{self.chat_id}'

		self.build()
		
		if self.pic_message_id and not self.pic.last_image == self.pic.menu:
			#self.md.bot.logger.debug('MessageController.update_msg\npic condition')			#LOG
			self.pic_updating = True
			self.send_to_distributer('UpdateMessage', 'pic')
			_log += '\npic condition passed\n("UpdateMessage", "pic") request was sendt to md'

		elif self.pic.message_id and not self.last_pic_markup == self.pic.mrkp:
			#self.md.bot.logger.debug(f'MessageController.update_msg\n pic markup condition')  #LOG
			self.pic_updating = True
			self.send_to_distributer('UpdateMarkup', 'pic')
			_log += '\npic markup condition passed\n("UpdateMarkup", "pic") request was sendt to md'
		
		if self.txt_message_id and not self.txt.last_text == self.txt.text:
			#self.md.bot.logger.debug('MessageController.update_msg\ntxt condition')			#LOG
			self.txt_updating = True
			self.send_to_distributer('UpdateMessage', 'txt')
			_log += '\ntxt condition passed\n("UpdateMessage", "txt") request was sendt to md'

		elif self.txt.message_id and not self.last_txt_markup == self.txt.mrkp:
			#self.md.bot.logger.debug(f'MessageController.update_msg\n txt markup condition')			#LOG
			self.txt_updating = True
			self.send_to_distributer('UpdateMarkup', 'txt')
			_log += '\ntxt markup condition passed\n("UpdateMarkup", "txt") request was sendt to md'

		_log += f'\nMessageController.update_msg end \n{"#" * 30}'
		self.md.bot.logger.debug(_log)
		#self.md.bot.logger.debug(f'MessageController.update_msg end \n{"#" * 30}')		#LOG

	def update_mrkp(self,msg_type): #Update inline markup of 'pic' or 'txt' message
		self.md.bot.logger.debug(f'{"#" * 30}\nMessageController.update_mrkp start\n{msg_type} in {self.chat_id}')  #LOG

		if not self.chat_id in self.md.chats:
			self.md.bot.logger.debug(f'MessageController.update_mrkp\n no {self.chat_id} in md.chats => chat_id added')  #LOG
			self.md.add_chat(self.chat_id)

		self.build()

		if msg_type == 'pic' and self.pic.message_id and not self.pic.last_mrkp == self.pic.mrkp:
			self.md.bot.logger.debug(f'MessageController.update_msg\n pic condition passed')  #LOG
			self.pic_updating = True
			self.send_to_distributer('UpdateMarkup', 'pic')
		
		if msg_type == 'txt' and self.txt.message_id and not self.txt.last_mrkp == self.txt.mrkp:
			self.md.bot.logger.debug(f'MessageController.update_msg\n txt condition passed')			#LOG
			self.txt_updating = True
			self.send_to_distributer('UpdateMarkup', 'txt')

		self.md.bot.logger.debug(f'MessageController.update_mrkp end\n{"#" * 30}')  #LOG
	
	def build(self):
		#print('mc build')
		for _m in self.messages:
			_m.build()

	'''
	def build(self):
		if self.pic: self.pic.build()
		if self.txt: self.txt.build()
	'''


