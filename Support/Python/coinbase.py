#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""
this was created and tested with Python 3.6.5
2018 by Chuck Wernicke for General Bytes

Call this from BASH, currently "CheckAPI"

# Requires python-requests. Install with pip:
#   pip install requests
# or, with easy-install:
#   easy_install requests
"""

import sys, json, hmac, hashlib, time, requests, getpass
from requests.auth import AuthBase

if sys.version_info[0] < 3:
	print ("ERROR: Python version 3 is required to use this script!")
	print ("Install with: sudo apt install python3")
	print ()
	quit ()

api_user_url = 'https://api.coinbase.com/v2/user'
CBAPIVer = '2018-04-30'

ShowKeys=False
if str(sys.argv).find("ShowKeys") > 0:
	ShowKeys=True

print ()
print("You are about to test your Coinbase API parameters...")
try:	
	if ShowKeys:
		str_api_key = input('Please enter your Coinbase API Key:')
	else:
		str_api_key = getpass.getpass('Please enter your Coinbase API Key:')
	# API Key can be set as a var here, or typed at the command line above
	#str_api_key = ""
	API_KEY = bytearray(str_api_key.encode())

	if ShowKeys:
		str_secret = input('Please enter your Coinbase API Secret:')
	else:
		str_secret = getpass.getpass('Please enter your Coinbase API Secret:')
	# API Secret can be set as a var here, or typed at the command line above
	#str_secret = ""
	API_SECRET = bytearray(str_secret.encode())

	# Create custom authentication for Coinbase API
	class CoinbaseWalletAuth(AuthBase):
		def __init__(self, api_key, secret_key):
			self.api_key = api_key
			self.secret_key = secret_key

		def __call__(self, request):
			timestamp = str(int(time.time()))
			msg_utf = timestamp + request.method + request.path_url + (request.body or '')
			message = msg_utf.encode()
			signature = hmac.new(self.secret_key, message, hashlib.sha256).hexdigest()

			request.headers.update({
				'CB-ACCESS-SIGN': signature,
				'CB-ACCESS-TIMESTAMP': timestamp,
				'CB-ACCESS-KEY': self.api_key,
				'CB-VERSION': CBAPIVer
			})
			return request

	auth = CoinbaseWalletAuth(API_KEY, API_SECRET)

	# Get current user data
	reply = requests.get(api_user_url, auth=auth, timeout=5)
	# test the reply
	assert reply.status_code != 401
	if reply.status_code != 200:
		raise ConnectionError('bad reply: ' + str(reply.status_code))

	# at this point, all errors have been tested or addressed
	data = reply.json()
	print ()
	print("SUCCESS: Your Coinbase API is working with your keys.")
	print('User Name: ' + data['data']['name'])
	print('Default Fiat: ' + data['data']['native_currency'])

except KeyboardInterrupt:
	print (" ABORTING!")
except ConnectionError:
	print ("ERROR: Coinbase refused to connect:" + str(sys.exc_info()))
except requests.Timeout:
	print ("ERROR: Timeout connecting to Coinbase!")
except AssertionError:
	print ("ERROR: Your API Keys failed!")
	if len(str_api_key) > 4:
		print ("Using KEY: "  + str_api_key[0:2] + "..." + str_api_key[-2:])
	else:
		print ("Bad KEY: " + str_api_key)
	if len(str_secret) > 4:
		print ("Using Secret: " + str_secret[0:2] + "..." + str_secret[-2:])
	else:
		print ("Bad Secret: " + str_secret)
except:
	print ("ERROR: Unknown failure testing Coinbase auth: " + str(sys.exc_info()))

print ()
print ("exiting Coinbase auth test...")

"""
transaction['sender']['email']
Status codes:
    200 OK Successful request
    201 Created New object saved
    204 No content Object deleted
    400 Bad Request Returns JSON with the error message
    401 Unauthorized Couldn’t authenticate your request
    402 2FA Token required Re-try request with user’s 2FA token as CB-2FA-Token header
    403 Invalid scope User hasn’t authorized necessary scope
    404 Not Found No such object
    429 Too Many Requests Your connection is being rate limited
    500 Internal Server Error Something went wrong
    503 Service Unavailable Your connection is being throttled or the service is down for maintenance
"""
