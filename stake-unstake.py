import asyncio
import random
import httpx
from aptos_sdk.account import Account
from aptos_sdk.async_client import RestClient
from aptos_sdk.transactions import EntryFunction, TransactionArgument, TransactionPayload
from aptos_sdk.bcs import Serializer
from colorama import init, Fore

init(autoreset=True)

rpc_url = "https://testnet.bardock.movementnetwork.xyz/v1"
rest_client = RestClient(rpc_url)

async def check_txn_status(txn_hash: str):
    url = f"https://testnet.bardock.movementnetwork.xyz/v1/transactions/by_hash/{txn_hash}"
    async with httpx.AsyncClient() as client:
        for _ in range(60):
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get("success", False):
                    return True
                elif data.get("vm_status") != "Executed successfully":
                    print(f"{Fore.YELLOW}⚠️  VM Status: {data.get('vm_status')}")
                    return False
            await asyncio.sleep(1)
    return False

async def deposit(sender: Account, token_amount: int):
    try:
        amount = token_amount * 100_000_000  
        print(f"{Fore.GREEN}[*] Menandatangani dan mengirim transaksi dengan {token_amount} token (hstmove) untuk stake...")
        payload = EntryFunction.natural(
            module="0xf7429cda18fc0dd78d0dc48b102158024f1dc3a511a2a65ea553b5970d65b028::eigenfi_move_vault_hstmove",
            function="stake",
            ty_args=[],
            args=[TransactionArgument(amount, Serializer.u64)] 
        )

        signed_txn = await rest_client.create_bcs_signed_transaction(sender, TransactionPayload(payload))
        txn_hash = await rest_client.submit_bcs_transaction(signed_txn)
        print(f"{Fore.CYAN}[+] Transaction Hash (Stake): {txn_hash}")

        success = await check_txn_status(txn_hash)
        if success:
            print(f"{Fore.GREEN}[✓] Transaction {txn_hash} confirmed!")
        else:
            print(f"{Fore.RED}❌ ERROR: transaction {txn_hash} failed or timed out")
    except Exception as e:
        print(f"{Fore.RED}❌ ERROR:", e)

async def withdraw(sender: Account, token_amount: int):
    try:
        amount = token_amount * 100_000_000
        print(f"{Fore.GREEN}[*] Menandatangani dan mengirim transaksi withdraw dengan {token_amount} token (hstmove)...")
        payload = EntryFunction.natural(
            module="0xf7429cda18fc0dd78d0dc48b102158024f1dc3a511a2a65ea553b5970d65b028::eigenfi_move_vault_hstmove",
            function="unstake",
            ty_args=[],
            args=[TransactionArgument([amount], Serializer.sequence_serializer(Serializer.u64))]
        )
        signed_txn = await rest_client.create_bcs_signed_transaction(sender, TransactionPayload(payload))
        txn_hash = await rest_client.submit_bcs_transaction(signed_txn)
        print(f"{Fore.CYAN}[+] Transaction Hash (Withdraw): {txn_hash}")
        success = await check_txn_status(txn_hash)
        if success:
            print(f"{Fore.GREEN}[✓] Transaction {txn_hash} confirmed!")
        else:
            print(f"{Fore.RED}❌ ERROR: transaction {txn_hash} failed or timed out")

    except Exception as e:
        print(f"{Fore.RED}❌ ERROR: {e}")


async def main():
    while True:  
        with open("pk.txt") as f:
            for line in f:
                pk = line.strip()
                if pk:
                    sender = Account.load_key(pk)
                    token_amount = random.randint(1, 10)
                    await withdraw(sender, token_amount)
                    await asyncio.sleep(30)
                    await withdraw(sender, token_amount)
                    await asyncio.sleep(random.uniform(2, 5)) 
                await asyncio.sleep(random.uniform(2, 5))  

if __name__ == "__main__":
    asyncio.run(main())
