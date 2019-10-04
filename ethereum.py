#!/usr/bin/env python3

import json
import sys

from web3.auto import w3

CONTRACT = "<INSERT CONTRACT ADDRESS HERE>"
ABI = json.loads('<INSERT ABI HERE>')
ACCOUNT = "<INSERT ACCOUNT ADDRESS HERE>"
PASSWORD = "<INSERT ACCOUNT PASSWORD HERE>"
UNLOCK_DURATION = 5 * 60

def unlockAccount():
	w3.personal.unlockAccount(ACCOUNT, PASSWORD, UNLOCK_DURATION)

def storeHash(hash):
	c = w3.eth.contract(address=CONTRACT, abi=ABI)
	try:
		tx_hash = c.functions.storeHash(hash).transact({"from": ACCOUNT})
		return tx_hash.hex()[2:]
	except:
		return -1

def verifyHash(hash):
	c = w3.eth.contract(address=CONTRACT, abi=ABI)
	try:
		return c.functions.getHash(hash).call()
	except:
		return -1

input = sys.stdin.read()
input = json.loads(input)

if "operation" not in data:
	raise Exception("Operation was not specified.")

elif input["operation"] == "store":
	unlockAccount()
	operationResult = storeHash(input["block_hash"])
	result = {}
	if operationResult == -1:
		result["success"] = False
	else:
		result["success"] = True
		result["contract"] = CONTRACT
		result["tx_hash"] = operationResult
	print(json.dumps(result))

elif input["operation"] == "verify":
	operationResult = verifyHash(input["block_hash"])
	result = {}
	if operationResult == -1:
		result = {}
		result["success"] = False
	else:
		result["success"] = True
		result["contract"] = CONTRACT
		result["timestamp"] = operationResult
	print(json.dumps(result))

else:
	raise Exception("Invalid operation specified.")
