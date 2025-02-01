from aptos_sdk.account import Account

private_key_hex = "pk here "
apt_account = Account.load_key(private_key_hex)
account_address = apt_account.address()
print(f"Account Address: {account_address}")
