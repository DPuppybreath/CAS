#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""
this is created and tested with Python 3.6.5
written 2018 by Chuck Wernicke for General Bytes

parts of this code were extracted from python3-krakenex
https://github.com/veox/python3-krakenex

# Requires python-requests. Install with pip:
#	pip install requests
# or, with easy-install:
#	easy_install requests
"""

import sys, json, hmac, hashlib, time, requests, getpass

# private query signing
import urllib.parse
import base64

if sys.version_info[0] < 3:
	print ("ERROR: Python version 3 is required to use this script!")
	print ("Install with: sudo apt install python3")
	print ()
	quit ()

API_URL = 'https://api.kraken.com'
API_VER = '0'

# Kraken API object
class KrakenAPI(object):
	def __init__(self, key='', secret=''):
		""" Create an object with authentication information.
		:param key: (optional) key identifier for queries to the API
		:type key: str
		:param secret: (optional) actual private key used to sign messages
		:type secret: str
		:returns: None
		"""
		self.key = key
		self.secret = secret
		self.uri = API_URL
		self.apiversion = API_VER
		self.session = requests.Session()
		self.session.headers.update({
			'User-Agent': 'GB Key Verifier/1.0 (+https://generalbytes.com)'
		})
		self.response = None
		self._json_options = {}
		return

	def _query(self, urlpath, data, headers=None, timeout=None):
		""" Low-level query handling.
		.. note::
		   Use :py:meth:`query_private` or :py:meth:`query_public`
		   unless you have a good reason not to.
		:param urlpath: API URL path sans host
		:type urlpath: str
		:param data: API request parameters
		:type data: dict
		:param headers: (optional) HTTPS headers
		:type headers: dict
		:param timeout: (optional) if not ``None``, a :py:exc:`requests.HTTPError`
						will be thrown after ``timeout`` seconds if a response
						has not been received
		:type timeout: int or float
		:returns: :py:meth:`requests.Response.json`-deserialised Python object
		:raises: :py:exc:`requests.HTTPError`: if response status not successful
		"""
		if data is None:
			data = {}
		if headers is None:
			headers = {}

		url = self.uri + urlpath

		self.response = self.session.post(url, data = data, headers = headers, timeout = timeout)

		if self.response.status_code not in (200, 201, 202):
			self.response.raise_for_status()

		return self.response.json(**self._json_options)

	def _nonce(self):
		""" Nonce counter.
		:returns: an always-increasing unsigned integer (up to 64 bits wide)
		"""
		return int(1000*time.time())
			
	def _sign(self, data, urlpath):
		""" Sign request data according to Kraken's scheme.
		:param data: API request parameters
		:type data: dict
		:param urlpath: API URL path sans host
		:type urlpath: str
		:returns: signature digest
		"""
		postdata = urllib.parse.urlencode(data)

		# Unicode-objects must be encoded before hashing
		encoded = (str(data['nonce']) + postdata).encode()
		message = urlpath.encode() + hashlib.sha256(encoded).digest()

		signature = hmac.new(base64.b64decode(self.secret),
							 message, hashlib.sha512)
		sigdigest = base64.b64encode(signature.digest())

		return sigdigest.decode()
	
	def query_private(self, method, data=None, timeout=None):
		""" Performs an API query that requires a valid key/secret pair.
		:param method: API method name
		:type method: str
		:param data: (optional) API request parameters
		:type data: dict
		:param timeout: (optional) if not ``None``, a :py:exc:`requests.HTTPError`
						will be thrown after ``timeout`` seconds if a response
						has not been received
		:type timeout: int or float
		:returns: :py:meth:`requests.Response.json`-deserialised Python object
		"""
		if data is None:
			data = {}

		if not self.key or not self.secret:
			raise Exception('Either key or secret is not set!')

		data['nonce'] = self._nonce()

		urlpath = '/' + self.apiversion + '/private/' + method

		headers = {
			'API-Key': self.key,
			'API-Sign': self._sign(data, urlpath)
		}

		return self._query(urlpath, data, headers, timeout = timeout)
		
	
	def query_public(self, method, data=None, timeout=None):
		""" Performs an API query that does not require a valid key/secret pair.
		:param method: API method name
		:type method: str
		:param data: (optional) API request parameters
		:type data: dict
		:param timeout: (optional) if not ``None``, a :py:exc:`requests.HTTPError`
						will be thrown after ``timeout`` seconds if a response
						has not been received
		:type timeout: int or float
		:returns: :py:meth:`requests.Response.json`-deserialised Python object
		"""
		if data is None:
			data = {}

		urlpath = '/' + self.apiversion + '/public/' + method

		return self._query(urlpath, data, timeout = timeout)

ShowKeys=False
if str(sys.argv).find("ShowKeys") > 0:
	ShowKeys=True

print ()
print("You are about to test your Kraken API parameters...")

try:	
	
	if ShowKeys:
		API_KEY = input('Please enter your Kraken API Key: ')
	else:
		API_KEY = getpass.getpass('Please enter your Kraken API Key: ')
	# API Key override can be entered here, or typed at the command line above
	#API_KEY = ""

	if ShowKeys:
		API_SECRET = input('Please enter your Kraken API Secret: ')
	else:
		API_SECRET = getpass.getpass('Please enter your Kraken API Secret: ')
	# API Secret override can be entered here, or typed at the command line above
	#API_SECRET = ""

	kraken = KrakenAPI(API_KEY, API_SECRET)

	reply = kraken.query_private('Balance', None, 5)
	assert reply['error'] == []

	print("SUCCESS! Your Kraken API is working with your keys.")
	print ()
	print ("Your Kraken fiat & balance:")
	for x in reply['result']:
		if str(x)[0] == "Z":
			print(str(x)[1:] + ": " + str(reply['result'][x]))
	print ()
	print ("Your Kraken wallets & balances:")
	for x in reply['result']:
		if str(x)[0] == "X":
			print(str(x)[1:] + ": " + str(reply['result'][x]))

except KeyboardInterrupt:
	print (" ABORTING!")
except ConnectionError:
	print ("ERROR: Kraken refused to connect:" + str(sys.exc_info()))
except requests.Timeout:
	print ("ERROR: Timeout connecting to Kraken!")
except AssertionError:
	print ()
	print ("ERROR: Your API Keys failed! Code: " + str(reply['error']))
	if len(API_KEY) > 4:
		print ("Using KEY: "  + API_KEY[0:2] + "..." + API_KEY[-2:])
	else:
		print ("Bad KEY: " + API_KEY)
	if len(API_SECRET) > 4:
		print ("Using Secret: " + API_SECRET[0:2] + "..." + API_SECRET[-2:])
	else:
		print ("Bad Secret: " + API_SECRET)
except:
	print ("ERROR: Unknown failure testing Kraken auth: " + str(sys.exc_info()))

print ()
print ("exiting Kraken auth test...")
