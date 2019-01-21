#!/usr/bin/env python3

import json
import math
import requests
import sys

from eth_account import Account
from web3 import Web3, HTTPProvider

if len(sys.argv) != 2:
	raise Exception("There should be exactly one argument, and it should be a JSON string")

CONTRACT = "<INSERT CONTRACT ADDRESS HERE>"
ABI = json.loads('<INSERT ABI HERE>')
PRIVATE_KEY = "<INSERT PRIVATE KEY HERE>"
INFURA_URL = "https://mainnet.infura.io/v3/faea15762de14e49b3f46a9d85d215e7"

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
		unsigned = contract.functions.storeHash(data["block_hash"]).buildTransaction(tx_data)
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

data = json.loads(sys.argv[1])
infura = Web3(HTTPProvider(INFURA_URL))
w3 = Web3(Web3.IPCProvider("~/.ethereum/geth.ipc"))

if "operation" not in data:
	raise Exception("Operation was not specified.")

elif data["operation"] == "store":
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
