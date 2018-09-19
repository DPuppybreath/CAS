#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""
this is created and tested with Python 3.6.5
written 2018 by Chuck Wernicke for General Bytes

# Requires python-requests. Install with pip:
#	pip install requests
# or, with easy-install:
#	easy_install requests
"""
import sys, json, hmac, hashlib, time, requests, getpass

import uuid
import time

from decimal import *

if sys.version_info[0] < 3:
	print ("ERROR: Python version 3 is required to use this script!")
	print ("Install with: sudo apt install python3")
	print ()
	quit ()


V2URL="https://api.hitbtc.com/api/2"

class Client(object):
    def __init__(self, public_key, secret):
        self.url = V2URL
        self.session = requests.session()
        self.session.auth = (public_key, secret)

    def get_address(self, currency_code):
        """Get address for deposit."""
        return self.session.get("%s/account/crypto/address/%s" % (self.url, currency_code)).json()

    def get_account_balance(self):
        """Get main balance."""
        return self.session.get("%s/account/balance" % self.url).json()

    def get_trading_balance(self):
        """Get trading balance."""
        return self.session.get("%s/trading/balance" % self.url).json()
		
ShowKeys=False
if str(sys.argv).find("ShowKeys") > 0:
	ShowKeys=True

print ()
print("You are about to test your HitBTC API parameters...")

try:	
	if ShowKeys:
		API_KEY = input('Please enter your HitBTC API Key: ')
	else:
		API_KEY = getpass.getpass('Please enter your HitBTC API Key: ')
	# API Key override can be entered here, or typed at the command line above
	#API_KEY = ""

	if ShowKeys:
		API_SECRET = input('Please enter your HitBTC API Secret: ')
	else:
		API_SECRET = getpass.getpass('Please enter your HitBTC API Secret: ')
	# API Secret override can be entered here, or typed at the command line above
	#API_SECRET = ""

	client = Client(API_KEY, API_SECRET)
	reply = client.get_trading_balance()
	assert type(reply) is list
	print("SUCCESS! Your HitBTC API is working with your keys.")
	print ()

	print ("Your HitBTC trading balance:")
	Funded=False
	for x in reply:
		if float(x['available']) > 0:
			Funded=True
			print (x['currency'] + " avail: " + str(x['available']) + ", reserved: " + str(x['reserved']))
	if not Funded:
		print ("You have no funds in your trading accounts.")
	
	print ("Your HitBTC wallets & balances:")
	reply = client.get_account_balance()
	Funded=False
	for x in reply:
		if float(x['available']) > 0:
			Funded=True
			print (x['currency'] + " avail: " + str(x['available']) + ", reserved: " + str(x['reserved']))
	if not Funded:
		print ("You have no funds in your HitBTC wallets.")

	print ()

except KeyboardInterrupt:
	print (" ABORTING!")
except ConnectionError:
	print ("ERROR: HitBTC refused to connect:" + str(sys.exc_info()))
except requests.Timeout:
	print ("ERROR: Timeout connecting to HitBTC!")
except AssertionError:
	print ()
	print ("ERROR: Your API Keys failed! Code: " + str(reply['error']['code']))
	if len(API_KEY) > 4:
		print ("Using KEY: "  + API_KEY[0:2] + "..." + API_KEY[-2:])
	else:
		print ("Bad KEY: " + API_KEY)
	if len(API_SECRET) > 4:
		print ("Using Secret: " + API_SECRET[0:2] + "..." + API_SECRET[-2:])
	else:
		print ("Bad Secret: " + API_SECRET)
except:
	print ("ERROR: Unknown failure testing HitBTC auth: " + str(sys.exc_info()))

print ()
print ("exiting HitBTC auth test...")
