import asyncio
from aptos_sdk.account import Account, AccountAddress
from aptos_sdk.async_client import RestClient
from aptos_sdk.transactions import (
    EntryFunction,
    TransactionArgument,
    TransactionPayload,
)
from aptos_sdk.type_tag import StructTag, TypeTag
from aptos_sdk.bcs import Serializer

rpc_url = "https://aptos.testnet.bardock.movementlabs.xyz/v1"
rest_client = RestClient(rpc_url)

private_key_hex = " " 
sender = Account.load_key(private_key_hex)

# Alamat penerima di move menggunakan wajib gunakan str_from 
recipient_address = AccountAddress.from_str("0x454583ccc18ffea9d0a3a007a8427c42c5410b8e192837fbb1cefcef79e3c492")
amount = 10000000000 # desimal di move di tulis dengan desimal *9


payload = EntryFunction.natural(
    "0x454583ccc18ffea9d0a3a007a8427c42c5410b8e192837fbb1cefcef79e3c492::gmoon_token",
    "transfer",
    [],
    [
        TransactionArgument(recipient_address, Serializer.struct),  # ✅ Perbaikan
        TransactionArgument(amount, Serializer.u64),
    ]
)


async def send_transaction():
    txn = await rest_client.create_bcs_transaction(sender, TransactionPayload(payload))
    signed_txn = sender.sign(txn)
    txn_hash = await rest_client.submit_bcs_transaction(signed_txn)
    print(f"Transaction Hash: {txn_hash}")
    await rest_client.wait_for_transaction(txn_hash)
    print(f"Transaction {txn_hash} confirmed!")

asyncio.run(send_transaction())
