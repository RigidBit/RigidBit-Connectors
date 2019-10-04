#!/usr/bin/env python3

# pip3 install --user bitcoin
# pip3 install --user python-bitcoinrpc
# pip3 install --user simplejson

import bitcoin
import simplejson as json
import sys
import traceback

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decimal import *

RPC_URL = "<INSERT RPC URL HERE>"
RPC_USERNAME = "<INSERT RPC USERNAME HERE>"
RPC_PASSWORD = "<INSERT RPC PASSWORD HERE>"

ZEN_FEE = Decimal("0.0001") # The fee paid per transaction.

SHOW_EXCEPTIONS = len(sys.argv) == 3 and int(sys.argv[2]) == 1

def connect():
	try:
		return AuthServiceProxy(RPC_URL.replace("//", f"//{RPC_USERNAME}:{RPC_PASSWORD}@"))
	except Exception as e:
		return handle_exception(e)

def determine_inputs(rpc, amount):
	try:
		rpc = connect()
		unspent_inputs = rpc.listunspent()
		inputs = []
		input_amount = 0
		for unspent_input in unspent_inputs:
			inputs.append(unspent_input)
			input_amount += unspent_input["amount"]
			if input_amount >= amount:
				break
		if input_amount < amount:
			raise ValueError("Not enough funds are available to cover fees.")
		return inputs
	except Exception as e:
		return handle_exception(e)

def determine_outputs(rpc, inputs):
	try:
		change_address = rpc.getrawchangeaddress()
		change_amount = get_total_input_amount(inputs) - Decimal(ZEN_FEE)
		outputs = {}
		outputs[change_address] = change_amount
		return outputs
	except Exception as e:
		return handle_exception(e)

def get_total_input_amount(inputs):
	try:
		total = Decimal("0.0")
		for input in inputs:
			total += input["amount"]
		return total
	except Exception as e:
		return handle_exception(e)

def generate_check_block_bytes(rpc):
	try:
		height = rpc.getblockcount()
		target = height - 300
		hash = rpc.getblockhash(target)
		hash_bytes = bytearray.fromhex(hash)
		hash_bytes.reverse()
		target_bytes = target.to_bytes(3, byteorder="little")
		output = bytearray([len(hash_bytes)]) + hash_bytes + bytearray([len(target_bytes)]) + target_bytes + bytearray.fromhex("b4")
		return output
	except Exception as e:
		return handle_exception(e)

def generate_op_return_bytes(hex_data):
	try:
		data_bytes = bytearray.fromhex(hex_data)
		output = bytearray.fromhex("6a") + bytearray([len(data_bytes)]) + data_bytes
		return output
	except Exception as e:
		return handle_exception(e)

def generate_store_transaction(rpc, block_hash):
	try:
		inputs = determine_inputs(rpc, ZEN_FEE)
		outputs = determine_outputs(rpc, inputs)
		raw_tx = rpc.createrawtransaction(inputs, outputs)
		tx = bitcoin.deserialize(raw_tx)
		op_return = generate_op_return_bytes(block_hash)
		check_block = generate_check_block_bytes(rpc)
		op_return_tx = {"value": 0, "script": op_return.hex() + check_block.hex()}
		tx["outs"].append(op_return_tx)
		raw_tx = bitcoin.serialize(tx)
		signed_tx = rpc.signrawtransaction(raw_tx)
		if not ("complete" in signed_tx and signed_tx["complete"]):
			raise Exception("Unable to sign transaction.")
		return signed_tx
	except Exception as e:
		return handle_exception(e)

def handle_exception(e):
	if SHOW_EXCEPTIONS:
		raise e
	else:
		return -1

def pp(input):
	print(json.dumps(input, indent=4))

def store_hash(rpc, block_hash):
	try:
		raw_tx = generate_store_transaction(rpc, block_hash)
		txid = rpc.sendrawtransaction(raw_tx["hex"])
		return txid
	except Exception as e:
		return handle_exception(e)

def verify_hash(rpc, block_hash, tx_hash):
	try:
		tx = rpc.gettransaction(tx_hash)
		if tx["confirmations"] < 1:
			raise Exception("Transaction has not confirmed.")
		blocktime = tx["blocktime"]
		tx = rpc.decoderawtransaction(tx["hex"])
		valid = False
		for output in tx["vout"]:
			if output["scriptPubKey"]["hex"][0:4] == "6a20" and len(output["scriptPubKey"]["hex"]) >= 68 and output["scriptPubKey"]["hex"][4:68] == block_hash:
				valid = True
				break
		if valid:
			return blocktime
		else:
			return -1
	except Exception as e:
		return handle_exception(e)

input = sys.stdin.read()
input = json.loads(input)
rpc = connect()

if "operation" not in data:
	raise Exception("Operation was not specified.")

elif input["operation"] == "store":
	operationResult = store_hash(rpc, input["block_hash"])
	result = {}
	if operationResult == -1:
		result["success"] = False
	else:
		result["success"] = True
		result["tx_hash"] = operationResult
	print(json.dumps(result))

elif input["operation"] == "verify":
	operationResult = verify_hash(rpc, input["block_hash"], input["tx_hash"])
	result = {}
	if operationResult == -1:
		result = {}
		result["success"] = False
	else:
		result["success"] = True
		result["timestamp"] = operationResult
	print(json.dumps(result))

else:
	raise Exception("Invalid operation specified.")
