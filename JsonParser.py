# -*- coding: utf-8 -*-

# Author: Bin LI (richardustc@gmail.com)
# All rights reserved.

# 本文件实现了类JsonParser，包含特性:
#    1、该类能读取json格式的数据，并以Python字典的方式读写数据
#    2、给定一个Python字典，可以更新类中数据，并以json格式输出
#    3、遵循json格式定义确保相同的同构数据源彼此转换后数据仍然一致
#    4、支持将数据分别以json或Python的格式存储到文件并加载回来使用

import exceptions
import sys

__all__ = ['InvalidJsonException', 'OutOfFloatRangeException', 'JsonParser']

class InvalidJsonException(Exception):
	def __init__(self, hint, position=-1):
		self.position = position
		self.hint = hint
	def __str__(self):
		return 'Invalid input at %dth character of input: %s' % (self.position, self.hint)
class OutOfFloatRangeException(Exception):
	def __init__(self, position):
		self.position = position
	def __str__(self):
		return 'Input float number out of python float range at %dth character of input' % (self.position,)

class Logger(object):
	debug = False
	@classmethod
	def _log(cls, message):
		sys.stderr.write(message)
		sys.stderr.write('\n')
	@classmethod
	def log(cls, message):
		if cls.debug:
			cls._log(message)
	@classmethod
	def showTokens(cls, tokenReader):
		if cls.debug:
			cls._log(tokenReader.dumpTokens())
	@classmethod
	def tryReduce(cls, name):
		if cls.debug:
			cls._log("Try to reduce the following input as '%s'" % name)
	@classmethod
	def cancelReduce(cls, name):
		if cls.debug:
			cls._log("Cancel the reduce of '%s'" % name)
	@classmethod
	def reduce(cls, name):
		if cls.debug:
			cls._log("Reduce as '%s'" % name)
	@classmethod
	def shift(cls, token):
		if cls.debug:
			cls._log("Shift '%s'" % token)

class Token(object):
	def __init__(self, position, type, value):
		self.type = type
		self.value = value
		self.position = position
	def __str__(self):
		return "Token <'%s', %s, @%d>" % (self.value, self.type, self.position)
class TokenReader(object):
	separator = ('{', '}', '[', ']', ',', ':')
	def __init__(self, input):
		self.tokenList = []
		self.currentTokenIndex = -1
		self._readTokens(input, 0)
	def _readString(self, input, start):
		end = start+1
		while end < len(input):
			char = input[end]
			if char == '\\':
				end += 2
			elif char == '"':
				break
			else:
				end += 1
		else:
			raise InvalidJsonException("invalid string", start)
		try:
			s = input[start+1:end].decode("unicode_escape")
		except UnicodeDecodeError:
			raise InvalidJsonException("invalid string", start)
		return (end+1, s)
	def _readTokens(self, input, start):
		"""
		读取token，存放到自身的tokenList中。input为输入，start为扫描起始点。
		如果扫描失败，抛出异常
		"""
		while start < len(input):
			# skip blanks
			while start < len(input) and input[start].isspace():
				start += 1
			if start >= len(input):
				break
			# separator
			if input[start] in self.separator:
				token = Token(start, input[start], input[start])
				self.tokenList.append(token)
				start += 1
				continue
			# special value
			if len(input) >= start+5:
				piece = input[start:start+5]
			elif len(input) >= start+4:
				piece = input[start:start+4]
			else:
				piece = "1234"
			if piece == "false":
				token = Token(start, "false", False)
				self.tokenList.append(token)
				start += 5
				continue
			elif piece[0:4] == "true":
				token = Token(start, "true", True)
				self.tokenList.append(token)
				start += 4
				continue
			elif piece[0:4] == 'null':
				token = Token(start, "null", None)
				self.tokenList.append(token)
				start += 4
				continue
			# string
			if input[start] == '"':
				(newStart, s) = self._readString(input, start)
				token = Token(start, "string", s)
				self.tokenList.append(token)
				start = newStart
				continue
			# number
			end = start+1
			while end < len(input):
				if input[end] in self.separator:
					break
				end += 1
			else:
				raise InvalidJsonException("invalid number", start)
			try:
				number = float(input[start:end])
				if abs(number) == float('Inf'):
					raise OutOfFloatRangeException(start)
				if number.is_integer():
					number = int(number)
				token = Token(start, "number", number)
				self.tokenList.append(token)
				start = end
			except ValueError:
				raise InvalidJsonException("invalid number", start)
		if len(self.tokenList) > 0:
			self.currentTokenIndex = 0
	def dumpTokens(self):
		"""
		获取所有尚未消耗的token的信息
		"""
		return '\n'.join([str(token) for token in self.tokenList[self.currentTokenIndex:]])

	def get(self):
		"""
		从tokenList中取出一个token。
		如果没有token，返回None
		"""
		if self.currentTokenIndex >= 0 and self.currentTokenIndex < len(self.tokenList):
			token = self.tokenList[self.currentTokenIndex]
			self.currentTokenIndex += 1
			return token
		else:
			return None
	def putBack(self, token):
		"""
		将读到的token放回tokenList的头部
		"""
		self.currentTokenIndex -= 1
	def createRestorePoint(self):
		"""
		创建一个还原点，返回还原点参数，可用restore方法回退至还原点状态
		"""
		return self.currentTokenIndex
	def restore(self, restorePoint):
		"""
		恢复至创建还原点'restorePoint'时的状态
		"""
		self.currentTokenIndex = restorePoint

