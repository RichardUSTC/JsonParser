# -*- coding: utf-8 -*-

# Author: Bin LI (richardustc@gmail.com)
# All rights reserved.

# 本文件实现了类JsonParser，包含特性:
#    1、该类能读取json格式的数据，并以Python字典的方式读写数据
#    2、给定一个Python字典，可以更新类中数据，并以json格式输出
#    3、遵循json格式定义确保相同的同构数据源彼此转换后数据仍然一致
#    4、支持将数据分别以json或Python的格式存储到文件并加载回来使用

class InvalidJsonException(object): pass
class OutOfFloatRangeException(object): pass

class JsonParser(object):
	def __init__(self):
		pass
	def load(self, s):
		"""
		从's'中读取Json数据。
		如果json数据不合法，抛出InvalidJsonException异常。
		如果数字超出Python浮点表示范围，抛出OutOfFloatRangeException异常。
		"""
		# TODO
		pass
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
