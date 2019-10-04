#!/usr/bin/env python3

import json
import math
import requests
import sys

from eth_account import Account
from web3 import Web3, HTTPProvider

CONTRACT = "<INSERT CONTRACT ADDRESS HERE>"
ABI = json.loads('<INSERT ABI HERE>')
PRIVATE_KEY = "<INSERT PRIVATE KEY HERE>"
INFURA_URL = "<INSERT INFURA URL HERE>"

def buildTxData():
	try:
		tx_data = {
			"gas": 150000,
			"gasPrice": infura.eth.gasPrice + 1,
			"nonce": infura.eth.getTransactionCount(Account.privateKeyToAccount(PRIVATE_KEY).address),
			"chainId": 1
		}
		return tx_data
	except:
		return -1

def storeHash(hash):
	try:
		tx_data = buildTxData()
		contract = infura.eth.contract(address=CONTRACT, abi=ABI)
		unsigned = contract.functions.storeHash(hash).buildTransaction(tx_data)
		signed = w3.eth.account.signTransaction(unsigned, PRIVATE_KEY)
		tx_hash = infura.eth.sendRawTransaction(signed.rawTransaction)
		return tx_hash.hex()[2:]
	except:
		return -1

def verifyHash(hash):
	contract = infura.eth.contract(address=CONTRACT, abi=ABI)
	try:
		return contract.functions.getHash(hash).call()
	except:
		return -1

input = sys.stdin.read()
input = json.loads(input)

infura = Web3(HTTPProvider(INFURA_URL))
w3 = Web3(Web3.IPCProvider("~/.ethereum/geth.ipc"))

if "operation" not in input:
	raise Exception("Operation was not specified.")

elif input["operation"] == "store":
	operationResult = storeHash(input["block_hash"])
	result = {}
	if operationResult == -1:
		result["success"] = False
	else:
		result["success"] = True
		result["address"] = CONTRACT
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
		result["address"] = CONTRACT
		result["timestamp"] = operationResult
	print(json.dumps(result))

else:
	raise Exception("Invalid operation specified.")
