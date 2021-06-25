import PWCore, {Address, Amount, AmountUnit, Builder, Cell, RawTransaction, SUDT, Transaction} from "@lay2/pw-core";
import BasicCollector from "./BasicCollector";

export default class StoreBuilder extends Builder
{
	address: Address;
	collector: BasicCollector;
	fee: Amount;
	hash: string;

	constructor(address: Address, collector: BasicCollector, fee: Amount, hash: string)
	{
		super();

		this.address = address;
		this.collector = collector;
		this.fee = fee;
		this.hash = hash;
	}

	async build(): Promise<Transaction>
	{
		// Aliases
		const address = this.address;
		const collector = this.collector;
		const fee = this.fee;
		const hash = this.hash;

		// Arrays for our input cells, output cells, and cell deps, which will be used in the final transaction.
		const inputCells = [];
		const outputCells = [];
		const cellDeps = [];

		// Create the SUDT output cell.
		const lockScript = address.toLockScript();
		const cell = new Cell(new Amount('93', AmountUnit.ckb), lockScript, undefined, undefined, hash);
		outputCells.push(cell);

		// Calculate the required capacity. (SUDT cell + change cell minimum (61) + fee)
		const neededAmount = cell.capacity.add(new Amount('61', AmountUnit.ckb)).add(fee);

		// Add necessary capacity.
		const capacityCells = await collector.collectCapacity(address, neededAmount);
		for(const cell of capacityCells)
			inputCells.push(cell);

		// Calculate the input capacity and change cell amounts.
		const inputCapacity = inputCells.reduce((a, c)=>a.add(c.capacity), Amount.ZERO);
		const changeCapacity = inputCapacity.sub(neededAmount.sub(new Amount("61", AmountUnit.ckb)));

		// Add the change cell.
		const changeCell = new Cell(changeCapacity, lockScript);
		outputCells.push(changeCell);

		// Add the required cell deps.
		cellDeps.push(PWCore.config.defaultLock.cellDep);
		cellDeps.push(PWCore.config.pwLock.cellDep);

		// Generate a transaction and calculate the fee. (The second argument for witness args is needed for more accurate fee calculation.)
		const tx = new Transaction(new RawTransaction(inputCells, outputCells, cellDeps), [Builder.WITNESS_ARGS.RawSecp256k1]);
		this.fee = Builder.calcFee(tx);

		// Throw error if the fee is too low.
		if(this.fee.gt(fee))
			throw new Error(`Fee of ${fee} is below the calculated fee requirements of ${this.fee}.`);

		// Return our unsigned and non-broadcasted transaction.
		return tx;
	}
}
