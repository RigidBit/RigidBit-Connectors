# RigidBit-Connectors

These are the officially supported connectors of the primary [RigidBit](https://github.com/RigidBit/RigidBit) application. Connectors extend the functionality of RigidBit, allowing it to interface with services that are not part of the core application.

## Connectors

## ethereum.py

Ethereum / Ethereum Classic sync connector written in Python 3. This connector uses a local [Geth](https://geth.ethereum.org/) daemon to broadcast transactions.

## ethereum_infura.py

Ethereum / Ethereum Classic sync connector written in Python 3. This connector uses [Infura](https://infura.io/) to broadcast transactions.

## ethereum.sol

Ethereum / Ethereum Classic smart contract used by the connector scripts for storing and verifying RigidBit information.

## nervos

Nervos CKB (Layer 1) sync connector written in TypeScript. This connector relies on a local or remote [CKB Node](https://github.com/nervosnetwork/ckb/) and [CKB Indexer](https://github.com/nervosnetwork/ckb-indexer/) to build and broadcast transactions.

Usage:

- Copy the `nervos` folder and all contents to into you RigidBit connectors folder. This defaults to `~/.rigidbit/connectors`.
- Open a terminal to the `nervos` connector folder and install all dependencies with `npm i`.
- Generate a 0x prefixed 256-bit private key. This should be a new private key for this purpose only. Do not share this key with any other application.
- Fund the corresponding Nervos address for the private key with CKBytes. A supply of 500 CKBytes should be enough to last a very long time.
- Set the CKB_PRIVATE_KEY environment variable to your private key.
- Create a `[[sync_connector]]` config in your RigidBit `config.toml` with the following settings:

```toml
[[sync_connector]]
connector = "nervos/src/index.ts"
connector_id = "nervos-testnet"
connector_interpreter="ts-node"
connector_params = ""
connector_type = "nervos"
```

Note: The `connector_id` should be set to `nervos-testnet` when using the Aggron Testnet, or a Devnet, and just `nervos` when using the Mainnet.

- Create a `[sync]` config in your RigidBit `config.toml` with the following settings:

```toml
[[sync]]
enabled = true
connector_id = "nervos-testnet"
connector_type = "nervos"
on_demand = true
schedule = "0 0 * * * * *" # Cron style job schedule. (Default: 1 hour)
sync_at_launch = true
```

- Save `config.toml` and restart RigidBit to apply the settings.
