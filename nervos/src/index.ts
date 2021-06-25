'use strict';

import {stdin} from 'process';
import {AddressPrefix, privateKeyToAddress} from '@nervosnetwork/ckb-sdk-utils';
import PWCore, {Address, AddressType, Amount, AmountUnit, AddressPrefix as PwAddressPrefix, getDefaultPrefix, Provider, RawProvider} from '@lay2/pw-core';
import * as _ from 'lodash';

import BasicCollector from './BasicCollector';
import StoreBuilder from './StoreBuilder';

const CKB_PRIVATE_KEY = add0x(String(process.env.CKB_PRIVATE_KEY));
const CKB_RPC_URL = 'http://localhost:8114/';
const CKB_INDEXER_RPC_URL = 'http://localhost:8116/';
const CKB_TX_FEE = 10_000n;

interface PwObject
{
	pwCore: PWCore,
	provider: RawProvider,
	collector: BasicCollector,
}

interface ResultObject
{
	success?: boolean,
	tx_hash?: string,
	timestamp?: Number,
}

/**
 * Returns the contents of STDIN in a UTF-8 string.
 * 
 * Source: https://github.com/sindresorhus/get-stdin/blob/main/index.js
 * 
 * @returns A UTF-8 string.
 */
async function getStdin()
{
	let result = '';

	if(stdin.isTTY)
		return result;

	stdin.setEncoding('utf8');

	for await (const chunk of stdin)
		result += chunk;

	return result;
}

/**
 * Add the "0x" prefix to hashes if it isn't already present.
 * 
 * @param hash - A string containing a hash that may or may not be prefixed with "0x".
 * @returns A hash string that is prefixed with "0x".
 */
function add0x(hash: string)
{
	if(hash.substring(0, 2) !== '0x')
		return '0x'+hash;
	else
		return hash;
}

/**
 * Initialize PWCore, BasicCollector, and RawProvider.
 * 
 * @returns A PwObject containing an instances of PWCore, BasicCollector, and RawProvider.
 */
async function initPwCore(): Promise<PwObject>
{
	const provider = new RawProvider(CKB_PRIVATE_KEY);
	const collector = new BasicCollector(CKB_INDEXER_RPC_URL);
	const pwCore = await new PWCore(CKB_RPC_URL).init(provider, collector);

	return {pwCore, provider, collector};
}

async function store_hash(pw: PwObject, blockHash: string): Promise<string|Number>
{
	const collector = new BasicCollector(CKB_INDEXER_RPC_URL);
	const fee = new Amount(String(CKB_TX_FEE), AmountUnit.shannon);

	const pwPrefix = getDefaultPrefix();
	const prefix = (pwPrefix === PwAddressPrefix.ckb) ? AddressPrefix.Mainnet : AddressPrefix.Testnet;
	const addressString = privateKeyToAddress(CKB_PRIVATE_KEY, {prefix});
	const address = new Address(addressString, AddressType.ckb);
	// console.info(address.addressString);

	const builder = new StoreBuilder(address, collector, fee, add0x(blockHash));
	const transaction = await builder.build();
	// console.info(transaction);

	const txId = await pw.pwCore.sendTransaction(transaction);
	// console.info(`Transaction submitted: ${txId}`);

	return txId;
}

async function verify_hash(pw: PwObject, blockHash: string, txHash: string): Promise<Number>
{
	// Retrieve the status and data from the RPC.
	const txData = await pw.pwCore.rpc.get_transaction(txHash);
	const status = txData?.tx_status?.status;
	const data = txData?.transaction?.outputs_data?.[0];

	// Check if tx has not confirmed.
	if(status === 'pending' || status === 'proposed')
		throw new Error('Transaction has not confirmed.');
	if(status !== 'committed')
		throw new Error('Transaction not found.');

	// Verify that the block hash stored in the data area of the first cell in the transaction matches the specified block hash.
	if(add0x(blockHash) !== data)
		throw new Error('Stored block hash does not match specified block hash.');

	// Retrieve the timestamp from the RPC.
	const txBlockHash = txData?.tx_status?.block_hash;
	const blockData = await pw.pwCore.rpc.get_block(add0x(txBlockHash));
	const timestamp = Math.floor(Number(blockData?.header?.timestamp) / 1000);

	return timestamp;
}

async function main()
{
	// Parse the stdin data, which should be a JSON formatted string.
	const inputStdin = await getStdin();
	const input = JSON.parse(inputStdin);

	if(!_.has(input, 'operation'))
		throw new Error('Operation was not specified.');

	if(input.operation === 'store')
	{
		const pw = await initPwCore();
		const operationResult = await store_hash(pw, input["block_hash"])
		const result: ResultObject = {};
		if(operationResult === -1)
			result["success"] = false;
		else
		{
			result["success"] = true;
			result["tx_hash"] = String(operationResult);
		}

		process.stdout.write(JSON.stringify(result));
	}
	else if(input.operation === 'verify')
	{
		const pw = await initPwCore();
		const operationResult = await verify_hash(pw, input["block_hash"], input["tx_hash"])
		const result: ResultObject = {};
		if(operationResult === -1)
			result["success"] = false;
		else
		{
			result["success"] = true;
			result["timestamp"] = operationResult;
		}

		process.stdout.write(JSON.stringify(result));
	}
	else
		throw new Error('Invalid operation specified.');
}
main();