class Grammar(object):
	def __init__(self, debug=False):
		Logger.debug = debug
	def parse(self, input):
		"""
		解析Json，假定Json最外层为object
		"""
		self.tokenReader = TokenReader(input)
		Logger.showTokens(self.tokenReader)
		obj = self.parseObject()
		return obj
	def parseObject(self):
		"""
		object
			{}
			{ members }
		"""
		obj = None
		Logger.tryReduce('object')
		try:
			token = self.tokenReader.get()
			assert token !=None and token.type == '{'
			Logger.shift(token)
			token = self.tokenReader.get()
			assert token != None
			if token.type == '}':
				Logger.shift(token)
				obj = dict()
			else:
				self.tokenReader.putBack(token)
				members = self.parseMembers()
				token = self.tokenReader.get()
				assert token != None and token.type == '}'
				Logger.shift(token)
				obj = members
		except AssertionError:
			raise InvalidJsonException("not an object")
		Logger.reduce('object')
		return obj
	def parseMembers(self):
		"""
		members
			pair
			pair, members

		"""
		members = {}
		Logger.tryReduce('members')
		try:
			while True:
				pair = self.parsePair()
				members.update(pair)
				token = self.tokenReader.get()
				assert token != None
				if token.type != ',':
					self.tokenReader.putBack(token)
					break
				Logger.shift(token)
		except AssertionError:
			raise InvalidJsonException("not a 'members'")
		Logger.reduce('members')
		return members
	def parsePair(self):
		"""
		pair
			string : value
		"""
		pair = None
		Logger.tryReduce('pair')
		try:
			token = self.tokenReader.get()
			assert token != None and token.type == 'string'
			Logger.shift(token)
			key = token.value
			token = self.tokenReader.get()
			assert token != None and token.type == ':'
			Logger.shift(token)
			value = self.parseValue()
			pair = {key: value}
		except AssertionError:
			raise InvalidJsonException("not a 'pair'")
		Logger.reduce('pair')
		return pair
	def parseArray(self):
		"""
		array
			[]
			[ elements ]
		"""
		array = None
		Logger.tryReduce('array')
		try:
			token = self.tokenReader.get()
			assert token != None and token.type == '['
			Logger.shift(token)
			token = self.tokenReader.get()
			assert token != None
			if token.type == ']':
				Logger.shift(token)
				array = []
			else:
				self.tokenReader.putBack(token)
				elements = self.parseElements()
				token = self.tokenReader.get()
				assert token != None and token.type == ']'
				Logger.shift(token)
				array = elements
		except AssertionError:
			raise InvalidJsonException("not an 'array'")
		Logger.reduce('array')
		return array
	def parseElements(self):
		"""
		elements
			value
			value, elements
		"""
		elements = []
		Logger.tryReduce('elements')
		try:
			while True:
				value = self.parseValue()
				elements.append(value)
				token = self.tokenReader.get()
				assert token != None
				if token.type != ',':
					self.tokenReader.putBack(token)
					break
				else:
					Logger.shift(token)
		except AssertionError:
			raise InvalidJsonException("not an 'elements'")
		Logger.reduce('elements')
		return elements
	def parseValue(self):
		"""
		value
			string
			number
			object
			array
			true
			false
			null
		"""
		value = None
		Logger.tryReduce('value')
		try:
			token = self.tokenReader.get()
			assert token != None
			if token.type in ('string', 'number', 'true', 'false', 'null'):
				Logger.shift(token)
				value = token.value
			elif token.type == '[':
				self.tokenReader.putBack(token)
				value = self.parseArray()
			elif token.type == '{':
				self.tokenReader.putBack(token)
				value = self.parseObject()
			else:
				raise InvalidJsonException("not a 'value")
		except AssertionError:
			raise InvalidJsonException("not a 'value'")
		Logger.reduce('value')
		return value

class JsonParser(object):
	def __init__(self):
		self.parser = Grammar(debug=False)
		self.dict = None
	def load(self, s):
		"""
		从's'中读取Json数据。
		如果json数据不合法，抛出InvalidJsonException异常。
		如果数字超出Python浮点表示范围，抛出OutOfFloatRangeException异常。
		"""
		self.dict = self.parser.parse(s)
	def dump(self):
		"""
		根据类中数据返回Json字符串
		"""
		# TODO
		return ""
	def loadJson(self, f):
		"""
		从文件中读入json格式数据，f为文件路径，异常处理同'load'，文件操作失败抛出异常。
		"""
		# TODO
		pass
	def dumpJson(self, f):
		"""
		将类中的内容以json格式存入文件，f为路径，文件若存在则覆盖，文件操作失败抛出异常。
		"""
		# TODO
		pass
	def loadDict(self, d):
		"""
		读取dict中的数据，存入类中，若遇到不是字符串的key则忽略。
		"""
		pass
	def dumpDict(self):
		"""
		返回一个字典，包含类中数据。
		"""
		pass
	def __getitem__(self, index):
		pass
	def __setitem__(self, index, value):
		pass
	def __delitem__(self, index):
		pass
	def update(self, d):
		"""
		用字典d更新类中的数据
		"""
		pass
