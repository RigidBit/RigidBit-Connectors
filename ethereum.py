#!/usr/bin/env python3

import json
import sys

from web3.auto import w3

if len(sys.argv) != 2:
	raise Exception("There should be exactly one argument, and it should be a JSON string")

data = json.loads(sys.argv[1])

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

if "operation" not in data:
	raise Exception("Operation was not specified.")

elif data["operation"] == "store":
	unlockAccount()
	operationResult = storeHash(data["block_hash"])
	result = {}
	if operationResult == -1:
		result["success"] = False
	else:
		result["success"] = True
		result["contract"] = CONTRACT
		result["tx_hash"] = operationResult
	print(json.dumps(result))

elif data["operation"] == "verify":
	operationResult = verifyHash(data["block_hash"])
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
